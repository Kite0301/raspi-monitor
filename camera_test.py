#!/usr/bin/env python3
"""
Camera testing script for Raspberry Pi
Tests different settings progressively
"""
import sys
import time
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import cv2

def test_camera_backends():
    """Test different OpenCV backends"""
    backends = [
        (cv2.CAP_V4L2, "V4L2"),
        (cv2.CAP_GSTREAMER, "GStreamer"), 
        (cv2.CAP_ANY, "Auto")
    ]
    
    for backend_id, backend_name in backends:
        print(f"\n=== Testing {backend_name} Backend ===")
        try:
            cap = cv2.VideoCapture(0, backend_id)
            if cap.isOpened():
                print(f"✅ {backend_name} backend opened successfully")
                
                # Test frame capture with timeout
                start_time = time.time()
                ret, frame = cap.read()
                elapsed = time.time() - start_time
                
                if ret:
                    print(f"✅ Frame captured in {elapsed:.2f}s - Shape: {frame.shape}")
                else:
                    print(f"❌ Frame capture failed after {elapsed:.2f}s")
                    
                cap.release()
            else:
                print(f"❌ {backend_name} backend failed to open")
        except Exception as e:
            print(f"❌ {backend_name} backend error: {e}")

def test_resolutions():
    """Test different resolutions"""
    resolutions = [
        (160, 120, "QQVGA"),
        (320, 240, "QVGA"), 
        (640, 480, "VGA"),
        (800, 600, "SVGA")
    ]
    
    print(f"\n=== Testing Resolutions ===")
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print("❌ Could not open camera for resolution test")
        return
    
    for width, height, name in resolutions:
        print(f"\nTesting {name} ({width}x{height}):")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, 5)
        
        # Get actual values
        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"  Set: {width}x{height} | Actual: {actual_w}x{actual_h} @ {actual_fps}fps")
        
        # Test frame capture
        start_time = time.time()
        ret, frame = cap.read()
        elapsed = time.time() - start_time
        
        if ret:
            print(f"  ✅ Frame captured in {elapsed:.2f}s")
        else:
            print(f"  ❌ Frame capture failed after {elapsed:.2f}s")
        
        time.sleep(0.5)
    
    cap.release()

def test_formats():
    """Test different pixel formats"""
    print(f"\n=== Testing Pixel Formats ===")
    
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("❌ Could not open camera for format test")
        return
    
    # Set basic resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    formats = [
        (cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'), "MJPG"),
        (cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y','U','Y','V'), "YUYV"),
    ]
    
    for prop, fourcc, name in formats:
        print(f"\nTesting {name} format:")
        cap.set(prop, fourcc)
        
        ret, frame = cap.read()
        if ret:
            print(f"  ✅ {name} format works - Shape: {frame.shape}")
        else:
            print(f"  ❌ {name} format failed")
    
    cap.release()

if __name__ == "__main__":
    print("🔍 Raspberry Pi Camera Diagnostic Tool")
    print("=====================================")
    
    test_camera_backends()
    test_resolutions() 
    test_formats()
    
    print("\n✅ Camera testing completed!")