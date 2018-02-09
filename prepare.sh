#!/bin/sh
apt-get update && apt-get install nano zsh nkf htop tmux -y

cd /word2vecf_ja/word2vecf
make -j4

mkdir /data && cd /data
gsutil cp gs://nd-dataset/wikipedia_20180101.tar.gz /data/wikipedia_20180101.tar.gz
tar zxf wikipedia_20180101.tar.gz
