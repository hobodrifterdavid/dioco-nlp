import os
from ufal.udpipe import Model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UDPIPE_MODELS_DIR = os.path.join(BASE_DIR, 'udpipe_models')
UD_PIPE_PROCESSOR = 'udpipe'

languages = {
    'af': {'verbose': 'Afrikaans', 'processor': UD_PIPE_PROCESSOR, 
       'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "afrikaans-afribooms-ud-2.5-191206.udpipe"))}, #####
    'sq': {'verbose': 'Albanian', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 94.6%, UPOS: 90.2%, Lemma: 88.4%; name: Arabic-PADT
    'ar': {'verbose': 'Arabic', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "arabic-padt-ud-2.3-181115.udpipe"))}, 
    'az': {'verbose': 'Azerbaijani', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 100.0%, UPOS: 92.3%, Lemma: 93.5%; name: Basque-BDT
    'eu': {'verbose': 'Basque', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "basque-bdt-ud-2.3-181115.udpipe"))},
    'bn': {'verbose': 'Bengali', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'be': {'verbose': 'Belarusian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "belarusian-hse-ud-2.5-191206.udpipe"))}, #####
    'bg': {'verbose': 'Bulgarian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "bulgarian-btb-ud-2.5-191206.udpipe"))}, #####
    # model accuracy: Words: 100.0%, UPOS: 98.0%, Lemma: 97.9%; name: Catalan-AnCora
    'ca': {'verbose': 'Catalan', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "catalan-ancora-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 90.0%, UPOS: 98.0%, Lemma: 97.9%; name: Chinese-GSD
    'zh-CN': {'verbose': 'Chinese Simplified', 'processor': UD_PIPE_PROCESSOR,
              'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "chinese-gsdsimp-ud-2.5-191206.udpipe"))},
    'zh-TW': {'verbose': 'Chinese Traditional', 'processor': UD_PIPE_PROCESSOR,
              'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "chinese-gsd-ud-2.5-191206.udpipe"))},
    # model accuracy: Words: 99.9%, UPOS: 96.3%, Lemma: 94.8%; name: Croatian-SET
    'hr': {'verbose': 'Croatian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "croatian-set-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 100.0%, UPOS: 98.1%, Lemma: 96.9%; name: Czech-CAC
    'cs': {'verbose': 'Czech', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "czech-cac-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 99.8%, UPOS: 95.4%, Lemma: 94.7%; name: Danish-DDT
    'da': {'verbose': 'Danish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "danish-ddt-ud-2.3-181115.udpipe"))},
    'dv': {'verbose': 'Dhivehi', 'processor': UD_PIPE_PROCESSOR, 'model': ''},
    # model accuracy: Words: 99.9%, UPOS: 94.3%, Lemma: 95.4%; name: Dutch-Alpino
    'nl': {'verbose': 'Dutch', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "dutch-alpino-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 99.1%, UPOS: 93.5%, Lemma: 96.0%; name: English-EWT
    'en': {'verbose': 'English', 'processor': UD_PIPE_PROCESSOR,
           'model': Model.load(os.path.join(UDPIPE_MODELS_DIR, "english-ewt-ud-2.3-181115.udpipe"))},
    'eo': {'verbose': 'Esperanto', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'et': {'verbose': 'Estonian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "estonian-edt-ud-2.5-191206.udpipe"))}, #####
    'tl': {'verbose': 'Filipino', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 99.7%, UPOS: 94.4%, Lemma: 86.5%; name: Finnish-TDT
    'fi': {'verbose': 'Finnish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "finnish-tdt-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 98.8%, UPOS: 95.8%, Lemma: 96.6%; name: French-GSD
    'fr': {'verbose': 'French', 'processor': UD_PIPE_PROCESSOR,
           'model': Model.load(os.path.join(UDPIPE_MODELS_DIR, "french-gsd-ud-2.3-181115.udpipe"))},
    'gl': {'verbose': 'Galician', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "galician-ctg-ud-2.5-191206.udpipe"))}, #####
    'ka': {'verbose': 'Georgian', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 99.6%, UPOS: 91.4%, Lemma: 95.4%; name: German-GSD
    'de': {'verbose': 'German', 'processor': UD_PIPE_PROCESSOR,
           'model': Model.load(os.path.join(UDPIPE_MODELS_DIR, "german-hdt-ud-2.5-191206.udpipe"))},
    'el': {'verbose': 'Greek', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, 'greek-gdt-ud-2.4.udpipe'))},
    'gu': {'verbose': 'Gujarati', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ha': {'verbose': 'Hausa', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ht': {'verbose': 'Haitian Creole', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 85.0%, UPOS: 80.5%, Lemma: 81.5%; name: Hebrew-HTB
    'iw': {'verbose': 'Hebrew', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "hebrew-htb-ud-2.5-191206.udpipe"))},
    # model accuracy: Words: 100.0%, UPOS: 95.8%, Lemma: 98.0%; name: Hindi-HDTB
    'hi': {'verbose': 'Hindi', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "hindi-hdtb-ud-2.3-181115.udpipe"))},
    'hu': {'verbose': 'Hungarian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "hungarian-szeged-ud-2.5-191206.udpipe"))}, #####
    # model - have to build model
    'is': {'verbose': 'Icelandic', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'id': {'verbose': 'Indonesian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "indonesian-gsd-ud-2.5-191206.udpipe"))}, #####
    'ga': {'verbose': 'Irish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "irish-idt-ud-2.5-191206.udpipe"))}, #####
    # model accuracy: Words: 99.7%, UPOS: 97.0%, Lemma: 97.2%; name: Italian-ISDT
    'it': {'verbose': 'Italian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "italian-vit-ud-2.5-191206.udpipe"))},
    'ja': {'verbose': 'Japanese', 'processor': 'mecab', 'model': ''},
    'kn': {'verbose': 'Kannada', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'kk': {'verbose': 'Kazakh', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'km': {'verbose': 'Khmer', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 99.8%, UPOS: 93.5%, Lemma: 87.1%; name: Korean-GSD
    'ko': {'verbose': 'Korean', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "korean-kaist-ud-2.5-191206.udpipe"))},
    'ku': {'verbose': 'Kurdish', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ky': {'verbose': 'Kyrgyz', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'la': {'verbose': 'Latin', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "latin-ittb-ud-2.5-191206.udpipe"))}, #####
    'lo': {'verbose': 'Laothian', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'lv': {'verbose': 'Latvian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "latvian-lvtb-ud-2.5-191206.udpipe"))}, #####
    'lt': {'verbose': 'Lithuanian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "lithuanian-alksnis-ud-2.5-191206.udpipe"))}, #####
    'mk': {'verbose': 'Macedonian', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ms': {'verbose': 'Malay', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ml': {'verbose': 'Malayalam', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'mt': {'verbose': 'Maltese', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "maltese-mudt-ud-2.5-191206.udpipe"))}, #####
    'mr': {'verbose': 'Marathi', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "marathi-ufal-ud-2.5-191206.udpipe"))}, #####
    'mn': {'verbose': 'Mongolian', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ne': {'verbose': 'Nepali', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 99.8%, UPOS: 96.5%, Lemma: 96.6%; name: Norwegian-Bokmaal
    'no': {'verbose': 'Norwegian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "norwegian-bokmaal-ud-2.3-181115.udpipe"))},
    'or': {'verbose': 'Oriya', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'ps': {'verbose': 'Pashto', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'fa': {'verbose': 'Persian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "persian-seraji-ud-2.5-191206.udpipe"))}, #####
    # model accuracy: Words: 99.8%, UPOS: 97.9%, Lemma: 94.5%; name: Polish-LFG
    'pl': {'verbose': 'Polish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "polish-lfg-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 99.9%, UPOS: 97.0%, Lemma: 98.5%; name: Portuguese-GSD
    'pt': {'verbose': 'Portuguese', 'processor': UD_PIPE_PROCESSOR,
           'model': Model.load(os.path.join(UDPIPE_MODELS_DIR, "portuguese-bosque-ud-2.5-191206.udpipe"))},
    'pa': {'verbose': 'Punjabi', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 99.7%, UPOS: 96.7%, Lemma: 96.6%; name: Romanian-RRT
    'ro': {'verbose': 'Romanian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "romanian-rrt-ud-2.3-181115.udpipe"))},
    # model accuracy: Words: 99.7%, UPOS: 97.9%, Lemma: 96.6%; name: Russian-SynTagRus
    'ru': {'verbose': 'Russian', 'processor': UD_PIPE_PROCESSOR,
           'model':  lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "russian-syntagrus-ud-2.3-181115.udpipe"))},
    'sr': {'verbose': 'Serbian', 'processor': UD_PIPE_PROCESSOR,
           'model':  lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "serbian-set-ud-2.5-191206.udpipe"))}, #####
    'si': {'verbose': 'Sinhalese', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'sk': {'verbose': 'Slovak', 'processor': UD_PIPE_PROCESSOR,
           'model':  lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "slovak-snk-ud-2.5-191206.udpipe"))}, #####
    'sl': {'verbose': 'Slovenian', 'processor': UD_PIPE_PROCESSOR,
           'model':  lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "slovenian-ssj-ud-2.5-191206.udpipe"))}, #####
    # model accuracy: Words: 99.9%, UPOS: 99.0%, Lemma: 98.0%; name: Spanish-Ancora
    'es': {'verbose': 'Spanish', 'processor': UD_PIPE_PROCESSOR,
           'model': Model.load(os.path.join(UDPIPE_MODELS_DIR, "spanish-ancora-ud-2.5-191206.udpipe"))},
    'sw': {'verbose': 'Swahili', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 100.0%, UPOS: 94.4%, Lemma: 94.5%; name: Swedish-LinES
    'sv': {'verbose': 'Swedish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "swedish-lines-ud-2.3-181115.udpipe"))},
    'tg': {'verbose': 'Tajik', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 95.0%, UPOS: 81.8%, Lemma: 84.6%; name: Tamil-TTB
    'ta': {'verbose': 'Tamil', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "tamil-ttb-ud-2.3-181115.udpipe"))},
    'te': {'verbose': 'Telugu', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, 'telugu-mtg-ud-2.5-191206.udpipe'))}, #####
    'th': {'verbose': 'Thai', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, 'thai-pud-ud-2.4.udpipe'))},
    # model accuracy: Words: 98.3%, UPOS: 91.7%, Lemma: 90.0%; name: Turkish-IMST
    'tr': {'verbose': 'Turkish', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "turkish-imst-ud-2.3-181115.udpipe"))},
    'uk': {'verbose': 'Ukrainian', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, 'ukrainian-iu-ud-2.5-191206.udpipe'))}, #####
    'ur': {'verbose': 'Urdu', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, 'urdu-udtb-ud-2.5-191206.udpipe'))}, #####
    'uz': {'verbose': 'Uzbek', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    # model accuracy: Words: 85.4%, UPOS: 76.2%, Lemma: 84.7%; name: Vietnamese-VTB
    'vi': {'verbose': 'Vietnamese', 'processor': UD_PIPE_PROCESSOR,
           'model': lambda: Model.load(os.path.join(UDPIPE_MODELS_DIR, "vietnamese-vtb-ud-2.5-191206.udpipe"))},
    'cy': {'verbose': 'Welsh', 'processor': UD_PIPE_PROCESSOR, 'model': ''}, # No model
    'yi': {'verbose': 'Yiddish', 'processor': UD_PIPE_PROCESSOR, 'model': ''} # No model
}
