from importlib import import_module
import os
from random import randint
from datetime import datetime
from flask import Flask, render_template, Response, redirect,send_from_directory
import cv2
import numpy as np

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_opencv import Camera

app = Flask(__name__)
SAVE_DIR='uploads'

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


@app.route('/send')
def send():
    def gen2(camera):
        return camera.get_frame()

    frame = gen2(Camera())
    nparr = np.frombuffer(frame, np.uint8)
    img = cv2.imdecode(nparr,cv2.IMREAD_COLOR)

    dt_now = datetime.now().strftime("%Y_%m_%d%_H_%M_%S_") + str(randint(0,10))
    save_path = os.path.join(SAVE_DIR, dt_now + ".jpg")
    cv2.imwrite(save_path,img)
    return render_template('index.html',img_url=save_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
