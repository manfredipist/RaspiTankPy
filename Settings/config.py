camera_selection = "picamera_v2_vga"

camera_configurations = {
    "picamera_v2_vga": {
        "id": "picamera_v2_vga",
        "fisheye": True,
        "canny_auto_levels": True,
        "stream_canny": False,
        "camera_x": 640,
        "camera_y": 480,
        "framerate": 90,
        "canny_params": {"upper": 160,
                         "lower": 40},
        "hough_params": {"minLineLength": 100,
                         "maxLineGap": 5,
                         "probabilistic": True},
    },
}

laser_configuration = {
    "right_vl53l1x": {
        "bus": 4
    },
    "front_vl53l1x": {
        "bus": 5
    },
    "left_vl53l1x": {
        "bus": 6
    }
}

accelerometergyroscope_configuration = {
    "bus": 3
}

motor_configuration = {
    "right_engine": {
        "en": 21,
        "in_1": 16,
        "in_2": 20
    },
    "left_engine": {
        "en": 13,
        "in_1": 26,
        "in_2": 19
    }
}