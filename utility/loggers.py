"""
@Time: 2022/11/03
@Author: LiuShu
@File: loggers.py
"""
import os
from utility.constant import BASE_DIR
import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '[%(asctime)s] %(filename)s-[line:%(lineno)d] %(levelname)s--%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            # TODO 文件路径修改位置
            'filename': os.path.join(BASE_DIR, 'logs/server.log'),
            'formatter': 'standard',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': True,
        },
        'system': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


def get_logger():
    logging.config.dictConfig(LOGGING)
    Logger = logging.getLogger("system")
    return Logger


logger = get_logger()
