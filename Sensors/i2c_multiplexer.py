import logging
import board
import adafruit_tca9548a
from time import sleep

from Settings import config
from Sensors import laser
from Sensors import accgyro

class I2CMultiplexer(object):
    
    def __init__(self):
        # Create I2C bus as normal
        i2c = board.I2C()  # uses board.SCL and board.SDA

        # Create the TCA9548A object and give it the I2C bus
        tca = adafruit_tca9548a.TCA9548A(i2c)

        for channel in range(8):
            if tca[channel].try_lock():
                print("Channel {}:".format(channel), end="")
                addresses = tca[channel].scan()
                print([hex(address) for address in addresses if address != 0x70])
                tca[channel].unlock()

        self.right_vl53l1x = laser.Laser(tca[config.laser_configuration["right_vl53l1x"]["bus"]])
        self.front_vl53l1x = laser.Laser(tca[config.laser_configuration["front_vl53l1x"]["bus"]])
        self.left_vl53l1x = laser.Laser(tca[config.laser_configuration["left_vl53l1x"]["bus"]])
        self.mpu6050 = accgyro.AccelerometerGyroscope(tca[config.accelerometergyroscope_configuration["bus"]])

    def start(self):
        while True:
            print("--------------------")
            print("Right Laser: {} cm".format(self.right_vl53l1x.getMeasurement()))
            print("Front Laser: {} cm".format(self.front_vl53l1x.getMeasurement()))
            print("Left Laser: {} cm".format(self.left_vl53l1x.getMeasurement()))

            acc_x, acc_y, acc_z = self.mpu6050.getAccelerometerMeasurements()
            print("Acceleration: X: {:6.2f} m/s^2, Y: {:6.2f} m/s^2, Z: {:6.2f} m/s^2".format(acc_x, acc_y, acc_z))

            gyro_x, gyro_y, gyro_z = self.mpu6050.getGyroscopeMeasurements()
            print("Gyro X: {:6.2f} rad/s, Y: {:6.2f} rad/s, Z: {:6.2f} rad/s".format(gyro_x, gyro_y, gyro_z))
            print("Temperature: {:6.2f} °C".format(self.mpu6050.getTemperature()))
           
            angle_xz, angle_yz = self.mpu6050.getInclination()
            print("Inclination: XZ angle: {:6.2f}°, YZ angle: {:6.2f}°".format(angle_xz, angle_yz))
            
            sleep(1)
            
if __name__ == "__main__":
    t = I2CMultiplexer()
    t.start()
