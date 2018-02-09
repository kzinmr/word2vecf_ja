#!/usr/bin/zsh

datadir=${1-/data/user/wikipedia_knp}
outdir=${2-/data/user/wikipedia_wakati}
p=${3-10}
py=${4-/home/user/miniconda3/envs/wikipedia/bin/python}
echo "extract wakati..."
for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    ls $d/*.gz | parallel --no-notice -j $p "${py} knp2wakati.py {} ${od}/{/.}.wakati.gz"
    echo "DONE:$d:t"
done
zcat ${outdir}/*/*.wakati.gz > ${outdir}/wakati.txt
