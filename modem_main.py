from constants import PDP_ACTIVATE_CMDS, MQTT_CONNECT_CMDS
from utils.modem_translator import write_commands
from utils.pub_sub_example import run

err = False


def main():
    # activate PDP context
    err = write_commands(PDP_ACTIVATE_CMDS)
    if err:
        return

    # activate MQTT context
    err = write_commands(MQTT_CONNECT_CMDS)
    if err:
        return

    # run our example publish/subscribe
    run()


if __name__ == "__main__":
    print("here")
    main()
