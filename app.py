from importlib import import_module
import os
from random import randint
from datetime import datetime
from flask import Flask, render_template, Response, redirect,send_from_directory,request
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

def tempmath(img_path,temp_path,threshold = 0.5):
    img = cv2.imread(img_path,0)
    temp = cv2.imread(temp_path,0)
    #マッチングテンプレートを実行
    result = cv2.matchTemplate(img, temp, cv2.TM_CCOEFF_NORMED)
    #検出結果から検出領域の位置を取得
    loc = np.where(result >= threshold)
    #検出領域を四角で囲んで保存
    result = cv2.imread(img_path)
    w, h = temp.shape[::-1]
    bias = 20
    for top_left in zip(*loc[::-1]):
        bottom_right = (top_left[0] + w-bias, top_left[1] + h-bias)
        cv2.rectangle(result,(top_left[0]+bias,top_left[1]+bias), bottom_right, (0, 0, 255), 5)

    cv2.imwrite(img_path[:-4]+temp_path[7:],result)
    return img_path[:-4]+temp_path[7:]
@app.route('/STANDARD',methods=['GET', 'POST'])
def standard():
    if request.method == 'POST':
        res = request.form['get_value']  
        standard_path = tempmath(res,'static/standard.png')

    return render_template('index.html',original_url=res,standard_url=standard_path)

@app.route('/LUCID',methods=['GET', 'POST'])
def lucid():
    if request.method == 'POST':
        res2 = request.form['get_value']  
        lucid_path = tempmath(res2,'static/lucid.png')

    return render_template('index.html',original_url=res2,lucid_url=lucid_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
