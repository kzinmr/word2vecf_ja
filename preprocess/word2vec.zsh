#!/usr/bin/zsh

wakatis=${1} # /data/user/wikipedia_dep/wikipedia.deps
vecdir=${2} # /data/user/wikipedia_vec
bindir=${3-../word2vecf}
p=${4-12}
py=${5}
dim=256
w=5
ns=10
ds=1e-5
alpha=0.025
mincount=100
out=${vecdir}/dim${dim}vecs
outcv=${vecdir}/dim${dim}context-vecs

${bindir}/word2vec -train $wakatis -output $out -size $dim -window $w -sample $ds -negative $ns -hs 0 -alpha $alpha -threads $p -save-vocab $out.vocab -dumpcv $outcv
nkf -w $out > ${out}.utf8
nkf -w $outcv > ${outcv}.utf8
mv ${out}.utf8 ${out}
mv ${outcv}.utf8 ${outcv}
${py} vecs2nps.py ${out} ${out}
${py} vecs2nps.py ${outcv} ${outcv}

