import cv2
import unidecode
from dal.NguoiDungDal import NguoiDungDal
from modules.face_detection import FaceDetection
from modules.face_recognition import FaceRecognition

if __name__ == '__main__':
    face_detector = FaceDetection()
    face_recognition = FaceRecognition()

    nguoi_dung_dal = NguoiDungDal()
    nguoi_dungs = nguoi_dung_dal.get()

    vid = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    count = 0
    while (True):
        # Capture the video frame
        # by frame
        ret, frame = vid.read()
        predict = face_detector.detect(frame)
        boxes = predict['boxes']
        faces = predict['faces']
        for idx, (x, y, w, h) in enumerate(boxes):
            cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
            face = faces[idx]
            nguoi_dung = face_recognition.search_face(face, nguoi_dungs)
            if nguoi_dung is not None:
                cv2.putText(frame, f"ID:{nguoi_dung.Id} {unidecode.unidecode(nguoi_dung.HoTen)}",
                            (x, y), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Face Recognition', frame)
        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()
