from os import environ
from google.cloud import translate_v2 as translate
from a.third_party import session_storage
import pinyin as pinyin_module
import thulac
import re
import datamuse
import jieba


def get_pronunciation(translated_term, is_learning_language=True):
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code == TW_CODE:
        pronunciation = pinyin_module.get(
            translated_term, format="numerical", delimiter=" "
        ).replace("5", "0")
        return pronunciation

    print("No pronunciation implemented, defaulting to nothing")
    return ""


def get_pronunciation_dict(sentence, is_learning_language=True):
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code == TW_CODE:
        filtered_characters = re.sub(r"[^\u4e00-\u9fa5]", "", sentence)
        pronunciation = pinyin_module.get(
            filtered_characters, format="numerical", delimiter=" "
        ).split(" ")
        return {char: p for char, p in zip(filtered_characters, pronunciation)}

    print("No pronunciation implemented, defaulting to nothing")
    return {}


def get_translation(term, to_learning_language=True):
    target_language_code = _get_language_code(to_learning_language)
    response = translate.Client().translate(term, target_language=target_language_code)

    translation = response["translatedText"]
    fixed_translation = _fix_translation_characters(translation)
    return fixed_translation


def segment_text(long_text, is_learning_language=True):
    "Splits into words and punctuation, returning [(segment, is_word),]."
    target_language_code = _get_language_code(is_learning_language)
    if target_language_code == TW_CODE:

        # use thulac if specifically told to
        if environ.get("CHINESE_SEGMENTER") == "thulac":
            segmenter = thulac.thulac()
            segments = [
                segment for segment, _ in segmenter.cut(long_text)
            ]  # returns (word, part of speech)

        # otherwise jieba
        else:
            segments = jieba.lcut(long_text)
    else:
        # segment non-chinese by spaces
        segments = long_text.split(" ")

    def _is_word(segment):
        return len(re.findall(r"[^!.?\s]", segment)) > 0

    is_words = [_is_word(segment) for segment in segments]
    return zip(segments, is_words)


def _fix_translation_characters(translated_text):
    return translated_text.replace("&#39;", "'").replace("&quot;", '"')


def get_related_words(keyword, limit, is_learning_language=False):
    words_puller = datamuse.Datamuse()
    scored_words = words_puller.words(rel_trg=keyword, max=limit)
    scored_sorted_words = sorted(scored_words, key=lambda d: -d["score"])
    return [d["word"] for d in scored_sorted_words]


def is_learning_language(text):
    response = translate.Client().detect_language(text)
    return (
        response["language"].split("-")[0]
        == session_storage.get("learning_language").split("-")[0]
    )


def _get_language_code(is_learning_language):
    if is_learning_language:
        return session_storage.get("learning_language")
    else:
        return session_storage.get("home_language")


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
