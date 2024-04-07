from common import palApi, common, loggerUtil
import time

config_ini = common.getConfigFile()

logFilePath = config_ini["DEFAULT"]["BackupLogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)


def sendServerMessage(MessageText):
    logger.debug("sendServerMessage")
    try:
        res = palApi.callPalworldMessageApi(MessageText)
        print("サーバーへメッセージ送信:" + res)
    except Exception as e:
        logger.error("サーバーへメッセージ送信失敗")
        logger.error(e)


def main():
    sendServerMessage("バックアップ実行の為、サーバーを15分後に再起動します")
    time.sleep(60 * int(5))

    sendServerMessage("バックアップ実行の為、サーバーを10分後に再起動します")
    time.sleep(60 * int(5))

    sendServerMessage("バックアップ実行の為、サーバーを5分後に再起動します")
    time.sleep(60 * int(1))

    sendServerMessage("バックアップ実行の為、サーバーを4分後に再起動します")
    time.sleep(60 * int(1))

    sendServerMessage("バックアップ実行の為、サーバーを3分後に再起動します")
    time.sleep(60 * int(1))

    sendServerMessage("バックアップ実行の為、サーバーを2分後に再起動します")
    time.sleep(60 * int(1))

    sendServerMessage("バックアップ実行の為、サーバーを1分後に再起動します")
    time.sleep(60 * int(1))


if __name__ == "__main__":

    main()
