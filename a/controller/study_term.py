import a
import math

DEFAULT_PAGE_LIMIT = 50


def get_term_page_and_num_pages(page_number, limit=DEFAULT_PAGE_LIMIT):
    total_count = a.model.study_term.get_count()
    num_pages = math.ceil(total_count * 1.0 / limit)
    terms = a.model.study_term.get_term_page(page_number, limit=limit)
    return terms, num_pages


def save(translated_terms=None, bulk_terms=None, term_dicts=None):
    study_terms = []

    if translated_terms:
        study_terms += [
            a.model.study_term.StudyTerm.build(translated_term=translated_term)
            for translated_term in translated_terms
        ]

    if bulk_terms:
        terms = bulk_terms.split("\r\n")
        study_terms += [
            a.model.study_term.StudyTerm.from_string(term) for term in terms if term
        ]

    if term_dicts:
        study_terms += [
            a.model.study_term.StudyTerm.build(
                term=term_dict["term"],
                pronunciation=term_dict["pronunciation"],
            )
            for term_dict in term_dicts
        ]

    [study_term.save() for study_term in study_terms]
    return study_terms
