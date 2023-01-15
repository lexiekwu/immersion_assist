from a.model import confirm_email
from flask_mail import Mail
import time


def test_send_email_confirmation_code_and_confirm_email(mocker):
    mock_send = mocker.patch("flask_mail.Mail.send")
    code = 123459
    email = "testley@gmail.com"
    mocker.patch("random.randrange", return_value=code)
    now = time.time()
    mocker.patch("time.time", return_value=now)
    fake_mailer = Mail()

    confirm_email.send_email_confirmation_code(email, fake_mailer)
    mock_send.assert_called_once()

    assert confirm_email.confirm_email(email, code)
    assert not confirm_email.confirm_email(email, code + 1)

    mocker.patch("time.time", return_value=now + 5 * 60 + 1)
    assert not confirm_email.confirm_email(email, code)
