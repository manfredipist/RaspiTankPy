"""Camera worker: capture frames, analyze with FrameProcessor, display via cv2.imshow (X11).
Accepts an I2C multiplexer instance to read sensor distances for overlay and safety decisions.
"""
import logging
import time
import cv2
import threading

from raspi_tank.vision.processor import FrameProcessor
from raspi_tank.config import camera as camera_conf

log = logging.getLogger('Camera')

class CameraWorker:
    def __init__(self, sensors=None):
        self.sensors = sensors
        self._stopped = False
        self.processor = FrameProcessor()
        self.frame = None
        self.annotated_frame = None
        self._frame_lock = threading.Lock()

        # try picamera first, fallback to cv2.VideoCapture
        try:
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self._use_picamera = True
            self.camera = PiCamera()
            self.camera.resolution = camera_conf['resolution']
            self.camera.framerate = camera_conf['framerate']
            self.rawCapture = PiRGBArray(self.camera, size=camera_conf['resolution'])
            self.stream = self.camera.capture_continuous(self.rawCapture, format='bgr', use_video_port=True)
            log.info('Using PiCamera')
        except Exception:
            self._use_picamera = False
            self.cap = cv2.VideoCapture(0)
            if camera_conf['resolution']:
                w, h = camera_conf['resolution']
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            log.info('Using cv2.VideoCapture')

    def start(self):
        log.info('CameraWorker started')
        if self._use_picamera:
            for f in self.stream:
                self.frame = f.array
                annotated, results = self.processor.analyze(self.frame, self.sensors)
                with self._frame_lock:
                    self.annotated_frame = annotated.copy()
                if camera_conf.get('show_window', True):
                    cv2.imshow('RaspiTank', annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                self.rawCapture.truncate(0)
                if self._stopped:
                    break
        else:
            while not self._stopped:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                self.frame = frame
                annotated, results = self.processor.analyze(frame, self.sensors)
                with self._frame_lock:
                    self.annotated_frame = annotated.copy()
                if camera_conf.get('show_window', True):
                    cv2.imshow('RaspiTank', annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                # small sleep so loop is not CPU bound
                time.sleep(0.01)
        # cleanup
        try:
            if self._use_picamera:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
            else:
                self.cap.release()
            cv2.destroyAllWindows()
        except Exception:
            pass
        log.info('CameraWorker stopped')

    def read(self):
        return self.frame

    def get_latest_annotated_frame(self):
        """Return the latest annotated frame for streaming (thread-safe)."""
        with self._frame_lock:
            return self.annotated_frame.copy() if self.annotated_frame is not None else None

    def stop(self):
        self._stopped = True
