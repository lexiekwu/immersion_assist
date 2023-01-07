from a.third_party import session_storage, api_wrap as apis
import re


def get_pronunciation(term, is_learning_language=True):
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code in CHINESE_CODES:
        pronunciation = apis.call_api(apis.Apis.PINYIN, [term])
        return pronunciation

    return ""


def get_pronunciation_dict(sentence, is_learning_language=True):
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code in CHINESE_CODES:
        filtered_characters = re.sub(r"[^\u4e00-\u9fa5]", "", sentence)
        pronunciation = apis.call_api(apis.Apis.PINYIN, [filtered_characters]).split(
            " "
        )
        return {char: p for char, p in zip(filtered_characters, pronunciation)}

    print("No pronunciation implemented, defaulting to nothing")
    return {}


def get_translation(term, to_learning_language=True):
    target_language_code = _get_language_code(to_learning_language)
    translation = apis.call_api(apis.Apis.TRANSLATE, [term, target_language_code])
    return translation


def segment_text(long_text, is_learning_language=True):
    "Splits into words and punctuation, returning [(segment, is_word),]."
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code in CHINESE_CODES:
        segments = apis.call_api(apis.Apis.ZH_SEGMENTER, [long_text])

        def _is_word(segment):
            return len(re.findall(r"[\u4e00-\u9fff]+", segment)) > 0

        is_words = [_is_word(segment) for segment in segments]
        return list(zip(segments, is_words))
    else:
        # segment non-chinese by spaces
        return _simple_segment(long_text)


def get_related_words(keyword, limit):
    return apis.call_api(apis.Apis.RELATED_WORDS, [keyword, limit])


def is_learning_language(text):
    response = apis.call_api(apis.Apis.LANGUAGE_DETECTION, [text])
    return (
        response["language"].split("-")[0]
        == session_storage.get("learning_language").split("-")[0]
    )


def _get_language_code(is_learning_language):
    if is_learning_language:
        return session_storage.get("learning_language")
    else:
        return session_storage.get("home_language")


def _simple_segment(long_text):
    segmented_terms = []
    current_word = ""

    for c in long_text:
        if c in PUNCTUATION:
            if current_word:
                segmented_terms.append((current_word, True))
            segmented_terms.append((c, False))
            current_word = ""
        else:
            current_word += c
    return segmented_terms


PUNCTUATION = "!#$%&()*+,-./:;<=>?@[]^_`{|}~\\ "

TW_CODE = "zh-TW"  # TODO make flexible
EN_CODE = "en"
SUPPORTED_LANGUAGES_AND_CODES = [
    ("Afrikaans", "af"),
    ("Akan", "ak"),
    ("Albanian", "sq"),
    ("Amharic", "am"),
    ("Arabic", "ar"),
    ("Armenian", "hy"),
    ("Assamese", "as"),
    ("Aymara", "ay"),
    ("Azerbaijani", "az"),
    ("Bambara", "bm"),
    ("Basque", "eu"),
    ("Belarusian", "be"),
    ("Bengali", "bn"),
    ("Bhojpuri", "bho"),
    ("Bosnian", "bs"),
    ("Bulgarian", "bg"),
    ("Catalan", "ca"),
    ("Cebuano", "ceb"),
    ("Chichewa", "ny"),
    ("Chinese (Simplified)", "zh"),
    ("Chinese (Traditional)", "zh-TW"),
    ("Corsican", "co"),
    ("Croatian", "hr"),
    ("Czech", "cs"),
    ("Danish", "da"),
    ("Divehi", "dv"),
    ("Dogri", "doi"),
    ("Dutch", "nl"),
    ("English", "en"),
    ("Esperanto", "eo"),
    ("Estonian", "et"),
    ("Ewe", "ee"),
    ("Filipino", "tl"),
    ("Finnish", "fi"),
    ("French", "fr"),
    ("Frisian", "fy"),
    ("Galician", "gl"),
    ("Ganda", "lg"),
    ("Georgian", "ka"),
    ("German", "de"),
    ("Goan Konkani", "gom"),
    ("Greek", "el"),
    ("Guarani", "gn"),
    ("Gujarati", "gu"),
    ("Haitian Creole", "ht"),
    ("Hausa", "ha"),
    ("Hawaiian", "haw"),
    ("Hebrew", "iw"),
    ("Hindi", "hi"),
    ("Hmong", "hmn"),
    ("Hungarian", "hu"),
    ("Icelandic", "is"),
    ("Igbo", "ig"),
    ("Iloko", "ilo"),
    ("Indonesian", "id"),
    ("Irish", "ga"),
    ("Italian", "it"),
    ("Japanese", "ja"),
    ("Javanese", "jw"),
    ("Kannada", "kn"),
    ("Kazakh", "kk"),
    ("Khmer", "km"),
    ("Kinyarwanda", "rw"),
    ("Korean", "ko"),
    ("Krio", "kri"),
    ("Kurdish (Kurmanji)", "ku"),
    ("Kurdish (Sorani)", "ckb"),
    ("Kyrgyz", "ky"),
    ("Lao", "lo"),
    ("Latin", "la"),
    ("Latvian", "lv"),
    ("Lingala", "ln"),
    ("Lithuanian", "lt"),
    ("Luxembourgish", "lb"),
    ("Macedonian", "mk"),
    ("Maithili", "mai"),
    ("Malagasy", "mg"),
    ("Malay", "ms"),
    ("Malayalam", "ml"),
    ("Maltese", "mt"),
    ("Manipuri (Meitei Mayek)", "mni-Mtei"),
    ("Maori", "mi"),
    ("Marathi", "mr"),
    ("Mizo", "lus"),
    ("Mongolian", "mn"),
    ("Myanmar (Burmese)", "my"),
    ("Nepali", "ne"),
    ("Northern Sotho", "nso"),
    ("Norwegian", "no"),
    ("Odia (Oriya)", "or"),
    ("Oromo", "om"),
    ("Pashto", "ps"),
    ("Persian", "fa"),
    ("Polish", "pl"),
    ("Portuguese", "pt"),
    ("Punjabi", "pa"),
    ("Quechua", "qu"),
    ("Romanian", "ro"),
    ("Russian", "ru"),
    ("Samoan", "sm"),
    ("Sanskrit", "sa"),
    ("Scots Gaelic", "gd"),
    ("Serbian", "sr"),
    ("Sesotho", "st"),
    ("Shona", "sn"),
    ("Sindhi", "sd"),
    ("Sinhala", "si"),
    ("Slovak", "sk"),
    ("Slovenian", "sl"),
    ("Somali", "so"),
    ("Spanish", "es"),
    ("Sundanese", "su"),
    ("Swahili", "sw"),
    ("Swedish", "sv"),
    ("Tajik", "tg"),
    ("Tamil", "ta"),
    ("Tatar", "tt"),
    ("Telugu", "te"),
    ("Thai", "th"),
    ("Tigrinya", "ti"),
    ("Tsonga", "ts"),
    ("Turkish", "tr"),
    ("Turkmen", "tk"),
    ("Ukrainian", "uk"),
    ("Urdu", "ur"),
    ("Uyghur", "ug"),
    ("Uzbek", "uz"),
    ("Vietnamese", "vi"),
    ("Welsh", "cy"),
    ("Xhosa", "xh"),
    ("Yiddish", "yi"),
    ("Yoruba", "yo"),
    ("Zulu", "zu"),
    ("Hebrew", "he"),
    ("Javanese", "jv"),
    ("Chinese (Simplified)", "zh-CN"),
]

CHINESE_CODES = ["zh-CN", "zh", "zh-TW"]
