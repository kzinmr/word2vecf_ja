#!/usr/bin/zsh
SECONDS=0

cores=${1-4}
py=/miniconda/envs/py3/bin/python
scriptdir=/word2vecf_ja/preprocess
slackdir=/word2vecf_ja/slackbot

datadir=/data/wikipedia
knpdir=/data/knp
mkdir -p $knpdir

echo "preprocessing..."
${scriptdir}/preprocess.zsh $datadir $knpdir $cores $py

echo "copying to GCS..."
knpd=$knpdir:t
cd /data
tar zcf $knpd.tar.gz $knpd
gsutil cp $knpd.tar.gz gs://nd-dataset/wikipedia_20180101/$knpd.tar.gz

time_elapsed=$(echo $SECONDS)

if [[ -f $slackdir/done.sh ]];then
    $slackdir/done.sh "$0: $time_elapsed"
fi