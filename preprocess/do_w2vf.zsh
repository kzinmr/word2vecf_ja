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


${scriptdir}/preprocess.zsh $datadir $knpdir $cores $py


${scriptdir}/vocab.zsh $knpdir $vocabdir $cores $py

${scriptdir}/extract_ja.zsh $knpdir ${vocabdir}/wikipedia.vocab.gz $depdir $cores $py

${scriptdir}/word2vecf.zsh ${depdir}/context.deps $vecdir $bindir $cores $py

cd /data
tar zcf $knpdir.tar.gz $knpdir
tar zcf $vecdir.tar.gz $vecdir
gsutil cp gs://nd-dataset/wikipedia_20180101.tar.gz /data/wikipedia_20180101.tar.gz
gsutil cp $knpdir.tar.gz gs://nd-dataset/wikipedia_20180101/$knpdir.tar.gz
gsutil cp $vecdir.tar.gz gs://nd-dataset/wikipedia_20180101/$vecdir.tar.gz

time_elapsed=$(echo $SECONDS)

if [[ -f $slackdir/done.sh ]];then
    $slackdir/done.sh "$0: $time_elapsed"
fi
