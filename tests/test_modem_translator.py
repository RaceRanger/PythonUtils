import unittest
from unittest.mock import patch, mock_open
import io
import sys

# Import functions and constants from your module in the utils folder.
from utils.modem_translator import read_response, process_command, main, ACCEPTED_RESPONSES, PORT, BAUD


class FakeSerial:
    """
    A FakeSerial that simulates a serial port by returning a sequence of responses.
    Each call to read() returns the next response in the list.
    """

    def __init__(self, responses=None):
        self.responses = responses[:] if responses else []
        self.read_count = 0
        self.written = []

    @property
    def in_waiting(self):
        # If there's a response available, return its length.
        if self.read_count < len(self.responses):
            return len(self.responses[self.read_count])
        return 0

    def read(self, n):
        # Return the entire next response regardless of n.
        if self.read_count < len(self.responses):
            data = self.responses[self.read_count]
            self.read_count += 1
            return data.encode("utf-8")
        return b""

    def write(self, data):
        self.written.append(data)
        # For testing, write() does not trigger an automatic response.

    def close(self):
        pass


class TestModemTranslator(unittest.TestCase):
    @patch("time.sleep", lambda x: None)
    def test_read_response(self):
        """Test that read_response returns the expected response when data is available."""
        fake_serial = FakeSerial(responses=["OK\n"])
        response = read_response(fake_serial, timeout=2)
        self.assertIn("OK", response)

    def test_process_command(self):
        """Test that process_command correctly combines two parts of a response."""
        responses = ["OK\n", "+QMTOPEN: 0,-1\n"]
        fake_serial = FakeSerial(responses=responses)
        combined_response = process_command(fake_serial, 'AT+QMTOPEN=0,"server",8883')
        expected_response = "OK +QMTOPEN: 0,-1"
        self.assertEqual(combined_response.strip(), expected_response)

    @patch("utils.modem_translator.serial.Serial")
    @patch("utils.modem_translator.open", new_callable=mock_open, read_data="AT+CMD1\nAT+CMD2\n")
    def test_main_with_file(self, mock_file, mock_serial_class):
        """
        Test main() when no command-line arguments are provided and commands are read from a file.
        For two commands, supply four responses so each command receives two parts.
        """
        # For command1: two responses; for command2: two responses.
        fake_serial = FakeSerial(responses=["OK\n", "CONNECT\n", "OK\n", "CONNECT\n"])
        mock_serial_class.return_value = fake_serial

        # Simulate running without additional command-line arguments.
        test_args = ["modem_translator.py"]
        with patch("sys.argv", test_args):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                # Both commands should be processed with acceptable responses.
                self.assertIn("Total commands processed: 2", output)
                self.assertIn("No errors detected", output)

    @patch("utils.modem_translator.serial.Serial")
    def test_main_with_args(self, mock_serial_class):
        """
        Test main() when command-line arguments are provided.
        Simulate two one-off commands passed as arguments.
        """
        # For command1: simulate two responses; for command2: simulate two responses.
        responses = ["OK\n", "+QMTOPEN: 0,0\n", "CONNECT\n", "OK\n"]
        fake_serial = FakeSerial(responses=responses)
        mock_serial_class.return_value = fake_serial

        test_args = ["modem_translator.py", "AT+CMD1", "AT+CMD2"]
        with patch("sys.argv", test_args):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("Processing commands from command-line arguments", output)
                self.assertIn("Command 1: AT+CMD1", output)
                self.assertIn("Command 2: AT+CMD2", output)
                self.assertIn("No errors detected", output)


if __name__ == "__main__":
    unittest.main()
