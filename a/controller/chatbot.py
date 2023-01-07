from a.third_party import api_wrap as apis
from a.controller import language

INITIAL_PROMPT = "Hi! I am your study buddy. I can help you practice chatting. What would you like to discuss today?"
COST_PER_TOKEN = 0.02 / 1000


class ChatBot:
    def __init__(self):
        self.responses = []
        self.tokens_spent = 0

    def get_response(self, input_text):
        if len(self.responses) == 0:
            self.responses = [
                language.get_translation(INITIAL_PROMPT, to_learning_language=False)
            ]
        self.responses.append(input_text)
        bot_text = self._call_openai()
        self.responses.append(bot_text)
        return bot_text

    def _call_openai(self):
        prompt = self._format_thread()
        response = apis.call_api(apis.Apis.CHATBOT, [prompt])
        bot_text = response["choices"][0]["text"]
        self.tokens_spent += response["usage"]["total_tokens"]
        return bot_text

    def _format_thread(self):
        # take the last 4 messages
        responses_to_format = (
            self.responses if len(self.responses) < 4 else self.responses[-4:]
        )
        formatted = ""
        for i, response in enumerate(responses_to_format):
            speaker = "Study Buddy" if i % 2 == 0 else "User"
            formatted += f"\n{speaker}: {response}"
        formatted += "\nStudy Buddy:"
        return formatted

    def get_cost(self):
        return f"${round(self.tokens_spent*COST_PER_TOKEN,3)}"
