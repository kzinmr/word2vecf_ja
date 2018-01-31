import sys
import gzip
import re
from collections import Counter

from pyknp import KNP


def result_reader(fp, splitter='EOS'):
    lines = ''
    split_pattern = '(?:^|\n){}($|\n)'.format(splitter)
    for line in fp:
        if not line.strip():
            continue
        m = re.match(split_pattern, line)
        if m:
            lines += line
            yield lines
            lines = ''
        else:
            lines += line
    return lines

def is_single(repname):
    surf = repname.split('/')[0]
    if not re.match('(\w\w+|[一-龥]+)', surf):
        return True
    else:
        return False

def gt_max_length(repname, maxlen=200):
    return len(repname) > maxlen

def write_vocab(knp, ifp, ofp):
    wc = Counter()
    thr = 2
    l = []
    i = 0
    for r in result_reader(ifp):
        if not r:
            continue
        try: # 半角など変な文字列
            blist = knp.result(r)
        except:
            continue
        for bnst in blist:
            i += 1
            b_rep = bnst.repname if not is_single(bnst.repname) else ''
            b_hrep = bnst.hrepname if not is_single(bnst.hrepname) else ''
            b_hprep = bnst.hprepname if not is_single(bnst.hprepname) else ''
            if gt_max_length(b_rep):
                b_rep = ''
            if gt_max_length(b_hrep):
                b_hrep = ''
            if gt_max_length(b_hprep):
                b_hprep = ''
            if i % 1000000 == 0:
                print('%s%s' % (i, len(wc)), file=sys.stderr)
                wc.update(l)
                l = []
            if b_rep:
                l.append(b_rep)
            if b_hrep:
                l.append(b_hrep)
            if b_hprep:
                l.append(b_hprep)
    wc.update(l)
    print('%s' % (len(wc)), file=sys.stderr)

    for w, c in sorted([(w, c) for w, c in wc.items()
                        if c >= thr and w != ''], key=lambda x: -x[1]):
        ofp.write('\t'.join([w.strip(), str(c)])+'\n')

def main():
    knp = KNP(jumanpp=True, option='-tab')
    knpfile = sys.argv[1] # '../dataset/mountains_ja.knp.gz'
    vocabfile = sys.argv[2] # '../dataset/mountains_ja.vocab.gz'
    assert 'gz' in knpfile
    with gzip.open(knpfile, mode='rt', encoding='utf8', errors='ignore') as ifp,\
         gzip.open(vocabfile, mode='wt', encoding='utf8') as ofp:
        write_vocab(knp, ifp, ofp)


if __name__ == "__main__":
    main()
