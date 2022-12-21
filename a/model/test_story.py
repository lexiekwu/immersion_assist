from a.model import story


class TestStory:
    def test_build(self, mocker):
        sentence = "這是 一個 句子 !"
        sentence_split = sentence.split(" ")
        mocker.patch(
            "a.third_party.language.segment_text",
            return_value=zip(sentence_split, [True, True, True, False]),
        )
        mocker.patch(
            "a.third_party.language.get_pronunciation_dict",
            return_value={c: f"_{i}" for i, c in enumerate(sentence)},
        )
        mocker.patch(
            "a.third_party.language.get_translation",
            return_value="This is a sentence!",
        )
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
        ) == ("!", False, "")
        assert s.translation == "This is a sentence!"

    def test_to_dict(self, mocker):
        sentence = "這是 一個 句子 !"
        sentence_split = sentence.split(" ")
        mocker.patch(
            "a.third_party.language.segment_text",
            return_value=zip(sentence_split, [True, True, True, False]),
        )
        mocker.patch(
            "a.third_party.language.get_pronunciation_dict",
            return_value={c: f"_{i}" for i, c in enumerate(sentence)},
        )
        mocker.patch(
            "a.third_party.language.get_translation",
            return_value="This is a sentence!",
        )
        s = story.Story.build(sentence)
        sd = s.to_dict()
        assert "這是" in sd["terms_html"]
        assert "一個" in sd["terms_html"]
        assert "!" in sd["terms_html"]
        assert sd["terms_html"].count("<label>") == 3
        assert sd["terms_html"].count("story_span") == 4
        assert sd["translation"] == "This is a sentence!"
