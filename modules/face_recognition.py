import os
import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import onnx_model_inference

def preprocess(image):
    # Kiểm tra kích thước và màu sắc trước khi tiền xử lý
    # print(f"Original image shape: {image.shape}")
    
    image = cv2.resize(image, (112, 112))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
    image = image / 255.0
    image = image.transpose(2, 0, 1)
    image = np.expand_dims(image, 0)
    
    # Kiểm tra sau khi tiền xử lý
    # print(f"Preprocessed image shape: {image.shape}")
    
    return image

class FaceRecognition:
    def __init__(self, path='models/w600k_mbf.onnx'):
        self.model = onnx_model_inference(path)

    def get_embed(self, face):
        face = preprocess(face)
        output = self.model.run(None, {self.model.get_inputs()[0].name: face})[0]
        # print(f"Shape of embedding: {output.shape}")
        return output
    
    def search_face(self, current_face, nguoi_dungs):
        current_emb = self.get_embed(current_face)
        # print(f"Current embedding shape: {current_emb.shape}")
        
        idx_max = -1
        max_score = 0
        for i, nguoi_dung in enumerate(nguoi_dungs):
            emb = nguoi_dung.Emb
            # print(f"Comparing with embedding for {nguoi_dung.HoTen}: {emb.shape}")
            
            current_emb = current_emb.reshape(1, -1)
            emb = emb.reshape(1, -1)
            
            score = cosine_similarity(current_emb, emb)[0][0]
            # print(f"Similarity score with {nguoi_dung.HoTen}: {score}")
            
            if score > 0.5 and score > max_score:  # Giảm ngưỡng để tăng khả năng tìm thấy khớp
                max_score = score
                idx_max = i
        if idx_max > -1:
            # print(f"Matched with {nguoi_dungs[idx_max].HoTen} with score {max_score}")
            return nguoi_dungs[idx_max]
        # print("No match found")
        return None
