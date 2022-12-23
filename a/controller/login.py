import a


def try_login(email, password):
    # check if exists, if not, send to signup
    user = a.model.user.User.get_by_email(email)
    if not user:
        return (False, False)

    # incorrect password, try again
    if not user.is_correct_password(password):
        return (True, False)

    # correct password, log in
    a.third_party.session_storage.update({"uid": user.uid, "name": user.name})

    return (True, True)
