from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask("__name__")

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

@app.route("/home")
def home():
    return render_template("home_page.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)