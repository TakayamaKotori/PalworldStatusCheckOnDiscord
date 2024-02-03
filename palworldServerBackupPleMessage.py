import configparser
from common import rcon, loggerUtil
import asyncio

config_ini = configparser.ConfigParser()
config_ini.read("setting.ini", encoding="utf-8")


logFilePath = config_ini["DEFAULT"]["BackupLogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)


def sendServerMessage(MessageText):
    logger.debug("getServerVersion")
    try:
        rcon.callPalworldRcon(f"/Broadcast {MessageText}")
    except Exception as e:
        logger.error("サーバーへメッセージ送信失敗")
        logger.error(e)


async def main():
    sendServerMessage("The server will restart after 15 minutes.")
    await asyncio.sleep(60 * int(5))

    sendServerMessage("The server will restart after 10 minutes.")
    await asyncio.sleep(60 * int(5))

    sendServerMessage("The server will restart after 5 minutes.")
    await asyncio.sleep(60 * int(1))

    sendServerMessage("The server will restart after 4 minutes.")
    await asyncio.sleep(60 * int(1))

    sendServerMessage("The server will restart after 3 minutes.")
    await asyncio.sleep(60 * int(1))

    sendServerMessage("The server will restart after 2 minutes.")
    await asyncio.sleep(60 * int(1))

    sendServerMessage("The server will restart after 1 minutes.")
    await asyncio.sleep(60 * int(1))


if __name__ == "__main__":

    main()
