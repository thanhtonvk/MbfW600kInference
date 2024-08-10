import cv2
import os
from modules.FaceDetector import FaceDetector
import numpy as np

class FaceDetection:
    def __init__(self):
        self.model = FaceDetector()

    def detect(self, image):
        faces, bboxes = self.model.detect(image)
        return {'faces': faces, 'boxes': bboxes}

    def save_face(self, id_sv, image:np.ndarray):
        faces = self.detect(image)['faces']
        os.makedirs(f'static/faces/{id_sv}',exist_ok=True)
        if len(faces)>0:
            cv2.imwrite(f"static/faces/{id_sv}/face.png", faces[0])
            return True
        return False
