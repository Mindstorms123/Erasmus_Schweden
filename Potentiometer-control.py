from machine import I2C, Pin, ADC
import time
from pca9685 import PCA9685
from servo import Servos

# --- I2C-Konfiguration ---
sda = Pin(0)
scl = Pin(1)
i2c_id = 0
i2c = I2C(id=i2c_id, sda=sda, scl=scl)

# --- PCA9685- und Servo-Initialisierung ---
pca = PCA9685(i2c=i2c)
servo = Servos(i2c=i2c)

# --- ADC für das Potentiometer ---
# ADC(2) bedeutet GPIO28 auf dem Raspberry Pi Pico
pot_pin = ADC(2)


# --- Hauptschleife ---
while True:
    # 1) ADC-Wert auslesen (0 - 65535)
    raw_value = pot_pin.read_u16()
    
    # 2) Umwandlung des ADC-Werts auf 0° - 270°
    servo_angle_0 = int((raw_value / 65535) * 270)
    
    # Für den zweiten Servo: gegenläufig = 270° - servo_angle_0
    servo_angle_1 = 270 - servo_angle_0
    
    # 3) Servo 0 auf den berechneten Winkel setzen
    servo.position(index=0, degrees=servo_angle_0)
    
    # 4) Servo 1 mit gegenläufigem Winkel ansteuern
    servo.position(index=1, degrees=servo_angle_1)
    
    # 5) Werte ausgeben
    print("ADC-Wert:", raw_value, 
          "-> Servo0-Winkel:", servo_angle_0, "°", 
          "-> Servo1-Winkel:", servo_angle_1, "°")
    
    # 6) Kurze Pause, damit die Servos Zeit haben, die Position zu erreichen
    time.sleep(0.05)