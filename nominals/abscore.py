import sys
import os
import gzip

def w2c_reader(ifp):
    lines = ifp.read().splitlines()
    d = {}
    for l in lines:
        if l:
            a, b, c = l.split('\t')
            d['\t'.join((a,b))] = int(c)
    return d

def main():
    dffile_ab = sys.argv[1] # head + '.ab.df.gz' # './wiki_00.ab.df.gz'
    dffile_anob = sys.argv[2] # head + '.anob.df.gz'# './wiki_00.anob.df.gz'
    outdir = sys.argv[3]
    # df(AB)/df(AのB)
    dffile_abscore = os.path.join(outdir, 'abscore.gz')
    with gzip.open(dffile_ab, mode='rt', encoding='utf8') as fp_df_ab,\
        gzip.open(dffile_anob, mode='rt', encoding='utf8') as fp_df_anob,\
        gzip.open(dffile_abscore, mode='wt', encoding='utf8') as ofp_score:
        ab2c = w2c_reader(fp_df_ab)
        anob2c = w2c_reader(fp_df_anob)
        ab_set = set.intersection(set(ab2c.keys()), set(anob2c.keys()))
        print('{}, {}, {}'.format(len(ab2c), len(anob2c), len(ab_set)))
        ab2score = {ab: ab2c[ab] / float(anob2c[ab]) for ab in ab_set}
        ofp_score.write('\n'.join(['\t'.join((ab, str(score))) for ab, score in ab2score.items()]) + '\n')

if __name__ == '__main__':
    main()
