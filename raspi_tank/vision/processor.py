"""Frame processing: obstacle overlay and QR decoding using OpenCV."""
import logging
import cv2
import numpy as np

log = logging.getLogger('Processor')

class FrameProcessor:
    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()
        self.last_qr_data = None

    def analyze(self, frame, sensors=None):
        """Analyze a frame. Returns annotated frame and a dict with analysis results."""
        results = {'qr_data': None, 'obstacle': False}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # QR detection
        data, points, _ = self.qr_detector.detectAndDecode(frame)
        if data:
            results['qr_data'] = data
            self.last_qr_data = data
            if points is not None:
                pts = points.astype(int).reshape((-1,2))
                cv2.polylines(frame, [pts], isClosed=True, color=(0,255,0), thickness=2)
                cv2.putText(frame, data, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        else:
            # Clear last QR data after 2 seconds (approximate)
            pass

        # Simple obstacle visual indicator using sensors front distance if provided
        if sensors is not None:
            try:
                front = sensors.front.distance
                if front is not None:
                    cv2.putText(frame, f'Front: {front:.1f} cm', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,200), 2)
                    if front < 40:
                        results['obstacle'] = True
                        cv2.putText(frame, 'OBSTACLE!', (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)
            except Exception:
                pass

        # Additional visual processing: edges
        edges = cv2.Canny(gray, 50, 150)
        # blend edges on top-left corner as a small thumbnail
        h, w = frame.shape[:2]
        th, tw = int(h*0.25), int(w*0.25)
        small_edges = cv2.resize(edges, (tw, th))
        small_edges_col = cv2.cvtColor(small_edges, cv2.COLOR_GRAY2BGR)
        frame[0:th, 0:tw] = small_edges_col

        return frame, results
