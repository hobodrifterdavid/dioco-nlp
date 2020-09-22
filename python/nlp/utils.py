# Number of Cores to run NLP
CORES = 8

import re
import MeCab
import logging
import time
from typing import List, NewType
from multiprocessing import Pool
from ufal.udpipe import Model, Pipeline, ProcessingError
from nlp.supported_languages import languages
# # # # # Pinyin
from pypinyin import pinyin, lazy_pinyin, Style
# Could add this for Cyrillic etc. sometime:
# https://github.com/barseghyanartur/transliterate

from hangul_romanize import Transliter
from hangul_romanize.rule import academic
translit_ko = Transliter(academic)

# PyThaiNLP
from pythainlp.transliterate import romanize
from pythainlp import sent_tokenize, word_tokenize


# from pyltp import Segmentor
# ltp_segmentor = Segmentor()
# ltp_segmentor.load("ltp_data_v3.4.0/cws.model")
# segmentor.release()

# import jieba
# jieba.enable_parallel(CORES)
import jieba.posseg

import pkuseg
pku_seg = pkuseg.pkuseg (postag = True) # Load the model in the default configuration


logger = logging.getLogger('root')

SubtitlesType = List[str]
SubtitlesVector = List[list]
UDpipeModel = NewType('UDpipeModel', Model)

udpipe_group_ignore_pattern = re.compile(r'^(\d+)-(\d+)')

space_char_maps = {
    's': ' ',
    't': '\t',
    'n': '\n'
}

def udpipe_space_char_map(space_info):
    space = r' '
    if space_info == '_':
        return space
    for space_info_part in space_info.split('|'):
        if space_info_part == 'SpaceAfter=No':
            space = ''
            break
        if not space_info_part.startswith('SpacesAfter'):
            continue
        space = ''
        space_chars = space_info_part.split('=')[-1]
        for s in space_chars:
            if s == '\\':
                continue
            space += space_char_maps.get(s, '')
    return space

def get_actual_data(processed_data: str, lang: str) -> list:
    """

    :param processed_data:
    :return:
    """
    # Parse the UDPIPE Output
    actual_data = []
    
    group_length = 0 
    group_record = []
    
    for line in processed_data.split("\n"):
        # word range ID's are skipping using udpipe_group_ignore_pattern regex
        
        # Normal:
        # 17 Panzerfahrzeuge Panzerfahrzeug NOUN NN Case=Nom|Gender=Neut|Number=Plu 13 conj _ _
        # 0  1               2              3    4  5                               6  7    8 9

        # We want the fields 1-7
        
        # Group:
        # 11-12 im _ _ _ _ _ _ _ _
        # 11 in in ADP APPR _ 13 case _ _
        # 12 dem der DET ART Case=Dat|Definite=Def|Gender=Neut|Number=Sing|PronType=Art 13 det _ _
        
        line = line.strip()
        
        if line.startswith("#"):
            # line starting with '#' is meta information & skipping it
            continue
            
        if not line:
            # skipping empty lines
            continue
        
        word_details = line.split('\t')
        
        match = udpipe_group_ignore_pattern.match(line)
        
        if match:
            # Beginning of a group
            # 11-12 im _ _ _ _ _ _ _ _
            group_range = list(map(int, match.groups()))
            group_length = group_range[-1] - group_range[0] + 1
            # group_record.append(word_details[1])
            group_record = { 'pos': 'GROUP', 'index': word_details[0], 'members': [], 'form': word_details[1] }

            # # # # # Add Pinyin # # # # #
            if lang.startswith('zh'):
                pinyinData = pinyin(word_details[1])
                pinyin_arr = []

                for item in pinyinData:
                    pinyin_arr.append(item[0])

                group_record["pinyin"] = pinyin_arr

                tone3Data = pinyin(word_details[1], style=Style.TONE3)
                # [['zhong1'], ['xin1']]
                tones_arr = []

                for item in tone3Data:
                    if len(item[0]) >= 2 and item[0][-1].isnumeric() and not item[0][-2].isnumeric():
                        lastChar = item[0][-1]
                        try:
                            tones_arr.append(int(lastChar))
                        except:
                            tones_arr.append(0)
                    else:
                        tones_arr.append(0)

                group_record["tones"] = tones_arr
            # # # # # End Add Pinyin # # # # #

            # # # # # Add KO # # # # #
            if lang.startswith('ko'):
                try:
                    group_record["translit"] = translit_ko.translit(word_details[1])
                except:
                    group_record["translit"] = word_details[1]
            # # # # # End Add KO # # # # #
            continue
            
        required_infos = {
            'form': word_details[1],
             # Always take some pos, even if it's '_'
            'pos': word_details[3]
        }

        if(word_details[0] != '_'):
            required_infos["index"] = int(word_details[0])

        if(word_details[2] != '_'):
            required_infos["lemma"] = word_details[2]

        if(word_details[4] != '_'):
            required_infos["xpos"] = word_details[4]

        if(word_details[5] != '_' and len(word_details[5]) > 0):
            features = {}
            for item in word_details[5].split('|'):
                single = item.split('=')
                features[single[0]] = single[1]
            required_infos["feats"] = features

        if(word_details[6] != '_'):
            if int(word_details[6]) != 0:
                required_infos["pointer"] = int(word_details[6])

        if(word_details[7] != '_'):
            required_infos["deprel"] = word_details[7]

        # # # # # Add Pinyin # # # # #
        if lang.startswith('zh'):
            pinyinData = pinyin(word_details[1])
            pinyin_arr = []

            for item in pinyinData:
                pinyin_arr.append(item[0])

            required_infos["pinyin"] = pinyin_arr

            tone3Data = pinyin(word_details[1], style=Style.TONE3)
            # [['zhong1'], ['xin1']]
            tones_arr = []

            for item in tone3Data:
                if len(item[0]) >= 2 and item[0][-1].isnumeric() and not item[0][-2].isnumeric():
                    lastChar = item[0][-1]
                    try:
                        tones_arr.append(int(lastChar))
                    except:
                        tones_arr.append(0)
                else:
                    tones_arr.append(0)

            required_infos["tones"] = tones_arr
        # # # # # End Add Pinyin # # # # #

        # # # # # Add KO # # # # #
        if lang.startswith('ko'):
            try:
                required_infos["translit"] = translit_ko.translit(word_details[1])
            except:
                required_infos["translit"] = word_details[1]
        # # # # # End Add KO # # # # #
        
        if group_length and group_record:
            # We are in a group still
            group_length -= 1
            group_record['members'].append(required_infos)
            if group_length == 0:
                # End of group
                actual_data.append(group_record)
                group_record = []
            continue
        
        # This record is complete, submit.
        actual_data.append(required_infos)

    return actual_data


