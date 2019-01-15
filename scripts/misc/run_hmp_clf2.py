#!/usr/bin/env python
 
import sys, getopt
import os , multiprocessing
import logging
import numpy as np 
import pandas as pd 

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
        _LOGGERS[name] = logger 
    return _LOGGERS[name]


logger = get_logger("run_hmp_clf")


def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def shell_run_and_wait(command, working_dir=None, env=None):
    logger.info("running " + command)
    curr_dir = os.getcwd()
    if working_dir is not None:
        os.chdir(working_dir)
    command = command.split(" ")
    import subprocess
    
    process = subprocess.Popen(command, env=env)
    process.wait()
    if working_dir is not None:
        os.chdir(curr_dir)
    return process.returncode


def shell_run_and_wait2(command1, command2, working_dir=None, env=None):
    logger.info("running {} | {}".format(command1, command2))
    curr_dir = os.getcwd()
    if working_dir is not None:
        os.chdir(working_dir)
    import subprocess
    ps = subprocess.Popen(command1.split(" "), stdout=subprocess.PIPE)
    output = subprocess.check_output(command2.split(" "), stdin=ps.stdout)
    ps.wait()
    if working_dir is not None:
        os.chdir(curr_dir)
    return ps.returncode
 
 
def run(train_file, test_file, out_prefix, working_dir, wordNgrams, word_dim, learning_rate, epoch, loss_fun, n_thread):
    logger.info("start running ...")
    logger.info ("parameters: " + str(locals()))

    train_file = os.path.abspath(train_file)
    logger.info("use train file: " + train_file)
    assert  os.path.exists(in_file)

    test_file = os.path.abspath(test_file)
    logger.info("use test file: " + hash_file)
    assert  os.path.exists(hash_file)
    
    if os.path.exists(working_dir): logger.warn("working dir <{}> exists. will overide.".format(working_dir))
    create_dir_if_not_exists(working_dir)
    os.chdir(working_dir)
    logger.info("working dir: " + os.getcwd())
    
    cmd = "fastseq supervised -input {} -output model -lr {} -epoch {} -wordNgrams {} -dim {} -loss {} -thread {}".format(
                     train_file, learning_rate, epoch, wordNgrams, word_dim, loss_fun, n_thread)
    status = shell_run_and_wait(cmd)
    logger.info("finish running train")
    assert status == 0
    
    cmd = "fastseq test model.bin {}".format(test_file) 
    status = shell_run_and_wait(cmd)
    logger.info("finish running test")
    assert status == 0
    
    logger.info("finish running...")

    
def main(argv):
    train_file = ''
    label_type = ""
    loss_fun = "hs"
    out_prefix = 'model'
    test_file = ''
    working_dir = "."
    learning_rate = 0.5
    epoch = 5
    wordNgrams = 1
    word_dim = 50
    n_thread = max(1, multiprocessing.cpu_count() - 1)
    
    help_msg = sys.argv[0] + ' -i <train_file> --test <test_file> --dim <dim> --label <label>  [--lr <learning rate>] [--n_thread <n>] [--epoch <n>] [--wordNgrams <n>] [--loss <loss>] [--working_dir <working_dir>]'
    if len(argv) < 2:
        print help_msg
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:", ["in_file=", "test=", "lr=", "dim=", "n_thread=", "epoch=", 'wordNgrams=', 'loss=', 'working_dir=', 'hash=', 'label='])
        except getopt.GetoptError as e:
            print e
            print help_msg
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print help_msg
                sys.exit()
            elif opt in ("-i", "--in_file"):
                train_file = arg
            elif opt in ("--loss"):
                loss_fun = arg
            elif opt in ("--test"):
                test_file = arg                
            elif opt in ("--working_dir"):
                working_dir = arg                                                
            elif opt in ("--n_thread"):
                n_thread = int(arg)
                assert n_thread > 0               
            elif opt in ("--lr"):
                learning_rate = float(arg)
                assert learning_rate > 0
            elif opt in ("--epoch"):
                epoch = int(arg)
                assert epoch > 0
            elif opt in ("--dim"):
                word_dim = int(arg)
                assert word_dim > 0                
            elif opt in ("--wordNgrams"):
                wordNgrams = int(arg)
                assert wordNgrams > 0
                                
    run(train_file, test_file, out_prefix, working_dir=working_dir, wordNgrams=wordNgrams, word_dim=word_dim, learning_rate=learning_rate, epoch=epoch, loss_fun=loss_fun, n_thread=n_thread)


if __name__ == "__main__":
    main(sys.argv[1:])
