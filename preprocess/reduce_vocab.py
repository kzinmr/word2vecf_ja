import argparse
import gzip
import os
import glob
from collections import defaultdict


def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--vocabdir', '-d', type=str,
                        help='vocabファイル群があるディレクトリ。ここに保存もする。')
    parser.add_argument('--threshold', type=int, default=50,
                        help='単語出現頻度による閾値カット')

    args = parser.parse_args()
    vocabdir = args.vocabdir
    threshold = args.threshold

    flist = glob.glob('{}/*/*.vocab.gz'.format(vocabdir))
    d = defaultdict(int)
    for filename in flist:
        with gzip.open(filename, mode='rt', encoding='utf8') as ifp:
            lines = ifp.read().splitlines()
        wc = map(lambda x: x.split('\t'), lines)
        for w, c in wc:
            d[w] += int(c)
    lines = ['{}\t{}\n'.format(w, d[w]) for w in d if d[w] > threshold]
    with gzip.open(os.path.join(vocabdir, 'wikipedia.vocab.gz'), 'wt', encoding='utf8') as ofp:
        ofp.write(''.join(lines))

if __name__ == "__main__":
    main()
