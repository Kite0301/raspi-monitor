const socket = io();
let isRecording = false;

const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const status = document.getElementById('status');
const recordingsList = document.getElementById('recordings-list');

recordBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);

function startRecording() {
    socket.emit('start_recording');
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    isRecording = true;
    updateStatus('録画中...', 'recording');
}

function stopRecording() {
    socket.emit('stop_recording');
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    isRecording = false;
    updateStatus('');
}

function updateStatus(message, className = '') {
    status.textContent = message;
    status.className = `status ${className}`;
}

socket.on('recording_started', (data) => {
    console.log('Recording started:', data.filename);
    updateStatus(`録画開始: ${data.filename}`, 'recording');
});

socket.on('recording_stopped', () => {
    console.log('Recording stopped');
    updateStatus('録画停止');
    setTimeout(() => updateStatus(''), 3000);
    loadRecordings();
});

socket.on('connect', () => {
    console.log('Connected to server');
    loadRecordings();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateStatus('サーバーとの接続が切れました', 'error');
});

function loadRecordings() {
    fetch('/api/recordings')
        .then(response => response.json())
        .then(recordings => {
            recordingsList.innerHTML = '';
            recordings.forEach(recording => {
                const item = document.createElement('div');
                item.className = 'recording-item';
                item.innerHTML = `
                    <span>${recording.name}</span>
                    <a href="/download/${recording.name}" download>ダウンロード</a>
                `;
                recordingsList.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error loading recordings:', error);
        });
}

window.addEventListener('beforeunload', () => {
    if (isRecording) {
        socket.emit('stop_recording');
    }
});