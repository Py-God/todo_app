from datetime import datetime, timedelta
from flask import redirect, session
from functools import wraps

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def date(input_date):
    formatted_date = datetime.strptime(input_date, "%Y-%m-%d").date()
    now = datetime.now().date()

    if now - formatted_date == timedelta(days=0):
        return "Today"
    elif now - formatted_date == timedelta(days=1):
        return "Yesterday"
    else:
        return input_date