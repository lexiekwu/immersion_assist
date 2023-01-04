import a
import uuid
import time
from a.controller import study_term


def test_get_term_page_and_num_pages():
    user = a.model.user.User.new("Testley", "testley2@aol.com", "iLikeTests")
    user.login("iLikeTests")

    def _get_numbered_term(i):
        return a.model.study_term.StudyTerm(
            uuid.uuid4(), f"你好{i}", f"hello{i}", "ni3 hao3"
        )

    _terms = []
    for i in range(5):
        term = _get_numbered_term(i)
        _terms.append(term)
        term.save()
        time.sleep(1.1)  # preserve order

    terms, num_pages = study_term.get_term_page_and_num_pages(3, limit=2)
    assert terms[0].term == _terms[0].term
    assert len(terms) == 1
    assert num_pages == 3

    user.delete_all_data_TESTS_ONLY()


def test_save(mocker):
    def _dict_translate(word, to_learning_language=True):
        return {"cat": "貓", "dog": "狗", "鯊魚": "shark", "鰻魚": "eel"}[word]

    def _dict_pronounce(word, _=None):
        return {"狗": "gou1", "貓": "mao1"}[word]

    mocker.patch("a.third_party.language.get_translation", _dict_translate)
    mocker.patch("a.third_party.language.get_pronunciation", _dict_pronounce)

    user = a.model.user.User.new("Testley", "testley2@aol.com", "iLikeTests")
    user.login("iLikeTests")

    study_terms = study_term.save(
        terms=["dog", "cat"],
        bulk_terms="\r\n獅子,lion,shi1 zi0\r\n烏龜,turtle,wu1 gui1\r\n",
        term_dicts=[
            {"term": "鰻魚", "pronunciation": "man2 yu2"},
            {"term": "鯊魚", "pronunciation": "sha1 yu2"},
        ],
    )
    assert len(study_terms) == 6

    # load the terms to make sure they're saved
    loaded_study_terms = a.model.study_term.get_term_page(1, 6)
    term_lookup = {st.term: st for st in loaded_study_terms}
    dummy_uuid = uuid.uuid4()
    assert term_lookup["狗"] == a.model.study_term.StudyTerm(
        dummy_uuid, "狗", "dog", "gou1"
    )

    assert term_lookup["貓"] == a.model.study_term.StudyTerm(
        dummy_uuid, "貓", "cat", "mao1"
    )

    assert term_lookup["獅子"] == a.model.study_term.StudyTerm(
        dummy_uuid, "獅子", "lion", "shi1 zi0"
    )

    assert term_lookup["烏龜"] == a.model.study_term.StudyTerm(
        dummy_uuid, "烏龜", "turtle", "wu1 gui1"
    )

    assert term_lookup["鰻魚"] == a.model.study_term.StudyTerm(
        dummy_uuid, "鰻魚", "eel", "man2 yu2"
    )

    assert term_lookup["鯊魚"] == a.model.study_term.StudyTerm(
        dummy_uuid, "鯊魚", "shark", "sha1 yu2"
    )

    user.delete_all_data_TESTS_ONLY()
