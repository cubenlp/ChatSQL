"""
@File: 存放固定的路径
"""
import os
import pandas as pd
# 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
configurable_file_path = os.path.join(BASE_DIR, 'configurable_file')
