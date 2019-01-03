#!/usr/bin/env python

 
import os
import gzip
import sys, getopt
import random
import re
import multiprocessing
import csparc as kg 
from joblib import Parallel, delayed
from rand_proj import RandProj
from tqdm import tqdm



def gen_for_line_fnv(line, k):
    seq = line.split("\t")[2].strip()
    return [kg.fnv_hash(u) for u in kg.generate_kmer(seq,k)]

def gen_for_line_lsh(line, k,rp):
    seq = line.split("\t")[2].strip()
    return rp.hash_read(seq)[0]

def convert(in_file, out_file, hash_fun, kmer_size,n_thread, hash_size):
    print ("parameters: "+str(locals()))
    with open(in_file) as fp:
        lines = list(fp)
    
    if hash_fun == 'fnv':
        sequences = Parallel(n_jobs=n_thread)(delayed(gen_for_line_fnv)(line,kmer_size ) for line in tqdm(lines))
    else:
         rp = RandProj(kmer_size=kmer_size, hash_size=hash_size, n_thread=n_thread)
         rp.create_hash(lines)
         sequences = Parallel(n_jobs=n_thread)(delayed(gen_for_line_lsh)(line,kmer_size,rp ) for line in lines)

    with open(out_file,'wt') as fp:
        for u in sequences:
            fp.write(" ".join([str(v) for v in u]))
            fp.write("\n")
        
    

def main(argv):
    in_file = ''
    paired = False
    shuffle = False
    hash_fun=""
    out_file = ''
    kmer_size=31
    hash_size=22
    n_thread = max(1,multiprocessing.cpu_count()-1)
    
    help_msg = sys.argv[0] + ' -i <seq_file> --hash <fnv or lsh> -o <outfile> [-k <kmer_size>] [--n_thread <n>] [--hash_size <m>]'
    if len(argv) < 2:
        print help_msg
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:o:k:", ["in_file=","hash=", "out_file=", "n_thread=", "hash_size="])
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
                assert kmer_size>1                
            elif opt in ("--n_thread"):
                n_thread = int(arg)
                assert n_thread>0               
            elif opt in ("--hash"):
                hash_fun= arg
            elif opt in ("--hash_size"):
                hash_size= int(arg)
                assert hash_size>0                
            elif opt in ("-o", "--out_file"):
                out_file = arg
        if hash_fun not in ['fnv','lsh']:
            print help_msg 
            exit(3)  
    convert(in_file, out_file, hash_fun,kmer_size,n_thread=n_thread,hash_size=hash_size)

if __name__ == "__main__":
    main(sys.argv[1:])
