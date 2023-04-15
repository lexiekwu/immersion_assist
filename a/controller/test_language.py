from a.controller import language
from a.third_party import session_storage
from os import environ


def test_get_pronunciation():
    session_storage.set("learning_language", language.TW_CODE)
    session_storage.set("home_language", language.EN_CODE)
    assert language.get_pronunciation("你好", True) == "ni3 hao3"
    assert language.get_pronunciation("你好", False) == ""


def test_pronunciation_dict():
    session_storage.set("learning_language", language.TW_CODE)
    session_storage.set("home_language", language.EN_CODE)
    sentence = "這是 一個句子!"
    assert language.get_pronunciation_dict(sentence) == {
        "這": "zhe4",
        "是": "shi4",
        "一": "yi1",
        "個": "ge4",
        "句": "ju4",
        "子": "zi3",
    }
    assert language.get_pronunciation_dict(sentence, False) == {}


def test_translation():
    session_storage.set("learning_language", language.TW_CODE)
    session_storage.set("home_language", language.EN_CODE)
    assert language.get_translation("how are you?") == "你好嗎？"
    assert language.get_translation("你好嗎？", False) == "Are you OK?"


def test_segment_text_and_translate_to_english():
    session_storage.set("learning_language", language.TW_CODE)
    session_storage.set("home_language", language.EN_CODE)
    sentence = "這是 一個句子!"
    assert ("句子", "sentence") in language.segment_and_translate_to_english(sentence)
    assert ("一個", "a") in language.segment_and_translate_to_english(sentence)


def test_get_language():
    assert language.is_learning_language("這是一個句子!")
    assert not language.is_learning_language("This is a sentence!")


def test_get_related_words():
    words = language.get_related_words("politics", 10)
    assert len(set(words) - set({"sociology", "economics"})) == 8
