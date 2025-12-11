#!/usr/bin/env python3
"""Main orchestrator: avvia sensori, camera, e watchdog di sicurezza."""
import threading
import logging
from time import sleep

from raspi_tank.motors import Motor
from raspi_tank.sensors.i2c_multiplexer import I2CMultiplexer
from raspi_tank.vision.camera import CameraWorker
from raspi_tank.streaming import MJPEGStreamer
from raspi_tank.controller import Watchdog
from raspi_tank.config import camera as camera_conf

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(threadName)s | %(message)s')

if __name__ == '__main__':
    logging.info('Starting RaspiTank Controller')

    motor = Motor()

    # Start I2C sensors (multiplexer handles sensors internally)
    i2c_mux = I2CMultiplexer()
    i2c_thread = threading.Thread(name='I2CThread', target=i2c_mux.start, daemon=True)
    i2c_thread.start()

    # Camera + processing
    camera = CameraWorker(i2c_mux)
    cam_thread = threading.Thread(name='CameraThread', target=camera.start, daemon=True)
    cam_thread.start()

    # MJPEG streaming (optional)
    streamer = None
    if camera_conf.get('enable_mjpeg_stream', False):
        streamer = MJPEGStreamer(
            camera,
            sensors=i2c_mux,
            motor=motor,
            host=camera_conf.get('stream_host', '0.0.0.0'),
            port=camera_conf.get('stream_port', 5000)
        )
        streamer.start()
        logging.info('MJPEG stream available at http://<raspberry-pi-ip>:%d', camera_conf['stream_port'])

    # Watchdog thread to enforce safety
    watchdog = Watchdog(motor, i2c_mux, camera)
    wd_thread = threading.Thread(name='Watchdog', target=watchdog.run, daemon=True)
    wd_thread.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logging.info('Stopping...')
        camera.stop()
        i2c_mux.stop()
        motor.stop()
        if streamer:
            streamer.stop()
        sleep(0.5)
        logging.info('Exited')
