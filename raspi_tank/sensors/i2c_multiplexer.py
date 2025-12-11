"""I2C multiplexer manager: creates sensor instances and regularly polls them in a thread."""
import logging
import time

log = logging.getLogger('I2CMux')

try:
    import board
    import adafruit_tca9548a
    HAS_TCA = True
except Exception:
    HAS_TCA = False

from raspi_tank.sensors.laser import Laser
from raspi_tank.sensors.accgyro import AccelerometerGyroscope
from raspi_tank.config import laser as laser_conf

class I2CMultiplexer:
    def __init__(self):
        # ensure assignments refer to module-level HAS_TCA
        global HAS_TCA
        self._stopped = False
        self._last_update = time.time()

        # sensor objects
        self.front = None
        self.left = None
        self.right = None
        self.mpu = None

        if HAS_TCA:
            i2c = board.I2C()
            tca = adafruit_tca9548a.TCA9548A(i2c)
            # create laser sensors on configured mux channels if present
            try:
                self.right = Laser(tca[4], name='right')
                self.front = Laser(tca[5], name='front')
                self.left = Laser(tca[6], name='left')
                self.mpu = AccelerometerGyroscope(tca[3])
                log.info('I2C multiplexer and sensors initialized')
            except Exception as e:
                log.exception('Error initializing sensors via TCA: %s', e)
                HAS_TCA = False

        if not HAS_TCA:
            # fallback: create stub sensors (they will return simulated values)
            self.front = Laser(None, name='front-stub')
            self.left = Laser(None, name='left-stub')
            self.right = Laser(None, name='right-stub')
            self.mpu = AccelerometerGyroscope(None)
            log.info('Using stub sensors')

    def start(self):
        log.info('Starting I2C polling loop')
        while not self._stopped:
            try:
                f = self.front.getMeasurement()
                l = self.left.getMeasurement()
                r = self.right.getMeasurement()
                acc = self.mpu.getAccelerometerMeasurements()
                gyro = self.mpu.getGyroscopeMeasurements()

                self._last_update = time.time()
                # simple console log; real app would push values to shared state
                log.debug('Front: %s cm | Left: %s cm | Right: %s cm', f, l, r)
                time.sleep(0.5)
            except Exception as e:
                log.exception('I2C polling error: %s', e)
                time.sleep(1.0)

    def last_update_time(self):
        return self._last_update

    def stop(self):
        self._stopped = True
        try:
            if self.front:
                self.front.stop()
            if self.left:
                self.left.stop()
            if self.right:
                self.right.stop()
            if self.mpu:
                self.mpu.stop()
            log.info('I2C multiplexer stopped')
        except Exception as e:
            log.warning('Error during I2C cleanup: %s', e)