def process_ud(x: int, lang: str, subtitles: SubtitlesType) -> tuple:
    """

    :param x:
    :param ud_model:
    :param subtitles:
    :return:
    """
    ud_model = languages[lang]['model']
    ud_model = ud_model() if callable(ud_model) else ud_model
    pipeline = Pipeline(ud_model, 'tokenize', Pipeline.DEFAULT, Pipeline.NONE, 'conllu')
    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitle = []
        error = ProcessingError()
        processed_data = pipeline.process(subtitle, error)
        if error.occurred():
            logger.error("udpipe processing error occured.")
            # skip processing faulty subtitles
            # an appropriate error response will be added
            continue
        dataWeGot = get_actual_data(processed_data, lang)
        processed_subtitle.extend(dataWeGot)
        processed_subtitles.append(processed_subtitle)
    return x, processed_subtitles

def multi_process_ud(lang: str, subtitles: SubtitlesType) -> SubtitlesVector:
    ud_model = languages[lang]['model']
    if callable(ud_model):
        return process_ud(0, lang, subtitles)[1]
    process_pool_size = CORES
    minimum_data_size = 10
    pool = Pool(processes=process_pool_size)
    start, results, calculated_data_size, request_pools = 0, [], len(subtitles) // process_pool_size, []
    data_size = minimum_data_size if calculated_data_size < minimum_data_size else calculated_data_size
    for i in range(1, process_pool_size + 1):
        if i < process_pool_size:
            subtitles_for_processing = subtitles[start:start+data_size]
        else:
            subtitles_for_processing = subtitles[start:]
        start += data_size
        if subtitles_for_processing:
            request_pools.append(pool.apply_async(process_ud, (i, lang, subtitles_for_processing)))
        if i > calculated_data_size or not subtitles_for_processing:
            break
    pool_results = [res.get(timeout=20) for res in request_pools]
    pool.close()
    pool_results.sort(key=lambda x: x[0])
    [results.extend(pool_result[1]) for pool_result in pool_results]
    return results


