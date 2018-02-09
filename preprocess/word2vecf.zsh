#!/usr/bin/zsh

deps=${1} # /data/user/wikipedia_dep/wikipedia.deps
vecdir=${2} # /data/user/wikipedia_vec
bindir=${3-../word2vecf}
p=${4-12}
py=${5}
mincount=100
dim=256
ns=15
dir=$deps:h
cv=${dir}/cv
wv=${dir}/wv
out=${dir}/dim${dim}vecs
outcv=${dir}/dim${dim}context-vecs
${bindir}/count_and_filter -train $deps -cvocab $cv -wvocab $wv -min-count $mincount
${bindir}/word2vecf -train $deps -wvocab $wv -cvocab $cv -output $out -size $dim -negative $ns -threads $p -dumpcv $outcv
nkf -w $out > ${out}.utf8
nkf -w $outcv > ${outcv}.utf8

python vecs2nps.py ${out}.utf8 ${out}.npy
python vecs2nps.py ${outcv}.utf8 ${out}.npy
mv ${out}.npy ${out}.npy ${out}.utf8 ${outcv}.utf8 $vecdir
