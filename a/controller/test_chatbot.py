from a.controller import chatbot
from a.third_party import api_wrap, session_storage
import uuid


class TestChatBot:
    def setup_method(self):
        session_storage.set("uid", uuid.uuid4())

    def test_get_response(self, mocker):
        cb = chatbot.ChatBot()
        mocker.patch(
            "a.third_party.api_wrap.call_api",
            return_value={
                "usage": {"total_tokens": 10},
                "choices": [{"message": {"content": "hello back to you!"}}],
            },
        )

        assert cb.get_response("hey there...") == "hello back to you!"

    def test_get_cost(self, mocker):
        cb = chatbot.ChatBot()
        mocker.patch(
            "a.third_party.api_wrap.call_api",
            return_value={
                "usage": {"total_tokens": 200},
                "choices": [{"message": {"content": "hello back to you!"}}],
            },
        )

        cb.get_response("hey there...")
        assert cb.get_cost() == "$0.004"
