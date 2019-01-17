#!/usr/bin/env python
 
import sys, getopt
import os , multiprocessing
import logging
import numpy as np 
import pandas as pd 


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
2623620609	Micromonospora coxensis DSM 45161	Actinobacteria	Actinobacteria	Micromonosporales	Micromonosporaceae
2623620557	Micromonospora echinaurantiaca DSM 43904	Actinobacteria	Actinobacteria	Micromonosporales	Micromonosporaceae
2623620567	Micromonospora echinofusca DSM 43913	Actinobacteria	Actinobacteria	Micromonosporales	Micromonosporaceae
2615840646	Propionibacteriaceae bacterium ES.041	Actinobacteria	Actinobacteria	Propionibacteriales	Propionibacteriaceae
2615840527	Muricauda sp. ES.050	Bacteroidetes	Flavobacteriia	Flavobacteriales	Flavobacteriaceae
2615840601	Cohaesibacter sp. ES.047	Proteobacteria	Alphaproteobacteria	Rhizobiales	Cohaesibacteraceae
2615840533	Thioclava sp. ES.032	Proteobacteria	Alphaproteobacteria	Rhodobacterales	Rhodobacteraceae
2623620617	Halomonas sp. HL-4	Proteobacteria	Gammaproteobacteria	Oceanospirillales	Halomonadaceae
2623620618	Halomonas sp. HL-93	Proteobacteria	Gammaproteobacteria	Oceanospirillales	Halomonadaceae
2616644829	Marinobacter sp. LV10MA510-1	Proteobacteria	Gammaproteobacteria	Alteromonadales	Alteromonadaceae
2615840697	Marinobacter sp. LV10R510-8	Proteobacteria	Gammaproteobacteria	Alteromonadales	Alteromonadaceae
2617270709	Psychrobacter sp. LV10R520-6	Proteobacteria	Gammaproteobacteria	Pseudomonadales	Moraxellaceae
"""
    s = [u.strip() for u in s.split("\n") if u.strip()]
    s = [u.split("\t") for u in s]
    s = pd.DataFrame(s)

    labels = pd.read_csv(seqfile, usecols=[1], sep='\t', header=None)
    
    if label_type == 'org':
        labels = labels[1].map(lambda u: u.split("-")[1]).values
    else:
        labels = labels[1].map(lambda u: u.split("-")[1]).values

    if label_type == 'phylum':        
        m = s.set_index(0)[2].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'class':
        m = s.set_index(0)[3].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'order':
        m = s.set_index(0)[4].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'family':
        m = s.set_index(0)[5].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'org':
	pass
    else:
        raise Exception("NA "+label_type)
    logger.info("Has {} labels".format(len(set(labels))))
    logger.info("Labels: " + " ".join(set(labels)))
    return labels    

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


logger = get_logger("split")

def main(argv):
    
    help_msg = sys.argv[0] + ' <seq_file> <hash_file> <target> <n_train>' 
    if len(argv) !=4:
        print help_msg
        sys.exit(2) 
    else:
	seq_file=sys.argv[1]
	hash_file=sys.argv[2]
	target=sys.argv[3]
    n_train=int(sys.argv[4])
    assert n_train>1000
    
    labels = create_labels(seq_file, target)
    
    make_train_test(hash_file, labels, n=n_train)
    logger.info("finish making train test")

if __name__ == "__main__":
    main(sys.argv[1:])
