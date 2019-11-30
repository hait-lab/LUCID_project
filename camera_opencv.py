import os
import cv2
from base_camera import BaseCamera


#前処理関数
def preprocessing(img):
    # 前処理が必要な場合はここに追記

    #リサイズ
    img = cv2.resize(img, (480,360))

    return img


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            _, img = camera.read()

            #前処理
            img = preprocessing(img)

            yield cv2.imencode('.jpg', img)[1].tobytes()
   