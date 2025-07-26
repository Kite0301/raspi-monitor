#!/usr/bin/env python3
import sys
import os
import signal
import time
from datetime import datetime

# Add system OpenCV path for Raspberry Pi
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from flask import Flask, render_template, Response
import cv2
import threading

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')

class LightweightCameraManager:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.active = False
        
    def initialize_camera_v4l2(self):
        """Initialize camera with V4L2 backend explicitly"""
        try:
            print("Attempting V4L2 backend initialization...")
            # Force V4L2 backend
            self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
            
            if not self.camera.isOpened():
                print("V4L2 backend failed, trying default...")
                self.camera.release()
                self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("All backends failed")
                return False
            
            # Start with very low resolution
            print("Setting minimal resolution...")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.camera.set(cv2.CAP_PROP_FPS, 5)  # Very low FPS
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame with timeout
            print("Testing frame capture...")
            start_time = time.time()
            for i in range(3):  # Try 3 times
                ret, frame = self.camera.read()
                if ret:
                    print(f"Frame captured successfully on attempt {i+1}: {frame.shape}")
                    self.active = True
                    return True
                time.sleep(0.5)
                
                # Timeout after 5 seconds
                if time.time() - start_time > 5:
                    print("Frame capture timeout")
                    break
            
            print("Failed to capture test frame")
            self.camera.release()
            self.camera = None
            return False
            
        except Exception as e:
            print(f"Camera initialization error: {e}")
            if self.camera:
                self.camera.release()
                self.camera = None
            return False
    
    def get_frame_with_timeout(self, timeout=2):
        """Get frame with timeout to prevent hanging"""
        if not self.active or not self.camera:
            return None
            
        with self.lock:
            start_time = time.time()
            ret, frame = self.camera.read()
            
            if ret and time.time() - start_time < timeout:
                # Compress heavily for performance
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                return buffer.tobytes()
            return None
    
    def release(self):
        """Clean up camera resources"""
        with self.lock:
            if self.camera:
                print("Releasing camera...")
                self.camera.release()
                self.camera = None
                self.active = False

camera_manager = LightweightCameraManager()

def generate_test_frames():
    """Generate frames with built-in error handling"""
    print("Starting lightweight frame generation...")
    frame_count = 0
    error_count = 0
    
    try:
        while True and error_count < 10:  # Stop after 10 consecutive errors
            frame_bytes = camera_manager.get_frame_with_timeout()
            
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                frame_count += 1
                error_count = 0  # Reset error count on success
                
                if frame_count % 10 == 0:
                    print(f"Streamed {frame_count} frames successfully")
            else:
                error_count += 1
                print(f"Frame error #{error_count}")
                # Send status frame
                status_msg = f"Frame error #{error_count}/10"
                yield (b'--frame\r\n'
                       b'Content-Type: text/plain\r\n\r\n' + status_msg.encode() + b'\r\n')
                time.sleep(1)  # Wait longer on error
            
            time.sleep(0.2)  # 5 FPS max
            
    except Exception as e:
        print(f"Stream generation error: {e}")
    finally:
        print("Stream generation ended")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_camera')
def init_camera():
    """Initialize camera endpoint"""
    try:
        if camera_manager.initialize_camera_v4l2():
            return {"status": "success", "message": "Camera initialized with V4L2"}
        else:
            return {"status": "error", "message": "Camera initialization failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/video_feed')
def video_feed():
    """Lightweight video feed"""
    print("Video feed requested")
    
    if not camera_manager.active:
        print("Camera not initialized, attempting initialization...")
        if not camera_manager.initialize_camera_v4l2():
            return "Camera initialization failed", 500
    
    return Response(generate_test_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_info')
def camera_info():
    """Get camera information"""
    if camera_manager.camera and camera_manager.active:
        width = camera_manager.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = camera_manager.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = camera_manager.camera.get(cv2.CAP_PROP_FPS)
        return {
            "status": "active",
            "resolution": f"{int(width)}x{int(height)}",
            "fps": int(fps),
            "backend": camera_manager.camera.getBackendName()
        }
    return {"status": "inactive"}

def cleanup():
    """Cleanup on exit"""
    print("Cleaning up...")
    camera_manager.release()

# Register cleanup handler
signal.signal(signal.SIGTERM, lambda s, f: cleanup())
signal.signal(signal.SIGINT, lambda s, f: cleanup())

if __name__ == '__main__':
    print("Starting Lightweight Camera Test Server")
    print("Endpoints:")
    print("  / - Main page")
    print("  /init_camera - Initialize camera")
    print("  /video_feed - Video stream")
    print("  /camera_info - Camera status")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    finally:
        cleanup()