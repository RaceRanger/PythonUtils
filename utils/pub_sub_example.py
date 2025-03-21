import time
import serial

from constants import PORT, PUBLISH_TOPIC, BAUD


def run():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return

    for i in range(10):
        message = f"Publish test {i} of 10"
        payload_length = len(message) + 1
        command = f"AT+QMTPUBEX=0,1,1,0,{PUBLISH_TOPIC},{payload_length}"

        # Send the publish command
        ser.write((command + "\r\n").encode("utf-8"))
        time.sleep(0.2)  # Small delay if the modem needs to respond with a prompt

        # # Send the actual message payload
        ser.write((message + "\r\n").encode("utf-8"))
        print(f"Published: {message}")

        # # Wait 5 seconds before publishing again

        # ser.reset_input_buffer()
        # ser.reset_output_buffer()
        time.sleep(1)
