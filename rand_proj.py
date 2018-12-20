import os
import gzip
import sys, getopt
import numpy as np 
import re
import csparc as kg 
from joblib import Parallel, delayed

ltc_q = {'A': complex(-1,0),'T': complex(1,0),'C': complex(0,-1),'G': complex(0,1)}

def seq_encoding(seq):
        return [ltc_q[u] for u in seq]
    

def coords_to_bins(Wheels, C,reverse_compliments=True):
    # ONLY NEED TO WRITE DOWN ONE KMER FROM REVERSE COMPLIMENT PAIR
    def _pick_one_from_rc_pair(b1,b2):
        B = [np.array([b1[i],b2[i]]) for i in range(len(b1))]
        return [b[b.argmin(0),range(b.shape[1])] for b in B] 

    num_wheels = Wheels[-1]['w'] + 1
    num_spokes = Wheels[-1]['s'] + 1
    pow2 = np.array([2**j for j in range(num_spokes)])
    Wc = np.array([w['c'] for w in Wheels])
    C = np.array(C)
    L = np.dot(C,np.transpose([w['p'] for w in Wheels]).conjugate())
    B = [np.dot((L[:,ws:ws+num_spokes] > Wc[ws:ws+num_spokes]),pow2) for ws in range(0,num_wheels*num_spokes,num_spokes)]
    if reverse_compliments:
        L = np.dot(C[:,::-1]*-1,np.transpose([w['p'] for w in Wheels]).conjugate())
        B2 = [np.dot((L[:,ws:ws+num_spokes] > Wc[ws:ws+num_spokes]),pow2) for ws in range(0,num_wheels*num_spokes,num_spokes)]
        return _pick_one_from_rc_pair(B,B2)
    else:
        return B


def hash_a_read(Wheels, read, kmer_size,reverse_compliments=True):
        C = []
        for kmer in kg.generate_kmer(read, kmer_size):
            C.append(seq_encoding(kmer))
        if len(C) > 0:
            return coords_to_bins(Wheels, C,reverse_compliments=reverse_compliments)
        else:
            return None        
        
class RandProj(object):
    def __init__(self, kmer_size, hash_size, n_thread):
        self.kmer_size=kmer_size 
        self.hash_size =hash_size 
        self.n_thread=n_thread
    
    def create_hash(self,lines):
        kmers = self._sample_kmers(lines)
        kmers = Parallel(n_jobs=self.n_thread)(delayed(seq_encoding)(u) for u in kmers)
        self._set_wheels(kmers,wheels=1)
        
    def _set_wheels(self,kmers, wheels=200):
        Wheels = []
        for w in xrange(wheels):
            Wheels += self._one_wheel(w,kmers)
        Wheels.sort()
        self.Wheels = [{'w': x[0],'s': x[1],'p': x[2],'c': x[3]} for x in Wheels]
    
    def _one_wheel(self,w,kmers):
        S = []
        for s in range(self.hash_size):
            L = [kmers[u] for u in np.random.choice(range(len(kmers)), size=self.kmer_size, replace=False)]
            P = self._affine_hull(L)
            C = P.pop()
            S.append((w,s,P,C))
        return S

    def _affine_hull(self,linear_system):
        # linear_system: d dimensions of n docs in this hyperplane
        linear_system=np.array(linear_system)
        linear_system=np.concatenate([linear_system, np.zeros([linear_system.shape[0],1])-1],axis=1)
        linear_system=np.concatenate([linear_system, np.zeros([1,linear_system.shape[1]])],axis=0)
        U,W,V = np.linalg.svd(linear_system)
        return list(V[-1,:])
            
    def _sample_kmers(self,lines):
        total_rand_kmers = self.kmer_size*self.hash_size*2
        n_reads = len(lines)
        kmers = [] 
        while len(kmers)< total_rand_kmers:
            read = lines[int(np.random.random()*n_reads)].split("\t")[2].strip()
            assert len(read)>=self.kmer_size
            kmer=kg.random_generate_kmer(read, self.kmer_size)
            if not "N" in kmer:
                kmers.append(kmer)
        return kmers 
    
    def hash_reads(self,reads):
        hashed_reads = Parallel(n_jobs=self.n_thread)(delayed(hash_a_read)(self.Wheels, u, self.kmer_size) for u in reads)
        return hash_reads
        
    def hash_read(self,read):
        return hash_a_read(self.Wheels, read, self.kmer_size)
   
    
    