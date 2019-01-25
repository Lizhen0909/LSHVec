#!/usr/bin/env python

# prepare data for Spark-shared-kmer
# input is fastq.gz files from Illumina
# Read pairs are already joined, if not, the pair will be joined
# output .seq file

import os
import gzip
import sys, getopt
import random
import re

sub_re=re.compile(r"[^ACGT]")

def extract_data(in_file, out_file, paired, shuffle):
    """
    Extract certain number of bases from a list of gzip files
    output format: no    ID    Seq
    """
    out = open(out_file, 'w')
    seq_list = []
    no_seq=1
    if paired:
        """
            join pairs together with 'NNNN'. use first read ID as the ID
        """
        lineno = 0    
        if in_file[-3:] == ".gz":
            seq = gzip.open(in_file, 'r')
        else:
            seq = open(in_file, 'r')
        for line in seq:
            lineno += 1
            if lineno%8 == 1: 
                seqID = line[1:-1]
            if lineno%8 == 2: 
                seqSeq = line[:-1]
            if lineno%8 == 6:    
                seq_list.append(str(no_seq)+"\t"+seqID + "\t" + sub_re.sub("N",seqSeq.upper() + 'N' + line[:-1].upper()) + "\n")
                no_seq+=1     
        seq.close()

    else:
        lineno = 0  
        if in_file[-3:] == ".gz":
            seq = gzip.open(in_file, 'r')
        else:
            seq = open(in_file, 'r')
        for line in seq:
            lineno += 1
            if lineno%4 == 1: 
                seqID = line[1:-1]
            if lineno%4 == 2: 
                seq_list.append(str(no_seq)+"\t"+seqID + "\t" + sub_re.sub("N",line[:-1].upper()) + "\n")
                no_seq+=1     
        if len(seq_list) > 1e6:
            if shuffle:
                random.shuffle(seq_list)
                out.writelines(seq_list)
                seq_list = []
        seq.close()
        
    if shuffle:
        random.shuffle(seq_list)
    out.writelines(seq_list)

    out.close()

def main(argv):
    in_file = ''
    paired = False
    shuffle = False
    out_file = ''
    help_msg = sys.argv[0] + ' -i <fastq_file> -p <1 is paired, 0 otherwise> -o <outfile> -s <1 to shuffle, 0 otherwise>'
    if len(argv) < 2:
        print (help_msg)
        sys.exit(2) 
    else:
        try:
            opts, args = getopt.getopt(argv, "hi:p:o:s:", ["in_file=","paired=", "out_file=", "shuffle="])
        except getopt.GetoptError:
            print (help_msg)
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print (help_msg)
                sys.exit()
            elif opt in ("-i", "--in_file"):
                in_file = arg
            elif opt in ("-p", "--paired"):
                if int(arg) == 1 :
                    paired = True
            elif opt in ("-s", "--shuffle"):
                if int(arg) == 1 :
                    shuffle = True
            elif opt in ("-o", "--out_file"):
                out_file = arg  
    extract_data(in_file, out_file, paired, shuffle)

if __name__ == "__main__":
    main(sys.argv[1:])
