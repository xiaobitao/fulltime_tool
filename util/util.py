import os
from configparser import ConfigParser
import re
import struct
import numpy as np

def get_config():
    cfg = ConfigParser()
    cfg.read('./config.ini', encoding="utf-8")
    print(cfg.sections())
    return cfg

def get_current_directory():
    return os.getcwd()

def read_binfile(filepath):
    param = re.findall(r'\d+', re.findall(r'\d+x\d+', filepath)[0])
    rows = int(param[0])
    cols = int(param[1])
    print(rows, cols)
    with open(filepath, 'rb') as f:
        data = f.read()
        value = struct.unpack(str(rows * cols) + 'f', data)
        records = np.array(value).reshape(rows, cols)
        return records
    return None

def get_current_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path