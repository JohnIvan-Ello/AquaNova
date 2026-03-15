import threading
import time
from flask import Flask, render_template, Response, jsonify, send_file, request
import config
from config import *
from sensors_thread import sensor_thread
from gps_thread import gps_thread
from camera_thread import gen_frames
from yolo_thread import yolo_thread
import os
import json
import cw_mode
import tnw_mode
import robot_actions
import waypoint_utils
import tc_mode
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WAYPOINTS_FILE = os.path.join(BASE_DIR, "waypoints.json")

app = Flask(__name__)

# ------------------------
# Helpers
# ------------------------


def save_waypoints(data):
    """Save dict of waypoints to file."""
    with open(WAYPOINTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------------------
# API Routes
# ------------------------
@app.route("/api/waypoints", methods=["GET", "POST"])
def api_waypoints():
    if request.method == "GET":
        return jsonify(waypoint_utils.load_waypoints())

    # POST: add/update a waypoint
    data = request.json
    waypoints = waypoint_utils.load_waypoints()
    waypoints[data["name"]] = {"lat": data["lat"], "lon": data["lon"]}
    save_waypoints(waypoints)
    return jsonify({"status": "saved"})

@app.route("/api/waypoints/<name>", methods=["DELETE"])
def delete_waypoint(name):
    waypoints = waypoint_utils.load_waypoints()
    if name in waypoints:
        del waypoints[name]
        save_waypoints(waypoints)
    return jsonify({"status": "ok"})

@app.route("/api/waypoints/download", methods=["GET"])
def download_waypoints():
    return send_file(WAYPOINTS_FILE, as_attachment=True)

@app.route("/api/waypoints/upload", methods=["POST"])
def upload_waypoints():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file uploaded"}), 400
    try:
        data = json.load(file)
        save_waypoints(data)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# Page Routes
# ------------------------
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/waypoints")
def waypoints_page():
    return render_template("waypoints.html")


@app.route("/api/mode/cw/start", methods=["POST"])
def start_cw():
    cw_mode.start_cw()
    return jsonify({"status": "cw started"})

@app.route("/api/mode/cw/stop", methods=["POST"])
def stop_cw():
    cw_mode.stop_cw()
    return jsonify({"status": "cw stopped"})

@app.route("/mode", methods=["POST"])
def toggle_mode():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode")
    state = data.get("state")
    print("MODE RECEIVED:", repr(mode), "STATE:", state)  # debug

    if mode == "CW":
        if state:
            cw_mode.start_cw()
            return {"status": "CW started"}
        else:
            cw_mode.stop_cw()
            return {"status": "CW stopped"}
    elif mode == "TNW":
        if state:
            tnw_mode.start_tnw()
            return {"status": "TNW started"}
        else:
            tnw_mode.stop_tnw()
            return {"status": "TNW stopped"}
    elif mode == "TC":
        if state:
            tc_mode.start_tc()
            return {"status": "TC started"}
        else:
            tc_mode.stop_tc()
            return {"status": "TC stopped"}
    return {"status": "unknown mode"}, 400

# ------------------------
# Flask Endpoints
# ------------------------
@app.route('/drive', methods=['POST'])
def drive():
    direction = request.args.get('direction', '').lower()
    if direction == 'forward': robot_actions.move_forward()
    elif direction == 'backward': robot_actions.move_backward()
    elif direction == 'left': robot_actions.turn_left()
    elif direction == 'right': robot_actions.turn_right()
    elif direction == 'stop': robot_actions.stop()
    else: return "Invalid direction", 400
    return "OK"

@app.route('/set_motor_speed', methods=['POST'])
def set_motor_speed():
    data = request.get_json()
    config.speed2 = int(data['speed2'])   # ✅ update config, not a separate global
    config.robot_state["speed2"] = config.speed2  # keep state in sync if you display it
    return jsonify({"speed2": config.speed2})


@app.route('/toggle_pump', methods=['POST'])
def toggle_pump():
    data = request.get_json()
    state = data.get("state")

    if state not in ["on", "off"]:
        return "Invalid state", 400

    # ✅ update global config and robot_state
    config.pump_state = state
    robot_state["pump"] = state

    # ✅ send command to Arduino
    if arduino_serial and arduino_serial.is_open:
        cmd = f"pump:{state}\n".encode()
        arduino_serial.write(cmd)
        print(f"[PUMP] Sent to Arduino: {cmd}")

    return jsonify({"pump": state})



@app.route("/door", methods=["POST"])
def door_control():
    data = request.get_json()
    left_angle = data.get("left")
    right_angle = data.get("right")
    if left_angle is None or right_angle is None:
        return {"status": "error", "message": "Missing angles"}, 400

    robot_actions.send_door_command(left_angle, right_angle)
    return {"status": "ok"}




@app.route('/sensors')
def sensors():
    robot_state["battery"] = config.battery_voltage
    robot_state["compass"] = config.compass_heading
    robot_state["ir_left"] = config.ir_left
    robot_state["ir_right"] = config.ir_right
    robot_state["pump"] = config.pump_state
    robot_state["latitude"] = config.gps_lat
    robot_state["longitude"] = config.gps_lon

    # ---- CW values ----
    if getattr(cw_mode, "active", False) and cw_mode.cw_current_target is not None and cw_mode.cw_distance_to_target is not None:
        robot_state["cw_target"] = cw_mode.cw_current_target
        robot_state["cw_distance"] = cw_mode.cw_distance_to_target
    else:
        robot_state["cw_target"] = None
        robot_state["cw_distance"] = None

    # ---- TNW values ----
    if getattr(tnw_mode, "active", False) and tnw_mode.tnw_current_item is not None:
        robot_state["tnw_target"] = tnw_mode.tnw_current_item
        robot_state["tnw_zone"] = tnw_mode.tnw_current_zone
    else:
        robot_state["tnw_target"] = None
        robot_state["tnw_zone"] = None
    # ---- TC values ----
    if getattr(tc_mode, "active", False):
        # Waypoint status
        robot_state["tc_waypoint"] = tc_mode.tc_current_waypoint
        robot_state["tc_distance"] = tc_mode.tc_distance_to_waypoint
        # Trash status
        robot_state["tc_target"] = tc_mode.tc_current_item
        robot_state["tc_zone"] = tc_mode.tc_current_zone
    else:
        robot_state["tc_waypoint"] = None
        robot_state["tc_distance"] = None
        robot_state["tc_target"] = None
        robot_state["tc_zone"] = None

    return jsonify(robot_state)



@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
# ---- Detections JSON route ----
@app.route('/detections')
def detections():
    return jsonify(config.detected_trash)
# ------------------------
# Main Entry
# ------------------------
if __name__ == '__main__':
    threading.Thread(target=sensor_thread, daemon=True).start()
    threading.Thread(target=gps_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
    t_yolo = threading.Thread(target=yolo_thread, daemon=True)
    t_yolo.start()