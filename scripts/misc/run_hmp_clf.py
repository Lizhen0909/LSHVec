#!/usr/bin/env python
 
import sys, getopt
import multiprocessing
import csparc as kg 
import os 
from joblib import Parallel, delayed
from rand_proj import RandProj
from tqdm import tqdm
import utils 

logger = utils.get_logger("run_hmp_clf")


def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def shell_run_and_wait(command, working_dir=None, env=None):
    curr_dir = os.getcwd()
    if working_dir is not None:
        os.chdir(working_dir)
    command = command.split(" ")
    import subprocess
    
    # process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process = subprocess.Popen(command, env=env)
    process.wait()
    if working_dir is not None:
        os.chdir(curr_dir)
    return process.returncode


def make_train_test(hashfile, labels, n):
    with open('data.train', 'wt') as ftrain, open('data.test', 'wt') as ftest:
        with open(hashfile) as fin:
            for i, line in enumerate(fin):
                if i < n:
                    ftrain.write("__label__" + labels[i] + " " + line)
                else:
                    ftest.write("__label__" + labels[i] + " " + line)


def create_labels(seqfile, label_type):
    s = """
286    Pseudomonas    genus    Proteobacteria    Gammaproteobacteria
357    Agrobacterium    genus    Proteobacteria    Alphaproteobacteria
475    Moraxella    genus    Proteobacteria    Gammaproteobacteria
481    Neisseriaceae    family    Proteobacteria    Betaproteobacteria
543    Enterobacteriaceae    family    Proteobacteria    Gammaproteobacteria
570    Klebsiella    genus    Proteobacteria    Gammaproteobacteria
1279    Staphylococcus    genus    Firmicutes    Bacilli
1301    Streptococcus    genus    Firmicutes    Bacilli
1386    Bacillus    genus    Firmicutes    Bacilli
1653    Corynebacteriaceae    family    Actinobacteria    Actinobacteria
1716    Corynebacterium    genus    Actinobacteria    Actinobacteria
2070    Pseudonocardiaceae    family    Actinobacteria    Actinobacteria
13687    Sphingomonas    genus    Proteobacteria    Alphaproteobacteria
41294    Bradyrhizobiaceae    family    Proteobacteria    Alphaproteobacteria
80864    Comamonadaceae    family    Proteobacteria    Betaproteobacteria
85031    Nakamurellaceae    family    Actinobacteria    Actinobacteria
"""
    s = [u.strip() for u in s.split("\n") if u.strip()]
    s = [u.split("\t") for u in s]
    s = pd.DataFrame(s)

    labels = pd.read_csv(seqfile, usecols=[1], sep='\t', header=None)
    
    if label_type == 'org':
        labels = labels[1].map(lambda u: u.split("-")[1]).values
    else:
        labels = labels[1].map(lambda u: u.split("-")[2]).values

    if label_type == 'phylum':        
        m = s.set_index(0)[3].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'class':
        m = s.set_index(0)[4].to_dict()
        labels = np.array([m[u] for u in labels])
        
    logger.info("Has {} labels".format(len(set(labels))))
    logger.info("Labels: " + " ".join(set(labels)))
    return labels    


def copy_file(src, dest):
    if src.endswith('.zst'):
        cmd = "cat {} | zstd -fo {}".format(src, dest)
    else:
        cmd = "cp {} {}".format(src, dest)
    status = shell_run_and_wait(cmd)
    assert status == 0                

                    
def run(in_file, hash_file, label_type, out_prefix, working_dir, wordNgrams, word_dim, learning_rate, epoch, loss_fun, n_thread):
    logger.info("start running ...")
    logger.info ("parameters: " + str(locals()))

    in_file = os.path.abspath(in_file)
    logger.info("use seq file: " + in_file)
    assert  os.path.exists(in_file)

    hash_file = os.path.abspath(in_file)
    logger.info("use seq file: " + hash_file)
    assert  os.path.exists(hash_file)
    
    create_dir_if_not_exists(working_dir)
    os.chdir(working_dir)
    logger.info("working dir: " + os.getcwd())
    
    copy_file(in_file, "data.seq")
    copy_file(hash_file, "data.hash")
    logger.info("finish copying files")
    
    labels = create_labels('data.seq', label_type)
    
    make_train_test('data.hash', labels, n=450000)
    logger.info("finish making train test")
    
    cmd = "fastseq supervised -input data.train -output model -lr {} -epoch {} -wordNgrams {}  -dim {} -loss {}".format(
                     learning_rate, epoch, wordNgrams, word_dim, loss_fun)
    logger.info("running " + cmd)
    status = shell_run_and_wait(cmd)
    logger.info("finish running train")
    assert status == 0
    
    cmd = "fastseq test model.bin data.test" 
    status = shell_run_and_wait(cmd)
    logger.info("finish running test")
    assert status == 0
    
    logger.info("finish running...")

    
def main(argv):
    in_file = ''
    label_type = ""
    loss_fun = ""
    out_prefix = 'model'
    hashfile = ''
    working_dir = "."
    learning_rate = 0.5
    epoch = 5
    wordNgrams = 1
    word_dim = 50
    n_thread = max(1, multiprocessing.cpu_count() - 1)
    
    help_msg = sys.argv[0] + ' -i <seq_file> --hash <hash_file> --dim <dim> --label <label>  [--lr <learning rate>] [--n_thread <n>] [--epoch <n>] [--wordNgrams <n>] [--loss <loss>] [--working_dir <working_dir>]'
    if len(argv) < 2:
        print help_msg
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:", ["in_file=", "lr=", "dim=", "n_thread=", "epoch=", 'wordNgrams=', 'loss=', 'working_dir='])
        except getopt.GetoptError:
            print help_msg
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print help_msg
                sys.exit()
            elif opt in ("-i", "--in_file"):
                in_file = arg
            elif opt in ("--loss"):
                loss_fun = arg
            elif opt in ("--label"):
                label_type = arg
                assert label_type in [ 'org', 'tax', 'class', 'phylum']                
            elif opt in ("--hash"):
                hash_file = arg                
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
                                
    run(in_file, hash_file, out_prefix, label_type, working_dir=working_dir, wordNgrams=wordNgrams, word_dim=word_dim, learning_rate=learning_rate, epoch=epoch, loss_fun=loss_fun, n_thread=n_thread)


if __name__ == "__main__":
    main(sys.argv[1:])
