import a.third_party.api_wrap as apis
import a.third_party.cockroachdb as db
from flask import json


class TestApiWrap:
    def setup_method(self):
        self.chatbot_str_1 = "Hello the're!"
        self.chatbot_str_2 = "Hello there!"
        self.segment_sentence = "你好我是一隻烏龜"
        self.zh_text = "你好"
        self.keyword_args = ["peel", 1]
        self.translate_args = ["hello", "zh-TW"]
        test_values = [
            (apis.Apis.CHATBOT, [self.chatbot_str_1]),
            (apis.Apis.CHATBOT, [self.chatbot_str_2]),
            (apis.Apis.ZH_SEGMENTER, [self.segment_sentence]),
            (apis.Apis.PINYIN, [self.zh_text]),
            (apis.Apis.RELATED_WORDS, self.keyword_args),
            (apis.Apis.TRANSLATE, self.translate_args),
            (apis.Apis.LANGUAGE_DETECTION, [self.zh_text]),
        ]
        for enum, args in test_values:
            db.sql_update(
                f"""
                DELETE FROM api_wrap 
                WHERE 
                    api_enum = {enum.value} AND
                    args_json = '{json.dumps(args).replace("'","''")}'
            """
            )

    def test_segmenter(self, mocker):
        mock_value = ["你好", "我是", "一隻烏龜"]
        mock = mocker.patch(
            "jieba.lcut",
            return_value=mock_value,
        )
        assert mock.call_count == 0

        response = apis.call_api(apis.Apis.ZH_SEGMENTER, [self.segment_sentence])
        assert response == mock_value
        assert mock.call_count == 1

        response = apis.call_api(apis.Apis.ZH_SEGMENTER, [self.segment_sentence])
        assert response == mock_value
        assert mock.call_count == 1

    def test_pinyin(self, mocker):
        mock_value = "ni3 hao3"
        mock = mocker.patch(
            "pinyin.get",
            return_value=mock_value,
        )
        assert mock.call_count == 0

        response = apis.call_api(apis.Apis.PINYIN, [self.zh_text])
        assert response == mock_value
        assert mock.call_count == 1

        response = apis.call_api(apis.Apis.PINYIN, [self.zh_text])
        assert response == mock_value
        assert mock.call_count == 1

    def test_related_words(self, mocker):
        mock_value = [{"word": "banana", "score": 0.1}]
        mock = mocker.patch(
            "datamuse.Datamuse.words",
            return_value=mock_value,
        )
        assert mock.call_count == 0

        response = apis.call_api(apis.Apis.RELATED_WORDS, self.keyword_args)
        assert response == ["banana"]
        assert mock.call_count == 1

        response = apis.call_api(apis.Apis.RELATED_WORDS, self.keyword_args)
        assert response == ["banana"]
        assert mock.call_count == 1

    def test_translate(self, mocker):
        mock_value = {"translatedText": "你好"}
        mock = mocker.patch(
            "google.cloud.translate_v2.Client.translate",
            return_value=mock_value,
        )
        assert mock.call_count == 0

        response = apis.call_api(apis.Apis.TRANSLATE, self.translate_args)
        assert response == "你好"
        assert mock.call_count == 1

        response = apis.call_api(apis.Apis.TRANSLATE, self.translate_args)
        assert response == "你好"
        assert mock.call_count == 1

    def test_language_detection(self, mocker):
        mock_value = {"language": "zh-TW"}
        mock = mocker.patch(
            "google.cloud.translate_v2.Client.detect_language",
            return_value=mock_value,
        )
        assert mock.call_count == 0

        response = apis.call_api(apis.Apis.LANGUAGE_DETECTION, [self.zh_text])
        assert response == "zh-TW"
        assert mock.call_count == 1

        response = apis.call_api(apis.Apis.LANGUAGE_DETECTION, [self.zh_text])
        assert response == "zh-TW"
        assert mock.call_count == 1
