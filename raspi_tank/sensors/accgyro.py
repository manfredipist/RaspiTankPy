"""MPU6050 wrapper - hardware-optional."""
import logging
import math

log = logging.getLogger('AccGyro')

try:
    import adafruit_mpu6050
    HAS_MPU = True
except Exception:
    HAS_MPU = False

class AccelerometerGyroscope:
    def __init__(self, i2c_or_bus=None):
        if HAS_MPU:
            self.mpu = adafruit_mpu6050.MPU6050(i2c_or_bus)
            self.mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
            self.mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS
            log.info('MPU6050 initialized')
        else:
            log.warning('MPU6050 not available, using stub')
            self.mpu = None

    def getAccelerometerMeasurements(self):
        if HAS_MPU and self.mpu is not None:
            return self.mpu.acceleration
        return (0.0, 0.0, 9.81)

    def getGyroscopeMeasurements(self):
        if HAS_MPU and self.mpu is not None:
            return self.mpu.gyro
        return (0.0, 0.0, 0.0)

    def getTemperature(self):
        if HAS_MPU and self.mpu is not None:
            return self.mpu.temperature
        return 25.0

    def vector2degrees(self, x, y):
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        return angle

    def getInclination(self):
        x, y, z = self.getAccelerometerMeasurements()
        return self.vector2degrees(x, z), self.vector2degrees(y, z)

    def getYawPitchRoll(self):
        x, y, z = self.getAccelerometerMeasurements()
        pitch = 180 * math.atan(x/math.sqrt(y*y + z*z))/math.pi if (y*y + z*z) != 0 else 0
        roll = 180 * math.atan(y/math.sqrt(x*x + z*z))/math.pi if (x*x + z*z) != 0 else 0
        yaw = 180 * math.atan(z/math.sqrt(x*x + z*z))/math.pi if (x*x + z*z) != 0 else 0
        return yaw, pitch, roll
