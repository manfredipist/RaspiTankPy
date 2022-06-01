import logging
import board
import adafruit_vl53l1x
from time import sleep

class Laser(object):

    def __init__(self, address):
        self.vl53l1x = adafruit_vl53l1x.VL53L1X(address)

        self.vl53l1x.distance_mode = 1
        self.vl53l1x.timing_budget = 100

        print("VL53L1X COM check")
        print("--------------------")
        model_id, module_type, mask_rev = self.vl53l1x.model_info
        print("Model ID: 0x{:0X}".format(model_id))
        print("Module Type: 0x{:0X}".format(module_type))
        print("Mask Revision: 0x{:0X}".format(mask_rev))
        print("Distance Mode: ", end="")
        if self.vl53l1x.distance_mode == 1:
            print("SHORT")
        elif self.vl53l1x.distance_mode == 2:
            print("LONG")
        else:
            print("UNKNOWN")
        print("Timing Budget: {}".format(self.vl53l1x.timing_budget))
        print("--------------------")

        self.vl53l1x.start_ranging()

    def getMeasurement(self):
        if self.vl53l1x.data_ready:
            self.distance = self.vl53l1x.distance
            self.vl53l1x.clear_interrupt()
            return self.distance