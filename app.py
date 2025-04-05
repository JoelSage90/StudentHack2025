from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask("__name__")

@app.route("/")
def index():
    return render_template("login_page.html")

@app.route("/home")
def home():
    return render_template("home_page.html")

if __name__ == "__main__":
    app.run(debug=True)