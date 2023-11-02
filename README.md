<p align="center">
  <img src="/static/nanotebook.png" alt="Nanotebook"/>
</p>

# Nanotebook

A reminder and notes app that one can access from anywhere.

Using Deta's free "mini cloud" and Flask, Nanotebook is a powerful application in which you can write completely confidential notes locked behind a password encrypted with SHA256.

---

# Deploying

Using PythonAnywhere's web feature, you can deploy your own instance of Nanotebook!

## Create a PythonAnywhere Account

Go to [PythonAnywhere](https://www.pythonanywhere.com) and create an account (just the basic one will do). If you need further explanation, this process is most likely too complex for you.

## PythonAnywhere Console

At the top, go to the `Consoles` tab and open a new `bash` console.

Run this command to get all the files from Nanotebook into your PythonAnywhere files: `git clone https://github.com/Anonymouseyy/nanotebook.git`

In the console, create a virtual environemnt named `nanotebook` using the following command: `mkvirtualenv nanotebook`.

Switch to your `nanotebook` directory using `cd nanotebook`

Install dependencies using `pip install -r requirements.txt`

## Create a Password

This is when you will create the password you will use to log into your instance of Nanotebook. You can also follow the below instructions to reset your password if you forget it.

Go to the `Consoles` tab and go into a `bash` console. Make sure you are in your Nanotebook directory.

Run `python generate_password.py`

It will prompt you for your desired password. Enter your desired password and press enter.

The console will print out something that starts with `pbkdf2:sha256`, this is your `sha256` encrypted password.

Go to your PythonAnywhere `Files`.

Enter the `nanotebook` directory at the left.

Open the file name `.env`

Paste your encrypted password after the `=` sign after the `password` parameter.

## Deta Setup

Go to [Deta](https://deta.space) and create an account.

At the bottom, click the Deta logo and hit settings. This should automatically open you up in the authentication menu.

In the authentication menu, create a new token by hitting generate token. Copy that token. When you close the tab, the token will not be shown again. If you lose it, create a new token.

Go back to PythonAnywhere and go to the `Files`  tab by hitting `Files` at the top.

Enter the `nanotebook` directory at the left.

Open the file name `.env`

Paste your Deta token after the `=` sign after the `API_KEY` parameter.

## PythonAnywhere Web Setup

Go to the `Web` tab on PythonAnywhere.

Create a new web app and press `next`. 

When asked for the framework, choose `flask`. 

When asked for the Python version, choose `Python 3.10`.

When asked to quick start, paste the following path: `/home/{your PythonAnywhere username}/nanotebook/main.py` into the path text box and press `next`. 

Scroll down to `Virtualenv:` and enter the following path: `/home/{your PythonAnywhere username}/.virtualenvs/nanotebook`

## Final Setup

Go back to the `Files` tab and got the the `main.py` file in the `nanotebook` directory.

Go into the main.py file in this repository and copy the code, paste it into the `main.py` file in your PythonAnywhere instance, replacing the code that was there. Hit save.

Go into the `Web` tab of PythonAnywhere and scroll to the code section. Click the link next to `WSGI configuration file:`. Copy and paste the below code into the top of that file.
```python
from dotenv import load_dotenv
import os
project_folder = os.path.expanduser('~/nanotebook')
load_dotenv(os.path.join(project_folder, '.env'))
```

Finally, go back to the `Web` tab, reload your site, and you should be able visit and use your own instance of `Nanotebook`!
