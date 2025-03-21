import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import time

# Import the functions and constants from your module.
import utils.modem_translator as modem


# A simple fake serial class to simulate in_waiting and read() behavior.
class FakeSerial:
    def __init__(self, responses):
        # 'responses' is a list of strings that will be returned in sequence.
        self.responses = responses[:]  # copy of responses
        self.index = 0

    @property
    def in_waiting(self):
        if self.index < len(self.responses):
            return len(self.responses[self.index])
        return 0

    def read(self, n):
        if self.index < len(self.responses):
            data = self.responses[self.index][:n]
            self.responses[self.index] = self.responses[self.index][n:]
            if not self.responses[self.index]:
                self.index += 1
            return data.encode("utf-8")
        return b""


class TestModemFunctions(unittest.TestCase):
    @patch("time.sleep", return_value=None)
    def test_read_response_complete(self, _):
        # Simulate a response that contains a newline.
        responses = ["Hello, World!\nExtra data"]
        fake_serial = FakeSerial(responses)
        result = modem.read_response(fake_serial, timeout=2)
        self.assertIn("Hello, World!", result)
        self.assertIn("\n", result)

    @patch("time.sleep", return_value=None)
    def test_read_response_timeout(self, _):
        # When no response is available, the function should eventually return an empty string.
        responses = []
        fake_serial = FakeSerial(responses)
        start_time = time.time()
        result = modem.read_response(fake_serial, timeout=1)
        end_time = time.time()
        self.assertEqual(result, "")
        self.assertTrue(end_time - start_time >= 1)

    def test_connect_serial_success(self):
        fake_serial = MagicMock()
        # Patch the serial.Serial call in the correct module.
        with patch("utils.modem_translator.serial.Serial", return_value=fake_serial) as mock_serial:
            ser = modem.connect_serial()
            mock_serial.assert_called_with(modem.PORT, modem.BAUD, timeout=1)
            self.assertEqual(ser, fake_serial)

    def test_connect_serial_failure(self):
        # Simulate an exception when trying to create a serial connection.
        with patch("utils.modem_translator.serial.Serial", side_effect=Exception("Failed")):
            ser = modem.connect_serial()
            self.assertIsNone(ser)

    def test_get_commands_valid(self):
        file_content = "CMD1;3\nCMD2\n"
        m = mock_open(read_data=file_content)
        with patch("utils.modem_translator.open", m):
            commands = modem.get_commands("dummy_file.txt")
            expected = [("CMD1", 3.0), ("CMD2", modem.DEFAULT_TIMEOUT)]
            self.assertEqual(commands, expected)

    def test_get_commands_invalid_timeout(self):
        file_content = "CMD1;abc\n"
        m = mock_open(read_data=file_content)
        with patch("utils.modem_translator.open", m):
            commands = modem.get_commands("dummy_file.txt")
            expected = [("CMD1", modem.DEFAULT_TIMEOUT)]
            self.assertEqual(commands, expected)

    def test_get_commands_file_error(self):
        # Simulate an error when opening the file.
        with patch("utils.modem_translator.open", side_effect=Exception("File not found")):
            commands = modem.get_commands("dummy_file.txt")
            self.assertIsNone(commands)

    def test_handle_certificate_upload_success(self):
        fake_serial = MagicMock()
        fake_serial.write = MagicMock()
        file_data = b"certificate content"
        # Example command that instructs a certificate upload.
        command = 'AT+QFUPL="UFS:cert.pem"'
        # Simulate that the device returns a CONNECT prompt.
        with patch("utils.modem_translator.read_response", return_value="CONNECT\n"):
            # For binary file mode, use io.BytesIO to simulate file content.
            with patch("utils.modem_translator.open", return_value=io.BytesIO(file_data)) as m:
                modem.handle_certificate_upload(fake_serial, command, timeout=2)
                m.assert_called_with("certs/cert.pem", "rb")
                fake_serial.write.assert_called_with(file_data)

    def test_handle_certificate_upload_no_connect(self):
        fake_serial = MagicMock()
        fake_serial.write = MagicMock()
        command = 'AT+QFUPL="UFS:cert.pem"'
        # Simulate no CONNECT prompt returned.
        with patch("utils.modem_translator.read_response", return_value="NO CONNECT"):
            modem.handle_certificate_upload(fake_serial, command, timeout=2)
            fake_serial.write.assert_not_called()

    def test_filter_echo_with_echo(self):
        command = "AT+TEST"
        response = "AT+TEST OK"
        filtered = modem.filter_echo(response, command)
        self.assertEqual(filtered, "OK")

    def test_filter_echo_without_echo(self):
        command = "AT+TEST"
        response = "Some other response"
        filtered = modem.filter_echo(response, command)
        self.assertEqual(filtered, "Some other response")

    def test_process_command_success(self):
        fake_serial = MagicMock()
        fake_serial.write = MagicMock()
        # Use an accepted response from the constants; if none exist, use "OK".
        accepted_response = modem.ACCEPTED_RESPONSES[0] if modem.ACCEPTED_RESPONSES else "OK"
        # Patch read_response to return an accepted response in two parts.
        with patch("utils.modem_translator.read_response", side_effect=[accepted_response + "\n", "\n"]):
            error = modem.process_command(fake_serial, "AT+TEST", 2, 1)
            self.assertFalse(error)
            fake_serial.write.assert_called_with(("AT+TEST\r\n").encode("utf-8"))

    def test_process_command_error(self):
        fake_serial = MagicMock()
        fake_serial.write = MagicMock()
        # Simulate responses that do not include any accepted response.
        with patch("utils.modem_translator.read_response", side_effect=["ERROR\n", "\n"]):
            error = modem.process_command(fake_serial, "AT+FAIL", 2, 1)
            self.assertTrue(error)

    def test_process_command_certificate_upload(self):
        fake_serial = MagicMock()
        fake_serial.write = MagicMock()
        command = 'AT+QFUPL="UFS:cert.pem"'
        accepted_response = modem.ACCEPTED_RESPONSES[0] if modem.ACCEPTED_RESPONSES else "OK"
        # Patch the certificate upload handler to verify it gets called.
        with patch("utils.modem_translator.handle_certificate_upload") as mock_upload:
            with patch("utils.modem_translator.read_response", side_effect=[accepted_response + "\n", accepted_response + "\n"]):
                error = modem.process_command(fake_serial, command, 2, 1)
                self.assertFalse(error)
                mock_upload.assert_called_once_with(fake_serial, command, 2)

    def test_write_commands(self):
        fake_serial = MagicMock()
        fake_serial.close = MagicMock()
        commands = [("AT+TEST", 2), ("AT+FAIL", 2)]
        with patch("utils.modem_translator.connect_serial", return_value=fake_serial):
            with patch("utils.modem_translator.get_commands", return_value=commands):
                # Simulate the first command succeeding and the second failing.
                with patch("utils.modem_translator.process_command", side_effect=[False, True]) as mock_process:
                    modem.write_commands("dummy_file.txt")
                    self.assertEqual(mock_process.call_count, 2)
                    fake_serial.close.assert_called_once()

    def test_write_commands_no_commands(self):
        fake_serial = MagicMock()
        fake_serial.close = MagicMock()
        with patch("utils.modem_translator.connect_serial", return_value=fake_serial):
            with patch("utils.modem_translator.get_commands", return_value=None):
                modem.write_commands("dummy_file.txt")
                fake_serial.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
