from flask import Flask, render_template, Response, request, send_file
from flask_socketio import SocketIO, emit
import cv2
import threading
import time
import os
from datetime import datetime
import base64

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SECRET_KEY'] = 'raspi-monitor-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class CameraManager:
    def __init__(self):
        self.camera = None
        self.recording = False
        self.video_writer = None
        self.lock = threading.Lock()
        
    def initialize_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
    
    def get_frame(self):
        if self.camera is None:
            self.initialize_camera()
        
        ret, frame = self.camera.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()
        return None
    
    def start_recording(self):
        with self.lock:
            if not self.recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recordings/video_{timestamp}.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
                self.recording = True
                return filename
        return None
    
    def stop_recording(self):
        with self.lock:
            if self.recording and self.video_writer:
                self.video_writer.release()
                self.recording = False
                return True
        return False
    
    def record_frame(self, frame):
        if self.recording and self.video_writer:
            self.video_writer.write(frame)

camera_manager = CameraManager()

def generate_frames():
    while True:
        frame_bytes = camera_manager.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('start_recording')
def handle_start_recording():
    filename = camera_manager.start_recording()
    if filename:
        emit('recording_started', {'filename': filename})

@socketio.on('stop_recording')
def handle_stop_recording():
    if camera_manager.stop_recording():
        emit('recording_stopped')

@app.route('/api/recordings')
def get_recordings():
    recordings_dir = 'recordings'
    recordings = []
    if os.path.exists(recordings_dir):
        for filename in os.listdir(recordings_dir):
            if filename.endswith(('.avi', '.mp4')):
                recordings.append({'name': filename})
    return recordings

@app.route('/download/<filename>')
def download_recording(filename):
    recordings_dir = 'recordings'
    filepath = os.path.join(recordings_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    os.makedirs('recordings', exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)