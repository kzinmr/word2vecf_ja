import sys
import re
import numpy as np


def lookup_match(q, w2vec):
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
                print_similar(q_new, w2vec)
                seen.add(w)
                ok = True
    return ok

def print_similar(q, w2vec, topk=3):
    print('top-{} similar to {}:'.format(topk, q))
    qv = w2vec[q]
    klist = sorted([(w, qv.dot(v)) for w, v in w2vec.items()], key=lambda x:-x[1])[:topk]
    for w, s in klist:
        print('{}:\t{}'.format(w, s))

def main():
    npyfile = sys.argv[1]
    vocabfile = sys.argv[2]
    vectors = np.load(npyfile)
    vocabs = open(vocabfile, 'rt', encoding='utf8').read().splitlines()
    assert len(vocabs) == vectors.shape[0]
    w2vec = {w: v / np.linalg.norm(v) for w, v in zip(vocabs, vectors)}

    while True:
        q = input()
        if q in w2vec:
            print_similar(q, w2vec)
        elif not lookup_match(q, w2vec):
            print('Not in vocab: {}'.format(q))


if __name__ == '__main__':
    main()
