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
out=${vecdir}/dim${dim}vecs
outcv=${vecdir}/dim${dim}context-vecs
${bindir}/count_and_filter -train $deps -cvocab $cv -wvocab $wv -min-count $mincount
${bindir}/word2vecf -train $deps -wvocab $wv -cvocab $cv -output $out -size $dim -negative $ns -threads $p -dumpcv $outcv
nkf -w $out > ${out}.utf8
nkf -w $outcv > ${outcv}.utf8
mv ${out}.utf8 ${out}
mv ${outcv}.utf8 ${outcv}
${py} vecs2nps.py ${out} ${out}
${py} vecs2nps.py ${outcv} ${outcv}
