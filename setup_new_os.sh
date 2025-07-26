#!/bin/bash
# Raspberry Pi OS Lite setup script for raspi-monitor
# Run this script after fresh OS installation

echo "🚀 Setting up Raspberry Pi OS Lite for raspi-monitor"

# System update
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y \
    git \
    python3-venv \
    python3-pip \
    motion \
    v4l-utils \
    fswebcam \
    curl \
    wget

# Power optimization settings
echo "⚡ Applying power optimization settings..."
echo "max_usb_current=1" | sudo tee -a /boot/firmware/config.txt
echo "gpu_mem=16" | sudo tee -a /boot/firmware/config.txt

# Create raspi-monitor directory and clone
echo "📂 Setting up raspi-monitor application..."
cd ~
git clone https://github.com/Kite0301/raspi-monitor.git
cd raspi-monitor

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-socketio python-socketio requests

# Create recordings directory
mkdir -p recordings

# Set up motion configuration
echo "🎥 Configuring Motion service..."
sudo cp motion.conf /etc/motion/motion.conf

# Disable unnecessary services for lighter system
echo "🔇 Disabling unnecessary services..."
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. Test camera: v4l2-ctl -d /dev/video0 --list-formats-ext"
echo "3. Start application: cd ~/raspi-monitor && source venv/bin/activate && python3 motion_app.py"
echo ""
echo "Application will be available at: http://192.168.1.12:5001/"