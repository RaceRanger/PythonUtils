# test_serial_script.py
import io
import unittest
from unittest.mock import mock_open, patch

# Import functions from your main script file.
# Make sure your file is named "serial_script.py" or adjust the import accordingly.
from utils.modem_translator import main, read_response


# A FakeSerial class to simulate a serial port for testing.
class FakeSerial:
    def __init__(self, responses=None):
        # responses is a list of byte strings that will be provided sequentially.
        self.responses = responses or []
        self.buffer = b""
        self.written = []  # Keep track of written data for verification

    @property
    def in_waiting(self):
        return len(self.buffer)

    def read(self, n):
        data = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return data

    def write(self, data):
        self.written.append(data)
        # Simulate an immediate device response if one is queued.
        if self.responses:
            self.buffer += self.responses.pop(0)

    def close(self):
        pass


class TestSerialScript(unittest.TestCase):
    def test_read_response_immediate(self):
        """Test that read_response returns the data immediately when available."""
        fake_serial = FakeSerial(responses=[b"OK\n"])
        # Trigger the queuing of the response by calling write (even with empty data)
        fake_serial.write(b"")
        response = read_response(fake_serial, timeout=5)
        self.assertIn("OK", response)

    def test_read_response_timeout(self):
        """Test that read_response returns an empty string if no data arrives."""
        fake_serial = FakeSerial(responses=[])
        # Use a short timeout so the test runs quickly.
        response = read_response(fake_serial, timeout=0.2)
        self.assertEqual(response, "")

    @patch("builtins.open", new_callable=mock_open, read_data="CMD1\nCMD2")
    @patch("serial.Serial")
    def test_main_all_ok(self, mock_serial_class, mock_file):
        """
        Test main() when all commands return a response containing "OK".
        The fake serial object will return "OK\n" for each command.
        """
        fake_serial = FakeSerial(responses=[b"OK\n", b"OK\n"])
        mock_serial_class.return_value = fake_serial

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn("Connected to", output)
            self.assertIn("Sending command: CMD1", output)
            self.assertIn("Response: OK", output)
            self.assertIn("Sending command: CMD2", output)
            self.assertIn("Response: OK", output)
            self.assertIn("All commands processed.", output)

    @patch("builtins.open", new_callable=mock_open, read_data="CMD1\nCMD2")
    @patch("serial.Serial")
    def test_main_error_response(self, mock_serial_class, mock_file):
        """
        Test main() when one of the commands returns an error response.
        In this case, the first command returns "OK\n" and the second returns "ERROR\n",
        causing an early exit.
        """
        fake_serial = FakeSerial(responses=[b"OK\n", b"ERROR\n"])
        mock_serial_class.return_value = fake_serial

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn("Sending command: CMD1", output)
            self.assertIn("Response: OK", output)
            self.assertIn("Sending command: CMD2", output)
            self.assertIn("Response: ERROR", output)
            self.assertIn("Error detected - early exit", output)


if __name__ == "__main__":
    unittest.main()
