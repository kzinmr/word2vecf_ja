import sys
import gzip
import re
from enum import Enum

from pyknp import KNP


class WORDFORM(Enum):
    MIDASI = 1
    LONGEST = 2
    HEAD = 3
    HEADPRIME = 4


def is_single(repname):
    surf = repname.split('/')[0]
    if not re.match('(?u)(\w\w+|[一-龥]+)', surf):
        return True
    return False

def is_ignored(bnst):
    repname = bnst.repname
    if repname:
        if is_single(repname):
            return True
    else:
        for m in bnst.mrph_list():
            if '<未知語><記英数カ><英記号><記号>' in m.fstring:
                return True
    return False

def no_ignored(bnst):
    return not is_ignored(bnst)

def extract_counter(bnst, direct_only=True):
    # INPUT: １０ｃｍ相当
    # OUTPUT: <数量>+センチメートル/せんちめーとる+相当/そうとう
    # suffix: カウンタの後に'カウンタ'で取れない接尾語(e.g. 10+分+前)がある場合
    num_r, counter_r, suffix = '', '', ''
    for tag in bnst.tag_list():
        fs = tag.features
        if 'カウンタ' in fs:
            counter = fs['カウンタ']
            if counter in tag.repname:
                for r in tag.repname.split('+'):
                    if counter in r:
                        counter_r = r
                    elif not num_r:
                        num_r = r
                    else:
                        suffix = r
            elif counter_r:
                suffix = '+'.join([suffix, tag.repname])
    suffix = '' if direct_only else suffix
    return num_r, counter_r, suffix

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def convert_bnst_number(bnst):
    num, cntr, suf =  extract_counter(bnst, False)
    if cntr:
        return '<数量>+{}'.format('+'.join([cntr, suf]) if suf else cntr)
    else:
        return '+'.join(filter(None, f7(['<数量>' if '数量' in t.features
                                                 else t.repname
                                         for t in bnst.tag_list()])))


def read_words(blist, wordform=WORDFORM.LONGEST):
    """
    KNP解析結果を一行一文の分かち書きに戻す
    # 複合語単位->全部とる(述語側からとる項はrepnameのみ)
    # 数量汎化しない（とりあえず）
    """
    words = []
    blist = list(filter(no_ignored, blist))
    # blist = [convert_bnst_number(b) for b in blist]
    if wordform == WORDFORM.MIDASI:
        words = [''.join([t.get_surface() for t in bnst.tag_list()])
                 for bnst in blist]
    elif wordform == WORDFORM.LONGEST:
        words = [bnst.repname for bnst in blist if bnst.repname]
    elif wordform == WORDFORM.HEAD:
        words = [bnst.hrepname for bnst in blist if bnst.repname]
    elif wordform == WORDFORM.HEADPRIME:
        words = [bnst.hprepname for bnst in blist if bnst.repname]
    return words

def result_reader(fp, splitter='EOS'): # TODO: 文単位(sid)・文書単位(did)出力
    # did, sid = -1, -1
    lines = ''
    split_pattern = '(?:^|\n){}($|\n)'.format(splitter)
    # header_pattern = '# S-ID:([0-9]+)-([0-9]+) '
    for line in fp:
        if not line.strip():
            continue
        # mh = re.match(header_pattern, line)
        # if mh:
        #     did = int(mh.group(1))
        #     sid = int(mh.group(2))
        m = re.match(split_pattern, line)
        if m:
            lines += line
            yield lines #, did, sid
            lines = ''
        else:
            lines += line

def write_wakati(knp, ifp, ofp, wordform=WORDFORM.LONGEST):
    current_did = -1
    for r in result_reader(ifp):
        if not r:
            continue
        try: # デコード成功だが変な文字列
            blist = knp.result(r)
        except:
            continue
        words = read_words(blist, wordform=wordform)
        if words:
            ofp.write(' '.join(words) + '\n')


def main():
    knp = KNP(jumanpp=True, option='-tab')
    knpfile = sys.argv[1] # '../dataset/wikipedia.knp.gz'
    wakatifile = sys.argv[2] # '../dataset/wikipedia.deps'

    assert 'gz' in knpfile
    assert 'gz' in wakatifile
    with gzip.open(knpfile, mode='rt', encoding='utf8', errors='ignore') as ifp,\
         gzip.open(wakatifile, mode='wt', encoding='utf8') as ofp:
        write_wakati(knp, ifp, ofp, WORDFORM.LONGEST)


if __name__ == "__main__":
    main()