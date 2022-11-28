from os import environ
from google.cloud import translate
from flask import session
import pinyin as pinyin_module
import jieba
import re


GCLOUD_PROJECT_PARENT = f"projects/{environ.get('GCLOUD_PROJECT_ID')}"
TW_CODE = "zh-TW"  # TODO make flexible
EN_CODE = "en"


def get_pronunciation(translated_term, target_language_code):
    # avoid repeated API calls
    if session.get("pronunciations", {}).get(translated_term):
        return session["pronunciations"][translated_term]

    if target_language_code == TW_CODE:
        pronunciation = pinyin_module.get(
            translated_term, format="numerical", delimiter=" "
        )

        # save to avoid repeated API calls
        if not session.get("pronunciations"):
            session["pronunciations"] = {}
            session["pronunciations"][translated_term] = pronunciation
        return pronunciation

    print("No pronunciation implemented, defaulting to nothing")
    return ""


def get_translation(term, target_language_code):

    # avoid repeated API calls
    if session.get("translations", {}).get(term):
        return session["translations"][term]

    response = translate.TranslationServiceClient().translate_text(
        contents=[term],
        target_language_code=target_language_code,
        parent=GCLOUD_PROJECT_PARENT,
    )

    for translation in response.translations:

        # save to avoid repeated API calls
        if not session.get("translations"):
            session["translations"] = {}
        session["translations"][term] = translation.translated_text

        return translation.translated_text

    raise KeyError  # could not find a translation


def segment_text(long_text, target_language_code=TW_CODE):
    "Splits into words and punctuation, returning [(segment, is_word),]."
    if target_language_code == TW_CODE:
        segments = jieba.lcut(long_text)
        is_words = [
            bool(re.findall(r"[\u4e00-\u9fff]+", segment)) for segment in segments
        ]
        return zip(segments, is_words)

    print("No segmentation implemented, defaulting to nothing")
    return ""
