#!/usr/bin/zsh

datadir=${1-/data/user/wikipedia_knp}
outdir=${2-/data/user/wikipedia_compound}
p=${3-10}
py=${4-/home/user/miniconda3/envs/wikipedia/bin/python}
echo "extract Anob/AB ..."
for d in $(ls -d ${datadir}/*)
do
    od=${outdir}/$d:t
    if [[ ! -d $od ]];then
        mkdir -p $od
    fi
    ls $d/*.gz | parallel --no-notice -j $p "${py} nominal_statistics.py {} ${od}"
    zcat ${od}/*.ab.tf.gz | gzip -c > ${od}.ab.tf.gz
    zcat ${od}/*.ab.df.gz | gzip -c > ${od}.ab.df.gz
    zcat ${od}/*.anob.tf.gz | gzip -c > ${od}.anob.tf.gz
    zcat ${od}/*.anob.df.gz | gzip -c > ${od}.anob.df.gz
    echo "DONE:$d:t"
done

echo "reducing TF/DF of AnoB/AB..."
zcat ${outdir}/*.ab.tf.gz | gzip -c > ${outdir}/AB.tf.raw.gz
$py reduce_w2c.py ${outdir}/AB.tf.raw.gz ${outdir}/AB.tf.gz
zcat ${outdir}/*.ab.df.gz | gzip -c > ${outdir}/AB.df.raw.gz
$py reduce_w2c.py ${outdir}/AB.df.raw.gz ${outdir}/AB.df.gz
zcat ${outdir}/*.anob.tf.gz | gzip -c > ${outdir}/AnoB.tf.raw.gz
$py reduce_w2c.py ${outdir}/AnoB.tf.raw.gz ${outdir}/AnoB.tf.gz
zcat ${outdir}/*.anob.df.gz | gzip -c > ${outdir}/AnoB.df.raw.gz
$py reduce_w2c.py ${outdir}/AnoB.df.raw.gz ${outdir}/AnoB.df.gz

echo "calc score..."
$py abscore.py ${outdir}/AB.df.gz ${outdir}/AnoB.df.gz ${outdir}
