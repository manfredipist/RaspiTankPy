import RPi.GPIO as GPIO          
from time import sleep

from Settings import config

class Motor(object):
    
    def __init__(self):
        GPIO.setup(config.motor_configuration["left_engine"]["en"],GPIO.OUT)
        GPIO.setup(config.motor_configuration["left_engine"]["in_1"],GPIO.OUT)
        GPIO.setup(config.motor_configuration["left_engine"]["in_2"],GPIO.OUT)

        GPIO.setup(config.motor_configuration["right_engine"]["en"],GPIO.OUT)
        GPIO.setup(config.motor_configuration["right_engine"]["in_1"],GPIO.OUT)
        GPIO.setup(config.motor_configuration["right_engine"]["in_2"],GPIO.OUT)

    def moveForward(self):
        GPIO.output(config.motor_configuration["left_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["left_engine"]["in_1"],GPIO.HIGH)     
        GPIO.output(config.motor_configuration["left_engine"]["in_2"],GPIO.LOW)  

        GPIO.output(config.motor_configuration["right_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["right_engine"]["in_1"],GPIO.HIGH)     
        GPIO.output(config.motor_configuration["right_engine"]["in_2"],GPIO.LOW)  

    def moveBackward(self):
        GPIO.output(config.motor_configuration["left_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["left_engine"]["in_1"],GPIO.LOW)     
        GPIO.output(config.motor_configuration["left_engine"]["in_2"],GPIO.HIGH)  

        GPIO.output(config.motor_configuration["right_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["right_engine"]["in_1"],GPIO.LOW)     
        GPIO.output(config.motor_configuration["right_engine"]["in_2"],GPIO.HIGH)  

    def moveLeft(self):
        GPIO.output(config.motor_configuration["left_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["left_engine"]["in_1"],GPIO.LOW)     
        GPIO.output(config.motor_configuration["left_engine"]["in_2"],GPIO.HIGH)  

        GPIO.output(config.motor_configuration["right_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["right_engine"]["in_1"],GPIO.HIGH)     
        GPIO.output(config.motor_configuration["right_engine"]["in_2"],GPIO.LOW) 

    def moveRight(self):
        GPIO.output(config.motor_configuration["left_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["left_engine"]["in_1"],GPIO.HIGH)     
        GPIO.output(config.motor_configuration["left_engine"]["in_2"],GPIO.LOW)  

        GPIO.output(config.motor_configuration["right_engine"]["en"],GPIO.HIGH)        
        GPIO.output(config.motor_configuration["right_engine"]["in_1"],GPIO.LOW)     
        GPIO.output(config.motor_configuration["right_engine"]["in_2"],GPIO.HIGH)  

    def stop(self):
        GPIO.output(config.motor_configuration["left_engine"]["en"],GPIO.LOW)        

        GPIO.output(config.motor_configuration["right_engine"]["en"],GPIO.LOW)     