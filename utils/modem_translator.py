import sys
import time
import serial
from constants import ACCEPTED_RESPONSES, BAUD, PORT

# Default timeout in seconds if none is provided in the command file.
DEFAULT_TIMEOUT = 5


def read_response(ser, timeout=5):
    """
    Waits for a response from the serial device until either a newline is received
    or the timeout (in seconds) is reached. Returns the response as a string.
    """
    start_time = time.time()
    response = ""
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting).decode("utf-8", errors="replace")
            if "\n" in response:
                break
        time.sleep(0.1)  # Avoid busy waiting
    return response


def connect_serial():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return None
    return ser


def get_commands(cmd_file):
    """
    Retrieves commands from a file.
    Each line in the file should be in the format:
      COMMAND;TIMEOUT
    where TIMEOUT is the response timeout in seconds.
    If a line does not contain a semicolon, a default timeout is used.
    Returns a list of tuples: (command, timeout)
    """
    try:
        with open(cmd_file, "r") as f:
            lines = f.read().splitlines()
        commands = []
        for line in lines:
            if not line.strip():
                continue  # Skip empty lines
            if ";" in line:
                parts = line.split(";", 1)
                cmd = parts[0].strip()
                try:
                    t_out = float(parts[1].strip())
                except ValueError:
                    print(f"Invalid timeout value in line: {line}. Using default {DEFAULT_TIMEOUT} sec.")
                    t_out = DEFAULT_TIMEOUT
            else:
                cmd = line.strip()
                t_out = DEFAULT_TIMEOUT
            commands.append((cmd, t_out))
        print("Processing commands from file:", cmd_file)
        return commands
    except Exception as e:
        print("Error reading commands file:", e)
        return None


def handle_certificate_upload(ser, command, timeout):
    """
    Handles certificate upload by waiting for the CONNECT response
    and then transmitting the file data.
    """
    # Wait for the CONNECT prompt with the specified timeout
    response = read_response(ser, timeout=timeout)
    if "CONNECT" in response:
        start_idx = command.find("UFS:") + len("UFS:")
        end_idx = command.find('"', start_idx)
        file_name = command[start_idx:end_idx]
        try:
            with open(f"certs/{file_name}", "rb") as f:
                file_data = f.read()
            print(f"Transmitting file: {file_name} ({len(file_data)} bytes)")
            ser.write(file_data)
        except Exception as file_error:
            print(f"Error reading file {file_name}: {file_error}")
    else:
        print("Did not receive CONNECT prompt within timeout for certificate upload.")


def filter_echo(response, command):
    # Remove the echoed command from the beginning of the response, if present.
    if response.startswith(command):
        # Remove the command text and any leading/trailing whitespace.
        return response[len(command) :].strip()
    return response.strip()


def process_command(ser, command, timeout, command_number):
    """
    Processes a single command by sending it to the modem,
    handling certificate uploads if necessary,
    reading responses using the specified timeout,
    and checking for errors.
    Returns True if an error was detected, False otherwise.
    """
    print("*" * 40)
    print(f"Command {command_number}: {command} (timeout: {timeout} sec)")
    ser.write((command + "\r\n").encode("utf-8"))

    # Check for certificate upload command.
    if command.startswith('AT+QFUPL="UFS:'):
        handle_certificate_upload(ser, command, timeout)

    # Use the command's timeout for reading responses.
    response_part1 = read_response(ser, timeout=timeout)
    response_part2 = read_response(ser, timeout=timeout)

    # Filter out echoed command text
    filtered_response1 = filter_echo(response_part1.strip(), command)
    filtered_response2 = filter_echo(response_part2.strip(), command)

    print("Response part 1:", filtered_response1)
    print("Response part 2:", filtered_response2)

    combined_response = filtered_response1 + "\n" + filtered_response2
    print("Combined Response:", combined_response.strip())

    # Determine if there is an error.
    if combined_response:
        if not any(accepted in combined_response for accepted in ACCEPTED_RESPONSES):
            print("Error detected for command:", command)
            return True
    else:
        print("No response received within timeout for command:", command)
        return True

    return False


def write_commands(cmd_file):
    """
    Connects to the modem, retrieves commands (with associated timeouts),
    processes each command, and prints a summary of any errors encountered.
    """
    ser = connect_serial()
    if not ser:
        return

    commands = get_commands(cmd_file)
    if commands is None:
        ser.close()
        return

    error_count = 0
    error_commands = []
    total_commands = 0

    for command, timeout in commands:
        total_commands += 1
        if process_command(ser, command, timeout, total_commands):
            error_count += 1
            error_commands.append((total_commands, command))

    ser.close()

    print("All commands processed.")
    print(f"Total commands processed: {total_commands}, Errors: {error_count}")

    if error_commands:
        print("\nErrored Commands:")
        for num, cmd in error_commands:
            print(f"{num}. {cmd}")
        return True
    else:
        print("\nNo errors detected.")
        return False
