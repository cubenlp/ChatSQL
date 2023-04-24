"""
@Time: 2022/12/06
@Author: LiuShu
@File: utility.py
"""
import os
import re
import sys
import shutil
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 读取config内容
import configparser
import yaml
import json
import requests
from utility.constant import BASE_DIR
from utility.loggers import logger
db_config_file_path = os.path.join(BASE_DIR, 'config.cfg')
logger.info(db_config_file_path)
yaml_file_path = os.path.join(BASE_DIR, 'group_config.yaml')
# logger.info(yaml_file_path)
# small_model_config_path = os.path.join(BASE_DIR, 'configurable_file/small_model.json')

def get_config():
    config = configparser.ConfigParser()
    config.read(db_config_file_path, encoding='utf8')
    logger.info(str(config._sections))
    return config


# 得到配置内容
config = get_config()


class ConfigParser:
    @staticmethod
    def load_config():
        with open(yaml_file_path, 'r', encoding='utf-8') as file_stream:
            config_dict = yaml.load(file_stream, Loader=yaml.Loader)

        logger.info('config_dict:' + str(config_dict))

        return config_dict


