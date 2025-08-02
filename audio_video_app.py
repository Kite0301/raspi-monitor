from flask import Flask, Response, render_template_string
from flask_socketio import SocketIO
import cv2
import pyaudio
import threading
import time
import base64
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspi-audio-video-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
AUDIO_DEVICE_INDEX = 1  # hw:1,0 corresponds to device index 1

# Video settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 15

# Global variables
audio_stream = None
p = None
audio_thread = None
audio_running = False

def audio_stream_generator():
    global audio_stream, p, audio_running
    
    try:
        p = pyaudio.PyAudio()
        audio_stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=AUDIO_DEVICE_INDEX,
                            frames_per_buffer=CHUNK)
        
        audio_running = True
        print("Audio streaming started")
        
        while audio_running:
            try:
                data = audio_stream.read(CHUNK, exception_on_overflow=False)
                # Convert audio data to base64 for transmission
                audio_b64 = base64.b64encode(data).decode('utf-8')
                socketio.emit('audio_data', {'audio': audio_b64})
                time.sleep(0.01)  # Small delay to prevent overwhelming the connection
            except Exception as e:
                print(f"Audio streaming error: {e}")
                break
                
    except Exception as e:
        print(f"Audio initialization error: {e}")
    finally:
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        if p:
            p.terminate()
        print("Audio streaming stopped")

def generate_frames():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1.0 / VIDEO_FPS)
    finally:
        camera.release()

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raspberry Pi Camera & Audio Stream</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 20px;
                background-color: #f0f0f0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            img {
                border: 2px solid #ddd;
                border-radius: 10px;
                max-width: 100%;
                height: auto;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .status {
                margin: 20px 0;
                padding: 10px;
                background-color: #e8f5e9;
                border-radius: 5px;
                font-size: 14px;
            }
            .controls {
                margin: 20px 0;
            }
            button {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 0 5px;
            }
            button:hover {
                background-color: #45a049;
            }
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            #audioStatus {
                margin-top: 10px;
                font-size: 14px;
                color: #666;
            }
        </style>
        <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>Raspberry Pi Camera & Audio Live Stream</h1>
            
            <img src="/video_feed" alt="Live Camera Feed">
            
            <div class="controls">
                <button id="audioBtn" onclick="toggleAudio()">Enable Audio</button>
                <div id="audioStatus">Audio: Disabled</div>
            </div>
            
            <div class="status">
                <p>Video: 640x480 @ 15 FPS | Audio: 16kHz Mono</p>
                <p id="connectionStatus">Connecting...</p>
            </div>
        </div>
        
        <script>
            const socket = io();
            let audioContext;
            let audioEnabled = false;
            let isConnected = false;
            
            socket.on('connect', function() {
                document.getElementById('connectionStatus').textContent = 'Connected to server';
                document.getElementById('connectionStatus').style.color = 'green';
                isConnected = true;
            });
            
            socket.on('disconnect', function() {
                document.getElementById('connectionStatus').textContent = 'Disconnected from server';
                document.getElementById('connectionStatus').style.color = 'red';
                isConnected = false;
            });
            
            socket.on('audio_data', function(data) {
                if (audioEnabled && audioContext) {
                    try {
                        // Decode base64 audio data
                        const audioData = atob(data.audio);
                        const arrayBuffer = new ArrayBuffer(audioData.length);
                        const view = new Uint8Array(arrayBuffer);
                        
                        for (let i = 0; i < audioData.length; i++) {
                            view[i] = audioData.charCodeAt(i);
                        }
                        
                        // Convert to Float32Array for Web Audio API
                        const int16Array = new Int16Array(arrayBuffer);
                        const float32Array = new Float32Array(int16Array.length);
                        
                        for (let i = 0; i < int16Array.length; i++) {
                            float32Array[i] = int16Array[i] / 32768.0;
                        }
                        
                        // Create and play audio buffer
                        const audioBuffer = audioContext.createBuffer(1, float32Array.length, 16000);
                        audioBuffer.getChannelData(0).set(float32Array);
                        
                        const source = audioContext.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(audioContext.destination);
                        source.start();
                    } catch (error) {
                        console.error('Error playing audio:', error);
                    }
                }
            });
            
            function toggleAudio() {
                if (!audioEnabled) {
                    // Enable audio
                    if (!audioContext) {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    }
                    audioEnabled = true;
                    document.getElementById('audioBtn').textContent = 'Disable Audio';
                    document.getElementById('audioStatus').textContent = 'Audio: Enabled';
                    document.getElementById('audioStatus').style.color = 'green';
                    
                    // Request to start audio streaming
                    socket.emit('start_audio');
                } else {
                    // Disable audio
                    audioEnabled = false;
                    document.getElementById('audioBtn').textContent = 'Enable Audio';
                    document.getElementById('audioStatus').textContent = 'Audio: Disabled';
                    document.getElementById('audioStatus').style.color = '#666';
                    
                    // Request to stop audio streaming
                    socket.emit('stop_audio');
                }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('start_audio')
def handle_start_audio():
    global audio_thread, audio_running
    if not audio_running:
        audio_thread = threading.Thread(target=audio_stream_generator)
        audio_thread.daemon = True
        audio_thread.start()

@socketio.on('stop_audio')
def handle_stop_audio():
    global audio_running
    audio_running = False

if __name__ == '__main__':
    # Kill any existing Flask processes
    import os
    os.system("pkill -f 'python.*simple_app.py'")
    time.sleep(1)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)