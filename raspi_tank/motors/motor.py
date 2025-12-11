"""Motor control (hardware-optional). If RPi.GPIO is available it will use real pins, otherwise it will log actions."""
import logging

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except Exception:
    HAS_GPIO = False

from raspi_tank.config import motor as motor_conf

log = logging.getLogger('Motor')

class Motor:
    def __init__(self):
        global HAS_GPIO
        if HAS_GPIO:
            GPIO.setmode(GPIO.BCM)
            for p in motor_conf['left_pins'].values():
                GPIO.setup(p, GPIO.OUT)
            for p in motor_conf['right_pins'].values():
                GPIO.setup(p, GPIO.OUT)
        log.info('Motor initialized (GPIO=%s)', HAS_GPIO)

    def move_forward(self):
        log.info('move_forward')
        if HAS_GPIO:
            GPIO.output(motor_conf['left_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_1'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_2'], GPIO.LOW)

            GPIO.output(motor_conf['right_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_1'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_2'], GPIO.LOW)

    def move_backward(self):
        log.info('move_backward')
        if HAS_GPIO:
            GPIO.output(motor_conf['left_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_1'], GPIO.LOW)
            GPIO.output(motor_conf['left_pins']['in_2'], GPIO.HIGH)

            GPIO.output(motor_conf['right_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_1'], GPIO.LOW)
            GPIO.output(motor_conf['right_pins']['in_2'], GPIO.HIGH)

    def move_left(self):
        log.info('move_left')
        if HAS_GPIO:
            GPIO.output(motor_conf['left_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_1'], GPIO.LOW)
            GPIO.output(motor_conf['left_pins']['in_2'], GPIO.HIGH)

            GPIO.output(motor_conf['right_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_1'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_2'], GPIO.LOW)

    def move_right(self):
        log.info('move_right')
        if HAS_GPIO:
            GPIO.output(motor_conf['left_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_1'], GPIO.HIGH)
            GPIO.output(motor_conf['left_pins']['in_2'], GPIO.LOW)

            GPIO.output(motor_conf['right_pins']['en'], GPIO.HIGH)
            GPIO.output(motor_conf['right_pins']['in_1'], GPIO.LOW)
            GPIO.output(motor_conf['right_pins']['in_2'], GPIO.HIGH)

    def stop(self):
        log.info('stop')
        if HAS_GPIO:
            GPIO.output(motor_conf['left_pins']['en'], GPIO.LOW)
            GPIO.output(motor_conf['right_pins']['en'], GPIO.LOW)
