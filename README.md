# dioco-nlp

NLP processing for subtitles (later will add support for long-form text). 

Uses: UDPipe, Mecab, pkuseg, pypinyin, jieba, hangul-romanize, pythainlp.

Runs on Ubuntu 18.04 LTS. There are setup scripts for node, python and nginx.

Output format is uniform for all tools. It's a kind of neat format, with all the CoNLL-U fields, but JSON, and with whitespace also returned as tokens (with 'WS' tag).
There's also transliterations and word frequency data added.

```typescript
interface ud_single {
    
    form: string;
    pos: 
    // 17 Universal POS tags:
    'ADJ'|'ADP'|'ADV'|'AUX'|'NOUN'| 
    'PROPN'|'VERB'|'DET'|'SYM'|'INTJ'|
    'CCONJ'|'PUNCT'|'X'|'NUM'|'PART'|
    'PRON'|'SCONJ'|
    // Unknown text, either UDPipe returned nothing 
    // for this token, or simpleNLP identified it as
    // not whitespace and not punctuation:
    '_'|
    // Whitespace:
    'WS';
    index?: number;
    lemma?: string;
    xpos?: string;
    features?: any;
    pointer?: number;
    deprel?: string;
    translit?: string; // currently only Korean, Thai, Japanese (kana)
    pinyin?: Array<string>;
    tones?: Array<number>;
    freq?: number;
}

interface ud_group {
    form: string;
    pos: 'GROUP'
    members: Array<ud_single>;
    index?: number;
    translit?: string; // currently only Korean, Thai
    pinyin?: Array<string>;
    tones?: Array<number>;
    freq?: number;
}
```

First commit, more info coming.

TODO:
- fix memory leak
- investigate KoNLPy for Korean
- Docker image?
