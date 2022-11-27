from os import environ
from google.cloud import translate
import pinyin as pinyin_module
import jieba


GCLOUD_PROJECT_PARENT = f"projects/{environ.get('GCLOUD_PROJECT_ID')}"
TW_CODE = "zh-TW"  # TODO make flexible


def get_pronunciation(translated_term, target_language_code):
    if target_language_code == TW_CODE:
        return pinyin_module.get(translated_term, format="numerical", delimiter=" ")

    print("No pronunciation implemented, defaulting to nothing")
    return ""


def get_translation(term, target_language_code):
    response = translate.TranslationServiceClient().translate_text(
        contents=[term],
        target_language_code=target_language_code,
        parent=GCLOUD_PROJECT_PARENT,
    )

    for translation in response.translations:
        return translation.translated_text

    raise KeyError  # could not find a translation


def segment_text(long_text, target_language_code=TW_CODE):

    if target_language_code == TW_CODE:
        return jieba.lcut(long_text)

    print("No segmentation implemented, defaulting to nothing")
    return ""
