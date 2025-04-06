let isRecording = false;

function toggleRecording() {
  const btn = document.querySelector('.record-btn');
  isRecording = !isRecording;
  if (isRecording) {
    btn.classList.add('recording');
    btn.textContent = '⏺️ Recording...';
    console.log('Recording started');
    // Add actual audio recording logic here
  } else {
    btn.classList.remove('recording');
    btn.textContent = '🎤';
    console.log('Recording stopped');
    // Stop audio recording logic
  }
}

function selectUser(name) {
  document.getElementById('currentUser').textContent = name;
}

function addUser() {
  const name = prompt("Enter new user's name:");
  if (name) {
    const btn = document.createElement('button');
    btn.textContent = name;
    btn.onclick = () => selectUser(name);
    document.querySelector('.sidebar nav').appendChild(btn);
  }
}
