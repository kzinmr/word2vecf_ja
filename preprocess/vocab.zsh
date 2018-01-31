#!/usr/bin/zsh

datadir=${1-/data/user/wikipedia_knp}
outdir=${2-/data/user/wikipedia_dep/vocab}
p=${3-10}
py=${4-/home/user/miniconda3/envs/wikipedia/bin/python}

for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    mkdir $od
    ls $d/*.gz | parallel --no-notice -j $p "${py} vocab.py {} ${od}/{/.}.vocab.gz"
    echo "DONE:$d:t"
done

python reduce_vocab.py -d ${outdir}
