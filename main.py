import threading
import logging
import RPi.GPIO as GPIO    

from Sensors import i2c_multiplexer
from Vision import camera

ROBOT_NAME = 'RaspiTank'
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(threadName)s | %(message)s')

if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)

    i2c_multiplexer = i2c_multiplexer.I2CMultiplexer()
    i2c_multiplexer_thread = threading.Thread(name='I2CMultiplexer', target=i2c_multiplexer.start, daemon=False)
    i2c_multiplexer_thread.start()

    camera = camera.VideoCamera()
    camera_thread = threading.Thread(name='VideoCamera', target=camera.start, daemon=False)
    camera_thread.start()
