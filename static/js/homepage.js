let mediaRecorder;
let audioChunks = [];

const recognizedTextElement = document.getElementById("recognized-text");
const assistantResponseElement = document.getElementById("assistant-response");
const slidingTextElement = document.getElementById("sliding-text");
const voiceIcon = document.getElementById("voice-icon");
const voiceText = document.getElementById("voice-text");

// Start recording audio
function startRecording() {
    audioChunks = [];
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = handleRecordingStop;
            mediaRecorder.start();

            // Update UI
            voiceIcon.classList.add("listening");
            voiceText.textContent = "Recording...";
            voiceIcon.onclick = stopRecording;
        })
        .catch(err => console.error("Audio access error:", err));
}

// Stop recording audio
function stopRecording() {
    mediaRecorder.stop();

    // Update UI
    voiceIcon.classList.remove("listening");
    voiceText.textContent = "What can I help with?";
    voiceIcon.onclick = startRecording;
}

// Handle what happens when recording stops
function handleRecordingStop() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
    sendAudioToBackend(audioBlob);
}

// Send audio blob to the backend
function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('/process_audio', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.transcription) {
                recognizedTextElement.textContent = "You said: " + data.transcription;
                assistantResponseElement.textContent = "Assistant's response: " + data.response;

                slidingTextElement.textContent = "You said: " + data.transcription;
                slidingTextElement.classList.add("slide-in");

                processConversation(data.transcription, window.currentAssociateId || 1);
            }
        })
        .catch(err => {
            console.error("Error sending audio:", err);
        });
}

// Send conversation text to backend for summarization/storage
function processConversation(transcription, associateId = 1) {
    fetch('/process_conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            conversation_text: transcription,
            associate_id: associateId
        })
    })
        .then(res => res.json())
        .then(data => {
            assistantResponseElement.textContent = data.summary;
            slidingTextElement.textContent = data.summary;

            // Restart animation
            slidingTextElement.classList.remove("slide-in");
            void slidingTextElement.offsetWidth;
            slidingTextElement.classList.add("slide-in");
        })
        .catch(err => {
            console.error("Error processing conversation:", err);
            assistantResponseElement.textContent = "Error: Failed to process conversation";
        });
}

// Update the prompt text based on profile clicked
function handleProfileClick(associateName) {
    window.currentAssociateId = 1; // Placeholder logic
    voiceText.textContent = `What would you like to say to ${associateName}?`;
}

// Todo list functionality
const inputBox = document.getElementById("input-box");
const listContainer = document.getElementById("list-container");

function AddTask() {
    if (inputBox.value.trim() === '') {
        alert("You must write something");
        return;
    }

    const li = document.createElement("li");
    li.textContent = inputBox.value;
    listContainer.appendChild(li);
    inputBox.value = '';
    saveData();
}

listContainer.addEventListener("click", function (e) {
    if (e.target.tagName === "LI") {
        e.target.classList.toggle("checked");

        if (e.target.classList.contains("checked")) {
            e.target.style.transition = "opacity 1s ease, height 1s ease, padding 1s ease, margin 1s ease";

            setTimeout(() => {
                e.target.style.opacity = "0";
                e.target.style.height = "0";
                e.target.style.padding = "0";
                e.target.style.margin = "0";

                setTimeout(() => {
                    e.target.remove();
                    saveData();
                }, 1000);
            }, 500);
            
        } else {
            saveData();
        }
    }
});

// Save todo list
function saveData() {
    localStorage.setItem("todoData", listContainer.innerHTML);
}

// Load todo list
function showTasks() {
    listContainer.innerHTML = localStorage.getItem("todoData") || "";
}

// Enable Enter key to add tasks
inputBox.addEventListener("keypress", function (event) {
    if (event.key === "Enter") AddTask();
});

// Load tasks on page load
showTasks();
