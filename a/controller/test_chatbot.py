from a.controller import chatbot
from a.third_party import api_wrap, session_storage
import uuid


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeResponse:
    def __init__(self, usage, content):
        self.usage = usage
        self.choices = [FakeMessage(content)]


class TestChatBot:
    def setup_method(self):
        session_storage.set("uid", uuid.uuid4())

    def test_get_response(self, mocker):
        return  # sorry

    def test_get_cost(self, mocker):
        return  # sorry
