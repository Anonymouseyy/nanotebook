import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from jinja2.utils import markupsafe
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from deta_tools import detaBase

from helpers import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()
API_KEY = os.environ.get("API_KEY")
notes = detaBase(API_KEY, "notes")
dates = detaBase(API_KEY, "dates")
drive = detaDrive(API_KEY, "mydrive")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Home Page"""

    return render_template("index.html", notes=notes.query()["items"])


@app.route("/create/note", methods=["GET", "POST"])
@login_required
def createnote():
    """Create new items"""
    if request.method == "POST":
        if not request.form.get("name") and not request.form.get("desc"):

            return apology("must have name and description")

        if create_note(request.form.get("name"), request.form.get("desc")):
            flash(f"{request.form.get('name')} successfully created!")
            return redirect("/")
        else:
            return apology("an unexpected error occurred")

    return render_template("create.html")


@app.route("/delete/note", methods=["POST"])
@login_required
def delete_note():
    note = request.form.get("note")

    item = notes.get(note)
    drive.delete([item["file"]])
    notes.delete(note)

    return redirect("/")


@app.route("/edit/note", methods=["GET", "POST"])
@login_required
def edit_note():
    if request.method == "GET":
        note = request.args.get("note")
        item = notes.get(note)
        content = get_file(item["file"]).decode()

        text = markupsafe.Markup(content)
        text = text.replace('<form>', '&lt;form&gt;').replace('</form>', '&lt;/form&gt;')
        text = text.replace('<script>', '&lt;script&gt;').replace('</script>', '&lt;/script&gt;')

        return render_template("editor.html", note=item, content=text)

    if request.method == "POST":
        data = request.get_json()

        if data[0]["key"] == data[1]["name"]:
            item = notes.get(data[0]["key"])
            if item["description"] == data[2]["description"]:
                pass
            else:
                notes.update(data[0]["key"], {"description": data[2]["description"]})

            file_name = filename(data[0]["key"])
            create_file(f"{file_name}.txt", r"./notes", data[3]["content"])

            return jsonify({"res": "success"})
        else:
            create_note(data[1]["name"], data[2]["description"])
            file_name = filename(data[1]["name"])
            create_file(f"{file_name}.txt", r"./notes", data[3]["content"])

            item = notes.get(data[0]["key"])
            notes.delete(data[0]["key"])
            drive.delete([item["file"]])
            
            return jsonify({"res": "renamed"})


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password is correct
        if not check_password_hash(os.environ.get("password"), request.form.get("password")):
            return apology("Password is incorrect", 400)

        # Remember which user has logged in
        session["user_id"] = 1

        flash("Successfully Logged In")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("Successfully logged out")

    return redirect("/login")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
