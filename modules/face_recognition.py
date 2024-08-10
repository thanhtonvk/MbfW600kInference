import os

import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from utils import onnx_model_inference


def preprocess(image):
    image = cv2.resize(image,(112,112))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
    image = image / 255.0
    image = image.transpose(2, 0, 1)
    image = np.expand_dims(image, 0)
    return image


class FaceRecognition:
    def __init__(self, path='models/w600k_mbf.onnx'):
        self.model = onnx_model_inference(path)

    def get_embed(self, face):
        face = preprocess(face)
        output = self.model.run(None, {self.model.get_inputs()[0].name: face})[0]
        return output
    
    def search_face(self, current_face, nguoi_dungs):
        current_emb = self.get_embed(current_face)
        idx_max = -1
        max_score = 0
        for i,nguoi_dung in enumerate(nguoi_dungs):
            emb = nguoi_dung.Emb
            score = cosine_similarity(current_emb,emb)
            if score>0.5 and score>max_score:
                max_score = score
                idx_max = i
        if idx_max>-1:
            return nguoi_dungs[idx_max]
        return None