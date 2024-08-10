import numpy as np
import cv2
from config import config
from modules.SCRFD import SCRFD
from skimage import transform


def align_face(cv_img, dst, size=(112, 112)):
    src = np.array([
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041]], dtype=np.float32) * (size[0] / 112)

    tform = transform.SimilarityTransform()
    tform.estimate(dst, src)
    M = tform.params[0:2, :]
    face_img = cv2.warpAffine(cv_img, M, size, borderValue=0.0)
    return face_img


class FaceDetector:
    def __init__(self, ctx_id=0, det_size=(640, 640)):
        self.ctx_id = ctx_id
        self.det_size = det_size
        self.model = SCRFD(model_file=config.MODEL_FACE_DETECTION)
        self.model.prepare()

    def detect(
            self,
            np_image: np.ndarray,
            confidence_threshold=0.5,
    ):
        faces = []
        bboxes = []
        org_image = np_image.copy()
        np_image = cv2.cvtColor(np_image,cv2.COLOR_BGR2RGB)
        predictions = self.model.get(
            np_image, threshold=confidence_threshold, input_size=self.det_size)
        if len(predictions) != 0:
            for _, face in enumerate(predictions):
                bbox = face["bbox"]
                bbox = list(map(int, bbox))
                warped_face = align_face(org_image, face['kps'])
                faces.append(warped_face)
                bboxes.append(bbox)
        return faces, bboxes
