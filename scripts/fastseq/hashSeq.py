#!/usr/bin/env python
 
import sys, getopt
import multiprocessing
import csparc as kg 
from joblib import Parallel, delayed
from rand_proj import RandProj
from tqdm import tqdm
import utils 

logger = utils.get_logger("hashSeq")

ONE_HOT_MAP={'A':'00','C':'01','G':'10','C':'11'}
def one_hot_hash(kmer):
    kmer= "".join([ONE_HOT_MAP[u] for u in kmer])
    return int(kmer, 2)

def gen_for_line_fnv(line, k, bucket):
    seq = line.split("\t")[2].strip()
    return [kg.fnv_hash(u) % bucket for u in kg.generate_kmer_for_fastseq(seq, k)]

def gen_for_line_onehot(line, k):
    seq = line.split("\t")[2].strip()
    return [one_hot_hash(u) for u in kg.generate_kmer_for_fastseq(seq, k)]

def gen_for_line_lsh(line, k, rp, bucket):
    seq = line.split("\t")[2].strip()
    return [u % bucket for u in rp.hash_read(seq)[0]]


def convert(in_file, out_file, hash_fun, kmer_size, n_thread, hash_size, batch_size, bucket):
    logger.info("start converting...")
    def f(lines,fout,rp=None):
        if hash_fun == 'fnv':
            sequences = Parallel(n_jobs=n_thread)(delayed(gen_for_line_fnv)(line, kmer_size, bucket) for line in tqdm(lines))
        elif hash_fun == 'onehot':
            sequences = Parallel(n_jobs=n_thread)(delayed(gen_for_line_onehot)(line, kmer_size) for line in tqdm(lines))
        else:
            sequences = Parallel(n_jobs=n_thread)(delayed(gen_for_line_lsh)(line, kmer_size, rp, bucket) for line in tqdm(lines))
        
        for u in sequences:
            fout.write(" ".join([str(v) for v in u]))
            fout.write("\n")
            
    
    logger.info ("parameters: " + str(locals()))
    rp=None
    if hash_fun == 'lsh':
        logger.info("creating hash ...")        
        with open(in_file) as fp:
            lines=list(fp)
        rp = RandProj(kmer_size=kmer_size, hash_size=hash_size, n_thread=n_thread)
        rp.create_hash(lines)
        logger.info("finish creating hash ...")
            
    cnt=0
    with open(out_file, 'wt') as fout:
        with open(in_file) as fp:
            lines=[]
            for line in fp:
                lines.append(line)
                if len(lines)>=batch_size:
                    f(lines,fout,rp)
                    cnt+=len(lines)
                    lines=[]
                    logger.info ("written {} lines".format(cnt))

        if len(lines)>0:
            f(lines,fout,rp)
            cnt+=len(lines)
            lines=[]
            logger.info ("written {} lines".format(cnt))            
    
    logger.info("finish converting...")
    
def main(argv):
    in_file = ''
    hash_fun = ""
    out_file = ''
    kmer_size = 31
    hash_size = 22
    batch_size = 100000
    bucket = 20000000
    n_thread = max(1, multiprocessing.cpu_count() - 1)
    
    help_msg = sys.argv[0] + ' -i <seq_file> --hash <fnv or lsh> -o <outfile> [-k <kmer_size>] [--n_thread <n>] [--hash_size <m>] [--batch_size <n>] [--chunk <n>]'
    if len(argv) < 2:
        print help_msg
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:o:k:", ["in_file=", "hash=", "out_file=", "n_thread=", "hash_size=", 'batch_size=', 'bucket='])
        except getopt.GetoptError:
            print help_msg
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print help_msg
                sys.exit()
            elif opt in ("-i", "--in_file"):
                in_file = arg
            elif opt in ("-k"):
                kmer_size = int(arg)
                assert kmer_size > 1                
            elif opt in ("--n_thread"):
                n_thread = int(arg)
                assert n_thread > 0               
            elif opt in ("--hash"):
                hash_fun = arg
            elif opt in ("--hash_size"):
                hash_size = int(arg)
                assert hash_size > 0
            elif opt in ("--batch_size"):
                batch_size = int(arg)
                assert batch_size > 0 
            elif opt in ("--bucket"):
                bucket = int(arg)
                assert bucket > 0                                                 
            elif opt in ("-o", "--out_file"):
                out_file = arg
        if hash_fun not in ['fnv', 'lsh', 'onehot']:
            print help_msg 
            exit(3)  
    convert(in_file, out_file, hash_fun, kmer_size, n_thread=n_thread, hash_size=hash_size, batch_size=batch_size, bucket=bucket)


if __name__ == "__main__":
    main(sys.argv[1:])
