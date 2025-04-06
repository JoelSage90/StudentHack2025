from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import secrets
import requests
import os
from pydub import AudioSegment
import whisper
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

model = whisper.load_model("base")  # You can change this to a larger model if needed

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
        return f'User {self.id}'

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

@app.route("/conversations")
def conversations():
    return render_template("conversations.html")

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

        session['user_id'] = user.id
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
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        prompt = f"Summarize this conversation (under 50 words): {conversation_text}"
        data = {
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False
        }


        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            full_response = str(response_json.get("response", ""))
            # Remove <think> tags
            full_response = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL).strip()
            return full_response
        else:
            response.raise_for_status()
        
    except Exception as e:
        print(f"Error with Ollama: {str(e)}")
        return "Error occurred while summarizing."

@app.route("/process_audio", methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    # Define directories for saving the uploaded and converted audio files
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Paths for the original and converted audio
    original_path = os.path.join(upload_dir, 'original_audio')
    converted_path = os.path.join(upload_dir, 'converted.wav')

    # Save the uploaded audio file to the original path
    audio_file.save(original_path)

    try:
        print("Converting audio to WAV...")  # Debug statement
        # Convert the uploaded audio to WAV format (single channel and 16 kHz sample rate)
        audio = AudioSegment.from_file(original_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(converted_path, format="wav")
        print(f"Audio saved at: {converted_path}")  # Debug statement
    except Exception as e:
        print(f"Error converting audio: {str(e)}")  # Debug statement
        return jsonify({'error': f'Failed to convert audio: {str(e)}'}), 500

    try:
        print("Loading Whisper model...")  # Debug statement
        # Transcribe the converted audio file using Whisper
        result = model.transcribe(converted_path)

        # Get the transcription text
        transcription = result["text"]
        print(f"Full transcription: {transcription}")  # Print the full transcription in the terminal

        # Create a response (you can adjust this as needed)
        assistant_response = f"I heard: {transcription}"
        return jsonify({'transcription': transcription, 'response': assistant_response})
    except Exception as e:
        print(f"Error during transcription: {str(e)}")  # Debug statement
        return jsonify({'error': f'Whisper transcription failed: {str(e)}'}), 500



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