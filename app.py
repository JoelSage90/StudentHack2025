from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import secrets
import subprocess
import os
import speech_recognition as sr
from pydub import AudioSegment

app = Flask("__name__")
app.secret_key = str(secrets.token_hex(16))

# Google OAuth Configuration
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "290862607506-slg7lnrk4d28gk05e19ksqin7nllelfq.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="google_login",  
    scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
)
app.register_blueprint(google_bp, url_prefix="/login")

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)

# Define Models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
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
    id = db.Column(db.Integer, primary_key=True)
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
    language = db.Column(db.String(3), default="en")
    voice_speed = db.Column(db.Float, default=1)
    voice_type = db.Column(db.String(50), default="Albert")
    
    def __repr__(self):
        return f'<Setting {self.id}>'

class Reminders(db.Model):
    __tablename__ = "reminders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    info = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Reminder {self.id}>'

class Conversations(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    associate_id = db.Column(db.Integer, db.ForeignKey('associates.id'))
    conversation_text = db.Column(db.String(1000), nullable=False)
    summary = db.Column(db.String(1000), nullable=False)
    
    user = db.relationship('User', backref='conversations')
    associate = db.relationship('Associates', backref='conversations')

    def __repr__(self):
        return f'<Conversation {self.id}>'

# Routes
@app.route("/")
def index():
    return render_template("login_page.html")

@app.route("/home")
def home():
    return render_template("home_page.html")

@app.route("/profile_page")
def profile_page():
    return render_template("profile_page.html")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    user_info = google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    
    if user_info.ok:
        google_user = user_info.json()
        google_id = google_user["sub"]
        name = google_user["name"]

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(google_id=google_id, name=name)
            db.session.add(user)
            db.session.commit()

        session[1] = user.id
        return redirect(url_for('home'))
    else:
        return f"Failed to fetch user info from Google. Status code: {user_info.status_code}. Response: {user_info.text}"

@app.route("/process_conversation", methods=['POST'])
def process_conversation():
    try:
        conversation_text = request.json.get('conversation_text')
        associate_id = request.json.get('associate_id', None)
        
        if not conversation_text:
            return jsonify({'error': 'No conversation text provided'}), 400

        user_id = 1
        user = User.query.get(user_id)
        if not user:
            test_user = User(google_id="simulated_google_id", name="Test User")
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id

        try:
            summary = summarize_conversation(conversation_text)
        except Exception as e:
            summary = f"Simple summary of: {conversation_text[:50]}..."

        try:
            conversation = Conversations(
                user_id=user_id,
                associate_id=associate_id,
                conversation_text=conversation_text,
                summary=summary
            )
            db.session.add(conversation)
            db.session.commit()
            return jsonify({
                'success': True,
                'conversation_id': conversation.id,
                'summary': summary
            }), 200
        except Exception as db_error:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def summarize_conversation(conversation_text):
    try:
        process = subprocess.run(['deepseek-cli', '--version'], 
                                 capture_output=True, 
                                 timeout=2)
        process = subprocess.Popen(['deepseek-cli', '--summarize', conversation_text],
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=10)

        if stdout:
            return stdout.decode().strip()
        else:
            return "DeepSeek returned no summary."
    except (subprocess.SubprocessError, FileNotFoundError):
        words = conversation_text.split()
        if len(words) > 20:
            return " ".join(words[:20]) + "... (simple summary, DeepSeek unavailable)"
        return conversation_text

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    original_path = os.path.join(upload_dir, 'original_audio')
    converted_path = os.path.join(upload_dir, 'converted.wav')

    audio_file.save(original_path)

    try:
        audio = AudioSegment.from_file(original_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(converted_path, format="wav")
    except Exception as e:
        return jsonify({'error': 'Failed to convert audio. Make sure ffmpeg is installed.'}), 500

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(converted_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
            assistant_response = f"I heard: {transcription}"
            return jsonify({'transcription': transcription, 'response': assistant_response})
    except sr.UnknownValueError:
        return jsonify({'error': 'Unable to transcribe audio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/check_conversations", methods=['GET'])
def check_conversations():
    try:
        conversations = Conversations.query.order_by(Conversations.id.desc()).limit(5).all()
        result = []
        for conv in conversations:
            result.append({
                'id': conv.id,
                'user_id': conv.user_id,
                'associate_id': conv.associate_id,
                'conversation_text': conv.conversation_text[:50] + "...",
                'summary': conv.summary[:50] + "..."
            })
        return jsonify({
            'success': True,
            'count': len(result),
            'conversations': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    use_ssl = os.environ.get("USE_SSL", "false").lower() == "true"
    
    if use_ssl:
        app.run(debug=True, host='localhost', port=4000, ssl_context=('cert.crt', 'cert.key'))
    else:
        app.run(debug=True, host='localhost', port=4000)
