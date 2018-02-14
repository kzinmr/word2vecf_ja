#!/bin/bash

cd /word2vecf_ja/word2vecf
make -j4

if [[ ! -f /data/wikipedia_20180101.tar.gz ]];then
    mkdir /data && cd /data
    gsutil cp gs://nd-dataset/wikipedia_20180101.tar.gz /data/wikipedia_20180101.tar.gz
fi
if [[ ! -d /data/wikipedia ]];then
    tar zxf wikipedia_20180101.tar.gz
fi

ldconfig
cd /word2vecf_ja
gcloud source repos clone slackbot
