#!/usr/bin/env python3
"""Demo script to test MJPEG streaming with simulated camera (no hardware required)."""
import cv2
import numpy as np
import threading
import time
import random
from raspi_tank.streaming import MJPEGStreamer

class DemoSensor:
    """Simulated sensor for testing."""
    def __init__(self, base_value=100):
        self.base_value = base_value
        self.distance = base_value
    
    def getMeasurement(self):
        # Simulate sensor drift
        self.distance = self.base_value + random.uniform(-20, 20)
        return self.distance

class DemoIMU:
    """Simulated IMU for testing."""
    def getTemperature(self):
        return 25.0 + random.uniform(-2, 2)
    
    def getYawPitchRoll(self):
        return (
            random.uniform(-5, 5),   # yaw
            random.uniform(-10, 10), # pitch
            random.uniform(-10, 10)  # roll
        )

class DemoSensors:
    """Simulated sensor multiplexer."""
    def __init__(self):
        self.front = DemoSensor(80)
        self.left = DemoSensor(120)
        self.right = DemoSensor(110)
        self.mpu = DemoIMU()

class DemoMotor:
    """Simulated motor for testing."""
    def __init__(self):
        self.last_command = "stop"
        self.command_time = time.time()
    
    def move_forward(self):
        self.last_command = "forward"
        self.command_time = time.time()
        print("🚗 Motor: FORWARD")
    
    def move_backward(self):
        self.last_command = "backward"
        self.command_time = time.time()
        print("🚗 Motor: BACKWARD")
    
    def move_left(self):
        self.last_command = "left"
        self.command_time = time.time()
        print("🚗 Motor: LEFT")
    
    def move_right(self):
        self.last_command = "right"
        self.command_time = time.time()
        print("🚗 Motor: RIGHT")
    
    def stop(self):
        self.last_command = "stop"
        self.command_time = time.time()
        print("🛑 Motor: STOP")

class DemoCameraWorker:
    """Simulated camera for testing."""
    def __init__(self, motor):
        self.frame_counter = 0
        self._stopped = False
        self.annotated_frame = None
        self.motor = motor
        
        # Add processor attribute for QR data
        class DemoProcessor:
            def __init__(self):
                self.last_qr_data = None
        self.processor = DemoProcessor()
        
    def generate_test_frame(self):
        """Generate a test pattern frame."""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw gradient background
        for i in range(480):
            color_val = int((i / 480) * 255)
            img[i, :] = [color_val // 3, color_val // 2, color_val]
        
        # Draw some shapes
        cv2.circle(img, (320, 240), 100, (0, 255, 0), 3)
        cv2.rectangle(img, (100, 100), (200, 200), (255, 0, 0), 2)
        
        # Add frame counter
        cv2.putText(img, f'Frame: {self.frame_counter}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = time.strftime('%H:%M:%S')
        cv2.putText(img, f'Time: {timestamp}', (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show motor status
        status_color = (0, 255, 0) if self.motor.last_command != "stop" else (100, 100, 100)
        cv2.putText(img, f'Motor: {self.motor.last_command.upper()}', (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        # Simulate QR detection box (appears randomly)
        if self.frame_counter % 100 < 50:  # Show for half the time
            cv2.rectangle(img, (400, 300), (550, 400), (0, 255, 0), 2)
            cv2.putText(img, 'QR: DEMO_123', (405, 290),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self.processor.last_qr_data = "DEMO_123"
        else:
            self.processor.last_qr_data = None
        
        return img
    
    def start(self):
        """Simulate camera capture loop."""
        print("Demo camera started - generating test frames")
        while not self._stopped:
            self.annotated_frame = self.generate_test_frame()
            self.frame_counter += 1
            time.sleep(0.033)  # ~30 FPS
        print("Demo camera stopped")
    
    def get_latest_annotated_frame(self):
        return self.annotated_frame.copy() if self.annotated_frame is not None else None
    
    def stop(self):
        self._stopped = True

if __name__ == '__main__':
    print("=" * 60)
    print("RaspiTank MJPEG Streaming Demo with Controls")
    print("=" * 60)
    print("\nStarting simulated components...")
    
    # Create demo motor
    motor = DemoMotor()
    
    # Create demo sensors
    sensors = DemoSensors()
    
    # Create and start demo camera
    camera = DemoCameraWorker(motor)
    cam_thread = threading.Thread(target=camera.start, daemon=True)
    cam_thread.start()
    
    # Wait for first frame
    time.sleep(0.5)
    
    print("\nStarting MJPEG streamer with full interface...")
    streamer = MJPEGStreamer(camera, sensors=sensors, motor=motor, host='0.0.0.0', port=5000)
    streamer.start()
    
    print("\n" + "=" * 60)
    print("✓ Streaming is now active!")
    print("=" * 60)
    print("\nOpen your browser and navigate to:")
    print("  → http://localhost:5000")
    print("  → http://<this-machine-ip>:5000")
    print("\nFeatures available:")
    print("  • Live video stream with test pattern")
    print("  • Real-time sensor data (simulated)")
    print("  • Motor controls via buttons or keyboard")
    print("  • Arrow keys or WASD to control")
    print("  • Space bar to stop")
    print("\nPress Ctrl+C to stop...")
    print("=" * 60 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping demo...")
        camera.stop()
        streamer.stop()
        print("Demo stopped. Goodbye!")