japTokensMap: any = {"その他": "X", "その他-間投": "INTJ", "フィラー": "X", "副詞": "ADV", "副詞-一般": "ADV", "副詞-助詞類接続": "ADV", "助動詞": "AUX", "助詞": "ADP", "助詞-並立助詞": "CCONJ", "助詞-係助詞": "ADP", "助詞-副助詞": "ADP", "助詞-副助詞／並立助詞／終助詞": "ADP", "助詞-副詞化": "ADP", "助詞-接続助詞": "ADP", "助詞-格助詞": "ADP", "助詞-格助詞-一般": "ADP", "助詞-格助詞-引用": "ADP", "助詞-格助詞-連語": "ADP", "助詞-特殊": "ADP", "助詞-終助詞": "ADP", "助詞-連体化": "ADP", "助詞-間投助詞": "ADP", "動詞": "VERB", "動詞-接尾": "VERB", "動詞-自立": "VERB", "動詞-非自立": "AUX", "名詞": "NOUN", "名詞-サ変接続": "NOUN", "名詞-ナイ形容詞語幹": "NOUN", "名詞-一般": "NOUN", "名詞-代名詞": "PRON", "名詞-代名詞-一般": "PRON", "名詞-代名詞-縮約": "PRON", "名詞-副詞可能": "NOUN", "名詞-動詞非自立的": "NOUN", "名詞-固有名詞": "PROPN", "名詞-固有名詞-一般": "PROPN", "名詞-固有名詞-人名": "PROPN", "名詞-固有名詞-人名-一般": "PROPN", "名詞-固有名詞-人名-名": "PROPN", "名詞-固有名詞-人名-姓": "PROPN", "名詞-固有名詞-地域": "PROPN", "名詞-固有名詞-地域-一般": "PROPN", "名詞-固有名詞-地域-国": "PROPN", "名詞-固有名詞-組織": "PROPN", "名詞-引用文字列": "NOUN", "名詞-形容動詞語幹": "NOUN", "名詞-接尾": "NOUN", "名詞-接尾-サ変接続": "NOUN", "名詞-接尾-一般": "NOUN", "名詞-接尾-人名": "NOUN", "名詞-接尾-副詞可能": "NOUN", "名詞-接尾-助動詞語幹": "NOUN", "名詞-接尾-助数詞": "NOUN", "名詞-接尾-地域": "NOUN", "名詞-接尾-形容動詞語幹": "NOUN", "名詞-接尾-特殊": "NOUN", "名詞-接続詞的": "NOUN", "名詞-数": "NUM", "名詞-特殊": "NOUN", "名詞-特殊-助動詞語幹": "NOUN", "名詞-非自立": "NOUN", "名詞-非自立-一般": "NOUN", "名詞-非自立-副詞可能": "NOUN", "名詞-非自立-助動詞語幹": "NOUN", "名詞-非自立-形容動詞語幹": "NOUN", "形容詞": "ADJ", "形容詞-接尾": "ADJ", "形容詞-自立": "ADJ", "形容詞-非自立": "ADJ", "感動詞": "INTJ", "接続詞": "CCONJ", "接頭詞": "X", "接頭詞-動詞接続": "VERB", "接頭詞-名詞接続": "NOUN", "接頭詞-形容詞接続": "ADJ", "接頭詞-数接続": "NUM", "記号": "SYM", "記号-アルファベット": "SYM", "記号-一般": "SYM", "記号-句点": "PUNCT", "記号-括弧閉": "PUNCT", "記号-括弧開": "PUNCT", "記号-空白": "PUNCT", "記号-読点": "PUNCT", "語断片": "X", "連体詞": "ADJ", "非言語音": "X"}

def process_mb(subtitles: SubtitlesType) -> SubtitlesVector:
    """

    :param subtitles:
    :return:
    """
    chasen = MeCab.Tagger("-Ochasen")
    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitle = []
        for line in chasen.parse(subtitle).splitlines():
            # For each token
            if line.startswith('EOS'):
                continue
            elements = line.split('\t')
            newToken = {
                "form": elements[0],
                "lemma": elements[2], # lemma
                "pos": japTokensMap[elements[3]], # pos
                "xpos": elements[3], # xpos
                "translit": elements[1] # transliteration
            }
            if(len(newToken["pos"]) == 0):
                newToken.pos = '_'

            processed_subtitle.append(newToken)
        processed_subtitles.append(processed_subtitle)
    return processed_subtitles

