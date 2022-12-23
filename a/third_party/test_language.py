from a.third_party import language
from os import environ

# All the success states are tested by the existing model tests
# so this will only test failure states
# and I am lazy ok?


def test_get_pronunciation():
    assert language.get_pronunciation("你好", language.TW_CODE) == "ni3 hao3"
    assert language.get_pronunciation("你好", language.EN_CODE) == ""


def test_pronunciation_dict():
    sentence = "這是 一個句子!"
    assert language.get_pronunciation_dict(sentence, language.TW_CODE) == {
        "這": "zhe4",
        "是": "shi4",
        "一": "yi1",
        "個": "ge4",
        "句": "ju4",
        "子": "zi3",
    }
    assert language.get_pronunciation_dict(sentence, language.EN_CODE) == {}


def test_translation():
    assert language.get_translation("how are you?", language.TW_CODE) == "你好嗎？"
    assert language.get_translation("你好嗎？", language.EN_CODE) == "Are you OK?"


def test_segment_text():
    sentence = "這是 一個句子!"
    environ["CHINESE_SEGMENTER"] = "jieba"
    assert list(language.segment_text(sentence)) == [
        ("這是", True),
        (" ", False),
        ("一個", True),
        ("句子", True),
        ("!", False),
    ]

    environ["CHINESE_SEGMENTER"] = "thulac"
    assert list(language.segment_text(sentence)) == [
        ("這", True),
        ("是", True),
        (" ", False),
        ("一", True),
        ("個", True),
        ("句子", True),
        ("!", False),
    ]

    assert language.segment_text(sentence, language.EN_CODE) == []


def test_get_related_words():
    words = language.get_related_words("politics", 10)
    assert len(set(words) - set({"sociology", "economics"})) == 8
