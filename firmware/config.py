import serial
import time
import RPi.GPIO as GPIO
import os, logging

# ------------------------
# Initial States
# ------------------------
pump_state = "off"
battery_voltage = 0.0
compass_heading = 0.0
ir_left = 0
ir_right = 0
speed2 = 255

# ------------------------
# GPS Serial (Pi UART)
# ------------------------
gps_lat = 0.0
gps_lon = 0.0

try:
    gps_serial = serial.Serial('/dev/serial0', 9600, timeout=1)
    print("[GPS] /dev/serial0 opened at 9600")
except Exception as e:
    gps_serial = None
    print(f"[GPS] Failed to open /dev/serial0: {e}")

# ------------------------
# Robot State
# ------------------------
robot_state = {
    "battery": 0.0,
    "compass": 0.0,
    "ir_left": 0,
    "ir_right": 0,
    "pump": pump_state,
    "latitude": 0.0,
    "speed2": speed2,   # ✅ include here too

    "longitude": 0.0,
}

# ------------------------
# GPIO Setup
# ------------------------
PUMP_RELAY_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_RELAY_PIN, GPIO.OUT)
GPIO.output(PUMP_RELAY_PIN, GPIO.HIGH)  # OFF by default

# ------------------------
# Arduino Serial
# ------------------------
try:
    arduino_serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    print("[Arduino] Connected on /dev/ttyUSB0")
except FileNotFoundError:
    arduino_serial = None
    print("[Arduino] Not connected. Skipping...")
time.sleep(2)  # Allow Arduino reset
_model = None
base_path = os.path.dirname(os.path.abspath(__file__))

def get_model():
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO
            model_path = os.path.join(base_path, "best.pt")  # put best.pt in same folder
            _model = YOLO(model_path)
            logging.info(f"[Config] YOLO model loaded from {model_path}")
        except Exception as e:
            logging.error(f"[Config] Failed to load YOLO model: {e}")
            _model = None
    return _model

# Shared detection results
detected_trash = []   # list of (cx, cy, w, h, class_name)
frame_width = 0
frame_height = 0