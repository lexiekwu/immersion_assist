from a.third_party import language, session_storage
from os import environ

# All the success states are tested by the existing model tests
# so this will only test failure states
# and I am lazy ok?


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


def test_segment_text():
    session_storage.set("learning_language", language.TW_CODE)
    session_storage.set("home_language", language.EN_CODE)
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
    assert set(list(language.segment_text(sentence))) == set(
        [
            ("這", True),
            ("是", True),
            (" ", False),
            ("一", True),
            ("個", True),
            ("句子", True),
            ("!", False),
        ]
    )

    assert list(language.segment_text(sentence, False)) == [
        ("這是", True),
        ("一個句子!", True),
    ]


def test_get_language():
    assert language.is_learning_language("這是一個句子!")
    assert not language.is_learning_language("This is a sentence!")


def test_get_related_words():
    words = language.get_related_words("politics", 10)
    assert len(set(words) - set({"sociology", "economics"})) == 8
