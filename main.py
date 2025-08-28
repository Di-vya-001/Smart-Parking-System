from machine import Pin, SoftI2C, PWM
import time
from hcsr04 import HCSR04
from i2c_lcd import I2cLcd

# ===============================
# CONFIGURATION
# ===============================

DIST_THRESHOLD = 30  # cm for detecting car

# I2C for LCD
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Ultrasonic Sensors
sensor1 = HCSR04(trigger_pin=5, echo_pin=18)
sensor2 = HCSR04(trigger_pin=19, echo_pin=23)
sensor3 = HCSR04(trigger_pin=32, echo_pin=33)

# LEDs for each slot
g1, r1 = Pin(2, Pin.OUT), Pin(4, Pin.OUT)
g2, r2 = Pin(16, Pin.OUT), Pin(17, Pin.OUT)
g3, r3 = Pin(25, Pin.OUT), Pin(26, Pin.OUT)

# Servo Motor (Gate)
servo = PWM(Pin(27), freq=50)

# IR Sensor (Entry Detection)
ir_sensor = Pin(14)

# ===============================
# FUNCTIONS
# ===============================

def set_servo_angle(angle):
    min_ns = 500_000
    max_ns = 2_500_000
    pulse = min_ns + int((angle / 180) * (max_ns - min_ns))
    servo.duty_ns(pulse)

def open_gate():
    set_servo_angle(90)  # Gate opens
    time.sleep(2)
    set_servo_angle(0)   # Gate closes

def check_slot(sensor, green_led, red_led):
    try:
        dist = sensor.distance_cm()
        if dist < DIST_THRESHOLD:
            green_led.off()
            red_led.on()
            return False
        else:
            green_led.on()
            red_led.off()
            return True
    except:
        green_led.off()
        red_led.on()
        return False

# ===============================
# SETUP
# ===============================

lcd.clear()
lcd.putstr("Smart Parking...")
time.sleep(2)
servo.duty(115)  # Start with gate closed

# ===============================
# MAIN LOOP
# ===============================

while True:
    free = []

    # Check all slots
    if check_slot(sensor1, g1, r1):
        free.append("1")
    if check_slot(sensor2, g2, r2):
        free.append("2")
    if check_slot(sensor3, g3, r3):
        free.append("3")

    # Update LCD
    lcd.clear()
    if len(free) == 0:
        lcd.putstr("No Slots Free")
    else:
        lcd.putstr(f"{len(free)} Free:\n")
        lcd.putstr(" ".join(free))

    # Gate Logic
    if ir_sensor.value() == 0 and len(free) > 0:
        open_gate()

    time.sleep(1)
