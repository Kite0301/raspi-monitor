#!/usr/bin/env python3
import sys
import os

# Add system OpenCV path for Raspberry Pi
sys.path.insert(0, '/usr/lib/python3/dist-packages')

# Import and run the main application
if __name__ == '__main__':
    from app import socketio, app
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)