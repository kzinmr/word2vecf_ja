#!/bin/sh
apt-get update && apt-get install nano zsh nkf htop tmux -y

cd /word2vecf_ja/word2vecf
make -j4

mkdir /data && cd /data
if [[ ! -f /data/wikipedia_20180101.tar.gz ]];then
    gsutil cp gs://nd-dataset/wikipedia_20180101.tar.gz /data/wikipedia_20180101.tar.gz
fi
if [[ ! -d /data/wikipedia ]];then
    tar zxf wikipedia_20180101.tar.gz
fi
gcloud source repos clone slackbot
