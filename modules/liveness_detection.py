from typing import List
import cv2
import numpy as np
from config import config
import cv2
from modules.detector import Detector
from utils import onnx_model_inference


def _get_new_box(image, bbox, scale):
    src_h, src_w, _ = image.shape
    x = bbox[0]
    y = bbox[1]
    box_w = bbox[2] - bbox[0]
    box_h = bbox[3] - bbox[1]
    scale = min((src_h-1)/box_h, min((src_w-1)/box_w, scale))
    new_width = box_w * scale
    new_height = box_h * scale
    center_x, center_y = box_w/2+x, box_h/2+y
    left_top_x = center_x-new_width/2
    left_top_y = center_y-new_height/2
    right_bottom_x = center_x+new_width/2
    right_bottom_y = center_y+new_height/2
    if left_top_x < 0:
        right_bottom_x -= left_top_x
        left_top_x = 0
    if left_top_y < 0:
        right_bottom_y -= left_top_y
        left_top_y = 0
    if right_bottom_x > src_w-1:
        left_top_x -= right_bottom_x-src_w+1
        right_bottom_x = src_w-1
    if right_bottom_y > src_h-1:
        left_top_y -= right_bottom_y-src_h+1
        right_bottom_y = src_h-1
    return int(left_top_x), int(left_top_y), int(right_bottom_x), int(right_bottom_y)


def resize(box):
    left, top, right, bottom = box
    w = (right - left)
    h = (bottom - top)
    if h > w:
        sub_size = h-w
        left -= int(sub_size/2)
        right += int(sub_size/2)
    else:
        sub_size = w-h
        top -= int(sub_size/2)
        bottom += int(sub_size/2)
    return left, top, right, bottom


def get_max(boxes):
    max = 0
    result = None
    for box in boxes:
        left, top, right, bottom = box
        w = (right - left)
        h = (bottom - top)
        area = w*h
        if area > max:
            max = area
            result = box
    return result


def load_model(eval_model):
    net = onnx_model_inference(eval_model)
    return net


def img_resize(img, smax=360):
    h, w, _ = img.shape
    m = min(h, w)
    if m > smax:
        if m == h:
            r = smax / h
        else:
            r = smax / w
    else:
        r = 1
    w = int(w*r)
    h = int(h*r)
    img = cv2.resize(img, (w, h))
    return img


def resize_1_0(box):
    expand_ratio = (1.1, 1.05)
    left, top, right, bottom = box
    w = (right - left)
    h = (bottom - top)
    dw = w * (expand_ratio[0] - 1.) / 2
    dh = h * (expand_ratio[1] - 1.) / 2
    left = max(int(left - dw), 0)
    right = int(right + dw)
    top = max(int(top - dh), 0)
    bottom = int(bottom + dh)
    return left, top, right, bottom


class LivenessDetection:

    MEAN = [0.5, 0.5, 0.5]
    STD = [0.5, 0.5, 0.5]

    def __init__(self, eval_model_1=config.MODEL_FACE_LIVENESS_CROP_1_0, eval_model_2=config.MODEL_FACE_LIVENESS_CROP_2_7):
        self.eval_model_1 = eval_model_1
        self.eval_model_2 = eval_model_2
        self.model_crop_1_0 = load_model(self.eval_model_1)
        self.model_crop_2_0 = load_model(self.eval_model_2)
        self.detector = Detector()

    def __preprocessing(self, face: np.ndarray, mode=1.0):
        SIZE = (128, 128)
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(
            face, SIZE, interpolation=cv2.INTER_CUBIC).astype('float')
        face /= 255.0
        face = (face - self.MEAN) / self.STD
        face = face.transpose((2, 0, 1)).astype(np.float32)
        face = np.expand_dims(face, 0)
        return face

    def predict(self, image: np.ndarray):
        image = img_resize(image)
        boxes = self.detector.detect(image)
        box = get_max(boxes)
        if box is None:
            return '', False
        box = [int(i) for i in box]
        left, top, right, bottom = box
        face_width = int(right-left)
        face_height = int(bottom-top)
        if face_width < 80 or face_height < 80:
            return "DUA MAT GAN HON", False
        if face_width > 230 or face_height > 230:
            return "DUA MAT RA XA HON", False

        left, top, right, bottom = resize_1_0(box)
        left, top, right, bottom = _get_new_box(
            image, (left, top, right, bottom), 1.0)
        face = image[top:bottom, left:right]
        face = self.__preprocessing(face, mode=1.0)
        ort_input = {self.model_crop_1_0.get_inputs()[0].name: face}
        ort_out = self.model_crop_1_0.run(None, ort_input)[0]
        score = float(ort_out[0][1].item())
        if score > 0.5:
            return score, False
        left, top, right, bottom = resize(box)
        left, top, right, bottom = _get_new_box(
            image, (left, top, right, bottom), 2.7)
        face = image[top:bottom, left:right]
        face = self.__preprocessing(face, mode=2.7)
        ort_input = {self.model_crop_2_0.get_inputs()[0].name: face}
        ort_out = self.model_crop_2_0.run(None, ort_input)[0]
        score = float(ort_out[0][1].item())
        if score > 0.5:
            return score, False
        else:
            return score, True
