from a.controller import language
from openai import OpenAI
from os import environ

INITIAL_PROMPT = "Hi! I am your study buddy. I can help you practice chatting. What would you like to discuss today?"
COST_PER_TOKEN = 0.02 / 1000


class ChatBot:
    def __init__(self):
        self.responses = []
        self.tokens_spent = 0

    def get_response(self, input_text):

        if len(self.responses) == 0:
            self._add_msg(language.get_translation(INITIAL_PROMPT), "assistant")

        self._add_msg(input_text, "user")
        bot_text = self._call_openai()
        self._add_msg(bot_text, "assistant")
        return bot_text

    def _add_msg(self, msg, role):
        message = {"role": role, "content": msg}
        self.responses.append(message)

    def _call_openai(self):
        client = OpenAI(
            # This is the default and can be omitted
            api_key=environ.get("OPENAI_KEY"),
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.responses,
        )
        bot_text = response.choices[0].message.content
        self.tokens_spent += response.usage.total_tokens
        return bot_text

    def get_cost(self):
        return f"${round(self.tokens_spent*COST_PER_TOKEN,3)}"
