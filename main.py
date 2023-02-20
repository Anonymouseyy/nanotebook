import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

from helpers import apology, login_required, get_all_notes, create_file, create_note

# Configure application
app = Flask(__name__)
load_dotenv()

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
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Home Page"""

    return render_template("index.html", notes=get_all_notes())


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create new items"""
    if request.method == "POST":
        if not request.form.get("name") and not request.form.get("desc"):
            return apology("must have name and description")

        if create_note(request.form.get("name"), request.form.get("desc")):
            flash(f"{request.form.get('name')} successfully created!")
            return redirect("/")

    return render_template("create.html")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        note = request.args.get('note')
        flash(note)
        return redirect("/")


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
        if not check_password_hash(os.environ.get('password'), request.form.get("password")):
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
