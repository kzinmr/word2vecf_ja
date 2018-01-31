import argparse
import os
import glob
import gzip
from collections import defaultdict


def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--vocabdir', '-d', type=str, 
                        help='vocabファイル群があるディレクトリ。')
    parser.add_argument('--outfilename', '-o', type=str, 
                        help='vocabを保存する。')
    parser.add_argument('--threshold', type=int, default=50, 
                        help='単語出現頻度による閾値カット')

    args = parser.parse_args()
    vocabdir = args.vocabdir
    threshold = args.threshold
    outfilename = args.outfilename

    flist = glob.glob('{}/*/*.vocab.gz'.format(vocabdir))
    d = defaultdict(int)
    for filename in flist:
        with gzip.open(filename, mode='rt', encoding='utf8') as ifp:
            lines = ifp.read().splitlines()
        wc = map(lambda x:x.split('\t'), lines)
        for w, c in wc:
            d[w] += int(c)
    lines = ['{}\t{}\n'.format(w, d[w]) for w in d if d[w] > threshold]
    assert 'gz' in outfilename
    outpath = os.path.join(vocabdir, outfilename)
    with gzip.open(outpath, 'wt', encoding='utf8') as ofp:
        ofp.write(''.join(lines))

if __name__ == "__main__":
    main()