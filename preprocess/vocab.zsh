#!/usr/bin/zsh

datadir=${1-/mnt/2tb_ssd_a/k_inamura/wikipedia_knp}
outdir=${2-/mnt/2tb_ssd_a/k_inamura/wikipedia_dep/vocab}
p=${3-10}

py=/home/k_inamura/miniconda3/envs/wikipedia/bin/python
for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    ls $d/*.gz | parallel --no-notice -j $p "${py} vocab.py {} ${od}/{/.}.vocab.gz"
    echo "DONE:$d:t"
done
outfilename=wikipedia.vocab.gz
python reduce_vocab.py -d ${outdir} ${outfilename}