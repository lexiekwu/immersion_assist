from os import environ
from google.cloud import translate
import pinyin as pinyin_module
import thulac
import re
import datamuse
import jieba

GCLOUD_PROJECT_PARENT = f"projects/{environ.get('GCLOUD_PROJECT_ID')}"
TW_CODE = "zh-TW"  # TODO make flexible
EN_CODE = "en"


def get_pronunciation(translated_term, target_language_code):
    if target_language_code == TW_CODE:
        pronunciation = pinyin_module.get(
            translated_term, format="numerical", delimiter=" "
        ).replace("5", "0")
        return pronunciation

    print("No pronunciation implemented, defaulting to nothing")
    return ""


def get_pronunciation_dict(sentence, target_language_code):
    if target_language_code == TW_CODE:
        filtered_characters = re.sub(r"[^\u4e00-\u9fa5]", "", sentence)
        pronunciation = pinyin_module.get(
            filtered_characters, format="numerical", delimiter=" "
        ).split(" ")
        return {char: p for char, p in zip(filtered_characters, pronunciation)}

    print("No pronunciation implemented, defaulting to nothing")
    return {}


def get_translation(term, target_language_code):
    response = translate.TranslationServiceClient().translate_text(
        contents=[term],
        target_language_code=target_language_code,
        parent=GCLOUD_PROJECT_PARENT,
    )

    for translation in response.translations:
        fixed_translation = _fix_translation_characters(translation.translated_text)
        return fixed_translation


def segment_text(long_text, target_language_code=TW_CODE):
    "Splits into words and punctuation, returning [(segment, is_word),]."
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

        is_words = [
            bool(re.findall(r"[\u4e00-\u9fff]+", segment)) for segment in segments
        ]
        return zip(segments, is_words)

    print("No segmentation implemented, defaulting to nothing")
    return []


def _fix_translation_characters(translated_text):
    return translated_text.replace("&#39;", "'").replace("&quot;", '"')


def get_related_words(keyword, limit):
    words_puller = datamuse.Datamuse()
    scored_words = words_puller.words(rel_trg=keyword, max=limit)
    scored_sorted_words = sorted(scored_words, key=lambda d: -d["score"])
    return [d["word"] for d in scored_sorted_words]
