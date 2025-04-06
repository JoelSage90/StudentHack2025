let context, analyser, dataArray, source;
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

const micCircle = document.getElementById('mic-circle');
const voiceText = document.getElementById('voice-text');
const recognizedTextElement = document.getElementById("recognized-text");
const assistantResponseElement = document.getElementById("assistant-response");
const slidingTextElement = document.getElementById("sliding-text");

function animate() {
    if (!isRecording || !analyser) return;

    analyser.getByteTimeDomainData(dataArray);
    const amplitude = Math.max(...dataArray) - 128;
    const scale = 1 + amplitude / 50;
    micCircle.style.transform = `scale(${scale})`;

    requestAnimationFrame(animate);
}

async function toggleRecording() {
  console.log("Mic clicked"); // ✅ Use this to test if click is working
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        context = new (window.AudioContext || window.webkitAudioContext)();

        if (context.state === 'suspended') await context.resume();

        // Visualization setup
        source = context.createMediaStreamSource(stream);
        analyser = context.createAnalyser();
        analyser.fftSize = 2048;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        source.connect(analyser);

        // Recording setup
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudioToBackend(audioBlob);

            // Clean up
            stream.getTracks().forEach(track => track.stop());
            if (context) context.close();
        };

        mediaRecorder.start();
        isRecording = true;
        voiceText.textContent = 'Listening...';
        animate();
    } catch (err) {
        console.error('Microphone error:', err);
        alert('Please allow microphone access');
    }
}

function stopRecording() {
    if (!isRecording) return;
    mediaRecorder.stop();
    isRecording = false;
    voiceText.textContent = 'Tap to start listening...';
    micCircle.style.transform = 'scale(1)';
}

function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    fetch('/process_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            recognizedTextElement.textContent = "You said: " + data.transcription;
            assistantResponseElement.textContent = "Assistant's response: " + data.response;

            slidingTextElement.textContent = data.transcription;
            slidingTextElement.classList.remove("slide-in");
            void slidingTextElement.offsetWidth;
            slidingTextElement.classList.add("slide-in");

            processConversation(data.transcription, window.currentAssociateId || 1);
        }
    })
    .catch(error => {
        console.error('Error processing audio:', error);
        assistantResponseElement.textContent = "Error: Failed to transcribe";
    });
}

function processConversation(transcription, associateId = 1) {
    fetch('/process_conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            conversation_text: transcription,
            associate_id: associateId
        })
    })
    .then(response => response.json())
    .then(data => {
        assistantResponseElement.textContent = "Assistant's response: " + data.summary;

        slidingTextElement.textContent = data.summary;
        slidingTextElement.classList.remove("slide-in");
        void slidingTextElement.offsetWidth;
        slidingTextElement.classList.add("slide-in");
    })
    .catch(err => {
        console.error("Error processing conversation:", err);
        assistantResponseElement.textContent = "Error: Failed to process conversation";
    });
}

// Handle associate profile clicks
function handleProfileClick(associateName) {
    window.currentAssociateId = 1; // Can dynamically map name to ID
    voiceText.textContent = `What would you like to say to ${associateName}?`;
}

async function fetchRelationships() {
try {
    const response = await fetch('/get_relationships');
    const data = await response.json();
    const dropdown = document.getElementById('relationship-dropdown');

    data.relationships.forEach(rel => {
        const option = document.createElement('option');
        option.value = rel.id;
        option.textContent = rel.name;
        dropdown.appendChild(option);
    });

    dropdown.addEventListener('change', () => {
        const selectedId = dropdown.value;
        const selectedName = dropdown.options[dropdown.selectedIndex].text;
        window.currentAssociateId = parseInt(selectedId, 10);
        voiceText.textContent = `What would you like to ask ${selectedName}?`;
    });
} catch (err) {
    console.error('Failed to fetch relationships:', err);
}}



document.addEventListener('DOMContentLoaded', () => {
    const micCircle = document.getElementById('mic-circle');
    if (micCircle) {
        micCircle.addEventListener('click', toggleRecording);
    }
    
    fetchRelationships(); // <-- Add this
    });
