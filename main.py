from flashcard import Flashcard
from flashcard_stack import FlashcardStack
from study_term import StudyTerm
from flask import Flask, render_template, request

app = Flask(__name__)
FLASHCARD_LIMIT = 20


@app.route("/")
def root():
    return render_template("index.html")

@app.route("/cards")
def cards():
    flashcard_stack = FlashcardStack()
    cards = flashcard_stack.get_ordered_cards(FLASHCARD_LIMIT)
    return render_template("cards.html", cards=cards)

@app.route("/new_card", methods=["GET"])
def new_card():
    return render_template("new_card.html")


@app.route("/add/", methods=["POST"])
def add():
    if request.method == "GET":
        return (
            f"The URL /data is accessed directly. Try going to '/form' to submit form"
        )
    if request.method == "POST":
        term = request.form.get("word")
        study_term = StudyTerm.create_and_save(term)
        return render_template("add.html", study_term=study_term)


@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    # case of first load
    flashcard_stack = FlashcardStack()
    new_card = flashcard_stack.pop_card()
    if request.method == "GET":
        return render_template(
            "quiz.html",
            current_card=new_card,
            last_card=None,
            last_guess=None,
        )

    # else
    guess = request.form["guess"]
    last_card = Flashcard.get_by_study_term_id_and_quiz_type(
        request.form["last_term_id"], request.form["quiz_type"]
    )
    last_card.update_after_guess(guess)
    current_card = new_card if last_card.is_correct_guess(guess) else last_card
    return render_template(
        "quiz.html",
        current_card=current_card,
        last_card=last_card,
        last_guess=guess,
    )

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)