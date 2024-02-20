from flask import Flask, render_template, request, session, flash, json, redirect
import flask_excel
from os import environ
from urllib.parse import urlparse
from flask_mail import Mail
import a

app = Flask(__name__)
app.secret_key = environ.get("SESSION_KEY")

GMAIL_SENDER = environ.get("GMAIL_USER")
app.config.update(
    {
        "MAIL_SERVER": "smtp.gmail.com",
        "MAIL_PORT": 465,
        "MAIL_USERNAME": GMAIL_SENDER,
        "MAIL_PASSWORD": environ.get("GMAIL_PW"),
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
    }
)
mail = Mail(app)


@app.route("/")
def root():

    if not session.get("uid"):
        return render_template("login.html")

    return render_template("index.html")


@app.route("/about")
def about():

    return render_template("about.html")


@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    is_user_found, is_correct_password = a.controller.login.try_login(
        request.form.get("email"), request.form.get("password")
    )

    # check if exists, if not, send to signup
    if not is_user_found:
        flash("No user exists for that email. Please sign up.", "bad")
        return render_template(
            "signup.html",
            supported_languages=a.controller.language.SUPPORTED_LANGUAGES_AND_CODES,
        )

    # incorrect password, try again
    if not is_correct_password:
        flash("That password is incorrect. Please try again.", "bad")
        return render_template("login.html")

    # if you came from somewhere within the app, direct
    # back to what you were trying to do
    referrer_url = urlparse(request.referrer)
    if (
        referrer_url.hostname == request.host.split(":")[0]
        and "login" not in request.referrer
        and "signup" not in request.referrer
    ):
        return redirect(request.referrer)

    return render_template("index.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "GET":
        return render_template(
            "signup.html",
            supported_languages=a.controller.language.SUPPORTED_LANGUAGES_AND_CODES,
        )

    is_success, failure_reason = a.controller.signup.try_signup(
        request.form.get("email"),
        request.form.get("password"),
        request.form.get("name"),
        request.form.get("home_language"),
        request.form.get("learning_language"),
    )

    if is_success:
        return redirect("/about")
    else:
        if failure_reason == a.controller.signup.SignupFailureReason.USER_EXISTS:
            flash("An account already exists for that email. Please log in.", "bad")

        elif failure_reason == a.controller.signup.SignupFailureReason.INVALID_EMAIL:
            flash(
                f"{request.form.get('email')} Is not a valid email address. Please try again.",
                "bad",
            )
            return render_template(
                "signup.html",
                supported_languages=a.controller.language.SUPPORTED_LANGUAGES_AND_CODES,
            )

        else:
            flash("Unable to log you in.", "bad")
        return render_template("login.html")


@app.route("/start_signup", methods=["POST", "GET"])
def start_signup():

    if request.method == "GET":
        return redirect("/signup")

    email = request.form.get("email")

    # check that there's not an issue with the email address
    email_ok, issue = a.controller.signup.can_email_signup(email)

    if not email_ok:
        if issue == a.controller.signup.SignupFailureReason.USER_EXISTS:
            flash("An account already exists for that email. Please log in.", "bad")
            return redirect("/login")

        elif issue == a.controller.signup.SignupFailureReason.INVALID_EMAIL:
            flash(
                f"{request.form.get('email')} Is not a valid email address. Please try again.",
                "bad",
            )
            return render_template(
                "signup.html",
                supported_languages=a.controller.language.SUPPORTED_LANGUAGES_AND_CODES,
            )

    # send confirmation code
    a.model.confirm_email.send_email_confirmation_code(email, mail)

    return render_template(
        "confirm_email.html",
        email=email,
        name=request.form.get("name"),
        home_language=request.form.get("home_language"),
        learning_language=request.form.get("learning_language"),
    )


@app.route("/email_confirmation", methods=["POST", "GET"])
def email_confirmation():

    if request.method == "GET":
        return redirect("/signup")

    email = request.form.get("email")
    code = request.form.get("code")

    if a.model.confirm_email.confirm_email(email, code):
        return render_template(
            "add_password.html",
            email=email,
            name=request.form.get("name"),
            home_language=request.form.get("home_language"),
            learning_language=request.form.get("learning_language"),
        )
    else:
        flash(
            f"Incorrect confirmation code. Please try again.",
            "bad",
        )
        return redirect("/signup")


@app.route("/terms")
def terms():

    if not session.get("uid"):
        return render_template("login.html")

    page_number = int(request.args.get("page_no", 1))
    terms, num_pages = a.controller.study_term.get_term_page_and_num_pages(page_number)

    return render_template(
        "terms.html",
        terms=terms,
        page_number=page_number,
        num_pages=num_pages,
    )


@app.route("/download_terms")
def download_terms():

    flask_excel.init_excel(app)
    data = a.model.study_term.get_all_records()
    output = flask_excel.make_response_from_records(data, "csv")
    output.headers["Content-Disposition"] = "attachment; filename=my_terms.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/stats")
def stats():

    if not session.get("uid"):
        return render_template("login.html")

    recent_stats = a.model.daily_stats.DailyStats.get_recent(50)
    recent_stats = [
        {
            "dt": s.dt,
            "count_correct": s.count_correct,
            "count_incorrect": s.count_incorrect,
            "avg_knowledge_factor": s.avg_knowledge_factor,
            "num_terms": s.num_terms,
        }
        for s in recent_stats
        if s is not None
    ]
    return render_template("stats.html", recent_stats=recent_stats)


