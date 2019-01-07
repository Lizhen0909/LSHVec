'''
Created on Apr 6, 2018

@author: Lizhen Shi
'''

import os
import logging
import pandas as pd 
def file_exists(file_path):
    return os.path.exists(file_path)

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def basename(path):        
    return os.path.basename(path)

def touch(filepath):
    with open(filepath, 'a'):
        os.utime(filepath, None)


_LOGGERS = {}


def get_logger(name):
    if name not in _LOGGERS:
        # create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        
        # add ch to logger
        logger.addHandler(ch)
        _LOGGERS[name]=logger 
    return _LOGGERS[name]


def shell_run_and_wait(command):
    command = command.split(" ")
    import subprocess
    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process = subprocess.Popen(command)
    process.wait()
    return process.returncode

def pandas_show_all(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)  
