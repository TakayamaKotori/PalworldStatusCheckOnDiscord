import base64
import requests
import json
from common import common


def getPalApiConfig():
    global palApiConfig
    config_ini = common.getConfigFile()

    palApiConfig = {
        "serverIp": config_ini["DEFAULT"]["PalWorldServerIP"],
        "password": config_ini["DEFAULT"]["PalWorldAdminPassword"],
        "port": int(config_ini["DEFAULT"]["PalworldPortApiPort"]),
    }


getPalApiConfig()


def callPalworldGetApi(endpoint):
    return callGetApi(
        palApiConfig["serverIp"],
        palApiConfig["port"],
        endpoint,
        "admin",
        palApiConfig["password"],
    )


def callPalworldMessageApi(message):
    messageDict = {"message": message}
    return callPostApi(
        palApiConfig["serverIp"],
        palApiConfig["port"],
        "/v1/api/announce",
        "admin",
        palApiConfig["password"],
        messageDict,
    )


def make_basic_auth_header(username, password):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    return f"Basic {encoded_credentials}"


def callGetApi(host, port, endpoint, username, password):

    url = f"http://{host}:{port}{endpoint}"

    payload = {}
    headers = {
        "Accept": "application/json",
        "Authorization": make_basic_auth_header(username, password),
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)


def callPostApi(host, port, endpoint, username, password, postDict):

    url = f"http://{host}:{port}{endpoint}"

    headers = {
        "Accept": "application/json",
        "Authorization": make_basic_auth_header(username, password),
    }

    response = requests.request("POST", url, headers=headers, json=postDict)

    return response.text


if __name__ == "__main__":
    res = callPalworldGetApi("/v1/api/info")
    print(res)
