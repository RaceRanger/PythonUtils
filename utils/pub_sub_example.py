import time
import serial

from constants import PORT, PUBLISH_TOPIC, BAUD


def run_transmit():
    """
    Connect to the modem and publish test messages.

    Connect to the modem using the configured PORT and BAUD rate.
    Publish 10 test messages to the specified PUBLISH_TOPIC.
    Each message is sent using the AT+QMTPUBEX command followed by the message payload.
    """
    print(10*'*')
    print("RUNNING TRANSMIT TEST")
    print(10*'*')

    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return

    try:
        for i in range(11):
            message = f"Topic: {PUBLISH_TOPIC} Publish test {i} of 10"
            payload_length = len(message) + 1
            command = f"AT+QMTPUBEX=0,1,1,0,{PUBLISH_TOPIC},{payload_length}"

            # Send the publish command.
            err = ser.write((command + "\r\n").encode("utf-8"))
            
            time.sleep(0.2)  # Allow modem to respond with a prompt.

            # Send the actual message payload.
            err = ser.write((message + "\r\n").encode("utf-8"))
            print(f"Published: {message}")

            time.sleep(1)  # Wait before publishing the next message.
    finally:
        ser.close()
        print("Serial connection closed.")

def run_receive():
    """
    Connect to the modem and publish test messages.

    Connect to the modem using the configured PORT and BAUD rate.
    Publish 10 test messages to the specified PUBLISH_TOPIC.
    Each message is sent using the AT+QMTPUBEX command followed by the message payload.
    """
    print(10*'*')
    print("RUNNING RECEIVE TEST")
    print(10*'*')
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT} at {BAUD} baud.")
    except Exception as e:
        print("Error connecting to serial port:", e)
        return

    try:
        while True:
            print(ser.read(100))
            time.sleep(1)
    finally:
        ser.close()
        print("Serial connection closed.")


if __name__ == "__main__":
    run()
