from os import environ
from google.cloud import translate_v2 as translate
from a.third_party import session_storage
import pinyin as pinyin_module
import thulac
import re
import datamuse
import jieba

GCLOUD_PROJECT_PARENT = f"projects/{environ.get('GCLOUD_PROJECT_ID')}"
TW_CODE = "zh-TW"  # TODO make flexible
EN_CODE = "en"


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
    assert (
        _get_language_code(is_learning_language) == EN_CODE
    ), "Only english is supported for related word generation."

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
