import logging
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep

from Settings import config


class VideoCamera(object):

    def __init__(self, resolution=(320, 240), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
        # grab the frame from the stream and clear the stream in
        # preparation for the next frame
            self.frame = f.array

            cv2.imshow("video", self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): # wait for 1 millisecond
                    break
                
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True