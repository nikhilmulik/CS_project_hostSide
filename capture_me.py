import os
import cv2
import time


def cap_pic():
    camera_port = 0
    ramp_frames = 30
    if not os.path.exists('caps'):
        os.makedirs('caps')
    camera = cv2.VideoCapture(camera_port)
    for i in xrange(ramp_frames):
        temp = camera.read()[1]
    print("Capturing image...")
    camera_capture = camera.read()[1]
    filename = 'caps\intrusion_%s.png' % time.strftime('%b_%d_%Y_%H-%M-%S')
    cv2.imwrite(filename, camera_capture)
    del(camera)
    return os.path.abspath(filename)

print cap_pic()