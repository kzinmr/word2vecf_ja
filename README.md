# word2vecf in japanese

日本語wikipediaダンプデータに対して構文解析を施しword2vecfを構築する。
形態素解析および構文解析にはJumannpp+KNPを使用。
wikipediaのテキスト抽出は[WikiExtractor](https://github.com/attardi/wikiextractor)によりすでに行っているものとする。

## Requirements
 - Juman++v2
 - KNP
 - GNU parallel
 - [pyknp-extend](https://github.com/kzinmr/pyknp-extend.git)

## Usage
