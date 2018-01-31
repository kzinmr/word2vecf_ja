import sys
import bz2
import json
import io

import nltk
import mojimoji


def sentence_splitter(doc):
    # 句点（！？。.）で分割（ただし句点に」』が続く場合(文頭が」』の場合)は前後を繋げる）
    # 「行く事は行くがじき帰る。来年の夏休みにはきっと帰る」　のような場合には分けてしまう
    sent_splitter = nltk.RegexpTokenizer('[^！？。.\n]*[！？。.\n]*')
    sentences = sent_splitter.tokenize(doc)
    sentences = map(lambda s: mojimoji.han_to_zen(s.strip()), filter(None, sentences))
    if '「' not in doc and '」' not in doc:
        return filter(None, sentences)

    prev = ''
    n_sentences = []
    for i, s in enumerate(sentences):
        if s.startswith('」') or s.startswith('』') or s.startswith('）')\
           or s.startswith('】') or s.startswith('”') or s.startswith('\]'):
            prev = prev + s
        else:
            n_sentences.append(prev)
            prev = s
    n_sentences.append(prev)
    return filter(None, map(lambda s: s.strip(), n_sentences))

def sid_header(did, sid):
    assert '-' not in str(sid)
    if isinstance(did, str) and '-' in did:
        did.replace('-', '_')
    header = '# S-ID:{}-{} Juman++:2.0.0'.format(did, sid)
    return header

def length_filter(s, threshold=5):
    return s if len(s.strip()) >= threshold else ''

def we_json_reader(fp):
    result = []
    for l in fp:
        jd = json.loads(l)
        sentences = sentence_splitter(jd['text'].strip(' \t\n\r'))
        sentences = filter(None, map(lambda x: length_filter(x).strip(), sentences))
        for i, s in enumerate(sentences):
            h = sid_header(jd['id'], i)
            result.append(h + '\n' + s)
    return result

def main():
    filename = sys.argv[1]
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    assert 'bz2' in filename
    with bz2.open(filename, mode='rt', encoding='utf8', errors='ignore') as ifp:
        rslt = we_json_reader(ifp)
        for s in rslt:
            print(s, file=sys.stdout)


if __name__ == '__main__':
    main()
