from flask import Flask, render_template, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask("__name__")
app.secret_key = str(secrets.token_hex(16))

#google login api stuff
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "290862607506-slg7lnrk4d28gk05e19ksqin7nllelfq.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="google_login",  
    scope=["profile", "email"],  
)
app.register_blueprint(google_bp, url_prefix="/login")

#patterning the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    bio = db.Column(db.String(500))
    associates = db.relationship('Associates', backref='user', lazy=True)
    settings = db.relationship('Settings', backref='user', uselist=False)
    reminders = db.relationship('Reminders', backref='user', lazy=True)
    def __repr__(self):
        return f'<User {self.id}>'

class Associates(db.Model):
    __tablename__ = "associates"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(500))
    voice_id = db.Column(db.String(50))
    relation_to_user = db.Column(db.String(50))

    def __repr__(self):
        return f'<Associates {self.id}>'



class Settings(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    language = db.Column(db.String(3), default = "en")
    voice_speed = db.Column(db.Float, default = 1)
    voice_type = db.Column(db.String(50),default = "Albert")
    def __repr__(self):
        return f'<setting {self.id}>'
    
class Reminders(db.Model):
    __tablename__ = "reminders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    info = db.Column(db.String(200),nullable = False)
    complete = db.Column(db.Boolean, default = False)
    def __repr__(self):
        return f'<Reminder {self.id}>'

#app routing and that
@app.route("/")
def index():
    return render_template("login_page.html")

@app.route("/home", methods = ["POST", "GET"])
def home():
    return render_template("home_page.html")
@app.route("/profile_page", methods = ["POST", "GET"])
def home():
    return render_template("progile_page.html")

#google login stuff
@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    # Fetch user info from Google
    user_info = google.get("/plus/v1/people/me")
    
    # Ensure the request was successful
    if user_info.ok:
        google_user = user_info.json()
        google_id = google_user["id"]
        name = google_user["displayName"]

        # Check if the user already exists in the database
        user = User.query.filter_by(google_id=google_id).first()
        if not user:

            user = User(google_id=google_id, name=name)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        
        return redirect(url_for('home'))
    else:
        return 'Failed to fetch user info from Google.'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='localhost', port=4000,ssl_context=('cert.crt', 'cert.key'))