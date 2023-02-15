import os
import urllib.parse
from deta import Deta

from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

deta = Deta(os.environ.get('API_KEY'))
notes = deta.Base('notes')
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
    return notes.fetch().items


def create_file(filename, path, content):
    try:
        result = drive.put(f"{path}/{filename}", content)
        return result
    except Exception as e:
        apology(e)


def create_note(name, description):
    file_name = name
    invalid_chars = ["#", "<", "$", "+", "%", ">", "!", "`", "&", "*", "'",
                     '"', "|", "{", "}", "?", "=", "/", ":", "\"", " ", "@"]

    for char in invalid_chars:
        file_name = file_name.replace(char, "_")

    try:
        create_file(f"{name}.txt", r"./notes", "Note")
        notes.put(data={"description": description, "file": f"./notes/{name}.txt"}, key=name)
        return 1
    except Exception as e:
        apology(e)


