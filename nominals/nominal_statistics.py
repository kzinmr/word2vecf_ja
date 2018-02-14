import sys
import os
import gzip
import re
from collections import defaultdict, Counter

from pyknp import KNP

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

def bnst_head(bnst):
    tag_list = bnst.tag_list()
    if len(tag_list) == 1:
        return tag_list[0]
    for tag in tag_list:
        if '文節内' not in tag.features:
            return tag
    return None

def is_meisi(bnst):
    return '<体言>' in bnst.fstring

def wordform(tag):
    return tag.repname


# AnoB, AB extraction module

def extract_anob(bnst, delimiter='\t'):
    """ 「AのB」の対を取得。
    再帰表現は係り受けの信頼性から「AのBのC」まで取得(AC, BC両方取得)。 
    """
    assert is_meisi(bnst)
    pairs = []
    atag = bnst_head(bnst) #.bnst_head()
    if '係' not in atag.features or atag.features['係'] != 'ノ格':
        return pairs
    btag = atag.parent
    assert btag
    arep = wordform(atag)
    brep = wordform(btag)
    if arep and brep:
        pairs = [delimiter.join((arep, brep))]
    if '係' in btag.features and btag.features['係'] == 'ノ格':
        ctag = btag.parent
        assert ctag
        crep = wordform(ctag)
        if crep:
            pairs.append(delimiter.join((brep, crep)))
            pairs.append(delimiter.join((arep, crep))) # とる?(20~30%程度の分布)
    return pairs

def extract_ab(bnst, delimiter='\t'):
    """ 文節内の連接基本句の組み合わせを返す(ABC-> AB, BC)
    """
    assert is_meisi(bnst)
    pairs = []
    tags = bnst.tag_list()
    if len(tags) < 2:
        return pairs
    for i, t1 in enumerate(tags[:-1]):
        t2 = tags[i+1]
        t1rep = wordform(t1)
        t2rep = wordform(t2)
        if t1rep and t2rep:
            pairs.append(delimiter.join((t1rep, t2rep)))
    return pairs


def parse_nominal(blist):
    anob_pairs = []
    ab_pairs = []
    for bnst in blist:
        if is_meisi(bnst) and no_ignored(bnst):
            anob = extract_anob(bnst)
            ab = extract_ab(bnst)
            anob_pairs.extend(anob)
            ab_pairs.extend(ab)
    return anob_pairs, ab_pairs

def result_doc_reader(fp, splitter='EOS'):
    results_doc = []
    did, sid = -1, -1
    first = True
    current_did = -1
    lines = ''
    split_pattern = '(?:^|\n){}($|\n)'.format(splitter)
    header_pattern = '# S-ID:([0-9]+)-([0-9]+) '
    for line in fp:
        if not line.strip():
            continue
        mh = re.match(header_pattern, line)
        if mh:
            did = int(mh.group(1))
            sid = int(mh.group(2))
            if first:
                first = False
                current_did = did
            elif did != current_did:
                yield did, results_doc
                results_doc = []
                current_did = did
        m = re.match(split_pattern, line)
        if m:
            lines += line
            results_doc.append(lines)
            lines = ''
        else:
            lines += line
    yield did, results_doc

def doc_parse(knp, ifp):
    current_did = -1
    did2tf_anob = {}
    did2df_anob = {}
    did2tf_ab = {}
    did2df_ab = {}
    for did, result_doc in result_doc_reader(ifp):
        if not result_doc:
            continue
        for result in result_doc:
            try: # デコード成功だが変な文字列
                blist = knp.result(result)
            except:
                continue
        anob_list, ab_list = parse_nominal(blist)
        if anob_list:
            anob_tf = Counter(anob_list)
            anob_df = Counter(set(anob_list))
            did2tf_anob[did] = anob_tf
            did2df_anob[did] = anob_df
        if ab_list:
            ab_tf = Counter(ab_list)
            ab_df = Counter(set(ab_list))
            did2tf_ab[did] = ab_tf
            did2df_ab[did] = ab_df
    return did2tf_anob, did2df_anob, did2tf_ab, did2df_ab

def reduce_count(did2count):
    global_count = defaultdict(int)
    for did in did2count:
        w2c  = did2count[did]
        for w, c in w2c.items():
            global_count[w] += c
    return global_count

def parse_and_write(knp, ifp, ofp_tf_anob, ofp_tf_ab, ofp_df_anob, ofp_df_ab):
    did2tf_anob, did2df_anob, did2tf_ab, did2df_ab = doc_parse(knp, ifp)
    tf_anob = reduce_count(did2tf_anob)
    ofp_tf_anob.write('\n'.join([w+'\t'+str(c) for w,c in tf_anob.items()]) + '\n')
    df_anob = reduce_count(did2df_anob)
    ofp_df_anob.write('\n'.join([w+'\t'+str(c) for w,c in df_anob.items()]) + '\n')
    tf_ab = reduce_count(did2tf_ab)
    ofp_tf_ab.write('\n'.join([w+'\t'+str(c) for w,c in tf_ab.items()]) + '\n')
    df_ab = reduce_count(did2df_ab)
    ofp_df_ab.write('\n'.join([w+'\t'+str(c) for w,c in df_ab.items()]) + '\n')


def main():
    knp = KNP(jumanpp=True, option='-tab')
    knpfile = sys.argv[1] # './wiki_00.knp.gz'
    outdir = sys.argv[2]
    assert '.knp.gz' in knpfile
    bn = os.path.basename(knpfile)
    head = os.path.join(outdir, bn.split('.')[0])
    tffile_ab = head + '.ab.tf.gz' # './wiki_00.ab.tf.gz'
    dffile_ab = head + '.ab.df.gz' # './wiki_00.ab.df.gz'
    tffile_anob = head + '.anob.tf.gz'# './wiki_00.anob.tf.gz'
    dffile_anob = head + '.anob.df.gz'# './wiki_00.anob.df.gz'

    with gzip.open(knpfile, mode='rt', encoding='utf8', errors='ignore') as ifp,\
        gzip.open(tffile_ab, mode='wt', encoding='utf8') as ofp_tf_ab,\
        gzip.open(dffile_ab, mode='wt', encoding='utf8') as ofp_df_ab,\
        gzip.open(tffile_anob, mode='wt', encoding='utf8') as ofp_tf_anob,\
        gzip.open(dffile_anob, mode='wt', encoding='utf8') as ofp_df_anob:
        parse_and_write(knp, ifp, ofp_tf_anob, ofp_tf_ab, ofp_df_anob, ofp_df_ab)

if __name__ == '__main__':
    main()
