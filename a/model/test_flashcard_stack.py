from a.model import study_term, flashcard_stack
import a
import uuid
import time


class TestFlashcardStack:
    def setup_method(self):
        self.test_user = a.model.user.User.new(
            "Testley", "testley2@aol.com", "iLikeTests"
        )
        self.test_user.login("iLikeTests")

    def _get_numbered_term(self, i):
        return study_term.StudyTerm(uuid.uuid4(), f"你好{i}", f"hello{i}", "ni3 hao3")

    def test__refresh(self):
        sts = [self._get_numbered_term(i) for i in range(12)]
        [st.save() for st in sts]

        # test initial population of stack, and that there aren't duplicates in the first 10 cards
        fcs = flashcard_stack.FlashcardStack()
        flashcard_stack.MIN_TIME_BETWEEN_REVIEWS_SEC = 1
        assert len(fcs.stack) == 0  # needs wait time
        time.sleep(1.0)
        fcs = flashcard_stack.FlashcardStack()
        assert len(fcs.stack) == flashcard_stack.DEFAULT_LIMIT
        terms = [fc.study_term.term for fc in fcs.stack]
        assert len(set(terms)) == len(terms)

        # even if the limit can't be met, still don't have duplicates
        fcs = flashcard_stack.FlashcardStack(limit=15)
        assert len(fcs.stack) == 12
        terms = [fc.study_term.term for fc in fcs.stack]
        assert len(set(terms)) == len(terms)

        # test passing in the stack
        fcs = flashcard_stack.FlashcardStack(existing_stack=sts[:3])
        assert len(fcs.stack) == 3

    def test_pop_card(self):
        sts = [self._get_numbered_term(i) for i in range(12)]
        [st.save() for st in sts]

        # test initial population of stack, and that there aren't duplicates in the first 10 cards
        fcs = flashcard_stack.FlashcardStack()
        flashcard_stack.MIN_TIME_BETWEEN_REVIEWS_SEC = 1
        time.sleep(1.0)
        fcs = flashcard_stack.FlashcardStack()
        assert len(fcs.stack) == flashcard_stack.DEFAULT_LIMIT
        terms = [fc.study_term.term for fc in fcs.stack]
        assert len(set(terms)) == len(terms)

        # even if the limit can't be met, still don't have duplicates
        fcs = flashcard_stack.FlashcardStack(limit=15)
        assert len(fcs.stack) == 12
        terms = [fc.study_term.term for fc in fcs.stack]
        assert len(set(terms)) == len(terms)

        # test passing in the stack
        fcs = flashcard_stack.FlashcardStack(existing_stack=sts[:3])
        assert len(fcs.stack) == 3

    def test_pop_card(self):
        sts = [self._get_numbered_term(i) for i in range(10)]
        [st.save() for st in sts]

        # test initial population of stack, and that there aren't duplicates in the first 10 cards
        fcs = flashcard_stack.FlashcardStack(limit=3)
        assert len(fcs.stack) == 3
        assert fcs.pop_card() is not None
        assert len(fcs.stack) == 2
        assert fcs.pop_card() is not None
        assert len(fcs.stack) == 1
        assert fcs.pop_card() is not None
        assert len(fcs.stack) == 0
        assert fcs.pop_card() is not None
        assert len(fcs.stack) == 2  # refilled then popped 1

    def test_to_from_dicts(self):
        sts = [self._get_numbered_term(i) for i in range(10)]
        [st.save() for st in sts]
        fcs = flashcard_stack.FlashcardStack()
        dicts = [fc.to_dict() for fc in fcs.stack]
        assert fcs.to_dicts() == dicts
        assert flashcard_stack.FlashcardStack.from_dicts(dicts).stack == fcs.stack

    def teardown_method(self):
        self.test_user.delete_all_data()
