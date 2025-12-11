"""Controller utilities: Watchdog that checks sensors and stops motors on danger."""
import logging
import time

from raspi_tank.config import safety, laser as laser_conf

log = logging.getLogger('Controller')

class Watchdog:
    def __init__(self, motor, sensors, camera):
        self.motor = motor
        self.sensors = sensors
        self.camera = camera
        self._stopped = False

    def run(self):
        log.info('Watchdog started')
        while not self._stopped:
            try:
                # check sensors freshness
                last = self.sensors.last_update_time() if self.sensors else 0
                age = time.time() - last
                if age > safety['sensor_timeout_s']:
                    log.error('Sensor timeout (%.1fs) - stopping motors', age)
                    self.motor.stop()

                # check front distance
                front_dist = None
                try:
                    front_dist = self.sensors.front.distance
                except Exception:
                    pass
                if front_dist is not None and front_dist < laser_conf['front_threshold_cm']:
                    log.warning('Obstacle detected at %.1f cm - stopping motors', front_dist)
                    self.motor.stop()

                time.sleep(0.3)
            except Exception as e:
                log.exception('Watchdog error: %s', e)
                time.sleep(1.0)

    def stop(self):
        self._stopped = True