def process_pkuseg(subtitles: SubtitlesType) -> SubtitlesVector:
    """

    :param subtitles:
    :return:
    """
    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitle = []
        for token in pku_seg.cut(subtitle):
            # [('使用', 'v'), ('新闻', 'n'), ('领域', 'n'), ('模型', 'n')]

            if(len(token[0].strip()) == 0):
                # No whitespace thank you
                continue
            
            newToken = {
                "form": token[0],
                # "lemma": elements[2], # lemma
                "pos": zh_xpos_to_upos(token[1]),
                "xpos": token[1]
            }

            # # # # # Add Pinyin # # # # #
            pinyinData = pinyin(token[0])
            pinyin_arr = []

            for item in pinyinData:
                pinyin_arr.append(item[0])

            newToken["pinyin"] = pinyin_arr

            tone3Data = pinyin(token[0], style=Style.TONE3)
            # [['zhong1'], ['xin1']]
            tones_arr = []

            for item in tone3Data:
                if len(item[0]) >= 2 and item[0][-1].isnumeric() and not item[0][-2].isnumeric():
                    lastChar = item[0][-1]
                    try:
                        tones_arr.append(int(lastChar))
                    except:
                        tones_arr.append(0)
                else:
                    tones_arr.append(0)

            newToken["tones"] = tones_arr
            # # # # # End Add Pinyin # # # # #

            processed_subtitle.append(newToken)
        processed_subtitles.append(processed_subtitle)
    return processed_subtitles

def process_jieba(x: int, subtitles: SubtitlesType) -> SubtitlesVector:
    """

    :param subtitles:
    :return:
    """
    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitle = []
        for token in jieba.posseg.lcut(subtitle):
            # [pair('我', 'r'), pair('爱', 'v'), pair('北京', 'ns'), pair('天安门', 'ns')]
            form, pos = token

            if(len(form.strip()) == 0):
                # No whitespace thank you
                continue
            newToken = {
                "form": form,
                # "lemma": elements[2], # lemma
                "pos": zh_xpos_to_upos(pos),
                "xpos": pos
            }

            # # # # # Add Pinyin # # # # #
            pinyinData = pinyin(form)
            pinyin_arr = []

            for item in pinyinData:
                pinyin_arr.append(item[0])

            newToken["pinyin"] = pinyin_arr

            tone3Data = pinyin(form, style=Style.TONE3)
            # [['zhong1'], ['xin1']]
            tones_arr = []

            for item in tone3Data:
                if len(item[0]) >= 2 and item[0][-1].isnumeric() and not item[0][-2].isnumeric():
                    lastChar = item[0][-1]
                    try:
                        tones_arr.append(int(lastChar))
                    except:
                        tones_arr.append(0)
                else:
                    tones_arr.append(0)

            newToken["tones"] = tones_arr
            # # # # # End Add Pinyin # # # # #

            processed_subtitle.append(newToken)
        processed_subtitles.append(processed_subtitle)
    return x, processed_subtitles

def multi_process_jieba(subtitles: SubtitlesType) -> SubtitlesVector:

    process_pool_size = CORES
    minimum_data_size = 10
    pool = Pool(processes=process_pool_size)
    start, results, calculated_data_size, request_pools = 0, [], len(subtitles) // process_pool_size, []
    data_size = minimum_data_size if calculated_data_size < minimum_data_size else calculated_data_size
    for i in range(1, process_pool_size + 1):
        if i < process_pool_size:
            subtitles_for_processing = subtitles[start:start+data_size]
        else:
            subtitles_for_processing = subtitles[start:]
        start += data_size
        if subtitles_for_processing:
            request_pools.append(pool.apply_async(process_jieba, (i, subtitles_for_processing)))
        if i > calculated_data_size or not subtitles_for_processing:
            break
    pool_results = [res.get(timeout=20) for res in request_pools]
    pool.close()
    pool_results.sort(key=lambda x: x[0])
    [results.extend(pool_result[1]) for pool_result in pool_results]
    return results

def process_pyThaiNLP(subtitles: SubtitlesType) -> SubtitlesVector:
    """

    :param subtitles:
    :return:
    """
    # https://github.com/PyThaiNLP/pythainlp
    # We don't handle POS tags yet.

    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitle = []
        for token in word_tokenize(subtitle, keep_whitespace=False):
            if(token[0] == '\n'):
                # wierd newline probably, continue
                continue

            translit = ''
            
            try:
                translit = romanize(token, engine='ipa')
            except:
                translit = token

            newToken = {
                "form": token,
                # "lemma": elements[2], # lemma
                "pos": "_",
                "translit": translit
            }
            
            processed_subtitle.append(newToken)
        processed_subtitles.append(processed_subtitle)
    return processed_subtitles


