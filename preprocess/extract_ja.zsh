#!/usr/bin/zsh

datadir=${1-/data/user/wikipedia_knp}
vocabfile=${2-/data/user/wikipedia_dep/vocab/wikipedia.vocab.gz}
outdir=${3-/data/user/wikipedia_dep/deps}
p=${4-10}
py=${5-/home/user/miniconda3/envs/wikipedia/bin/python}

for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    ls $d/*.gz | parallel --no-notice -j $p "${py} extract_ja.py {} ${vocabfile} ${od}/{/.}.deps.gz"
    echo "DONE:$d:t"
done

zcat ${outdir}/*/*.deps.gz | gzip -c > ${outdir}/context.deps.gz
