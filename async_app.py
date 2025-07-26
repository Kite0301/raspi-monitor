#!/usr/bin/env python3
import sys
import os

# Add system OpenCV path for Raspberry Pi
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from flask import Flask, render_template, Response, request
import cv2
import threading
import time
from datetime import datetime

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SECRET_KEY'] = 'raspi-monitor-async'

class OptimizedCameraManager:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.active_clients = 0
        self.frame_cache = None
        self.last_frame_time = 0
        self.frame_rate_limit = 0.1  # 10 FPS max
        
    def initialize_camera(self):
        """Initialize camera only when needed"""
        if self.camera is None:
            try:
                print("Initializing camera...")
                self.camera = cv2.VideoCapture(0)
                
                # Check if camera opened successfully
                if not self.camera.isOpened():
                    print("Failed to open camera device")
                    self.camera.release()
                    self.camera = None
                    return False
                
                # Optimize settings for Raspberry Pi
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # Reduced resolution
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                self.camera.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
                
                # Test frame capture
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to capture test frame")
                    self.camera.release()
                    self.camera = None
                    return False
                    
                print(f"Camera initialized successfully - Resolution: {frame.shape}")
                return True
            except Exception as e:
                print(f"Camera initialization failed: {e}")
                if self.camera:
                    self.camera.release()
                    self.camera = None
                return False
        return True
    
    def get_frame(self):
        """Get frame with rate limiting and caching"""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_frame_time < self.frame_rate_limit:
            if self.frame_cache is not None:
                return self.frame_cache
        
        with self.lock:
            if not self.initialize_camera():
                return None
                
            ret, frame = self.camera.read()
            if ret:
                # Resize frame for better performance
                frame = cv2.resize(frame, (480, 360))
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                self.frame_cache = buffer.tobytes()
                self.last_frame_time = current_time
                return self.frame_cache
            return None
    
    def add_client(self):
        """Register a new streaming client"""
        with self.lock:
            self.active_clients += 1
            print(f"Client connected. Active clients: {self.active_clients}")
    
    def remove_client(self):
        """Unregister a streaming client"""
        with self.lock:
            self.active_clients = max(0, self.active_clients - 1)
            print(f"Client disconnected. Active clients: {self.active_clients}")
            
            # Release camera if no active clients
            if self.active_clients == 0 and self.camera is not None:
                print("Releasing camera - no active clients")
                self.camera.release()
                self.camera = None
                self.frame_cache = None

camera_manager = OptimizedCameraManager()

def generate_frames():
    """Generate video frames for streaming"""
    camera_manager.add_client()
    print("Starting video stream generation")
    
    try:
        frame_count = 0
        while True:
            frame_bytes = camera_manager.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                frame_count += 1
                if frame_count % 50 == 0:  # Log every 50 frames
                    print(f"Streamed {frame_count} frames")
            else:
                print("Failed to get frame from camera")
                # Send error frame
                error_msg = b'Camera initialization failed or unavailable'
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + error_msg + b'\r\n')
                time.sleep(1)  # Wait longer on error
            time.sleep(0.1)  # 10 FPS
    except GeneratorExit:
        print("Video stream ended by client")
    except Exception as e:
        print(f"Error in video stream: {e}")
    finally:
        print("Cleaning up video stream resources")
        camera_manager.remove_client()

@app.route('/')
def index():
    """Main page - loads quickly without video"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint - only loads when requested"""
    print("Video feed endpoint accessed")
    try:
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in video_feed: {e}")
        return f"Video feed error: {e}", 500

@app.route('/test_camera')
def test_camera():
    """Test camera initialization without streaming"""
    try:
        if camera_manager.initialize_camera():
            return {"status": "success", "message": "Camera initialized successfully"}
        else:
            return {"status": "error", "message": "Camera initialization failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/camera_status')
def camera_status():
    """Check camera availability without initializing it"""
    try:
        # Quick check for camera device
        camera_available = os.path.exists('/dev/video0')
        return {
            'status': 'available' if camera_available else 'unavailable',
            'active_clients': camera_manager.active_clients,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@app.route('/system_status')
def system_status():
    """System information endpoint"""
    return {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'server': 'Raspberry Pi Async Video Server',
        'active_video_clients': camera_manager.active_clients
    }

if __name__ == '__main__':
    print("Starting Raspberry Pi Async Video Monitor on port 5001")
    print("Page loads fast, video streams only when requested")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)