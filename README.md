# 🌊 AquaNova: Autonomous Solar-Powered Floating Robot
**AI-Driven Robotics | IoT Ecosystem | Sustainable Engineering**

AquaNova is a sophisticated, autonomous robotic platform designed for environmental preservation through intelligent aquatic waste collection. By integrating real-time Object Detection (AI) with GPS-based waypoint navigation, AquaNova operates as a self-sustaining unit capable of cleaning water bodies with minimal human intervention.

---

## 🚀 System Highlights
* **AI Computer Vision:** Custom-trained YOLOv8/PyTorch model for real-time aquatic debris identification.
* **Autonomous Pathfinding:** GPS & Magnetometer integration for precise waypoint navigation and boundary control.
* **Renewable Energy:** High-efficiency solar harvesting system with intelligent voltage regulation for 24/7 operation.
* **IoT Telemetry Dashboard:** A specialized web interface for real-time sensor monitoring and manual override capabilities.

---

## 🛠️ The Technical Ecosystem
The project is built on a "Multi-Tier" architecture, bridging the gap between hardware and cloud data.

| Layer | Technologies & Components |
| :--- | :--- |
| **Firmware (Logic)** | Python, Raspberry Pi (High-Level), Arduino Nano (Low-Level) |
| **AI / Machine Learning** | PyTorch (.pt weights), Computer Vision, Object Detection |
| **Hardware / IoT** | GPS NEO-6M, Compass HMC5883L, IR Sensors, Solar Array |
| **Software (UI/UX)** | HTML5, CSS3, JavaScript, JSON-based Waypoint Management |

---

## 📂 Repository Structure
This repository is organized to reflect a professional engineering pipeline:

* **`/firmware`**: Core Python scripts for sensor threading, camera processing, and robot actions.
* **`/hardware`**: CAD Wireframes, detailed circuit diagrams, and physical layout designs.
* **`/software`**: The user-facing dashboard and waypoint management JSON system.
* **`/documentation`**: Technical manuals, hardware part lists, and operational guides.
* **`/models`**: Trained AI model weights (`best.pt`) used for object detection.

---

## ⚙️ Core Functionality
### 1. Computer Vision & Detection
AquaNova utilizes a Raspberry Pi to process live video feeds. The onboard AI scans for floating waste, calculates the distance via IR sensors, and triggers the collection relay.

### 2. Waypoint Management
Using the **Waypoints Manager**, users can pre-define a search area. The robot utilizes its GPS and Compass modules to navigate between these points autonomously.

### 3. Energy Management
The system is powered by a Sealed Lead-Acid battery array charged via a PWM Solar Controller. The **DC/DC Step Down Converter** ensures that the sensitive electronics (Raspberry Pi/Arduino) receive a stable 5V feed.

---

## 🧪 Quality Assurance & Testing
As a project led by a QA-focused developer, AquaNova underwent rigorous testing:
* **Sensor Calibration:** Field-tested GPS/Compass accuracy in open-water environments.
* **Battery Lifecycle:** Verified solar charging rates against the system's power consumption.
* **Object Accuracy:** Iterative training of the `.pt` model to reduce false positives in dynamic lighting.

---
**Developed by John Ivan Ello** *Third-Year IT Student | Pamantasan ng Lungsod ng Maynila* *Specializing in Full-Stack Web, Robotics, and IoT Systems.*
