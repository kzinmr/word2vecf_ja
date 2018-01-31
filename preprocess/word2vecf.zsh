#!/usr/bin/zsh

deps=${1} # /data/user/wikipedia_dep/wikipedia.deps.gz
dir=$deps:h
cv=${dir}/cv
wv=${dir}/wv
out=${dir}/dim256vecs
../word2vecf/count_and_filter -train $deps -cvocab $cv -wvocab $wv -min-count 100
../word2vecf/word2vecf -train $deps -wvocab $wv -cvocab $cv -output $out -size 256 -negative 15 -threads 12
