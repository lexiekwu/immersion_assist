from flashcard import Flashcard
from flashcard_stack import FlashcardStack
from study_term import StudyTerm
from daily_stats import DailyStats
from datetime import datetime, timedelta
from user import User
from flask import Flask, render_template, request, session
from os import environ

app = Flask(__name__)
app.secret_key = environ.get("SESSION_KEY")
FLASHCARD_LIMIT = 20


@app.route("/")
def root():
    if not session.get("uid"):
        return render_template("login.html")
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # check if exists, if not, send to signup
    this_user = User.get_by_email(request.form.get("email"))
    if not this_user:
        return render_template("signup.html")

    # incorrect password, try again
    if not this_user.is_correct_password(request.form.get("password")):
        return render_template("login.html")

    # correct password, log in
    session["uid"] = this_user.uid
    session["name"] = this_user.name
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    this_user = User.new(
        name=request.form.get("name"),
        email=request.form.get("email"),
        password=request.form.get("password")
    )

    session["uid"] = this_user.uid
    session["name"] = this_user.name
    return render_template("index.html")

@app.route("/cards")
def cards():
    if not session.get("uid"):
        return render_template("login.html")

    flashcard_stack = FlashcardStack()
    cards = flashcard_stack.get_ordered_cards(FLASHCARD_LIMIT)
    return render_template("cards.html", cards=cards)

@app.route("/stats")
def stats():
    if not session.get("uid"):
        return render_template("login.html")

    today = datetime.today().date()
    week_days = [today] + [
        today - timedelta(i)
        for i in range(1,8)
    ]
    week_stats = [
        DailyStats.get_for_day(dt=str(day))
        for day in week_days
    ]
    return render_template("stats.html", week_stats=week_stats)

@app.route("/new_card", methods=["GET"])
def new_card():
    if not session.get("uid"):
        return render_template("login.html")

    return render_template("new_card.html")


@app.route("/add/", methods=["POST"])
def add():
    if not session.get("uid"):
        return render_template("login.html")

    term = request.form.get("word")
    study_term = StudyTerm.create_and_save(term)
    return render_template("add.html", study_term=study_term)

@app.route("/add_multi/", methods=["POST"])
def add_multi():
    if not session.get("uid"):
        return render_template("login.html")

    terms = request.form.get("terms").split("\r\n")
    [
        StudyTerm.create_and_save(term) for term in terms if term
    ]
    return render_template("new_card.html")


@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    if not session.get("uid"):
        return render_template("login.html")
        
    flashcard_stack = FlashcardStack()

    # case of first load
    if request.method == "GET":
        new_card = flashcard_stack.pop_card()
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

    current_card = flashcard_stack.pop_card() if last_card.is_correct_guess(guess) else last_card
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