import language
from flask import json


class Story:
    def __init__(self, story_terms, translation):
        self.story_terms = story_terms
        self.translation = translation

    @classmethod
    def build(cls, raw_story):
        segmented_story = list(language.segment_text(raw_story))
        pronunciation_lookup = language.get_pronunciation_dict(
            raw_story, language.TW_CODE
        )
        translated_story = language.get_translation(raw_story, language.EN_CODE)

        def _get_segment_pronunciation(segment, is_word):
            if not is_word:
                return ""

            return " ".join(
                [pronunciation_lookup[c] for c in segment if c in pronunciation_lookup]
            )

        story_terms = [
            StoryTerm(segment, is_word, _get_segment_pronunciation(segment, is_word))
            for segment, is_word in segmented_story
        ]

        return cls(story_terms, translated_story)


class StoryTerm:
    def __init__(self, term, is_word, pronunciation):
        self.term = term
        self.is_word = is_word
        self.pronunciation = pronunciation

    def to_json(self):
        return json.dumps({"term": self.term, "pronunciation": self.pronunciation})
