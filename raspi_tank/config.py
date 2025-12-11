# Simple configuration used by modules

camera = {
    'resolution': (640, 480),
    'framerate': 30,
    'show_window': False,  # uses cv2.imshow -> requires X11/XQuartz forwarding to mac, set False for headless
    'enable_mjpeg_stream': True,  # enable Flask MJPEG streaming on port 5000
    'stream_host': '0.0.0.0',
    'stream_port': 5000
}

laser = {
    'front_threshold_cm': 40,  # if object closer than this, consider obstacle
}

motor = {
    'left_pins': {'en':13, 'in_1':26, 'in_2':19},
    'right_pins': {'en':21, 'in_1':16, 'in_2':20}
}

safety = {
    'sensor_timeout_s': 2.5
}
