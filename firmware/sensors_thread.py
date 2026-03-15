import time
import serial
import config
from config import arduino_serial, battery_voltage, compass_heading, ir_left, ir_right
COMPASS_OFFSET = -14.0  
def normalize_angle(angle: float) -> float:
    """Keep angle in range [0, 360)."""
    return (angle + 360) % 360

def sensor_thread():
    global battery_voltage, compass_heading, ir_left, ir_right, arduino_serial

    while True:
        try:
            if arduino_serial and arduino_serial.in_waiting:
                line = arduino_serial.readline().decode(errors="ignore").strip()
                if line:
                    try:
                        parts = line.split(";")
                        data = {}
                        for part in parts:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                data[key] = value

                        if "battery" in data:
                            config.battery_voltage = float(data["battery"])
                        if "compass" in data:
                            raw_heading = float(data["compass"])
                            config.compass_heading = normalize_angle(raw_heading + COMPASS_OFFSET)

                        if "IR_L" in data:
                            config.ir_left = int(data["IR_L"])
                        if "IR_R" in data:
                            config.ir_right = int(data["IR_R"])
                        print(f"[Sensors] Battery={config.battery_voltage:.2f}V | "
                              f"Compass={config.compass_heading:.1f}° | "
                              f"IR_L={config.ir_left} | IR_R={config.ir_right}")
                    except Exception as parse_err:
                        print("Parse error:", line, parse_err)

        except Exception as e:
            print(f"Sensor thread error: {e}")
            time.sleep(1)
            try:
                arduino_serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
                print("Reconnected to Arduino.")
            except Exception as reconnect_err:
                print("Reconnect failed:", reconnect_err)
                time.sleep(2)
