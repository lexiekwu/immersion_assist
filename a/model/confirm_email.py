from a.third_party import cockroachdb as db
import random
import bcrypt
import time
from os import environ
from flask_mail import Message, Mail


def send_email_confirmation_code(email, mailer: Mail):
    code = random.randrange(100000, 999999)
    expiry_time = int(time.time()) + 60 * 5  # 5 minutes
    hashed_code = bcrypt.hashpw(str(code).encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    db.sql_update(
        f"""
        UPSERT INTO email_confirmation (email, hashed_code, expiry_time)
        VALUES ('{email}', '{hashed_code}', {expiry_time})
        """
    )
    _send_confirmation_email(email, code, mailer)


def confirm_email(email, code):
    code = int(code)
    email_confirmation = db.sql_query_single(
        f"""
        SELECT *
        FROM email_confirmation
        WHERE email = '{email}'
        """
    )
    if not email_confirmation:
        return False
    hashed_code = email_confirmation["hashed_code"]
    expiry_time = email_confirmation["expiry_time"]
    if not bcrypt.checkpw(str(code).encode("utf-8"), hashed_code.encode("utf-8")):
        return False
    if int(time.time()) > expiry_time:
        return False
    return True


def _send_confirmation_email(email, code, mailer: Mail):
    msg = Message(
        "Immersion Assist - Confirm your email",
        sender=environ.get("GMAIL_USER"),
        recipients=[email],
        html=f"""
        <h1>Welcome to Immersion Assist!</h1>
        <p>Use this code to confirm your email: </p>
        <h2> {code} </h2>
    """,
    )
    mailer.send(msg)
