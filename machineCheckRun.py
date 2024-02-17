import discord
import asyncio
from common import loggerUtil, common, macineCheck


log_config_ini = common.getConfigFile()
logFilePath = log_config_ini["DEFAULT"]["MacineCheckLogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)


def getConfigFile():
    logger.debug("getConfigFile")
    global MacineStatusPostChannel, CheckIntervalMin, NomalCheckInterval

    config_ini = common.getConfigFile()

    MacineStatusPostChannel = int(config_ini["DEFAULT"]["MacineStatusPostChannel"])

    CheckIntervalMin = config_ini["DEFAULT"]["CheckIntervalMin"]

    NomalCheckInterval = 60 * int(CheckIntervalMin)


# Intentsを定義
intents = discord.Intents.default()
intents.all()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.debug("on_ready")
    while True:
        getConfigFile()
        await macineCheck.run(logger, client, MacineStatusPostChannel)

        # 次のチェックまで一時停止
        await asyncio.sleep(NomalCheckInterval)


def main():
    config_ini = common.getConfigFile()

    DiscordBotToken = config_ini["DEFAULT"]["DiscordBotToken"]
    client.run(DiscordBotToken)


if __name__ == "__main__":
    main()
