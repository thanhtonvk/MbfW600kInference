import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import pygame
from time import time, strftime, sleep
import torch
import requests
import os
from datetime import datetime
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Hàm phát âm thanh cảnh báo
def play_sound(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    print("Playing sound...")

# Hàm tắt âm thanh sau 1 giây
def stop_sound():
    sleep(1)
    pygame.mixer.music.stop()
    print("Sound stopped...")

# Hàm gửi tin nhắn Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)

# Hàm gửi ảnh Telegram
def send_telegram_photo(bot_token, chat_id, photo_path):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {'photo': open(photo_path, 'rb')}
    payload = {
        'chat_id': chat_id
    }
    requests.post(url, files=files, data=payload)

class ObjectDetection:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.model.names
        self.box_annotator = sv.BoxAnnotator(sv.ColorPalette.default(), thickness=3, text_thickness=3, text_scale=1.5)
        self.polygon_points = []  # Danh sách để lưu các điểm của đa giác
        self.current_polygon = 0  # Biến để theo dõi đa giác hiện tại
        self.alarm_triggered = False  # Trạng thái của âm báo
        self.alarm_start_time = 0  # Thời gian bắt đầu của âm báo
        self.warning_count = 0  # Đếm số lần cảnh báo

        # Telegram bot token và chat_id
        self.bot_token = '7233650823:AAGr1Cmpr56o4NBdJFyloFUDfltqjnA1dwA'
        self.chat_id = '7131930827'

        # Tạo thư mục để lưu video và âm thanh
        self.video_output_dir = os.path.join("videos", datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.video_output_dir, exist_ok=True)
        self.video_writer = None
        self.frame_size = None
        self.audio_clips = []

    # Hàm tải mô hình
    def load_model(self):
        model = YOLO("models/troms.pt")  # Tải mô hình YOLOv8 đã huấn luyện sẵn
        model.to(self.device)
        return model

    # Hàm dự đoán
    def predict(self, frame):
        if not isinstance(frame, np.ndarray):
            raise TypeError("Input frame must be a numpy array")
        results = self.model(frame, conf=0.25)
        return results

    # Hàm vẽ hộp bao quanh và kiểm tra đối tượng trong đa giác
    def plot_bboxes(self, results, frame):
        xyxys = []
        confidences = []
        class_ids = []

        # Chỉ hiển thị các phát hiện cho lớp "mask" và "person"
        target_classes = ["mask", "person"]

        # Trích xuất các phát hiện cho mỗi kết quả
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                if self.CLASS_NAMES_DICT[class_id] in target_classes:
                    xyxys.append(box.xyxy.cpu().numpy().reshape(1, -1))
                    confidences.append(box.conf.cpu().numpy().reshape(-1))
                    class_ids.append(class_id)

        # Chuyển đổi danh sách thành mảng NumPy
        if xyxys:
            xyxys = np.concatenate(xyxys, axis=0).reshape(-1, 4)
            confidences = np.concatenate(confidences, axis=0)
            class_ids = np.array(class_ids)

            # Kiểm tra và chỉ hiển thị các đối tượng nằm trong các đa giác
            valid_detections = []
            valid_labels = []
            count_in_polygons = [0] * len(self.polygon_points)
            for i, polygon in enumerate(self.polygon_points):
                if len(polygon) >= 5:  # Chỉ kiểm tra nếu đa giác có ít nhất 5 điểm
                    polygon = np.array(polygon, dtype=np.int32)
                    for xyxy, confidence, class_id in zip(xyxys, confidences, class_ids):
                        x_center = (xyxy[0] + xyxy[2]) / 2
                        y_center = (xyxy[1] + xyxy[3]) / 2
                        if self.point_in_polygon(x_center, y_center, polygon):
                            valid_detections.append((xyxy, confidence, class_id))
                            # Thay đổi nhãn dựa trên đa giác
                            if i == 0:
                                valid_labels.append(f"tai_xe {int(confidence * 100)}%")
                            elif i == 1:
                                valid_labels.append(f"tre_em {int(confidence * 100)}%")
                            elif i == 2:
                                valid_labels.append(f"khach {int(confidence * 100)}%")
                            count_in_polygons[i] += 1

            print(f"Number of targets in polygons: {count_in_polygons}")

            # Chỉ cảnh báo nếu đa giác 2 có đúng 1 người và các đa giác khác không có người
            if len(count_in_polygons) > 1 and count_in_polygons[1] == 1 and all(count == 0 for idx, count in enumerate(count_in_polygons) if idx != 1):
                threading.Thread(target=self.trigger_alarm, args=(frame,)).start()

            # Thiết lập các phát hiện hợp lệ để trực quan hóa
            if valid_detections:
                xyxys, confidences, class_ids = zip(*valid_detections)
                detections = sv.Detections(
                    xyxy=np.array(xyxys),
                    confidence=np.array(confidences),
                    class_id=np.array(class_ids),
                )
                # Ghi chú và hiển thị khung hình với các phát hiện hợp lệ
                frame = self.box_annotator.annotate(scene=frame, detections=detections, labels=valid_labels)

            # Vẽ tâm đối tượng với màu đỏ
            for xyxy in xyxys:
                x_center = int((xyxy[0] + xyxy[2]) / 2)
                y_center = int((xyxy[1] + xyxy[3]) / 2)
                cv2.circle(frame, (x_center, y_center), radius=5, color=(0, 0, 255), thickness=-1)  # Vẽ vòng tròn đỏ tại tâm đối tượng

        # Vẽ các điểm dấu chấm và đa giác trên khung hình
        for i, polygon in enumerate(self.polygon_points):
            if len(polygon) > 0:
                for point in polygon:
                    cv2.circle(frame, tuple(point), radius=5, color=(255, 0, 0), thickness=-1)  # Vẽ dấu chấm màu xanh
                if len(polygon) >= 5:
                    cv2.polylines(frame, [np.array(polygon, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)  # Vẽ đường kẻ màu xanh lá cây

        # Tắt âm báo sau 1 giây
        if self.alarm_triggered and time() - self.alarm_start_time > 1:
            pygame.mixer.music.stop()
            self.alarm_triggered = False

        return frame

    # Hàm kiểm tra nếu một điểm nằm trong đa giác
    def point_in_polygon(self, x, y, polygon):
        result = cv2.pointPolygonTest(polygon, (x, y), False)
        print(f"pointPolygonTest result: {result}")
        return result >= 0

    # Hàm phát cảnh báo và gửi tin nhắn Telegram
    def trigger_alarm(self, frame):
        if not self.alarm_triggered:
            play_sound('Alarm/alarm.wav')
            message = "Cảnh báo! Có trẻ ở trên ô tô!"
            print("Cảnh báo! Có trẻ ở trên ô tô!")

            self.alarm_triggered = True
            self.alarm_start_time = time()

            # Gửi tin nhắn và ảnh về Telegram
            send_telegram_message(self.bot_token, self.chat_id, message)
            image_path = os.path.join(self.video_output_dir, f'alert_frame_{int(self.alarm_start_time)}.jpg')
            cv2.imwrite(image_path, frame)
            send_telegram_photo(self.bot_token, self.chat_id, image_path)

            # Bắt đầu luồng để tắt âm báo sau 1 giây
            threading.Thread(target=stop_sound).start()

    # Hàm gọi đối tượng
    def __call__(self, frame):
        results = self.predict(frame)
        frame = self.plot_bboxes(results, frame)

        # Kiểm tra và khởi tạo VideoWriter nếu cần thiết
        if self.video_writer is None:
            self.frame_size = (frame.shape[1], frame.shape[0])
            video_path = os.path.join(self.video_output_dir, 'detected_video.avi')
            self.video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, self.frame_size)

        # Ghi khung hình vào video
        self.video_writer.write(frame)

        return frame

    def release_video_writer(self):
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

        # Kết hợp âm thanh cảnh báo với video
        self.combine_audio_video()

    # Hàm kết hợp âm thanh và video
    def combine_audio_video(self):
        video_path = os.path.join(self.video_output_dir, 'detected_video.avi')
        final_video_path = os.path.join(self.video_output_dir, 'final_detected_video.mp4')

class Camera:
    def __init__(self, video_source):
        self.video = cv2.VideoCapture(video_source)  # Use 0 for the default camera
        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None
        return frame

# Định nghĩa một lớp cho GUI
class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG PHÁT HIỆN VÀ CẢNH BÁO TRẺ EM BỊ BỎ QUÊN TRÊN XE Ô TÔ")

        self.video_source = "Test Videos/thief_video3.mp4"  # Default video source
        self.detector = ObjectDetection()
        self.camera = Camera(self.video_source)

        # Biến lưu tỷ lệ phóng to, thu nhỏ
        self.zoom_level = 1.0

        # Biến trạng thái để kiểm tra xem video đã được khởi động hay chưa
        self.video_started = False

        # Tạo một canvas để hiển thị các khung hình video với kích thước cố định 800x500 và khung màu xanh lá cây
        self.canvas = tk.Canvas(root, width=800, height=500, bg="green", highlightthickness=5, highlightbackground="green")
        self.canvas.pack(pady=10)

        # Frame to hold the buttons
        button_frame = tk.Frame(root, bg="white")
        button_frame.pack(pady=10)

        # Tạo các nút điều khiển
        button_style = {"bg": "yellow", "fg": "darkblue", "font": ("Helvetica", 16, "bold"), "height": 1, "anchor": "center"}

        self.btn_select_video = tk.Button(button_frame, text="Video", width=8, **button_style, command=self.select_video)
        self.btn_select_video.grid(row=0, column=0, padx=3)

        self.btn_camera = tk.Button(button_frame, text="Camera", width=8, **button_style, command=self.start_camera)
        self.btn_camera.grid(row=0, column=1, padx=3)

        self.btn_zoom_in = tk.Button(button_frame, text="Phóng to", width=8, **button_style, command=self.zoom_in)
        self.btn_zoom_in.grid(row=0, column=2, padx=3)

        self.btn_zoom_out = tk.Button(button_frame, text="Thu nhỏ", width=8, **button_style, command=self.zoom_out)
        self.btn_zoom_out.grid(row=0, column=3, padx=3)

        self.btn_quit = tk.Button(button_frame, text="Thoát", width=8, **button_style, command=root.quit)
        self.btn_quit.grid(row=0, column=4, padx=3)

        # Thiết lập callback chuột để chọn các điểm và khởi động video khi nhấp chuột
        self.canvas.bind("<Button-1>", self.mouse_callback)
        self.canvas.bind("<Button-3>", self.clear_polygon)  # Thêm sự kiện chuột phải

        # Khởi tạo các biến để tính FPS
        self.prev_time = time()

        # Bắt đầu vòng lặp video
        self.update_frame()

    def select_video(self):
        video_path = filedialog.askopenfilename()
        if video_path:
            self.camera = Camera(video_path)
            self.video_started = True

    def start_camera(self):
        self.camera = Camera(0)  # Sử dụng 0 để sử dụng camera mặc định
        self.video_started = True

    def mouse_callback(self, event):
        if not self.video_started:
            self.video_started = True
            return

        if len(self.detector.polygon_points) >= 100:
            print("Only 100 polygons allowed.")
            return

        # Tính tỷ lệ thu phóng
        x_ratio = self.camera.width / (800 * self.zoom_level)
        y_ratio = self.camera.height / (500 * self.zoom_level)
        # Điều chỉnh tọa độ khi click chuột
        x, y = int(event.x * x_ratio), int(event.y * y_ratio)
        if self.detector.current_polygon >= len(self.detector.polygon_points):
            self.detector.polygon_points.append([])
        self.detector.polygon_points[self.detector.current_polygon].append((x, y))
        print(f"Point added to polygon {self.detector.current_polygon + 1}: {(x, y)}")

        # Kiểm tra nếu đủ điều kiện để tạo đa giác (ít nhất 5 điểm)
        if len(self.detector.polygon_points[self.detector.current_polygon]) >= 5:
            self.detector.current_polygon += 1

    def clear_polygon(self, event):
        self.detector.polygon_points = []
        self.detector.current_polygon = 0
        print("Polygons cleared")

    def zoom_in(self):
        self.zoom_level *= 1.2
        new_width = int(800 * self.zoom_level)
        new_height = int(500 * self.zoom_level)
        self.canvas.config(width=new_width, height=new_height)
        print(f"Zoom level: {self.zoom_level}, Canvas size: {new_width}x{new_height}")

    def zoom_out(self):
        self.zoom_level /= 1.2
        new_width = int(800 * self.zoom_level)
        new_height = int(500 * self.zoom_level)
        self.canvas.config(width=new_width, height=new_height)
        print(f"Zoom level: {self.zoom_level}, Canvas size: {new_width}x{new_height}")

    def update_frame(self):
        if self.video_started:
            frame = self.camera.get_frame()
            if frame is not None:
                # Gọi hàm phát hiện đối tượng
                frame = self.detector(frame)

                # Thay đổi kích thước khung hình để phù hợp với canvas
                frame = cv2.resize(frame, (int(800 * self.zoom_level), int(500 * self.zoom_level)))

                # Tính FPS
                current_time = time()
                fps = 1 / (current_time - self.prev_time)
                self.prev_time = current_time

                # Hiển thị FPS trên khung hình
                cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Chuyển đổi khung hình thành ảnh cho Tkinter
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # Cập nhật canvas với khung hình mới
                self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
                self.canvas.image = image

        self.root.after(10, self.update_frame)

# Hàm chính để khởi động ứng dụng
def main():
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
