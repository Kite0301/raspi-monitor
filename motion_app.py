#!/usr/bin/env python3
from flask import Flask, render_template, Response, request, jsonify
import subprocess
import os
import time
import requests
from datetime import datetime
import signal
import threading

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')

class MotionManager:
    def __init__(self):
        self.motion_process = None
        self.is_running = False
        self.stream_url = "http://localhost:8081"
        self.control_url = "http://localhost:8080"
        
    def start_motion(self):
        """Start motion service"""
        try:
            if self.is_running:
                return True, "Motion is already running"
            
            print("Starting motion service...")
            
            # Stop any existing motion process
            subprocess.run(["sudo", "systemctl", "stop", "motion"], 
                         capture_output=True, check=False)
            time.sleep(2)
            
            # Start motion with our config
            config_path = "/home/pi/raspi-monitor/motion.conf"
            self.motion_process = subprocess.Popen([
                "motion", "-c", config_path, "-n"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for motion to initialize
            time.sleep(5)
            
            # Check if motion is responding
            for i in range(10):  # Try for 10 seconds
                try:
                    response = requests.get(f"{self.stream_url}", timeout=2)
                    if response.status_code == 200:
                        self.is_running = True
                        print("Motion started successfully")
                        return True, "Motion started successfully"
                except:
                    time.sleep(1)
            
            print("Motion failed to start properly")
            return False, "Motion failed to start"
            
        except Exception as e:
            print(f"Error starting motion: {e}")
            return False, f"Error: {e}"
    
    def stop_motion(self):
        """Stop motion service"""
        try:
            print("Stopping motion service...")
            
            if self.motion_process:
                self.motion_process.terminate()
                time.sleep(2)
                if self.motion_process.poll() is None:
                    self.motion_process.kill()
                    
            # Also stop systemd service
            subprocess.run(["sudo", "systemctl", "stop", "motion"], 
                         capture_output=True, check=False)
            
            self.is_running = False
            self.motion_process = None
            return True, "Motion stopped successfully"
            
        except Exception as e:
            print(f"Error stopping motion: {e}")
            return False, f"Error: {e}"
    
    def get_status(self):
        """Get motion status"""
        try:
            if not self.is_running:
                return {"status": "stopped", "stream_available": False}
            
            # Check if stream is accessible
            response = requests.get(f"{self.stream_url}", timeout=2)
            stream_available = response.status_code == 200
            
            return {
                "status": "running",
                "stream_available": stream_available,
                "stream_url": self.stream_url,
                "control_url": self.control_url
            }
        except:
            return {"status": "error", "stream_available": False}

motion_manager = MotionManager()

@app.route('/')
def index():
    """Main page with motion integration"""
    return render_template('motion_index.html')

@app.route('/motion/start', methods=['POST'])
def start_motion():
    """Start motion service"""
    success, message = motion_manager.start_motion()
    return jsonify({"success": success, "message": message})

@app.route('/motion/stop', methods=['POST'])
def stop_motion():
    """Stop motion service"""
    success, message = motion_manager.stop_motion()
    return jsonify({"success": success, "message": message})

@app.route('/motion/status')
def motion_status():
    """Get motion status"""
    status = motion_manager.get_status()
    status["timestamp"] = datetime.now().isoformat()
    return jsonify(status)

@app.route('/motion/stream')
def motion_stream():
    """Proxy motion stream"""
    def generate():
        try:
            response = requests.get(motion_manager.stream_url, stream=True, timeout=10)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        except Exception as e:
            print(f"Stream proxy error: {e}")
            yield b"Stream unavailable"
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=BoundaryString')

@app.route('/recordings')
def get_recordings():
    """Get list of recorded videos"""
    recordings_dir = '/home/pi/raspi-monitor/recordings'
    recordings = []
    
    if os.path.exists(recordings_dir):
        for filename in os.listdir(recordings_dir):
            if filename.endswith(('.mp4', '.avi', '.mov')):
                filepath = os.path.join(recordings_dir, filename)
                stat = os.stat(filepath)
                recordings.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    return jsonify(sorted(recordings, key=lambda x: x['modified'], reverse=True))

@app.route('/system_info')
def system_info():
    """System information"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "server": "Raspberry Pi Motion Server",
        "motion_status": motion_manager.get_status()
    })

def cleanup():
    """Cleanup on exit"""
    print("Cleaning up...")
    motion_manager.stop_motion()

# Register cleanup handlers
signal.signal(signal.SIGTERM, lambda s, f: cleanup())
signal.signal(signal.SIGINT, lambda s, f: cleanup())

if __name__ == '__main__':
    print("🎥 Starting Raspberry Pi Motion Integration Server")
    print("Endpoints:")
    print("  / - Main page with motion viewer")
    print("  /motion/start - Start motion service")
    print("  /motion/stop - Stop motion service")
    print("  /motion/status - Motion status")
    print("  /motion/stream - Video stream")
    print("  /recordings - List recordings")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    finally:
        cleanup()