# EchoSphere 🧠🔊

> *Your voice, their memories. Helping Alzheimer's patients connect through meaningful, voice-based conversations.*

---

## 🧪 Status: Work in Progress

EchoSphere was built as part of a StudentHack2025 submission. While still in development, it showcases core features that aim to assist users with memory-related conditions using voice-driven interactions, personalized context, and reminders.

---

## 💡 Inspiration

Watching someone struggle to recall the people and moments that shaped their life is heartbreaking. We wanted to build a tool that makes those reconnections easier — especially through voice, which can often trigger emotional memory even when words don't.

---

## 🚀 What It Does

- Users log in with Google
- Create a profile and list important people in their lives
- Add and manage reminders
- Record voice conversations and get real-time transcription
- Summarize conversations to keep memory "snapshots"
- (In Progress): AI-powered speech-to-speech chatbot for ongoing support

---

## 🛠 How We Built It

- **Flask** backend + **SQLAlchemy** for user management and data
- **Google OAuth** for secure login
- **Whisper** for speech-to-text transcription
- **Ollama** (or local LLM) for summarizing conversations
- **Frontend**: HTML/CSS/JS (Flask templates)
- **Context memory system** for feeding relevant info into conversations
- **Chatbot Engine** using custom `SpeechToSpeechChatbot` class

---

## 😅 Challenges

- Handling audio formats and converting reliably for Whisper
- Keeping context memory accurate and fresh
- Summarizing conversations in a way that feels human and helpful
- Voice output pipeline is still under construction!

---

## ✅ Accomplishments We're Proud Of

- Recording and transcribing audio from browser
- Saving and summarizing conversations
- Clean UI design that’s accessible to seniors

---

## 📚 What We Learned

- Handling async audio and file uploads can be tricky!
- Flask + SQLAlchemy is super flexible for quick prototypes
- Whisper is surprisingly accurate — and fast — for a local solution
- Building for accessibility forces you to think deeper

---

## 🔮 What's Next
- Finish speech-to-speech chatbot pipeline
- Add more personalization (tones, personalities)
- Export conversation memory logs to caregivers
- Mobile optimization + offline functionality
- Error handling + polish for production readiness

---

## 📸 Screenshots

<!-- Paste your screenshots here -->
![Login Page]<img width="1440" alt="Screenshot 2025-04-09 at 00 51 53" src="https://github.com/user-attachments/assets/f7f1f38b-2efa-41e1-924c-65fb6e73a8b5" />

![Home Page](<img width="1440" alt="Screenshot 2025-04-09 at 00 53 34" src="https://github.com/user-attachments/assets/69ae55b9-177a-4fd6-8d0c-fc8354c99971" />

![Relationship-Simulating Agent]<img width="1440" alt="Screenshot 2025-04-09 at 00 53 52" src="https://github.com/user-attachments/assets/e5d42fb1-6d58-4cb9-b938-48b0e1bf6691" />

![Relations list database]<img width="1440" alt="Screenshot 2025-04-09 at 00 54 13" src="https://github.com/user-attachments/assets/6e403d8f-7e8a-416a-9389-47d1858ee94f" />



---

## 🛠 Installation (WIP)

```bash
git clone https://github.com/JoelSage90/StudentHack2025.git
cd StudentHack2025
pip install -r requirements.txt
flask run
