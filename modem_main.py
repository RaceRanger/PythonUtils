"""
Activate PDP and MQTT contexts and run the publish/subscribe example.

This module imports command constants for PDP activation and MQTT connection, then uses the
modem_translator to send those commands. If both command sequences are successful, it runs the
publish/subscribe example.
"""

from constants import PDP_ACTIVATE_CMDS, MQTT_CONNECT_CMDS, MQTT_CONFIGURE_CMDS
from utils.modem_translator import write_commands
from utils.pub_sub_example import run_transmit, run_receive


def main():
    """
    Activate PDP and MQTT contexts and run the publish/subscribe example.

    Send the PDP activation commands and, if successful, send the MQTT connection commands.
    If both command sequences are successful, run the publish/subscribe example.
    """
    # Activate PDP context.

    write_commands(PDP_ACTIVATE_CMDS)

    write_commands(MQTT_CONFIGURE_CMDS)
    # Activate MQTT context.
    write_commands(MQTT_CONNECT_CMDS)

    # Run the publish/subscribe example.
    run_transmit()
    run_receive()


if __name__ == "__main__":
    print("here")
    main()
