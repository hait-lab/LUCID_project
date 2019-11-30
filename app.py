#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, redirect
import cv2
import numpy as np
# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_opencv import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/send',methods=['GET', 'POST'])
def send():
    def gen2(camera):
        return camera.get_frame()

    frame = gen2(Camera())
    nparr = np.frombuffer(frame, np.uint8)
    img = cv2.imdecode(nparr,cv2.IMREAD_COLOR)

    cv2.imwrite("test.jpg",img)
    
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
