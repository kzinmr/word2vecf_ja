import argparse
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
    klist = sorted([(w, qv.dot(v)) for w, v in w2vec.items()], key=lambda x: -x[1])[:topk]
    for w, s in klist:
        print('{}:\t{}'.format(w, s))

def print_fired(q, c2vec, w2vec, topk=3):
    print('\ttop-{} fired context by {}:'.format(topk, q))
    wv = w2vec[q]
    klist = sorted([(c, wv.dot(v)) for c, v in c2vec.items()], key=lambda x: -x[1])[:topk]
    for c, s in klist:
        print('\t{}:\t{}'.format(c, s))

def print_noparse(q, w2vec, topk=3, c2vec={}):
    if q in w2vec:
        print_similar(q, w2vec, topk)
        if c2vec:
            print_fired(q, c2vec, w2vec, topk=5)
    else:
        print('Not in vocab: {}'.format(q))

def parse_and_print(q, knp, w2vec, topk=3, c2vec={}):
    if '/' in q:
        print_noparse(q, w2vec, topk, c2vec)

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
    f = False
    if qrep and qrep in w2vec:
        f = True
        print_similar(qrep, w2vec, topk)
        if c2vec:
            print_fired(qrep, c2vec, w2vec, topk=5)
    if qhrep and qhrep in w2vec:
        f = True
        print_similar(qhrep, w2vec, topk)
        if c2vec:
            print_fired(qhrep, c2vec, w2vec, topk=5)
    if qhprep and qhprep in w2vec:
        f = True
        print_similar(qhprep, w2vec, topk)
        if c2vec:
            print_fired(qhprep, c2vec, w2vec, topk=5)
    if not f:
        print('Not in vocab: {}({})'.format(q, qrep))

def load_model(npyfile, vocabfile):
    vectors = np.load(npyfile)
    vocabs = open(vocabfile, 'rt', encoding='utf8').read().splitlines()
    assert len(vocabs) == vectors.shape[0]
    w2vec = {w: v / np.linalg.norm(v) for w, v in zip(vocabs, vectors)}
    return w2vec


def main():
    knp = KNP(jumanpp=True, option='-tab -assignf')

    parser = argparse.ArgumentParser()
    parser.add_argument("--npyfile", "-m")
    parser.add_argument("--vocabfile", "-v")
    parser.add_argument("--topk", "-k", type=int, default=5)
    parser.add_argument("--query", "-q", type=str, default='')
    parser.add_argument("--cnpyfile", "-c", type=str, default='')
    parser.add_argument("--cvocabfile", "-u", type=str, default='')
    args = parser.parse_args()

    npyfile = args.npyfile
    vocabfile = args.vocabfile
    topk = args.topk
    query = args.query
    cnpyfile = args.cnpyfile
    cvocabfile = args.cvocabfile

    w2vec = load_model(npyfile, vocabfile)
    c2vec = {}
    cvocabs = []
    if cnpyfile and cvocabfile:
        c2vec = load_model(cnpyfile, cvocabfile)

    if query:
        parse_and_print(query, knp, w2vec, topk, c2vec)
        return
    while True:
        q = input()
        parse_and_print(q, knp, w2vec, topk, c2vec)


if __name__ == '__main__':
    main()
