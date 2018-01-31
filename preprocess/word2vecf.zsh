#!/usr/bin/zsh

deps=${1} # /data/user/wikipedia_dep/wikipedia.deps
p=${2-12}
mincount=100
dim=256
ns=15
dir=$deps:h
cv=${dir}/cv
wv=${dir}/wv
out=${dir}/dim${dim}vecs
outcv=${dir}/dim${dim}context-vecs
../word2vecf/count_and_filter -train $deps -cvocab $cv -wvocab $wv -min-count $mincount
../word2vecf/word2vecf -train $deps -wvocab $wv -cvocab $cv -output $out -size $dim -negative $ns -threads $p -dumpcv $outcv
nkf -w $out > ${out}.utf8
nkf -w $outcv > ${outcv}.utf8
