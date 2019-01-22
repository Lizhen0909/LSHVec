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
                    
def create_labels(labels, label_type):
    s = """
286	Pseudomonas	genus	Proteobacteria	Gammaproteobacteria	Pseudomonadales	Pseudomonadaceae
357	Agrobacterium	genus	Proteobacteria	Alphaproteobacteria	Rhizobiales	Rhizobiaceae
475	Moraxella	genus	Proteobacteria	Gammaproteobacteria	Pseudomonadales	Pseudomonadaceae
481	Neisseriaceae	family	Proteobacteria	Betaproteobacteria	Neisseriales	Neisseriaceae
543	Enterobacteriaceae	family	Proteobacteria	Gammaproteobacteria	Enterobacterales	Enterobacteriaceae
570	Klebsiella	genus	Proteobacteria	Gammaproteobacteria	Enterobacterales	Enterobacteriaceae
1279	Staphylococcus	genus	Firmicutes	Bacilli	Bacillales	Staphylococceae
1301	Streptococcus	genus	Firmicutes	Bacilli	Lactobacillales	Streptococcaceae
1386	Bacillus	genus	Firmicutes	Bacilli	Bacillales	Bacillaceae
1653	Corynebacteriaceae	family	Actinobacteria	Actinobacteria	Corynebacteriales	Corynebacteriaceae
1716	Corynebacterium	genus	Actinobacteria	Actinobacteria	Corynebacteriales	Corynebacteriaceae
2070	Pseudonocardiaceae	family	Actinobacteria	Actinobacteria	Pseudonocardiales	Pseudonocardiaceae
13687	Sphingomonas	genus	Proteobacteria	Alphaproteobacteria	Sphingomonadales	Sphingomonadaceae
41294	Bradyrhizobiaceae	family	Proteobacteria	Alphaproteobacteria	Rhizobiales	Bradyrhizobiaceae
80864	Comamonadaceae	family	Proteobacteria	Betaproteobacteria	Burkholderiales	Comamonadaceae
85031	Nakamurellaceae	family	Actinobacteria	Actinobacteria	Nakamurellales	Nakamurellaceae
"""

    s = [u.strip() for u in s.split("\n") if u.strip()]
    s = [u.split("\t") for u in s]
    s = pd.DataFrame(s)

    if label_type == 'org':
        return labels

    if label_type == 'phylum':        
        m = s.set_index(0)[3].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'class':
        m = s.set_index(0)[4].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'order':
        m = s.set_index(0)[5].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'family':
        m = s.set_index(0)[6].to_dict()
        labels = np.array([m[u] for u in labels])
    elif label_type == 'tax':
        m = s.set_index(0)[1].to_dict()
        labels = np.array([m[u] for u in labels])
    else:
        raise Exception("NA "+label_type)
    print("Has {} labels".format(len(set(labels))))
    print("Labels: " + " ".join(set(labels)))
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
