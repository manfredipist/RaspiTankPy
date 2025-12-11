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
        global HAS_MPU
        if HAS_MPU:
            try:
                self.mpu = adafruit_mpu6050.MPU6050(i2c_or_bus)
                self.mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
                self.mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS
                log.info('MPU6050 initialized')
            except Exception as e:
                log.warning('MPU6050 initialization failed: %s', e)
                self.mpu = None
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
            try:
                return self.mpu.temperature
            except Exception as e:
                log.warning('Error reading temperature: %s', e)
                return 25.0
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
        """Calculate yaw, pitch, roll from accelerometer data.
        Note: Yaw cannot be determined from accelerometer alone (needs gyro/magnetometer).
        Returns angles in degrees.
        """
        x, y, z = self.getAccelerometerMeasurements()
        
        # Pitch: rotation around Y axis (forward/backward tilt)
        pitch = math.atan2(x, math.sqrt(y*y + z*z)) * 180.0 / math.pi if (y*y + z*z) != 0 else 0
        
        # Roll: rotation around X axis (left/right tilt)
        roll = math.atan2(y, math.sqrt(x*x + z*z)) * 180.0 / math.pi if (x*x + z*z) != 0 else 0
        
        # Yaw: rotation around Z axis (cannot be computed from accelerometer alone)
        # Would need gyroscope integration or magnetometer
        yaw = 0.0
        
        return yaw, pitch, roll
    
    def stop(self):
        """Cleanup I2C resources to prevent locks."""
        try:
            if self.mpu is not None:
                # MPU6050 doesn't have explicit cleanup, but we can deinitialize
                self.mpu = None
                log.info('MPU6050 stopped')
        except Exception as e:
            log.warning('Error during MPU6050 cleanup: %s', e)
