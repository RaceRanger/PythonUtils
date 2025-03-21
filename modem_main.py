from constants import PDP_ACTIVATE_CMDS, MQTT_CONNECT_CMDS
from utils.modem_translator import write_commands


def main():
    write_commands(PDP_ACTIVATE_CMDS)
    write_commands(MQTT_CONNECT_CMDS)


if __name__ == "__main__":
    print("here")
    main()
