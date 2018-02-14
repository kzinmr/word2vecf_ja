#!/usr/bin/zsh
SECONDS=0

cores=${1-4}
py=/miniconda/envs/py3/bin/python
scriptdir=/word2vecf_ja/preprocess
bindir=/word2vecf_ja/word2vecf
slackdir=/word2vecf_ja/slackbot

datadir=/data/wikipedia
knpdir=/data/knp
wakatidir=/data/wakati
vecdir=/data/vec_w2v
vocabdir=${depdir}/vocab
mkdir -p $knpdir $vocabdir $vecdir

echo "converting knp to wakati..."
# ${scriptdir}/extract_ja.zsh $knpdir ${vocabdir}/wikipedia.vocab.gz $depdir $cores $py
${scriptdir}/knp2wakati.zsh $knpdir $wakatidir $cores $py
echo "lerning w2v vectors..."
${scriptdir}/word2vec.zsh $wakatidir/wakati.txt $vecdir $bindir $cores $py

echo "copying to GCS..."
cd /data
wakatid=$wakatidir:t
vecd=$vecdir:t
tar zcf $wakatid.tar.gz $wakatid
tar zcf $vecd.tar.gz $vecd
gsutil cp $wakatid.tar.gz gs://nd-dataset/wikipedia_20180101/$wakatid.tar.gz
gsutil cp $vecd.tar.gz gs://nd-dataset/wikipedia_20180101/$vecd.tar.gz

time_elapsed=$(echo $SECONDS)

if [[ -f $slackdir/done.sh ]];then
    $slackdir/done.sh "$0: $time_elapsed"
fi
