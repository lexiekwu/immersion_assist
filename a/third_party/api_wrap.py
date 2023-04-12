"""
When ya cheap af so you avoid calling APIs
"""
import openai
import jieba
import pinyin
import datamuse
from google.cloud import translate_v2 as translate
from enum import Enum
from flask import json
from os import environ
import a.third_party.cockroachdb as db
import a

MAX_ARGS_LENGTH = 128
MAX_RESPONSE_LENGTH = 256


class Apis(Enum):
    CHATBOT = 1
    ZH_SEGMENTER = 2
    PINYIN = 3
    RELATED_WORDS = 4
    TRANSLATE = 5
    LANGUAGE_DETECTION = 6
    CHATBOT_V2 = 7


openai.api_key = environ.get("OPENAI_KEY")


def call_api(api_enum, args):
    a.model.rate_limit.rate_limited_action("call_api", "minutely", 100)
    a.model.rate_limit.rate_limited_action("call_api", "daily", 1000)

    stored_response = _lookup_call(api_enum, args)
    if stored_response:
        return stored_response

    response = None
    if api_enum == Apis.CHATBOT:
        raise NotImplementedError("Use CHATBOT_V2 instead")

    elif api_enum == Apis.CHATBOT_V2:
        messages = args
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
    elif api_enum == Apis.ZH_SEGMENTER:
        text = args[0]
        response = jieba.lcut(text)
    elif api_enum == Apis.PINYIN:
        characters = args[0]
        response = pinyin.get(characters, format="numerical", delimiter=" ").replace(
            "5", "0"
        )
    elif api_enum == Apis.RELATED_WORDS:
        keyword, limit = args
        words_puller = datamuse.Datamuse()
        scored_words = words_puller.words(rel_trg=keyword, max=limit)
        scored_sorted_words = sorted(scored_words, key=lambda d: -d["score"])
        response = [d["word"] for d in scored_sorted_words]
    elif api_enum == Apis.TRANSLATE:
        term, target_language_code = args
        response = translate.Client().translate(
            term, target_language=target_language_code
        )
        translation = response["translatedText"]
        response = translation.replace("&#39;", "'").replace("&quot;", '"')

    elif api_enum == Apis.LANGUAGE_DETECTION:
        text = args[0]
        response = translate.Client().detect_language(text)["language"]

    _store_response(api_enum, args, response)
    return response


def _store_response(api_enum, args, response):
    args_json = _jsonify(args)
    response_json = _jsonify(response)

    # skip if too long
    if len(args_json) > MAX_ARGS_LENGTH or len(response) > MAX_RESPONSE_LENGTH:
        return

    db.sql_update(
        f"""
    INSERT INTO api_wrap 
        (api_enum, args_json, response_json)
    VALUES
        ({api_enum.value}, '{args_json}', '{response_json}')
    """
    )


def _lookup_call(api_enum, args):
    args_json = _jsonify(args)

    # skip if too long
    if len(args_json) > MAX_ARGS_LENGTH:
        return

    result = db.sql_query_single(
        f"""
    SELECT response_json
    FROM api_wrap
    WHERE
        api_enum = {api_enum.value} AND
        args_json = '{args_json}'
    """
    )
    if not result:
        return None
    else:
        return json.loads(result["response_json"])


def _jsonify(string):
    return json.dumps(string).replace("'", "''")
