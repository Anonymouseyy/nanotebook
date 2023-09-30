import os
from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv
from deta_tools import detaBase, detaDrive

load_dotenv()
API_KEY = os.environ.get("API_KEY")

notes = detaBase(API_KEY, "notes")
drive = detaDrive(API_KEY, "mydrive")


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


def filename(name):
    '''
    Returns a valid file name by escaping all invalid characters in a file name
    :param name: str
        Name of the file
    :return: str
        Name of the valid file name
    '''
    file_name = name
    invalid_chars = ["#", "<", "$", "+", "%", ">", "!", "`", "&", "*", "'",
                     '"', "|", "{", "}", "?", "=", "/", ":", "\"", " ", "@"]

    for char in invalid_chars:
        file_name = file_name.replace(char, "_")

    return file_name


def create_file(filename, path, content):
    '''
    Creates a file with a name, path, and content
    :param filename: str
        The name of the file to be created
    :param path: str
        The path of the file, folders to be seperate by /
    :param content: anything
        The content of the file
    :return:
        The file name if successful, otherwise redirects to apology
    '''
    try:
        drive.put(f"{path}/{filename}", content=content)
        return 1
    except Exception as e:
        return 0


def create_note(name, description):
    '''
    Creates a note with the given name and description
    :param name: str
        The name of the note
    :param description: str
        The description of the note
    :return: int
        Returns 1 if successful, otherwise returns apology
    '''
    file_name = filename(name)

    try:
        def_data = """
        {
            "ops": [
                {       
                    "insert": "Compose something epicc"
                }
            ]
        }"""
        if not create_file(f"{file_name}.json", r"./notes", def_data):
            return 0
        notes.put(data={"description": description, "file": f"./notes/{file_name}.json"}, keys=name)
        return 1
    except Exception as e:
        return 0


def get_file(name, return_type="str"):
    '''
    Get a file from the deta database
    :param name: str
        The name of the file including its path
    :param return_type:
        The type of return it should return, either a string of the bytes, or the path to a file where the file was put
    :return:
        A string of bytes or a file path
    '''
    res = drive.get(name)
    if return_type == "str":
        return res
    else:
        with open(f"tempfile.{os.path.splitext(res)[-1]}", "wb+") as f:
            for chunk in res.iter_chunks(4096):
                f.write(chunk)
            res.close()
        return f"tempfile.{os.path.splitext(f)[-1]}"

