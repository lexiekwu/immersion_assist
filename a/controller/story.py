from a.controller import language
from flask import json, escape


class Story:
    def __init__(self, story_terms, translation):
        self.story_terms = story_terms
        self.translation = translation

    @classmethod
    def build(cls, raw_story):
        if language.is_learning_language(raw_story):
            learning_language_story = raw_story
            translated_story = language.get_translation(
                raw_story, to_learning_language=False
            )
        else:
            learning_language_story = language.get_translation(
                raw_story, to_learning_language=True
            )
            translated_story = raw_story

        segmented_story = list(language.segment_text(learning_language_story))
        pronunciation_lookup = language.get_pronunciation_dict(learning_language_story)

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

    def to_dict(self):
        return {
            "terms_html": "".join([term.to_html() for term in self.story_terms]),
            "translation": self.translation,
        }


class StoryTerm:
    def __init__(self, term, is_word, pronunciation):
        self.term = term
        self.is_word = is_word
        self.pronunciation = pronunciation

    def to_dict(self):
        return {
            "term": self.term,
            "pronunciation": self.pronunciation,
            "is_word": self.is_word,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_html(self):
        if self.is_word:
            return f"""
                <label>
                    <input type="checkbox" class="story_word_check" name="{escape(self.to_json())}">
                    <span class="story_span story_word_span">
                        <span>{self.term}</span>
                        <span class="story_word_pronunciation">{self.pronunciation}</span>
                    </span>
                </label>
            """
        else:
            return f"""<span class="story_span">{self.term}</span>"""
