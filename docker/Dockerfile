FROM python:3.6 
MAINTAINER LizhenShi "ls15x@my.fsu.edu"

USER root

RUN apt-get -y update && apt-get install -y git cmake && apt-get clean 

RUN pip install joblib tqdm numpy pandas sklearn MulticoreTSNE cython


#ARG INCUBATOR_VER=unknown

RUN  git clone https://github.com/Lizhen0909/LSHVec.git && cd LSHVec && pip install pysparc-0.1-cp36-cp36m-linux_x86_64.whl && make && cp lshvec /usr/bin && cp scripts/fastseq/*.py /usr/bin && rm -fr LSHVec

