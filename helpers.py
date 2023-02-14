import os
import urllib.parse
from deta import Deta

from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

deta = Deta(os.environ.get('API_KEY'))
db = deta.Base('notes')
drive = deta.Drive("mydrive")


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_all_notes():
    return db.fetch().items


def create_note_file(filename, content):
    try:
        result = drive.put(f"./notes/{filename}.html", content)
        return result
    except Exception as e:
        apology(e)

