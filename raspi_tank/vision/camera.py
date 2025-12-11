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

        # try picamera2 first, fallback to cv2.VideoCapture
        try:
            from picamera2 import Picamera2
            self._use_picamera = True
            self.camera = Picamera2()
            
            # Configure camera for video mode
            config = self.camera.create_video_configuration(
                main={"size": camera_conf['resolution'], "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            log.info('Using Picamera2')
        except Exception as e:
            log.warning(f'Picamera2 not available: {e}')
            self._use_picamera = False
            self.cap = cv2.VideoCapture(0)
            if camera_conf['resolution']:
                w, h = camera_conf['resolution']
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            log.info('Using cv2.VideoCapture')

    def start(self):
        log.info('CameraWorker started')
        frame_count = 0
        if self._use_picamera:
            log.info('Using Picamera2 for frame capture')
            while not self._stopped:
                try:
                    # Capture frame from picamera2
                    frame = self.camera.capture_array()
                    # Convert RGB to BGR for OpenCV compatibility
                    self.frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    annotated, results = self.processor.analyze(self.frame, self.sensors)
                    with self._frame_lock:
                        self.annotated_frame = annotated.copy()
                    
                    frame_count += 1
                    if frame_count == 1:
                        log.info('First camera frame captured successfully!')
                    elif frame_count % 100 == 0:
                        log.debug('Camera captured %d frames', frame_count)
                    
                    if camera_conf.get('show_window', False):
                        cv2.imshow('RaspiTank', annotated)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                except Exception as e:
                    log.exception('Error capturing/processing frame: %s', e)
                    time.sleep(0.1)
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
                self.camera.stop()
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
