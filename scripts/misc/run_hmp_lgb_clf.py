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

logger = get_logger("run_hmp_lgb_clf")



def create_labels(labels, label_type):
    s = """
286    Pseudomonas    genus    Proteobacteria    Gammaproteobacteria    Pseudomonadales    Pseudomonadaceae
357    Agrobacterium    genus    Proteobacteria    Alphaproteobacteria    Rhizobiales    Rhizobiaceae
475    Moraxella    genus    Proteobacteria    Gammaproteobacteria    Pseudomonadales    Pseudomonadaceae
481    Neisseriaceae    family    Proteobacteria    Betaproteobacteria    Neisseriales    Neisseriaceae
543    Enterobacteriaceae    family    Proteobacteria    Gammaproteobacteria    Enterobacterales    Enterobacteriaceae
570    Klebsiella    genus    Proteobacteria    Gammaproteobacteria    Enterobacterales    Enterobacteriaceae
1279    Staphylococcus    genus    Firmicutes    Bacilli    Bacillales    Staphylococceae
1301    Streptococcus    genus    Firmicutes    Bacilli    Lactobacillales    Streptococcaceae
1386    Bacillus    genus    Firmicutes    Bacilli    Bacillales    Bacillaceae
1653    Corynebacteriaceae    family    Actinobacteria    Actinobacteria    Corynebacteriales    Corynebacteriaceae
1716    Corynebacterium    genus    Actinobacteria    Actinobacteria    Corynebacteriales    Corynebacteriaceae
2070    Pseudonocardiaceae    family    Actinobacteria    Actinobacteria    Pseudonocardiales    Pseudonocardiaceae
13687    Sphingomonas    genus    Proteobacteria    Alphaproteobacteria    Sphingomonadales    Sphingomonadaceae
41294    Bradyrhizobiaceae    family    Proteobacteria    Alphaproteobacteria    Rhizobiales    Bradyrhizobiaceae
80864    Comamonadaceae    family    Proteobacteria    Betaproteobacteria    Burkholderiales    Comamonadaceae
85031    Nakamurellaceae    family    Actinobacteria    Actinobacteria    Nakamurellales    Nakamurellaceae
"""

    s = [u.strip() for u in s.split("\n") if u.strip()]
    s = [u.split() for u in s]
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

def make_data(datafile, target,seed=1234):
    with open(datafile) as f:
        df = pickle.load(f)
    df[target]=create_labels(df['tax_id'],target)
    np.random.seed(seed=seed)
    df['fold']=np.random.permutation(range(len(df)))%5
    return df

def get_train_test(df,fold, target):
    idx=df['fold']==fold
    labels=sorted(list(set(df[target])))
    labels={v:u for u,v in enumerate(labels)}
    X_test=np.array(list(df[idx]['vec'].values))
    y_test=df[target][idx].map(labels).values
    X_train=np.array(list(df[~idx]['vec'].values))
    y_train=df[target][~idx].map(labels).values
    return X_train,y_train,X_test,y_test,labels

def run_fold(df, param, target, n_fold, nround=1500):
    X_train,y_train,X_test,y_test,labels=get_train_test(df,n_fold,target)
    print ("train data shape:", str(X_train.shape))
    print ("test data shape:", str(X_test.shape))

    d_train = lgb.Dataset(X_train, label=y_train)
    d_valid = lgb.Dataset(X_test, label=y_test)

    print ("training model...")
    param['num_class']=len(labels)
    for i,u in enumerate(['bagging_seed', 'feature_fraction_seed', 'data_random_seed', 'drop_seed']):
        param[u] = 100+i*1000 + n_fold
    
    print (param)
    
    gbm = lgb.train(param,
                    d_train,
                    num_boost_round=nround,
                    valid_sets=[d_valid, d_train],
                    early_stopping_rounds=50)

    print ("train best iteration: {}, best score: {}".format(gbm.best_iteration, str(gbm.best_score)))
    #importance = gbm.feature_importance(iteration=gbm.best_iteration)
    #impdf = pd.DataFrame({'s':importance, 'name':range(len(importance))})
    #print impdf.sort_values(by='s', ascending=False).head(20)

    #pred = np.argmax(gbm.predict(X_train, num_iteration=gbm.best_iteration),axis=1)
    #print("train accuracy={}".format(np.mean(pred==y_train)))
    pred = np.argmax(gbm.predict(X_test, num_iteration=gbm.best_iteration),axis=1)
    print("test accuracy={}".format(np.mean(pred==y_test)))
    
    return gbm.best_score['valid_0']['multi_logloss']

               
def run(data_file, param_file,   n_thread):
    logger.info("start running ...")
    logger.info ("parameters: " + str(locals()))

    data_file = os.path.abspath(data_file)
    logger.info("use data file: " + data_file)
    assert  os.path.exists(data_file)

    param_file = os.path.abspath(param_file)
    logger.info("use param file: " + param_file)
    assert  os.path.exists(param_file)
    
    with open(param_file) as f:
        param=json.load(f)
    
    logger.info("params="+str(param))
    
    target=param['target']
    del param['target']
    no_fold=1
    df=make_data(data_file,target)
    best_loss=run_fold(df, param, target, no_fold, nround=1500)
    print "AAAAA Best_loss={}".format(best_loss)

    logger.info("finish running...")

    
def main(argv):
    data_file = ''
    param_file = ''
    n_thread = max(1, multiprocessing.cpu_count() - 1)
    help_msg = sys.argv[0] + ' -i <data_file> --param <param_file>  [--n_thread <n>]'
    if len(argv) < 2:
        print help_msg
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:", ["in_file=", "param=", "n_thread="])
        except getopt.GetoptError as e:
            print e
            print help_msg
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print help_msg
                sys.exit()
            elif opt in ("-i", "--in_file"):
                data_file = arg
            elif opt in ("--param"):
                param_file = arg
            elif opt in ("--n_thread"):
                n_thread = int(arg)
                assert n_thread > 0               
                                
    run(data_file,param_file, n_thread=n_thread)


if __name__ == "__main__":
    main(sys.argv[1:])
