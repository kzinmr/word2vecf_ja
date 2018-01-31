#!/usr/bin/zsh

datadir=${1-/mnt/2tb_ssd_a/k_inamura/wikipedia}
outdir=${2-/mnt/2tb_ssd_a/k_inamura/wikipedia_knp}
p=${3-10}

py=/home/k_inamura/miniconda3/envs/wikipedia/bin/python
for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    of=$
    ls $d/*.bz2 | parallel --no-notice --dry-run -j $p "${py} preprocess.py {}| jumanpp | knp -tab |gzip -c > ${od}/{/.}.knp.gz"
done