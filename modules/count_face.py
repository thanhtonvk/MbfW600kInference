from modules.SCRFD import SCRFD
import numpy as np
model = SCRFD(model_file="models/scrfd_10g_bnkps.onnx")
model.prepare()


def dem_sl_face(
        np_image: np.ndarray,
        confidence_threshold=0.5,
):
    predictions =model.get(
        np_image, threshold=confidence_threshold, input_size=(640, 640))
    bboxes = []
    if len(predictions) != 0:
        for _, face in enumerate(predictions):
            bbox = face["bbox"]
            bbox = list(map(int, bbox))
            bboxes.append(bbox)
    return bboxes
