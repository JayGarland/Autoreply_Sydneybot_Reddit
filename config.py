# encoding:utf-8

import json
import logging
import os
import pickle

from log import logger

# 将所有可用的配置项写在字典里, 请使用小写字母
# 此处的配置值无实际意义，程序不会读取此处的配置，仅用于提示格式，请将配置加入到config.json中
available_setting = {
    "bot_name": "",
    "password" : "",
    "client_id" : "",
    "client_secret" : "",
    "proxy" : "",
    "bot_account": [],
    "blacklist":[], 
    "blocked_account": [""],
    "TargetSubreddits":[""],
    "min_char" : 10,  # at least how many word in user's speech will trigger the bot reply
    "interval" : 3, # check every interval minute
    "submission_num" : 10,  # everytime bot observe how many posts
    "comment_num" : 30,  # every pattern when triggered the reply randomly, how many replies will be pulled and let the bot observe
    "comment_rate" : 0.7,  # every pattern when triggered the reply randomly, how much rate of the bot choose to reply the comment under a post, if not, reply to a post
    "random_check_rate" : 6,  # bot everytime when bot checks, how many check patterns would trigger the bot to reply randomly otherwise only reply when someone @ the bot
    "gemini_api_key": "",
    "cohere_api_key": "",
    "deepseek_api_key": "",
    "persona": "",
    "customSet": [{'':''}],
    "bot_statement":"",

    #system config 
    "debug":"",
    "appdata_dir": "",  # date dir
    "ai_model": "AZURE",  # default ai model, can be "gemini", "cohere", "deepseek", "azure"
    "azure_endpoint": "https://redditreplybot.services.ai.azure.com/models",
    "azure_key": "",
    "azure_deployment": ""
}


class Config(dict):
    def __init__(self, d=None):
        super().__init__()
        if d is None:
            d = {}
        for k, v in d.items():
            self[k] = v
        # user_datas: 用户数据，key为用户名，value为用户数据，也是dict
        self.user_datas = {}

    def __getitem__(self, key):
        if key not in available_setting:
            raise Exception("key {} not in available_setting".format(key))
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key not in available_setting:
            raise Exception("key {} not in available_setting".format(key))
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            return default
        except Exception as e:
            raise e

    # Make sure to return a dictionary to ensure atomic
    def get_user_data(self, user) -> dict:
        if self.user_datas.get(user) is None:
            self.user_datas[user] = {}
        return self.user_datas[user]

    def load_user_datas(self):
        try:
            # Get data path using this config instance to avoid circular dependency
            data_dir = self.get("appdata_dir", "")
            data_path = os.path.join(get_root(), data_dir)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            
            with open(os.path.join(data_path, "user_datas.pkl"), "rb") as f:
                self.user_datas = pickle.load(f)
                logger.info("[Config] User datas loaded.")
        except FileNotFoundError as e:
            logger.info("[Config] User datas file not found, ignore.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))
            self.user_datas = {}

    def save_user_datas(self):
        try:
            # Get data path using this config instance to avoid circular dependency
            data_dir = self.get("appdata_dir", "")
            data_path = os.path.join(get_root(), data_dir)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
                
            with open(os.path.join(data_path, "user_datas.pkl"), "wb") as f:
                pickle.dump(self.user_datas, f)
                logger.info("[Config] User datas saved.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))


class ConfigManager:
    """Singleton configuration manager with lazy loading."""
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_config(self) -> Config:
        """Get configuration instance, loading if necessary."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Config:
        """Internal config loading logic."""
        config_path = "./config.json"
        if not os.path.exists(config_path):
            logger.info("配置文件不存在，将使用config-template.json模板")
            config_path = "./config-template.json"

        config_str = read_file(config_path)
        logger.debug("[INIT] config str: {}".format(config_str))

        # 将json字符串反序列化为dict类型
        config = Config(json.loads(config_str))

        # override config with environment variables.
        # Some online deployment platforms (e.g. Railway) deploy project from github directly. 
        # So you shouldn't put your secrets like api key in a config file, instead use environment variables to override the default config.
        for name, value in os.environ.items():
            name = name.lower()
            if name in available_setting:
                logger.info("[INIT] override config by environ args: {}={}".format(name, value))
                try:
                    config[name] = eval(value)
                except:
                    if value == "false":
                        config[name] = False
                    elif value == "true":
                        config[name] = True
                    else:
                        config[name] = value

        if config.get("debug", False):
            logger.setLevel(logging.DEBUG)
            logger.debug("[INIT] set log level to DEBUG")

        logger.info("[INIT] load config: {}".format(config))

        config.load_user_datas()
        return config
    
    def reload_config(self):
        """Force reload configuration from file."""
        self._config = None
        return self.get_config()
    
    def is_loaded(self) -> bool:
        """Check if configuration is currently loaded."""
        return self._config is not None


# Global configuration manager instance
_config_manager = ConfigManager()


def load_config():
    """Load configuration (legacy function for compatibility)."""
    return _config_manager.get_config()


def conf():
    """Get current configuration."""
    return _config_manager.get_config()


def reload_config():
    """Reload configuration from file."""
    return _config_manager.reload_config()


def is_config_loaded() -> bool:
    """Check if configuration is currently loaded."""
    return _config_manager.is_loaded()


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def read_file(path):
    with open(path, mode="r", encoding="utf-8") as f:
        return f.read()


def get_appdata_dir():
    # Prevent circular dependency by getting config without triggering load if needed
    config_instance = _config_manager._config
    if config_instance is None:
        # If config not loaded yet, use default data dir
        data_path = os.path.join(get_root(), "data")
    else:
        data_path = os.path.join(get_root(), config_instance.get("appdata_dir", ""))
    
    if not os.path.exists(data_path):
        logger.info("[INIT] data path not exists, create it: {}".format(data_path))
        os.makedirs(data_path)
    return data_path


def subscribe_msg():
    trigger_prefix = conf().get("single_chat_prefix", [""])[0]
    msg = conf().get("subscribe_msg", "")
    return msg.format(trigger_prefix=trigger_prefix)


# global plugin config
plugin_config = {}


def write_plugin_config(pconf: dict):
    """
    写入插件全局配置
    :param pconf: 全量插件配置
    """
    global plugin_config
    for k in pconf:
        plugin_config[k.lower()] = pconf[k]


def pconf(plugin_name: str) -> dict:
    """
    根据插件名称获取配置
    :param plugin_name: 插件名称
    :return: 该插件的配置项
    """
    return plugin_config.get(plugin_name.lower())


# 全局配置，用于存放全局生效的状态
global_config = {
    "admin_users": []
}

# Configuration is now loaded lazily when first accessed via conf()
# No automatic loading on module import
