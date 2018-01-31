#!/usr/bin/zsh

datadir=${1-/data/user/wikipedia}
outdir=${2-/data/user/wikipedia_knp}
p=${3-10}
py=${4-/home/user/miniconda3/envs/wikipedia/bin/python}

for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    of=$
    ls $d/*.bz2 | parallel --no-notice -j $p "${py} preprocess.py {}| jumanpp | knp -tab |gzip -c > ${od}/{/.}.knp.gz"
done
