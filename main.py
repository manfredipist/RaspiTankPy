import threading
import logging
import RPi.GPIO as GPIO    
from sshkeyboard import listen_keyboard
from time import sleep

from Motor import motor
from Sensors import i2c_multiplexer
from Vision import camera

ROBOT_NAME = 'RaspiTank'
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(threadName)s | %(message)s')

engine = motor.Motor()

def press(key):
    print(f"'{key}' pressed")
    if key == 'w':
        engine.moveForward()
    elif key == 'a':
        engine.moveLeft()
    elif key == 's':
        engine.moveBackward()
    elif key == 'd':
        engine.moveRight()
    sleep(0.1)
    engine.stop()

if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)

    i2c_multiplexer = i2c_multiplexer.I2CMultiplexer()
    i2c_multiplexer_thread = threading.Thread(name='I2CMultiplexer', target=i2c_multiplexer.start, daemon=False)
    i2c_multiplexer_thread.start()

    camera = camera.VideoCamera()
    camera_thread = threading.Thread(name='VideoCamera', target=camera.start, daemon=False)
    camera_thread.start()

    listen_keyboard(
        on_press=press,
        debug=True
    )

