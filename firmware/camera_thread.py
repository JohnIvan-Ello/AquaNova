import cv2
import time
from picamera2 import Picamera2
from ultralytics import YOLO
import config

# Camera setup
camera = Picamera2()
camera_config = camera.create_preview_configuration()
camera.configure(camera_config)
camera.start()

# Load YOLO model
model = YOLO("/home/novapi/pi_robot/best.pt")  # make sure best.pt is in the same folder
TRASH_CLASSES = {"plastic", "glass", "metal"}

# Frame skipping for speed
frame_count = 0
SKIP_FRAMES = 3  # run YOLO every 3rd frame

def gen_frames():
    global frame_count
    while True:
        # Capture frame from PiCamera2
        frame = camera.capture_array()

        # 🔹 Fix: Convert from RGBA (4 channels) → BGR (3 channels)
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        detections = []

        # Run YOLO only every SKIP_FRAMES
        if frame_count % SKIP_FRAMES == 0:
            results = model(frame, verbose=False)

            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0])
                class_name = results[0].names[class_id].lower()

                if class_name in TRASH_CLASSES:
                    print(f"Detected {class_name} ({conf:.2f}) at {int(x1)},{int(y1)},{int(x2)},{int(y2)}")
                    detections.append({
                        "class": class_name,
                        "confidence": round(conf, 2),
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    })

                    # Draw bounding box + label
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"{class_name} {conf:.2f}",
                                (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (0, 255, 0), 2)

            # Update global detection state
            config.detected_trash = detections

        frame_count += 1

        # Encode frame as JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Small delay to avoid CPU overload
        time.sleep(0.05)
