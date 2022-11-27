from flashcard import Flashcard
from flashcard_stack import FlashcardStack
from study_term import StudyTerm, get_term_page, get_count as get_study_term_count
from daily_stats import DailyStats
from datetime import datetime, timedelta
from user import User
from flask import Flask, render_template, request, session, flash
from os import environ
from language import segment_text
import math

app = Flask(__name__)
app.secret_key = environ.get("SESSION_KEY")
DEFAULT_PAGE_LIMIT = 50


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
        flash("No user exists for that email. Please sign up.", "bad")
        return render_template("signup.html")

    # incorrect password, try again
    if not this_user.is_correct_password(request.form.get("password")):
        flash("That password is incorrect. Please try again.", "bad")
        return render_template("login.html")

    # correct password, log in
    session["uid"] = this_user.uid
    session["name"] = this_user.name
    flash("Login successful.", "good")
    return render_template("index.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    if User.get_by_email(request.form.get("email")):
        flash("An account already exists for that email. Please log in.", "bad")
        return render_template("login.html")

    this_user = User.new(
        name=request.form.get("name"),
        email=request.form.get("email"),
        password=request.form.get("password"),
    )

    session["uid"] = this_user.uid
    session["name"] = this_user.name
    return render_template("index.html")


@app.route("/terms")
def terms():
    if not session.get("uid"):
        return render_template("login.html")

    page_number = int(request.args.get("page_no", 1))
    total_count = get_study_term_count()
    num_pages = math.ceil(total_count * 1.0 / DEFAULT_PAGE_LIMIT)
    terms = get_term_page(page_number, limit=DEFAULT_PAGE_LIMIT)
    return render_template(
        "terms.html",
        terms=terms,
        page_number=page_number,
        num_pages=num_pages,
    )


@app.route("/stats")
def stats():
    if not session.get("uid"):
        return render_template("login.html")

    today = datetime.today().date()
    week_days = [today] + [today - timedelta(i) for i in range(1, 8)]
    week_stats = [DailyStats.get_for_day(dt=str(day)) for day in week_days]
    return render_template("stats.html", week_stats=week_stats)


@app.route("/new_card", methods=["GET"])
def new_card():
    if not session.get("uid"):
        return render_template("login.html")

    return render_template("new_card.html")


@app.route("/story_time", methods=["GET", "POST"])
def story_time():
    if not session.get("uid"):
        return render_template("login.html")

    raw_story = request.form.get("story", "")
    segmented_story = segment_text(raw_story)

    return render_template("story_time.html", segmented_story=segmented_story)


@app.route("/add/", methods=["POST"])
def add():
    if not session.get("uid"):
        return render_template("login.html")

    try:
        term = request.form.get("word")
        study_term = StudyTerm.create_and_save(term)
    except Exception as e:
        flash(f"Did not successfully create your card. Error was '{str(e)}'", "bad")
        return render_template("new_card.html")

    return render_template("add.html", study_term=study_term)


@app.route("/edit", methods=["GET"])
def edit():
    if not session.get("uid"):
        return render_template("login.html")

    study_term = StudyTerm.get_by_id(request.args.get("study_term_id_to_edit"))

    if not study_term:
        flash(
            f"Could not find the term you're trying to edit. Please try again.", "bad"
        )
        render_template("index.html")

    return render_template("edit_card.html", study_term=study_term)


@app.route("/update", methods=["POST"])
def update():
    if not session.get("uid"):
        return render_template("login.html")

    try:
        study_term = StudyTerm.get_by_id(request.form.get("study_term_id_to_edit"))
        study_term.update(
            request.form.get("term"),
            request.form.get("translation"),
            request.form.get("pronunciation"),
        )
    except Exception as e:
        flash(f"Did not successfully update your card. Error was '{str(e)}'", "bad")
        return render_template("index.html")

    return render_template("add.html", study_term=study_term)


@app.route("/add_multi/", methods=["POST"])
def add_multi():
    if not session.get("uid"):
        return render_template("login.html")

    try:
        terms = request.form.get("terms").split("\r\n")
        [StudyTerm.save_from_string(term) for term in terms if term]
        flash(f"Successfully added {len(terms)} cards.", "good")
    except Exception as e:
        flash(f"Did not successfully create your cards. Error was '{str(e)}'", "bad")
    return render_template("new_card.html")


@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    if not session.get("uid"):
        return render_template("login.html")

    flashcard_stack = FlashcardStack.from_dicts(session.get("flashcard_stack", []))

    # case of first load
    if request.method == "GET":
        new_card = flashcard_stack.pop_card()

        if not new_card:
            flash(f"No cards available for quizzing. Try adding more.", "good")
            return render_template("new_card.html")

        session["current_card"] = new_card.to_dict()
        session["flashcard_stack"] = flashcard_stack.to_dicts()
        return render_template(
            "quiz.html",
            current_card=new_card,
            last_card=None,
        )

    # else
    guess = request.form["guess"]
    last_card = Flashcard.from_dict(session["current_card"])
    was_correct = last_card.is_correct_guess(guess)

    if was_correct:
        last_card.update_on_correct()
        current_card = flashcard_stack.pop_card()
    else:
        last_card.update_on_incorrect()
        current_card = last_card

    if not current_card:
        flash(f"No cards available for quizzing. Try adding more.", "good")
        return render_template("new_card.html")

    session["current_card"] = current_card.to_dict()
    session["flashcard_stack"] = flashcard_stack.to_dicts()
    return render_template(
        "quiz.html",
        current_card=current_card,
        last_card=last_card,
        was_correct=was_correct,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
