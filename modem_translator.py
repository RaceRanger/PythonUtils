import serial
import time

CMD_FILE = "commands.txt"
PORT = "COM46"
BAUD = 9600  # Note: BAUD is now an integer


def read_response(ser, timeout=5):
    """
    Waits for a response from the serial device until either a newline is received
    or the timeout (in seconds) is reached. Returns the response as a string.
    """
    start_time = time.time()
    response = ""

    # Continue reading until timeout
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            # Read all available data
            response += ser.read(ser.in_waiting).decode("utf-8", errors="replace")
            # Optionally, if your response always terminates with a newline, you can break
            if "\n" in response:
                break
        time.sleep(0.1)  # Avoid busy waiting
    return response


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return

    # Read commands from a file named "commands.txt"
    try:
        with open(CMD_FILE, "r") as f:
            commands = f.read().splitlines()
    except Exception as e:
        print("Error reading commands file:", e)
        ser.close()
        return

    for command in commands:
        print("*" * 40)
        if command.strip() == "":
            continue  # Skip empty lines

        print(f"Sending command: {command}")
        ser.write((command + "\r\n").encode("utf-8"))

        # Wait up to 5 seconds for a response
        response = read_response(ser, timeout=5)
        if response:
            print("Response:", response.strip())
            # Check for success indicator in response
            if "OK" not in response:
                print("Error detected - early exit")
                break
        else:
            print("No response received within 5 seconds. Exiting.")
            break

    ser.close()
    print("All commands processed.")


if __name__ == "__main__":
    main()
