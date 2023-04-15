from a.controller import story
import a


def _mock_translate(text, to_learning_language):
    if not to_learning_language:
        return "This is a sentence!"
    return "這是一個句子！"


class TestStory:
    def setup_method(self):
        self.test_user = a.model.user.User.new(
            "Testley", "testley2@aol.com", "iLikeTests"
        )
        self.test_user.login("iLikeTests")

    def test_build(self, mocker):
        sentence = "這是 一個 句子 !"
        sentence_split = sentence.split(" ")
        mocker.patch(
            "a.controller.language.segment_and_translate_to_english",
            return_value=zip(sentence_split, [True, True, True, False]),
        )
        mocker.patch(
            "a.controller.language.get_pronunciation_dict",
            return_value={c: f"_{i}" for i, c in enumerate(sentence)},
        )
        mocker.patch("a.controller.language.get_translation", _mock_translate)
        s = story.Story.build(sentence)
        assert len(s.story_terms) == 4
        assert (
            s.story_terms[1].term,
            s.story_terms[1].is_word,
            s.story_terms[1].pronunciation,
        ) == ("一個", True, "_3 _4")
        assert (
            s.story_terms[3].term,
            s.story_terms[3].is_word,
            s.story_terms[3].pronunciation,
        ) == ("!", False, None)
        assert s.translation == "This is a sentence!"

    def test_to_dict(self, mocker):
        sentence = "這是 一個 句子 !"
        sentence_split = sentence.split(" ")
        mocker.patch(
            "a.controller.language.segment_and_translate_to_english",
            return_value=zip(sentence_split, [True, True, True, False]),
        )
        mocker.patch(
            "a.controller.language.get_pronunciation_dict",
            return_value={c: f"_{i}" for i, c in enumerate(sentence)},
        )
        mocker.patch("a.controller.language.get_translation", _mock_translate)
        s = story.Story.build(sentence)
        sd = s.to_dict()
        assert "這是" in sd["terms_html"]
        assert "一個" in sd["terms_html"]
        assert "!" in sd["terms_html"]
        assert sd["terms_html"].count("<label>") == 3
        assert sd["terms_html"].count("story_span") == 4
        assert sd["translation"] == "This is a sentence!"

    def teardown_method(self):
        self.test_user.delete_all_data_TESTS_ONLY()
