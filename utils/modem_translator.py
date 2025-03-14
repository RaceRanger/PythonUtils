import serial
import time
import sys

CMD_FILE = "commands2.txt"
PORT = "COM49"
BAUD = 9600  # BAUD is now an integer

# Array of accepted responses
ACCEPTED_RESPONSES = ["OK", "CONNECT"]


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


def process_command(ser, command, command_number=None):
    """
    Sends a command to the serial device, reads the response in two parts,
    combines them (removing newlines), and prints the details.
    Returns the combined response.
    """
    if command_number:
        print("*" * 40)
        print(f"Command {command_number}: {command}")
    else:
        print("*" * 40)
        print(f"One-off command: {command}")

    ser.write((command + "\r\n").encode("utf-8"))
    # Optionally, allow a brief delay for the device to start responding
    time.sleep(0.2)

    response_part1 = read_response(ser, timeout=0.2)
    response_part2 = read_response(ser, timeout=3)

    print("Response part 1:", response_part1.strip())
    print("Response part 2:", response_part2.strip())

    final_response = response_part1 + response_part2
    # Replace newlines with a space so the response prints on one line.
    final_response = " ".join(final_response.splitlines())
    print("Combined Response:", final_response)
    return final_response


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
            combined_response = process_command(ser, command, command_number=total_commands)
            if combined_response:
                # Check if the combined response contains any accepted responses
                if not any(accepted in combined_response for accepted in ACCEPTED_RESPONSES):
                    print("Error detected for command:", command)
                    error_count += 1
                    error_commands.append((total_commands, command))
            else:
                print("No response received within 5 seconds for command:", command)
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
            combined_response = process_command(ser, command, command_number=total_commands)
            if combined_response:
                if not any(accepted in combined_response for accepted in ACCEPTED_RESPONSES):
                    print("Error detected for command:", command)
                    error_count += 1
                    error_commands.append((total_commands, command))
            else:
                print("No response received within 5 seconds for command:", command)
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
