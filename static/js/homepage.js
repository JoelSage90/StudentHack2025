let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;
let audio;
const recognizedTextElement = document.getElementById("recognized-text");
const assistantResponseElement = document.getElementById("assistant-response");
const slidingTextElement = document.getElementById("sliding-text");
const voiceIcon = document.getElementById("voice-icon"); // Reference to the voice icon button

// Function to start recording
function startRecording() {
    audioChunks = [];
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioUrl = URL.createObjectURL(audioBlob);
                audio = new Audio(audioUrl);
                audio.play();

                // Process the recorded audio (send it to your backend for transcription)
                sendAudioToBackend(audioBlob);
            };
            mediaRecorder.start();

            // Change button color to indicate recording (on)
            voiceIcon.style.backgroundColor = "#ff6347";  // Red color when recording
            voiceIcon.style.color = "#fff";  // White text for visibility
            document.getElementById("voice-text").textContent = "Recording...";
            voiceIcon.onclick = stopRecording;  // Change the function to stop recording
        })
        .catch(err => {
            console.log("Error accessing audio: ", err);
        });
}

// Function to stop recording
function stopRecording() {
    mediaRecorder.stop();
    
    // Update UI after stopping the recording
    document.getElementById("voice-text").textContent = "What can I help with?";
    voiceIcon.style.backgroundColor = "";  // Reset to normal color (default)
    voiceIcon.style.color = "";  // Reset text color
    voiceIcon.onclick = startRecording;  // Re-enable the start recording function
}

// Function to send recorded audio to the backend for processing (e.g., transcription)
function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('/process_audio', { 
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            recognizedTextElement.textContent = "You said: " + data.transcription;
            assistantResponseElement.textContent = "Assistant's response: " + data.response;

            // Make the sliding text appear and slide in with the transcription
            slidingTextElement.textContent = "You said: " + data.transcription;
            slidingTextElement.classList.add("slide-in");
            
            // NEW CODE: Send the transcription for processing and storing
            processConversation(data.transcription);
        }
    })
    .catch(error => {
        console.error("Error sending audio to backend:", error);
    });
}

// NEW FUNCTION: Process conversation and store in database
function processConversation(transcription, associateId = 1) {
    console.log("Processing conversation:", transcription);
    
    fetch('/process_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            conversation_text: transcription,
            associate_id: associateId  // Default to associate ID 1 or get from UI
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.status);
        }
        return response.json();
    })
    .then(summaryData => {
        console.log('Conversation processed successfully:', summaryData);
        
        // Display the summary
        assistantResponseElement.textContent = "Assistant's response: " + summaryData.summary;
            
        // Update the sliding text with the summary
        slidingTextElement.textContent = summaryData.summary;
        slidingTextElement.classList.remove("slide-in");
        // Trigger reflow
        void slidingTextElement.offsetWidth;
        slidingTextElement.classList.add("slide-in");
    })
    .catch(error => {
        console.error("Error processing conversation:", error);
        assistantResponseElement.textContent = "Error: Failed to process conversation";
    });
}

// If you have a function to handle clicking on profile/associate
function handleProfileClick(associateName) {
    // You might want to get the associate ID from the backend based on the name
    // For now, we'll just use a default ID of 1
    const associateId = 1;
    
    // You could display a prompt or activate voice recording here
    document.getElementById("voice-text").textContent = `What would you like to say to ${associateName}?`;
    
    // You might want to store the current associate ID in a variable
    // so it can be used when processing the conversation
    window.currentAssociateId = associateId;
}