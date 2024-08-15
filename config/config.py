# config.py

DB_HOST = 'localhost'        # Địa chỉ máy chủ MySQL (ví dụ: 'localhost' nếu chạy trên máy cục bộ)
DB_USER = 'root'    # Tên đăng nhập MySQL của bạn
DB_PASSWORD = '' # Mật khẩu MySQL của bạn
DB_NAME = 'face_recognizer'    # Tên cơ sở dữ liệu bạn sử dụng
MODEL_FACE_DETECTION = 'models/scr_face_detector.onnx'
MODEL_FACE_LIVENESS = 'models/MobileNetv3_2_7.onnx'
DATABASE = 'database/database.sqlite'