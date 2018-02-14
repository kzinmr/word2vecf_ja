import sys
import gzip

from collections import defaultdict

def w2c_reader(ifp):
    lines = ifp.read().splitlines()
    d = {}
    for l in lines:
        if l and len(l.split('\t'))==3:
            a, b, c = l.split('\t')
            d['\t'.join((a,b))] = int(c)
    return d

def reduce_count(did2count):
    global_count = defaultdict(int)
    for did in did2count:
        w2c  = did2count[did]
        for w, c in w2c.items():
            global_count[w] += c
    return global_count

def main():
    filename = sys.argv[1]
    outfilepath = sys.argv[2]
    with gzip.open(filename, mode='rt', encoding='utf8') as ifp,\
        gzip.open(outfilepath, mode='wt', encoding='utf8') as ofp:
        w2c = w2c_reader(ifp)
        w2c_reduced = reduce_count(w2c)
        ofp.write('\n'.join([w+'\t'+str(c) for w,c in w2c_reduced.items()]) + '\n')

if __name__ == '__main__':
    main()
