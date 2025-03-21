import serial
import time
import sys

CMD_FILE = "commands/test_cmds.txt"
PORT = "COM49"
BAUD = 9600  # BAUD is now an integer

# Array of accepted responses
ACCEPTED_RESPONSES = ["OK", "CONNECT", "+QFUPL"]


def read_response(ser, timeout=5):
    """
    Waits for a response from the serial device until a newline is received
    or the timeout (in seconds) is reached. Returns the response as a string.
    """
    start_time = time.time()
    response = ""
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting).decode("utf-8", errors="replace")
            # If a newline is received, break out of the loop.
            if "\n" in response:
                break
        time.sleep(0.1)  # Avoid busy waiting
    return response


def process_command(ser, command, command_number=None):
    """
    Sends a command to the serial device, waits for a response (until newline),
    and if the command is one of the certificate upload commands, opens and
    transmits the respective certificate file.
    Returns the initial response.
    """
    if command_number:
        print("*" * 40)
        print(f"Command {command_number}: {command}")
    else:
        print("*" * 40)
        print(f"One-off command: {command}")

    # Send the command (including the required newline/carriage return)
    ser.write((command + "\r\n").encode("utf-8"))
    # Allow a brief delay for the device to start responding
    time.sleep(0.2)

    # Read the initial response from the modem
    response = read_response(ser, timeout=5)
    print("Response:", response.rstrip())

    # Check if the command is a certificate upload command
    if command.startswith('AT+QFUPL="UFS:'):
        # Extract the file name from the command (e.g., cacert.pem, client.pem, or user_key.pem)
        try:
            start_idx = command.find("UFS:") + len("UFS:")
            end_idx = command.find('"', start_idx)
            file_name = command[start_idx:end_idx]
            # Only process if it's one of the expected cert files
            if file_name in ["cacert.pem", "client.pem", "user_key.pem"]:
                try:
                    with open(file_name, "rb") as f:
                        file_data = f.read()
                    print(f"Transmitting file: {file_name} ({len(file_data)} bytes)")
                    ser.write(file_data)
                    # Optional: Wait for a post-transfer response from the modem
                    post_transfer_response = read_response(ser, timeout=5)
                    print("Response after file transmission:", post_transfer_response.rstrip())
                except Exception as file_error:
                    print(f"Error reading file {file_name}: {file_error}")
        except Exception as parse_error:
            print(f"Error parsing certificate file from command: {parse_error}")

    return response


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return

    error_count = 0
    error_commands = []  # List to store tuples (command number, command text)
    total_commands = 0

    # Check if command-line arguments are provided; use them as commands.
    if len(sys.argv) > 1:
        commands = sys.argv[1:]
        print("Processing commands from command-line arguments:")
        for idx, command in enumerate(commands, start=1):
            total_commands += 1
            response = process_command(ser, command, command_number=total_commands)
            if response:
                # Check if the response contains any accepted responses
                if not any(accepted in response for accepted in ACCEPTED_RESPONSES):
                    print("Error detected for command:", command)
                    error_count += 1
                    error_commands.append((total_commands, command))
            else:
                print("No response received for command:", command)
                error_count += 1
                error_commands.append((total_commands, command))
    else:
        # Otherwise, read commands from the file
        try:
            with open(CMD_FILE, "r") as f:
                commands = f.read().splitlines()
        except Exception as e:
            print("Error reading commands file:", e)
            ser.close()
            return

        for idx, command in enumerate(commands, start=1):
            if command.strip() == "":
                continue  # Skip empty lines
            total_commands += 1
            response = process_command(ser, command, command_number=total_commands)
            if response:
                if not any(accepted in response for accepted in ACCEPTED_RESPONSES):
                    print("Error detected for command:", command)
                    error_count += 1
                    error_commands.append((total_commands, command))
            else:
                print("No response received for command:", command)
                error_count += 1
                error_commands.append((total_commands, command))

    ser.close()
    print("All commands processed.")
    print(f"Total commands processed: {total_commands}, Errors: {error_count}")

    if error_commands:
        print("\nErrored Commands:")
        for num, cmd in error_commands:
            print(f"{num}. {cmd}")
    else:
        print("\nNo errors detected.")


if __name__ == "__main__":
    main()
