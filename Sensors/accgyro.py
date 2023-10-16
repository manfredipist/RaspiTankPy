import logging
import adafruit_mpu6050
from time import sleep
import math

from Settings import config

class AccelerometerGyroscope(object):

    def __init__(self, address):
        self.mpu6050 = adafruit_mpu6050.MPU6050(address)

        print("MPU6050 COM check")
        print("--------------------")

    def getAccelerometerMeasurements(self):
        return self.mpu6050.acceleration

    def getGyroscopeMeasurements(self):
        return self.mpu6050.gyro

    def getTemperature(self):
        return self.mpu6050.temperature

    def vector2degrees(self, x, y):
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        return angle

    # Given an accelerometer sensor object return the inclination angles of X/Z and Y/Z
    # Returns: tuple containing the two angles in degrees

    def getInclination(self):
        x, y, z = self.mpu6050.acceleration
        return self.vector2degrees(x, z), self.vector2degrees(y, z)

    def getYawPitchRoll(self):
        x, y, z = self.mpu6050.acceleration
        pitch = 180 * math.atan (x/math.sqrt(y*y + z*z))/math.pi;
        roll = 180 * math.atan (y/math.sqrt(x*x + z*z))/math.pi;
        yaw = 180 * math.atan (z/math.sqrt(x*x + z*z))/math.pi;
        return yaw, pitch, roll