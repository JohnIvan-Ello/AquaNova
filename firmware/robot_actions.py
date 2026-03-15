import config

# ------------------------
# ------------------------
# Movement Functions
# ------------------------
def move_forward(angle=90):
    global speed2
    command = f"motors:{config.speed2}\n"
    config.arduino_serial.write(command.encode())
    servo_command = f"servo:{angle}\n"
    config.arduino_serial.write(servo_command.encode())
    print(f"[Move] Forward -> {command.strip()}, Servo -> {angle}")

def move_backward(angle=90):
    global speed2
    command = f"motors:-{config.speed2}\n"
    config.arduino_serial.write(command.encode())
    servo_command = f"servo:{angle}\n"
    config.arduino_serial.write(servo_command.encode())
    print(f"[Move] Backward -> {command.strip()}, Servo -> {angle}")

def turn_left():
    global speed2
    # Reduce speed a bit for turning
    speed = max(config.speed2 -50, 0)
    move_forward(angle=120)  # adjust 60° as left steering
    print(f"[Move] Turn Left -> Speed: {speed}, Servo -> 120")

def turn_right():
    global speed2
    # Reduce speed a bit for turning
    speed = max(config.speed2 -50, 0)
    move_forward(angle=60)  # adjust 120° as right steering
    print(f"[Move] Turn Right -> Speed: {speed}, Servo -> 60")

def stop():
    command = "motors:0\n"
    config.arduino_serial.write(command.encode())
    print("[Move] Stop")


def send_door_command(left_angle, right_angle):
    command = f"chambers:{left_angle},{right_angle}\n"
    config.arduino_serial.write(command.encode())
    print(f"[Door] Sent command -> {command.strip()}")
