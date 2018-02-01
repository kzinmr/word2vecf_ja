import numpy as np
import sys

filename=sys.argv[1]
foutname=sys.argv[2]
with open(filename, mode='rt', encoding='utf8') as fh:
    first = fh.readline()
    size = list(map(int, first.strip().split(' ')))
    dim = size[1]
    wvecs = [] # np.zeros((size[0], size[1]), float)
    vocab = []
    for line in fh:
        line = line.strip().split(' ')
        v = list(map(float, line[1:]))
        if len(v) == dim:
            wvecs.append(v)
            vocab.append(line[0]+'\n')
        else:
            print(line[0])
    wvecs = np.array(wvecs)
np.save(foutname+".npy", wvecs)
with open(foutname+".vocab", "wt") as outf:
    outf.write("".join(vocab)+"\n")
