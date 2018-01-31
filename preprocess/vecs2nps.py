import numpy as np
import sys

filename=sys.argv[1]
foutname=sys.argv[2]
with open(filename, mode='rt', encoding='utf8') as fh:
    first = fh.readline()
    size = list(map(int, first.strip().split(' ')))
    wvecs = np.zeros((size[0], size[1]), float)
    vocab = []
    for i, line in enumerate(fh):
        line = line.strip().split(' ')
        try:
            wvecs[i,] = np.array(list(map(float, line[1:])))
            vocab.append(line[0]+'\n')
        except:
            print(line[0])

np.save(foutname+".npy", wvecs)
with open(foutname+".vocab", "wt") as outf:
    outf.write("".join(vocab)+"\n")
