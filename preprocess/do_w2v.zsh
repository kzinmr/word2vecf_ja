
#!/usr/bin/zsh

cores=${1-4}
py=/miniconda/envs/py3/bin/python
scriptdir=/word2vecf_ja/preprocess
bindir=/word2vecf_ja/word2vecf

datadir=/data/wikipedia
knpdir=/data/knp
wakatidir=/data/wakati
vecdir=/data/vec_w2v
vocabdir=${depdir}/vocab
mkdir -p $knpdir $vocabdir $vecdir

# ${scriptdir}/extract_ja.zsh $knpdir ${vocabdir}/wikipedia.vocab.gz $depdir $cores $py
${scriptdir}/knp2wakati.zsh $knpdir $wakatidir $cores $py

${scriptdir}/word2vec.zsh $wakatidir/wakati.txt $vecdir $bindir $cores $py

cd /data
tar zcf $wakatidir.tar.gz $wakatidir
tar zcf $vecdir.tar.gz $vecdir
gsutil cp gs://nd-dataset/wikipedia_20180101.tar.gz /data/wikipedia_20180101.tar.gz
gsutil cp $wakatidir.tar.gz gs://nd-dataset/wikipedia_20180101/$wakatidir.tar.gz
gsutil cp $vecdir.tar.gz gs://nd-dataset/wikipedia_20180101/$vecdir.tar.gz

if [[ -f done.sh ]];then
    $scriptdir/done.sh $0
fi
