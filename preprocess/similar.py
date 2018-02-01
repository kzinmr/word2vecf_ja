import sys
import re
import numpy as np

from pyknp import KNP


def lookup_match(q, w2vec, topk=3):
    if '_' in q:
        return False
    ok = False
    pattern = r'\w+_{}$'.format(q)
    seen = set()
    for w in w2vec:
        if w not in seen:
            m = re.match(pattern, w)
            if m:
                print(w)
                q_new = m.group(0)
                print_similar(q_new, w2vec, topk)
                seen.add(w)
                ok = True
    return ok

def print_similar(q, w2vec, topk=3):
    print('top-{} similar to {}:'.format(topk, q))
    qv = w2vec[q]
    klist = sorted([(w, qv.dot(v)) for w, v in w2vec.items()], key=lambda x:-x[1])[:topk]
    for w, s in klist:
        print('{}:\t{}'.format(w, s))

def parse_and_print(q, knp, w2vec, topk=3):
    if '/' in q:
        if q in w2vec:
            print_similar(q, w2vec, topk)
        else:
            print('Not in vocab: {}'.format(q))
            return

    blist = knp.parse(q)
    if not blist:
        print('parse error: {}'.format(q))
        return
    if len(blist) > 1:
        print('multiple bunsetsu input: {}'.format('|'.join([b.repname for b in blist])))
    b = blist[0]
    qrep = b.repname
    qhrep = b.hrepname
    qhprep = b.hprepname
    if qrep and qrep in w2vec:
        print_similar(qrep, w2vec, topk)
    elif qhrep and qhrep in w2vec:
        print_similar(qhrep, w2vec, topk)
    elif qhprep and qhprep in w2vec:
        print_similar(qhprep, w2vec, topk)
    else:
        print('Not in vocab: {}({})'.format(q, qrep))


def main():
    knp = KNP(jumanpp=True, option='-tab -assignf')
    npyfile = sys.argv[1]
    vocabfile = sys.argv[2]
    topk = int(sys.argv[3])
    vectors = np.load(npyfile)
    vocabs = open(vocabfile, 'rt', encoding='utf8').read().splitlines()
    assert len(vocabs) == vectors.shape[0]
    w2vec = {w: v / np.linalg.norm(v) for w, v in zip(vocabs, vectors)}

    while True:
        q = input()
        parse_and_print(q, knp, w2vec, topk)


if __name__ == '__main__':
    main()
