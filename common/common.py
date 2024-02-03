import configparser


def getConfigFile():
    config_file_ini = configparser.ConfigParser()
    config_file_ini.read("settingFilePath.ini", encoding="utf-8")
    config_ini = configparser.ConfigParser()
    config_ini.read(config_file_ini["SETTINGS"]["filePath"], encoding="utf-8")
    return config_ini
