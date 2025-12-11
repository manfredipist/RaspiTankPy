"""VL53L1X wrapper - hardware-optional (uses adafruit lib if available)."""
import logging
from time import sleep

log = logging.getLogger('Laser')

try:
    import board
    import adafruit_vl53l1x
    HAS_VL53 = True
except Exception:
    HAS_VL53 = False

class Laser:
    def __init__(self, i2c_or_bus=None, name='laser'):
        self.name = name
        global HAS_VL53
        if HAS_VL53:
            # i2c_or_bus expected to be an I2C object (or multiplexer channel)
            self.vl = adafruit_vl53l1x.VL53L1X(i2c_or_bus)
            self.vl.distance_mode = 1
            self.vl.timing_budget = 100
            self.vl.start_ranging()
            log.info('%s: VL53L1X started', self.name)
        else:
            log.warning('%s: adafruit_vl53l1x not available, using stub', self.name)
            self.vl = None
        self.distance = None

    def getMeasurement(self):
        if HAS_VL53 and self.vl is not None:
            try:
                if self.vl.data_ready:
                    self.distance = self.vl.distance
                    self.vl.clear_interrupt()
                return self.distance
            except Exception as e:
                log.exception('VL53 read error: %s', e)
                return None
        # stubbed behavior
        import random
        self.distance = random.uniform(60, 200)  # cm
        return self.distance

    def stop(self):
        if HAS_VL53 and self.vl is not None:
            try:
                self.vl.stop_ranging()
                log.info('%s: VL53L1X stopped', self.name)
            except Exception as e:
                log.warning('%s: Error stopping VL53L1X: %s', self.name, e)
