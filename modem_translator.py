import serial
import time

CMD_FILE = "commands.txt"
PORT = "COM46"
BAUD = "9600"


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
            # splitlines() removes the newline characters
            commands = f.read().splitlines()
    except Exception as e:
        print("Error reading commands file:", e)
        ser.close()
        return

    for command in commands:
        print("*" * 40)

        if command.strip() == "":
            continue  # Skip empty lines
        print(f"Sending command 1: {command}")
        # Write command followed by carriage return/newline
        ser.write((command + "\r\n").encode("utf-8"))
        # Wait 1 second for response
        time.sleep(1)
        response = ser.read_all().decode("utf-8", errors="replace")
        if response:
            print("Response:", response)
            if not response.__contains__("OK"):
                print("Error detected - early exit")
                break
        else:
            print("No response received.")

    ser.close()
    print("All commands processed.")


if __name__ == "__main__":
    main()
