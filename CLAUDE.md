# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Raspberry Pi monitoring system that provides live video streaming and recording capabilities through a web interface. The system is designed to work as a baby monitor with webcam integration.

## Architecture

- **Backend**: Flask web application with SocketIO for real-time communication
- **Frontend**: Single-page HTML application with vanilla JavaScript
- **Camera Integration**: OpenCV for video capture and processing
- **File Structure**:
  - `app.py` - Main Flask application with camera management
  - `src/templates/index.html` - Web interface (Japanese UI)
  - `src/static/js/main.js` - Client-side JavaScript for controls and SocketIO
  - `src/static/css/style.css` - Responsive styling
  - `recordings/` - Directory for video recordings (auto-created)

## Key Components

### CameraManager Class (`app.py:14-60`)
- Handles camera initialization, frame capture, and video recording
- Thread-safe operations with locks
- Supports start/stop recording with timestamped filenames

### Real-time Communication
- Uses Flask-SocketIO for live video streaming
- WebSocket events: `start_recording`, `stop_recording`
- REST API endpoint `/api/recordings` for file listing

### Frontend Features
- Live video stream display
- Recording controls (start/stop buttons)
- Real-time status updates
- Recordings list with download links
- Japanese language interface

## Development Commands

### Running the Application
```bash
python app.py
```
- Starts Flask development server on `0.0.0.0:5000`
- Creates `recordings/` directory if it doesn't exist
- Debug mode enabled by default

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Key Dependencies
- Flask 3.0.3 with SocketIO support
- OpenCV 4.10.0.84 for camera operations
- Eventlet/Gunicorn for production deployment

## Configuration

- Camera settings: 640x480 resolution, 30 FPS (`app.py:24-26`)
- Recording format: AVI with XVID codec (`app.py:43`)
- Static files served from `src/static/`
- Templates from `src/templates/`

## Target Deployment

The application is designed to run on Raspberry Pi 3 B+ with USB webcam, accessible via browser from devices on the same network.