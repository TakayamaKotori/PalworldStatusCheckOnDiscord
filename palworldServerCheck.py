import discord
import csv
from datetime import datetime, timedelta, timezone
import os
import re
from common import rcon, common, discordTextMessage, loggerUtil, macineCheck
import asyncio
import pandas as pd
from croniter import croniter
import pytz


log_config_ini = common.getConfigFile()
logFilePath = log_config_ini["DEFAULT"]["LogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)

saveCsvPath = "palworldplayers.csv"


beforeLoginData = []
severVersion = "-"

nameColumn = 0
playeruidColumn = 1
steamidColumn = 2

logintimeColumnName = "logintime"
logintimeColumn = 3

serverOnline = False

CheckInterval = 60 * int(5)

# バージョンを抜き出す正規表現
# "Welcome to Pal Server[v0.1.3.0] Takayama's Palworld Server"
reg = "(?<=\[).+?(?=\])"


def getConfigFile():
    logger.debug("getConfigFile")
    global StatusPostChannel, LogPostChannel, MacineStatusPostChannel, StatusEditMessageId
    global CheckIntervalMin, ErrorCheckIntervalMin
    global StatusPostTitle, StatusAuthorImageUrl, StatusThumbnailUrl, StatusImage
    global MaxPlayer, NomalCheckInterval, ErrorCheckInterval
    global crontab1, crontab2

    config_ini = common.getConfigFile()

    LogPostChannel = int(config_ini["DEFAULT"]["LogPostChannel"])
    MacineStatusPostChannel = int(config_ini["DEFAULT"]["MacineStatusPostChannel"])
    StatusPostChannel = int(config_ini["DEFAULT"]["StatusPostChannel"])
    StatusEditMessageId = int(config_ini["DEFAULT"]["StatusEditMessage"])

    CheckIntervalMin = config_ini["DEFAULT"]["CheckIntervalMin"]
    ErrorCheckIntervalMin = config_ini["DEFAULT"]["ErrorCheckIntervalMin"]

    StatusPostTitle = config_ini["DEFAULT"]["StatusPostTitle"]

    StatusAuthorImageUrl = config_ini["DEFAULT"]["StatusAuthorImageUrl"]
    StatusThumbnailUrl = config_ini["DEFAULT"]["StatusThumbnailUrl"]
    StatusImage = config_ini["DEFAULT"]["StatusImage"]

    MaxPlayer = config_ini["DEFAULT"]["MaxPlayer"]

    NomalCheckInterval = 60 * int(CheckIntervalMin)
    ErrorCheckInterval = 60 * int(ErrorCheckIntervalMin)

    crontab1 = config_ini["DEFAULT"]["crontab1"]
    crontab2 = config_ini["DEFAULT"]["crontab2"]


def readPlayersCsvRows():
    logger.debug("readPlayersCsvRows")
    """
    初回のみCSVの物理データを読み込み
    """

    global beforeLoginData
    # 前回データ読み込み
    is_file = os.path.isfile(saveCsvPath)
    if is_file:
        with open(saveCsvPath) as f:
            reader = csv.reader(f)
            l = [row for row in reader]
            # グローバル変数へ保存
            beforeLoginData = l
    else:
        beforeLoginData = [["name", "playeruid", "steamid", "logintime"]]


readPlayersCsvRows()


def listWriteCsv(list):
    logger.debug("listWriteCsv")

    with open(saveCsvPath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(list)


def getServerVersion():
    logger.debug("getServerVersion")
    global severVersion, serverOnline
    try:
        welcomeMessage = rcon.callPalworldRcon("Info")
        versionInfo = re.findall(reg, welcomeMessage)
        severVersion = versionInfo[0]
        serverOnline = True
    except Exception as e:
        serverOnline = False


def getCurrentPlayer():
    logger.debug("getCurrentPlayer")
    global beforeLoginData

    currentPlayerCsvList = []

    # 現在のプレイヤー取得
    currentPlayer = rcon.callPalworldRcon("ShowPlayers")

    rows = currentPlayer.strip().splitlines()
    for i in range(len(rows)):
        rowList = rows[i].split(",")
        if i == 0:
            # ヘッダー確認
            for j in range(len(rowList)):
                if "name" == rowList[j]:
                    nameColumn = j
                if "playeruid" == rowList[j]:
                    playeruidColumn = j
                if "steamid" == rowList[j]:
                    steamidColumn = j
            # ヘッダー確認終了

        replaceRow = []

        if 3 == len(rowList):
            # 'name', 'playeruid', 'steamid'
            replaceRow.append(rowList[nameColumn].strip())
            replaceRow.append(rowList[playeruidColumn].strip())
            replaceRow.append(rowList[steamidColumn].strip())

            currentPlayerCsvList.append(replaceRow)

    # ヘッダー追加
    currentPlayerCsvList[0].append(logintimeColumnName)

    return currentPlayerCsvList


def checkMorePlayerRows(table1, table2, timeStr):
    logger.debug("checkMorePlayerRows")
    # rows1にないプレイヤー情報をrows2が持っている場合は時刻を付けて返却
    rows1 = list(table1)
    rows2 = list(table2)
    # ヘッダーを抜く
    rows1.pop(0)
    rows2.pop(0)
    moreList = []
    for row2 in rows2:
        for row1 in rows1:
            if row2[playeruidColumn] == row1[playeruidColumn]:
                break
        else:
            if 3 == len(row2):
                row2.append(timeStr)
            moreList.append(row2)
    return moreList


async def diffPlayerCheckAndGetPlayerCount():
    logger.debug("diffPlayerCheckAndGetPlayerCount")
    global beforeLoginData

    # 現在時刻インスタンス
    dt_now_jst_aware = datetime.now(timezone(timedelta(hours=9)))

    # 文字列に変換
    tstr = dt_now_jst_aware.strftime("%Y-%m-%d %H:%M:%S")

    currentPlayer = getCurrentPlayer()

    # 増えたユーザー
    addUserList = checkMorePlayerRows(beforeLoginData, currentPlayer, tstr)
    for addUser in addUserList:
        line = "Login: name: {0} , playeruId: {1} , steamId: {2}".format(
            str(addUser[nameColumn]),
            str(addUser[playeruidColumn]),
            str(addUser[steamidColumn]),
        )
        logger.info(line)
        await sendMessageLogChannel(line)

    # 減ったユーザー
    decUserList = checkMorePlayerRows(currentPlayer, beforeLoginData, tstr)
    # プレイ時間を算出
    for decUser in decUserList:
        # 文字列日付をタイムゾーン付き変換
        loginTime = datetime.strptime(
            decUser[logintimeColumn] + "+0900", "%Y-%m-%d %H:%M:%S%z"
        )
        playTime = dt_now_jst_aware - loginTime
        line = (
            "Logout: name: {0} , playeruId: {1} , steamId: {2} プレイ時間: {3}".format(
                str(decUser[nameColumn]),
                str(decUser[playeruidColumn]),
                str(decUser[steamidColumn]),
                str(playTime),
            )
        )
        logger.info(line)
        await sendMessageLogChannel(line)

    for delUser in decUserList:
        for i in range(len(beforeLoginData)):
            # ログイン中リストから減ったユーザーを調べて削除
            if delUser[playeruidColumn] == beforeLoginData[i][playeruidColumn]:
                beforeLoginData.pop(i)
                break

    beforeLoginData = beforeLoginData + addUserList

    listWriteCsv(beforeLoginData)

    return len(beforeLoginData) - 1


async def sendMessageLogChannel(message):
    logger.debug("sendMessageLogChannel")
    await discordTextMessage.sendMessage(client, message, LogPostChannel)


async def editEmbedStatusChannelMessage(embed):
    logger.debug("editEmbedStatusChannelMessage")
    await discordTextMessage.editEmbed(
        client, embed, StatusPostChannel, StatusEditMessageId
    )


async def editStatus(
    playerCount,
    serverOnlineMessage,
    checkStatus,
    cpuUsage,
    memoryUsage,
    swapMemoryUsage,
    nextBuckUptime,
):
    logger.debug("editStatus")
    discriptionText = "サーバーステータス"
    if playerCount == "-":
        discriptionText = (
            discriptionText
            + "\nユーザー名にマルチバイト文字が使用されているユーザーがログイン中は"
            + "サーバーから接続人数を取得できない不具合があるため、一時的に非表示としています。"
            + "\nゲーム内で確認してください"
        )

    embed = discord.Embed(
        title=StatusPostTitle,
        color=0x31C7DE,
        description=discriptionText,
    )
    embed.set_author(
        name="サーバー確認BOT",
        icon_url=StatusAuthorImageUrl,
    )

    embed.set_thumbnail(url=StatusThumbnailUrl)

    embed.set_image(url=StatusImage)

    embed.add_field(name="ステータス", value=serverOnlineMessage)
    embed.add_field(name="バージョン", value="```" + severVersion + "```")
    embed.add_field(
        name="接続人数", value="```" + str(playerCount) + "/" + MaxPlayer + "```"
    )

    embed.add_field(name="CPU\n使用率", value=str(cpuUsage) + "%")
    embed.add_field(name="メモリ\n使用率", value=str(memoryUsage) + "%")
    embed.add_field(name="スワップメモリ\n使用率", value=str(swapMemoryUsage) + "%")
    embed.add_field(name="次回再起動＆バックアップ実行時刻", value=nextBuckUptime)

    footerMessage = (
        "サーバー不具合により一時的に" + ErrorCheckIntervalMin + "分間隔で確認中"
    )
    if checkStatus:
        footerMessage = CheckIntervalMin + "分間隔で確認中"

    embed.set_footer(
        text=footerMessage,
        icon_url=client.user.avatar.url,
    )

    return await editEmbedStatusChannelMessage(embed)


def getLastMachineStatus(filePath):
    df = pd.read_csv(filePath, index_col=0)
    # 最終行のデータを取得
    last_row = df.tail(1)
    c = last_row["CpuUsage"].values[0]
    m = last_row["MemoryUsage"].values[0]
    s = last_row["SwapMemoryUsage"].values[0]
    return c, m, s


def getCronRunDate(cron_schedule, addMinites=0):

    # タイムゾーンを取得
    pytztimezone = pytz.timezone("Asia/Tokyo")

    # 現在の日時
    now = datetime.now(pytztimezone)

    # croniterオブジェクトの作成（タイムゾーンを考慮）
    iter = croniter(cron_schedule, now, ret_type=float, day_or=True)
    iter.tzinfo = pytztimezone

    # 次の実行時刻の取得
    next_execution_time_epoch = iter.get_next()

    # エポックタイムをdatetimeオブジェクトに変換
    next_execution_time = datetime.fromtimestamp(
        next_execution_time_epoch, tz=pytztimezone
    )

    new_add_datetime = next_execution_time + timedelta(minutes=addMinites)

    # 次の実行時刻をわかりやすい形式に変換
    formatted_next_execution_time = new_add_datetime.strftime("%Y-%m-%d %H:%M")

    logger.debug(f"Backup実行時刻解析: {formatted_next_execution_time}")

    return formatted_next_execution_time, next_execution_time


def getNextCronRunDate(addMinites):
    # Crontab形式の日時指定
    formatDate1, time1 = getCronRunDate(crontab1, addMinites)

    formatDate2, time2 = getCronRunDate(crontab2, addMinites)
    if time1 < time2:
        return formatDate1
    else:
        return formatDate2


async def palworldServerCheck(csvFilePath):
    logger.debug("palworld server check")
    global CheckInterval

    checkStatus = False

    c, m, s = getLastMachineStatus(csvFilePath)
    formatDate = getNextCronRunDate(15)

    logger.debug(f"次回実行時刻: {formatDate}")

    getServerVersion()
    playerCount = "-"
    serverOnlineMessage = ":no_entry:  停止中"
    logStatus = "停止中"
    if serverOnline:
        try:
            playerCount = await diffPlayerCheckAndGetPlayerCount()
            serverOnlineMessage = ":green_circle: 稼働中"
            logStatus = "稼働中"
            checkStatus = True
        except ConnectionRefusedError as e:
            logger.error("ConnectionRefusedError")
            logger.error(e)
            serverOnlineMessage = ":warning: 稼働中？"
            logStatus = "Rconエラー"
            checkStatus = False
        except Exception as e:
            # TODO 現バージョンはユーザー名にマルチバイト文字が使われているとタイムアウト
            logger.error("playerCheck timeout")
            logger.error(e)
            serverOnlineMessage = ":green_circle: 稼働中"
            logStatus = "稼働中"
            checkStatus = False

    await editStatus(playerCount, serverOnlineMessage, checkStatus, c, m, s, formatDate)

    if checkStatus:
        CheckInterval = NomalCheckInterval
    else:
        CheckInterval = ErrorCheckInterval

    logMessage = f"palworld server check version:{severVersion} status:{logStatus} online:{playerCount}"
    logger.info(logMessage)


# Intentsを定義
intents = discord.Intents.default()
intents.all()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logger.debug("on_ready")
    while True:

        getConfigFile()

        lastCsvFilePath = await macineCheck.run(client, MacineStatusPostChannel)

        await palworldServerCheck(lastCsvFilePath)

        # 次のチェックまで一時停止
        await asyncio.sleep(CheckInterval)


def main():
    config_ini = common.getConfigFile()

    DiscordBotToken = config_ini["DEFAULT"]["DiscordBotToken"]
    client.run(DiscordBotToken)


if __name__ == "__main__":
    main()
