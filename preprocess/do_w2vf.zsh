#!/usr/bin/zsh
SECONDS=0

cores=${1-4}
py=/miniconda/envs/py3/bin/python
scriptdir=/word2vecf_ja/preprocess
bindir=/word2vecf_ja/word2vecf
slackdir=/word2vecf_ja/slackbot

datadir=/data/wikipedia
knpdir=/data/knp
depdir=/data/dep
vecdir=/data/vec
vocabdir=${depdir}/vocab
mkdir -p $knpdir $vocabdir $vecdir

echo "constructing vocab..."
${scriptdir}/vocab.zsh $knpdir $vocabdir $cores $py
echo "extracting deps..."
${scriptdir}/extract_ja.zsh $knpdir ${vocabdir}/wikipedia.vocab.gz $depdir $cores $py
echo "lerning w2vf vectors..."
${scriptdir}/word2vecf.zsh ${depdir}/context.deps $vecdir $bindir $cores $py

echo "copying to GCS..."
cd /data
depd=$depdir:t
vecd=$vecdir:t
tar zcf $depd.tar.gz $depd
tar zcf $vecd.tar.gz $vecd
gsutil cp $depd.tar.gz gs://nd-dataset/wikipedia_20180101/$depd.tar.gz
gsutil cp $vecd.tar.gz gs://nd-dataset/wikipedia_20180101/$vecd.tar.gz

time_elapsed=$(echo $SECONDS)

if [[ -f $slackdir/done.sh ]];then
    $slackdir/done.sh "$0: $time_elapsed"
fi
