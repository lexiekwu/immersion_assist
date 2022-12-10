import openai
from os import environ

openai.api_key = environ.get("OPENAI_KEY")
INITIAL_PROMPT = "你好！我是你的學習夥伴。我可以幫你練習聊天。你今天想討論什麼？"
COST_PER_TOKEN = 0.02 / 1000


class ChatBot:
    def __init__(self):
        self.responses = ["You: " + INITIAL_PROMPT]
        self.tokens_spent = 0

    def get_response(self, input_text):
        self.responses.append(input_text)
        bot_text = self._call_openai()
        self.responses.append(bot_text)
        return bot_text

    def _call_openai(self):
        prompt = self._format_thread()
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=50,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"],
        )
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
            speaker = "Friend" if i % 2 == 0 else "You"
            formatted += f"\n{speaker}: {response}"
        formatted += "\nFriend:"
        print("FORMATTED AS", formatted)
        return formatted

    def get_cost(self):
        return f"${round(self.tokens_spent*COST_PER_TOKEN,3)}"
