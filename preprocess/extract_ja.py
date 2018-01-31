import sys
import gzip
import re
from collections import defaultdict

from pyknp import KNP


def attach_case(blist):
    """
    # 複合語単位->全部とる(述語側からとる項はrepnameのみ)
    # 数量汎化しない（とりあえず）
    # argument側からrel取得する場合: bnst -rel-> parent
    # predicate側からrel取得する場合(連格など): children -rel-> bnst
    # 冗長にとる方針 （複合語headと項の代表headが不一致する場合(教授らほか３人が話す)）
    # TODO: 照応解析施してから行うべき
    # ?: 連用, 複合辞連用 (ため, よる, また, )
    """

    def yield_case(m, h, rel):
        case = "_".join((rel, m))
        icase = "I_".join((rel, h))
        return case, icase

    for i, bnst in enumerate(blist):
        # bnst -rel-> parent
        b_rep = bnst.repname
        b_hrep = bnst.hrepname if bnst.hrepname != bnst.repname else ''
        b_hprep = bnst.hprepname if bnst.hprepname != bnst.repname else ''

        par = bnst.parent
        reltype = bnst.dpndtype
        if par:
            p_rep = par.repname
            p_hrep = par.hrepname if par.hrepname != par.repname else ''
            p_hprep = par.hprepname if par.hprepname != par.repname else ''

            if reltype == 'P':
                # paratype = bnst.bnst_head().features['並列タイプ']
                rel = '並列'
                m = b_rep
                h = p_rep
            elif reltype == 'A':
                # KNPのバグ: gold=(教授ら -A-> ３人の), sys=(教授ら -A-> 予定)
                rel = '同格'
                m = b_rep
                par = blist[i+1].bnst_head()
                h = par.repname # p_rep
            else:
                # 表層格パート (incl. 'ノ格', '隣', '連格')
                rel = bnst.bnst_head().features['係']
                if rel == 'NONE':
                    continue
                m = b_rep
                h = p_rep
            if m and h:
                yield yield_case(m,h,rel)
                if p_hrep:
                    yield yield_case(m,p_hrep,rel)
                if p_hprep:
                    yield yield_case(m,p_hprep,rel)                
                if b_hrep:
                    yield yield_case(b_hrep,h,rel)
                    if p_hrep:
                        yield yield_case(b_hrep,p_hrep,rel)
                    if p_hprep:
                        yield yield_case(b_hrep,p_hprep,rel)
                if b_hprep:
                    yield yield_case(b_hprep,h,rel)
                    if p_hrep:
                        yield yield_case(b_hprep,p_hrep,rel)
                    if p_hprep:
                        yield yield_case(b_hprep,p_hprep,rel)                        

        # children -rel-> bnst (述語がpasを持つ場合)
        # implicitな格を述語側から付与（したがって一部重複あり; uniqするべき?）
        h = b_rep
        parpas = bnst.bnst_head().features.pas
        if parpas:
            case2args = parpas.arguments
            for case, args in case2args.items():
                for arg in args:
                    rel = '{}格'.format(case)
                    m = arg.rep # 辿るの面倒なので項の複合語展開しない
                    if m and h:
                        yield yield_case(m,h,rel)
                        if b_hrep:
                            yield yield_case(m,b_hrep,rel)
                        if b_hprep:
                            yield yield_case(m,b_hprep,rel)

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

def read_vocab(fp, threshold=3):
    v = {}
    for line in fp:
        line = line.strip().split('\t')
        if len(line) != 2: continue
        if int(line[1]) >= threshold:
            v[line[0]] = int(line[1])
    return v

def write_deps(knp, vocab, ifp, ofp):
    for r in result_reader(ifp):
        if not r:
            continue
        try: # デコード成功だが変な文字列
            blist = knp.result(r)
        except:
            continue
        for case, icase in attach_case(blist):
            if case.split('_')[-1] in vocab and icase.split('_')[-1] in vocab:
                m = case.split('_')[1]
                h = icase.split('_')[1]
                ofp.write(h + ' ' + case + '\n')
                ofp.write(m + ' ' + icase + '\n')


def main():
    knp = KNP(jumanpp=True, option='-tab')
    knpfile = sys.argv[1] # '../dataset/wikipedia.knp.gz'
    vocabfile = sys.argv[2] # '../dataset/wikipedia.vocab'
    depsfile = sys.argv[3] # '../dataset/wikipedia.deps'

    # 全単語集合に関する頻度足切り
    vocab_thre = 100
    assert 'gz' in vocabfile
    with gzip.open(vocabfile, mode='rt', encoding='utf8') as ifp:
        vocab = read_vocab(ifp, vocab_thre)

    # extract dependency pairs from a knp parsed file.
    # CoNLL: tokens = [(id,form, head,deprel)]
    assert 'gz' in knpfile
    assert 'gz' in depsfile
    with gzip.open(knpfile, mode='rt', encoding='utf8', errors='ignore') as ifp,\
         gzip.open(depsfile, mode='wt', encoding='utf8') as ofp:
        write_deps(knp, vocab, ifp, ofp)


if __name__ == "__main__":
    main()