@app.route("/new", methods=["GET"])
def new():

    if not session.get("uid"):
        return render_template("login.html")

    return render_template("new.html")


@app.route("/story_time", methods=["GET", "POST"])
def story_time():

    if not session.get("uid"):
        return render_template("login.html")

    try:
        raw_story = request.form.get("story")
        story = a.controller.story.Story.build(raw_story)
    except Exception as e:
        flash(f"Could not successfully generate story. Error was '{str(e)}'", "bad")
        return render_template("new.html")

    return render_template("story_time.html", story=story)


@app.route("/select_words", methods=["GET", "POST"])
def select_words():

    if not session.get("uid"):
        return render_template("login.html")

    try:
        keyword = request.form.get("keyword")
        number = int(request.form.get("number"))
        if number > 5000:
            raise Exception("{number} is too many: try <5000.")
        words = [keyword] + a.controller.language.get_related_words(keyword, number)
    except Exception as e:
        flash(f"Could not successfully generate words. Error was '{str(e)}'", "bad")
        return render_template("new.html")

    return render_template("select_words.html", words=words)


@app.route("/save_terms", methods=["POST", "GET"])
def save_terms():

    if not session.get("uid"):
        return render_template("login.html")

    _reserved_keys = ["bulk_terms", "translated_term", "msg"]

    if not session.get("uid"):
        return render_template("login.html")

    try:
        terms = []
        term_dicts = []

        if request.form.get("translated_term"):
            terms.append(request.form.get("translated_term"))

        # look for selected keys from story_time or select_words
        form_keys = set(request.form.keys())
        for form_key in form_keys:

            if form_key in _reserved_keys:
                continue  # ignore

            elif _is_json(form_key):
                term_dict = json.loads(form_key)
                term_dicts.append(term_dict)

            # case of select_words
            else:
                terms.append(form_key)

        study_terms = a.controller.study_term.save(
            terms=terms,
            bulk_terms=request.form.get("bulk_terms"),
            term_dicts=term_dicts,
        )

    except Exception as e:
        flash(f"Did not successfully create your cards. Error was '{str(e)}'", "bad")
        return render_template("new.html")

    flash(f"Successfully added {len(study_terms)} terms.", "good")
    return redirect("/terms")


@app.route("/edit", methods=["GET"])
def edit():

    if not session.get("uid"):
        return render_template("login.html")

    study_term = a.model.study_term.StudyTerm.get_by_id(
        request.args.get("study_term_id_to_edit")
    )

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

    study_term = a.model.study_term.StudyTerm.get_by_id(
        request.args.get("study_term_id_to_delete")
    )

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
        study_term = a.model.study_term.StudyTerm.get_by_id(
            request.form.get("study_term_id_to_edit")
        )
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

    flashcard_stack = a.model.flashcard_stack.FlashcardStack.from_dicts(
        session.get("flashcard_stack", [])
    )

    # case of first load
    if request.method == "GET":
        new_card = flashcard_stack.pop_card()

        if not new_card:
            flash(
                f"No cards available for quizzing. Try adding more! If you just added some, they will be available in 2 minutes.",
                "good",
            )
            return render_template("new.html")

        session["current_card"] = new_card.to_dict()
        session["flashcard_stack"] = flashcard_stack.to_dicts()
        return render_template(
            "quiz.html", current_card=new_card, last_card=None, is_first_try=True
        )

    # else
    guess = request.form["guess"]
    last_card = a.model.flashcard.Flashcard.from_dict(session["current_card"])
    was_correct = last_card.is_correct_guess(guess)
    is_first_try = request.form.get("is_first_try") == "True"

    if was_correct:
        # only update knowledge factor after the first try
        if is_first_try:
            last_card.update_on_correct()

        current_card = flashcard_stack.pop_card()
    else:

        # only update knowledge factor after the first try
        if is_first_try:
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
        is_first_try=was_correct,
    )


@app.route("/chat", methods=["POST", "GET"])
def chat():

    if not session.get("uid"):
        return render_template("login.html")

    initial_prompt_story = a.controller.story.Story.build(
        a.controller.chatbot.INITIAL_PROMPT
    )
    initial_prompt_html = initial_prompt_story.to_dict()["terms_html"]
    initial_prompt_translation = initial_prompt_story.translation

    return render_template(
        "chat.html",
        initial_prompt_html=initial_prompt_html,
        initial_prompt_translation=initial_prompt_translation,
        is_debug_view=a.model.gating.is_feature_enabled("debug_view"),
    )


chatbot = a.controller.chatbot.ChatBot()


@app.route("/chatbot_response", methods=["GET", "POST"])
def chatbot_response():

    msg = request.form["msg"]
    response = chatbot.get_response(msg)
    story = a.controller.story.Story.build(response)
    return {
        "runningCost": chatbot.get_cost(),
        "story": story.to_dict(),
    }


def _is_json(maybe_json):
    try:
        json.loads(maybe_json)
    except ValueError as e:
        return False
    return True


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
