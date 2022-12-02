from flashcard import Flashcard
from flashcard_stack import FlashcardStack
from study_term import StudyTerm, get_term_page, get_count as get_study_term_count
from daily_stats import DailyStats
from datetime import datetime, timedelta
from user import User
from flask import Flask, render_template, request, session, flash, json, redirect
from os import environ
from language import segment_text
from urllib.parse import urlparse

import math
import re

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

    # if you came from somewhere within the app, direct
    # back to what you were trying to do
    referrer_url = urlparse(request.referrer)
    if referrer_url.hostname == request.host.split(":")[0]:
        return redirect(request.referrer)

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


@app.route("/new", methods=["GET"])
def new():
    if not session.get("uid"):
        return render_template("login.html")

    return render_template("new.html")


@app.route("/story_time", methods=["GET", "POST"])
def story_time():
    if not session.get("uid"):
        return render_template("login.html")

    if not request.form.get("story"):
        return render_template("story_time.html", segmented_story=None)

    raw_story = request.form.get("story")
    segmented_story = list(segment_text(raw_story))

    # convert words to StudyTerms
    for i in range(len(segmented_story)):
        segment, is_word = segmented_story[i]
        if not is_word:
            continue
        study_term = StudyTerm.build_from_term(segment)
        segmented_story[i] = (study_term, is_word)

    return render_template("story_time.html", segmented_story=segmented_story)


@app.route("/save_cards", methods=["POST"])
def save_cards():
    if not session.get("uid"):
        return render_template("login.html")

    study_terms = []

    try:
        if request.form.get("word"):
            study_term = StudyTerm.build_and_save_from_translated_term(
                request.form.get("word")
            )
            study_terms.append(study_term)
        elif request.form.get("terms"):
            terms = request.form.get("terms").split("\r\n")
            study_terms += [StudyTerm.save_from_string(term) for term in terms if term]
        else:
            # look for selected keys from story_time
            form_keys = set(request.form.keys())
            for form_key in form_keys:
                term_to_save = json.loads(form_key)
                if term_to_save:
                    study_term = StudyTerm.from_dict(term_to_save)
                    study_term.save()
                    study_terms.append(study_term)

    except Exception as e:
        flash(f"Did not successfully create your cards. Error was '{str(e)}'", "bad")
        return render_template("new.html")

    flash(f"Successfully added {len(study_terms)} terms.", "good")
    return render_template("save_cards.html", study_terms=study_terms)


@app.route("/edit", methods=["GET"])
def edit():
    if not session.get("uid"):
        return render_template("login.html")

    study_term = StudyTerm.get_by_id(request.args.get("study_term_id_to_edit"))

    if not study_term:
        flash(
            f"Could not find the term you're trying to edit. Please try again.", "bad"
        )
        return render_template("index.html")

    session["next"] = request.referrer
    return render_template("edit_card.html", study_term=study_term)


@app.route("/delete", methods=["GET"])
def delete():
    if not session.get("uid"):
        return render_template("login.html")

    study_term = StudyTerm.get_by_id(request.args.get("study_term_id_to_delete"))

    if not study_term:
        flash(
            f"Could not find the term you're trying to delete. Please try again.", "bad"
        )
        render_template("index.html")

    study_term.delete()
    flash(f"Deleted term {study_term.term}.", "good")

    return redirect(request.referrer or "/")


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
        flash(f"Updated term {study_term.term}.", "good")
    except Exception as e:
        flash(f"Did not successfully update your card. Error was '{str(e)}'", "bad")
        return render_template("index.html")

    return redirect(session.get("next") or "/")


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
            return render_template("new.html")

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
        return render_template("new.html")

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
