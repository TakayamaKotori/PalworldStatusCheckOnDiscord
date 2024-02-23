import configparser
from common import rcon, common, loggerUtil
import time

config_ini = common.getConfigFile()

logFilePath = config_ini["DEFAULT"]["BackupLogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)


def sendServerMessage(MessageText):
    logger.debug("sendServerMessage")
    try:
        rcon.callPalworldRcon(f"Broadcast {MessageText}")
    except Exception as e:
        logger.error("サーバーへメッセージ送信失敗")
        logger.error(e)


def main():
    sendServerMessage("The_server_will_restart_after_15_minutes.")
    time.sleep(60 * int(5))

    sendServerMessage("The_server_will_restart_after_10_minutes.")
    time.sleep(60 * int(5))

    sendServerMessage("The_server_will_restart_after_5_minutes.")
    time.sleep(60 * int(1))

    sendServerMessage("The_server_will_restart_after_4_minutes.")
    time.sleep(60 * int(1))

    sendServerMessage("The_server_will_restart_after_3_minutes.")
    time.sleep(60 * int(1))

    sendServerMessage("The_server_will_restart_after_2_minutes.")
    time.sleep(60 * int(1))

    sendServerMessage("The_server_will_restart_after_1_minutes.")
    time.sleep(60 * int(1))


if __name__ == "__main__":

    main()
