# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Raspberry Pi Monitor v1 is a real-time video and audio streaming system designed for monitoring purposes. It provides browser-based access to live camera feeds with audio support.

## Architecture

- **Backend**: Flask with Flask-SocketIO for real-time communication
- **Video Streaming**: OpenCV for camera capture, JPEG encoding via HTTP multipart
- **Audio Streaming**: PyAudio for audio capture, WebSocket transmission via Socket.IO
- **Frontend**: HTML5 with Web Audio API for audio playback

## Main Application (audio_video_app.py)

### Key Components:
- **Video Stream**: 640x480 @ 15 FPS via `/video_feed` endpoint
- **Audio Stream**: 16kHz mono via WebSocket events
- **Audio Control**: Client-initiated start/stop for bandwidth efficiency

### Configuration:
```python
# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
AUDIO_DEVICE_INDEX = 1  # USB camera microphone

# Video settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 15
```

## Development Commands

### Running the Application
```bash
source venv/bin/activate
python audio_video_app.py
```
- Runs on `0.0.0.0:5000`
- Accessible from any device on the network

### Key Dependencies
- Flask 3.1.1 - Web framework
- Flask-SocketIO 5.5.1 - WebSocket support
- OpenCV 4.12.0.88 - Video processing
- PyAudio 0.2.14 - Audio capture
- NumPy 2.2.6 - Array processing

## Important Notes

- Motion service must be stopped to avoid camera conflicts
- User must be in 'video' group for camera access
- Audio is opt-in to reduce bandwidth usage
- Development server warning is suppressed with `allow_unsafe_werkzeug=True`

## Target Deployment

Designed for Raspberry Pi 3 B+ or newer with USB webcam (tested with Logitech Brio 100).