def zh_xpos_to_upos(xpos):

    xpos = xpos[0:2]

    # pkuseg:
    # https://github.com/lancopku/pkuseg-python/blob/master/tags.txt
    # Jieba (ICTCLAS labels)
    # https://pynlpir.readthedocs.io/en/latest/_modules/pynlpir/pos_map.html

    # This should handle both ok
    tags = {
        'n': 'NOUN',
        'nr': 'PROPN',
        'ns': 'PROPN',
        'nt': 'PROPN',
        'nz': 'PROPN',
        'nl': 'NOUN',
        'ng': 'NOUN',
        'nx': 'X',

        'v': 'VERB',
        'vd': 'AUX',
        'vn': 'VERB',
        'vx': 'VERB',

        'a': 'ADJ',
        'ad': 'ADJ',
        'an': 'ADJ',
        'ag': 'ADJ',
        'al': 'ADJ',

        'r': 'PROPN',
        'rr': 'PROPN',
        'rz': 'PROPN',
        'ry': 'PROPN',
        'rg': 'PROPN',

        'm': 'NUM',
        'mq': 'NUM',
        'mg': 'NUM',
        
        'd': 'ADV',

        'p': 'ADP',
        'pb': 'ADP',

        'c': 'CCONJ',
        'cc': 'CCONJ',

        'u': 'PART',
        'uz': 'PART',
        'ul': 'PART',
        'ug': 'PART',
        'ud': 'PART',
        'us': 'PART',
        'uy': 'PART',
        'u': 'PART',

        'e': 'INTJ',

        'x': 'SYM',
        'xe': 'SYM',
        'xs': 'SYM',
        'xm': 'SYM',
        'xu': 'SYM',
        'xx': 'SYM',

        'w': 'PUNCT',
        'wk': 'PUNCT',
        'wy': 'PUNCT',
        'wj': 'PUNCT',
        'ww': 'PUNCT',
        'wt': 'PUNCT',
        'wd': 'PUNCT',
        'wf': 'PUNCT',
        'wn': 'PUNCT',
        'wm': 'PUNCT',
        'ws': 'PUNCT',
        'wp': 'PUNCT',
        'wb': 'PUNCT',
        'wh': 'PUNCT',

        # These are not handled :-/
        # function returns '_'

        # 't' 'time word' ?
        # 's': ('处所词', 'locative word'), ?
        # 'f': ('方位词', 'noun of locality'), ?
        # 'b': ('区别词', 'distinguishing word', ?
        # 'z': ('状态词', 'status word'), ?
        # 'q': ('量词', 'classifier', ?
        #    'y': ('语气词', 'modal particle'),
        # 'o': ('拟声词', 'onomatopoeia'),
        # 'h': ('前缀', 'prefix'),
        # 'k': ('后缀', 'suffix'),
        # 'g': ('复合语', 'multiword expression'),
        # 'j': ('略语', 'abbreviation'),
    }

    return tags.get(xpos, "_")

def addTranslitOnly(tokens, langCode_G):

    for token in tokens:

        if langCode_G.startswith('th'):
            
            try:
                token["translit"] = romanize(token["form"], engine='ipa')
            except:
                token["translit"] = token

        if langCode_G.startswith('ko'):

            try:
                token["translit"] = translit_ko.translit(token["form"])
            except:
                token["translit"] = token["form"]

        if langCode_G.startswith('zh'):

            pinyinData = pinyin(token["form"])
            pinyin_arr = []

            for item in pinyinData:
                pinyin_arr.append(item[0])

            token["pinyin"] = pinyin_arr

            tone3Data = pinyin(token["form"], style=Style.TONE3)
            # [['zhong1'], ['xin1']]
            tones_arr = []

            for item in tone3Data:
                # last char must be number and preceeding not
                if len(item[0]) >= 2 and item[0][-1].isnumeric() and not item[0][-2].isnumeric():
                    lastChar = item[0][-1]
                    try:
                        tones_arr.append(int(lastChar))
                    except:
                        tones_arr.append(0)
                else:
                    tones_arr.append(0)

            token["tones"] = tones_arr

    return tokens