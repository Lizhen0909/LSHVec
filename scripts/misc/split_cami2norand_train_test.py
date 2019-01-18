import pandas as pd
import numpy as np 
df=pd.read_csv("data.seq", header=None, usecols=[1],sep='\t')
df['org']=df[1].map(lambda u: u.split('-')[1])
df['taxid']=df[1].map(lambda u: u.split('-')[2])
a=df.groupby(['org','taxid'])[1].count().reset_index().sort_values('taxid')

test_orgs=[
"OTU_97.32155.0",
"OTU_97.41740.0",
"OTU_97.45281.1",
"OTU_97.1263.0",
"OTU_97.38699.0",
"OTU_97.37297.0",
"OTU_97.45365.1",
"OTU_97.9612.1",
"OTU_97.20828.0",
"OTU_97.80.0",
"OTU_97.161.0",
"OTU_97.18721.1",
]

df['istest']=df['org'].isin(test_orgs)
print df.istest.mean()


def create_labels(labels, label_type):
    s = """
286	Pseudomonas	genus	Proteobacteria	Gammaproteobacteria	Pseudomonadales
357	Agrobacterium	genus	Proteobacteria	Alphaproteobacteria	Rhizobiales
475	Moraxella	genus	Proteobacteria	Gammaproteobacteria	Pseudomonadales
481	Neisseriaceae	family	Proteobacteria	Betaproteobacteria	Neisseriales
543	Enterobacteriaceae	family	Proteobacteria	Gammaproteobacteria	Enterobacterales
570	Klebsiella	genus	Proteobacteria	Gammaproteobacteria	Enterobacterales
1279	Staphylococcus	genus	Firmicutes	Bacilli	Bacillales
1301	Streptococcus	genus	Firmicutes	Bacilli	Lactobacillales
1386	Bacillus	genus	Firmicutes	Bacilli	Bacillales
1653	Corynebacteriaceae	family	Actinobacteria	Actinobacteria	Actinobacteria
1716	Corynebacterium	genus	Actinobacteria	Actinobacteria	Actinobacteria
2070	Pseudonocardiaceae	family	Actinobacteria	Actinobacteria	Actinobacteria
13687	Sphingomonas	genus	Proteobacteria	Alphaproteobacteria	Sphingomonadales
41294	Bradyrhizobiaceae	family	Proteobacteria	Alphaproteobacteria	Rhizobiales
80864	Comamonadaceae	family	Proteobacteria	Betaproteobacteria	Burkholderiales
85031	Nakamurellaceae	family	Actinobacteria	Actinobacteria	Actinobacteria
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
    elif label_type == 'tax':
        m = s.set_index(0)[1].to_dict()
        labels = np.array([m[u] for u in labels])
    else:
        raise Exception("NA "+label_type)
    print("Has {} labels".format(len(set(labels))))
    print("Labels: " + " ".join(set(labels)))
    return labels 



df['tax']=create_labels(df['taxid'],'tax')
df['order']=create_labels(df['taxid'],'order')
df['class']=create_labels(df['taxid'],'class')
df['phylum']=create_labels(df['taxid'],'phylum')

import os
for target in ['tax','order','class','phylum']:
    os.mkdir(target)
    
for target in ['tax','order','class','phylum']:    
    print target
    labels = df[target].values
    istests=df['istest'].values
    with open(target+'/data.train', 'wt') as ftrain, open(target+'/data.test', 'wt') as ftest:
        with open('data.hash') as fin:
            for i, line in enumerate(fin):
                if not istests[i]:
                    ftrain.write("__label__" + labels[i] + " " + line)
                else:
                    ftest.write("__label__" + labels[i] + " " + line)
    

