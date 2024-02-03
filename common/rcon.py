from mcrcon import MCRcon
from common import common


def getRconConfig():
    global rconConfig
    config_ini = common.getConfigFile()

    rconConfig = {
        "serverIp": config_ini["DEFAULT"]["PalWorldServerIP"],
        "password": config_ini["DEFAULT"]["PalWorldAdminPassword"],
        "port": int(config_ini["DEFAULT"]["PalworldPortRconPort"]),
    }


getRconConfig()


def callPalworldRcon(command):
    return callRcon(
        rconConfig["serverIp"],
        rconConfig["password"],
        rconConfig["port"],
        command,
    )


def callRcon(serverIp, password, port, command):
    """
    RCONにコマンド送信、レスポンスを受信
    """
    res = None
    with MCRcon(
        serverIp,
        password,
        port,
    ) as mcr:
        res = mcr.command(command)

    return res
