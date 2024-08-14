import tkinter as tk
from tkinter import filedialog
import cv2
import threading
import time
import numpy as np
from ultralytics import YOLO
import torch
import pygame
import requests
import psutil
import unidecode
import subprocess  # Thêm thư viện để chạy file
from dal.NguoiDungDal import NguoiDungDal
# from dal.NguoiDungDalSqlite import NguoiDungDal
from modules.face_detection import FaceDetection
from modules.face_recognition import FaceRecognition
from PIL import Image, ImageTk
from objects.Checkin import Checkin
from dal.CheckinDal import CheckinDal
from objects.NguoiDung import NguoiDung
import threading
# Initialize pygame for sound playback
pygame.init()
pygame.mixer.init()

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = '7233650823:AAGr1Cmpr56o4NBdJFyloFUDfltqjnA1dwA'
TELEGRAM_CHAT_ID = '7131930827'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
TELEGRAM_PHOTO_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'


class ObjectDetection:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.names

    def load_model(self):
        model = YOLO("models/tromm.pt")
        model.to(self.device)
        return model

    def detect_objects(self, frame):
        results = self.model(frame)
        xyxys = []
        confidences = []
        class_ids = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                if self.CLASS_NAMES_DICT[class_id] in ["mask", "person"]:
                    xyxys.append(box.xyxy.cpu().numpy().flatten())
                    confidences.append(box.conf.cpu().numpy().item())
                    class_ids.append(class_id)

        if xyxys:
            xyxys = np.array(xyxys)
            confidences = np.array(confidences)
            class_ids = np.array(class_ids)

            for (xyxy, confidence, class_id) in zip(xyxys, confidences, class_ids):
                if xyxy.size == 4:
                    x1, y1, x2, y2 = map(int, xyxy)
                    label = f"{self.CLASS_NAMES_DICT[class_id]} {int(confidence * 100)}%"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    x_center = (x1 + x2) // 2
                    y_center = (y1 + y2) // 2
                    cv2.circle(frame, (x_center, y_center), 5, (0, 0, 255), -1)

        return frame, xyxys, confidences, class_ids


class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Camera Interface")
        self.geometry("1920x1080")

        # Load and set the background image
        self.background_image = Image.open("hugo.jpg")
        self.background_image = self.background_image.resize(
            (self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Add logo at the top left
        self.logo_image = Image.open("logo.png")
        self.logo_image = self.logo_image.resize(
            (100, 100), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo, bg="#2c3e50")
        self.logo_label.place(x=20, y=10)

       # Create a title frame with an inner red border
        self.title_frame = tk.Frame(self, bg="#00BFFF", bd=10, relief="ridge")
        self.title_frame.place(x=320, y=20, width=900, height=90)

        self.title_label = tk.Label(self.title_frame, text="HỆ THỐNG THÔNG MINH TRÊN XE ĐƯA ĐÓN HỌC SINH", font=(
            "Helvetica", 24, "bold"), fg="#FF0000", bg="#F5F5F5")
        self.title_label.pack(padx=20, pady=20)

        # Khởi tạo các đối tượng cho nhận diện khuôn mặt và nhận diện đối tượng
        self.face_detector = FaceDetection()
        self.face_recognition = FaceRecognition()

        self.object_detection = ObjectDetection()
        self.video_source_left = 0
        self.video_source_right = 0
        self.cap_left = None
        self.cap_right = None
        self.running_left = False
        self.running_right = False
        self.lock_left = threading.Lock()
        self.lock_right = threading.Lock()

        self.font_large = ("Helvetica", 16, "bold")
        self.font_small = ("Helvetica", 12)

        button_width = 15
        button_height = 2

        # Camera frame 1
        self.frame_camera1 = tk.Frame(self, width=700, height=500, bg="#00BFFF", bd=10, relief="solid",
                                      highlightbackground="#00BFFF", highlightcolor="#00BFFF", highlightthickness=4)
        self.frame_camera1.place(x=45, y=140)

        # Camera frame 2
        self.frame_camera2 = tk.Frame(self, width=700, height=500, bg="#00BFFF", bd=10, relief="solid",
                                      highlightbackground="#00BFFF", highlightcolor="#00BFFF", highlightthickness=4)
        self.frame_camera2.place(x=775, y=140)

        # Buttons frame 1
        self.frame_buttons1 = tk.Frame(self, bg="#2c3e50")
        self.frame_buttons1.place(x=73, y=680)

        self.button_camera1 = tk.Button(self.frame_buttons1, text="Camera", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                        width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.start_camera_left)
        self.button_camera1.pack(side=tk.LEFT, padx=10)

        self.button_video1 = tk.Button(self.frame_buttons1, text="Video", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                       width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.load_video_left)
        self.button_video1.pack(side=tk.LEFT, padx=10)

        self.button_connect1 = tk.Button(self.frame_buttons1, text="Kết nối", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                         width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.run_nhapanh)
        self.button_connect1.pack(side=tk.LEFT, padx=10)

        self.button_exit1 = tk.Button(self.frame_buttons1, text="Exit", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                      width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.quit)
        self.button_exit1.pack(side=tk.LEFT, padx=10)

        self.frame_buttons3 = tk.Frame(self, bg="#2c3e50")
        self.frame_buttons3.place(x=73, y=780)

        self.button_camera1 = tk.Button(self.frame_buttons3, text="Bắt đầu checkin", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                        width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.startCheckin)
        self.button_camera1.pack(side=tk.LEFT, padx=10)

        self.button_video1 = tk.Button(self.frame_buttons3, text="Kết thúc checkin", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                       width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.endCheckin)
        self.button_video1.pack(side=tk.LEFT, padx=10)

        self.button_camera1 = tk.Button(self.frame_buttons3, text="Bắt đầu checkout", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                        width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.startCheckout)
        self.button_camera1.pack(side=tk.LEFT, padx=10)

        self.button_video1 = tk.Button(self.frame_buttons3, text="Kết thúc checkout", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                       width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.endCheckout)
        self.button_video1.pack(side=tk.LEFT, padx=10)

        # Buttons frame 2
        self.frame_buttons2 = tk.Frame(self, bg="#2c3e50")
        self.frame_buttons2.place(x=800, y=680)

        self.button_camera2 = tk.Button(self.frame_buttons2, text="Camera", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                        width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.start_camera_right)
        self.button_camera2.pack(side=tk.LEFT, padx=10)

        self.button_video2 = tk.Button(self.frame_buttons2, text="Video", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                       width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.load_video_right)
        self.button_video2.pack(side=tk.LEFT, padx=10)

        self.button_connect2 = tk.Button(self.frame_buttons2, text="Kết nối", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                         width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.connect_camera_right)
        self.button_connect2.pack(side=tk.LEFT, padx=10)

        self.button_exit2 = tk.Button(self.frame_buttons2, text="Exit", font=self.font_small, bg="#1abc9c", fg="#ffffff",
                                      width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.quit)
        self.button_exit2.pack(side=tk.LEFT, padx=10)

        self.add_hover_effects([self.button_camera1, self.button_video1, self.button_connect1, self.button_exit1,
                                self.button_camera2, self.button_video2, self.button_connect2, self.button_exit2])

        # Canvas for Camera 1
        self.canvas_left = tk.Canvas(
            self.frame_camera1, width=680, height=480, bg="#34495e")
        self.canvas_left.pack()

        # Canvas for Camera 2
        self.canvas_right = tk.Canvas(
            self.frame_camera2, width=680, height=480, bg="#34495e")
        self.canvas_right.pack()

        self.fps_start_time_left = time.time()
        self.fps_start_time_right = time.time()
        self.frame_count_left = 0
        self.frame_count_right = 0

        self.points_left = []
        self.polygons_left = []

        self.points_right = []
        self.polygons_right = []

        self.canvas_left.bind("<Button-1>", self.add_point_left)
        self.canvas_right.bind("<Button-1>", self.add_point_right)

        self.canvas_left.bind("<Button-3>", self.clear_polygons_left)
        self.canvas_right.bind("<Button-3>", self.clear_polygons_right)

        # Initialize the list of users
        self.nguoi_dung_dal = NguoiDungDal()
        self.nguoi_dungs = self.nguoi_dung_dal.get()
        self.checkin_dal = CheckinDal()
        self.mode = 'NONE'

    def run_nhapanh(self):
        subprocess.Popen(["python", "nhapanh.py"])

    def add_hover_effects(self, buttons):
        for button in buttons:
            button.bind("<Enter>", self.on_enter)
            button.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        event.widget.config(fg="#2980b9")

    def on_leave(self, event):
        event.widget.config(fg="#ffffff")

    def start_camera_left(self):
        if not self.running_left:
            self.running_left = True
            threading.Thread(target=self.process_left, daemon=True).start()

    def load_video_left(self):
        video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")])
        if video_path:
            if self.running_left:
                self.running_left = False
                time.sleep(1)  # Wait for the previous thread to close
            threading.Thread(target=self.process_video_left,
                             args=(video_path,), daemon=True).start()

    def connect_camera_left(self):
        pass

    def start_camera_right(self):
        if not self.running_right:
            self.running_right = True
            threading.Thread(target=self.process_right, daemon=True).start()

    def load_video_right(self):
        video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")])
        if video_path:
            if self.running_right:
                self.running_right = False
                time.sleep(1)  # Wait for the previous thread to close
            threading.Thread(target=self.process_video_right,
                             args=(video_path,), daemon=True).start()

    def connect_camera_right(self):
        pass

    def add_point_left(self, event):
        x, y = event.x, event.y
        self.points_left.append((x, y))
        self.canvas_left.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')

        if len(self.points_left) >= 4:
            polygon_coords = self.points_left.copy()
            self.polygons_left.append(polygon_coords)
            self.canvas_left.create_polygon(
                polygon_coords, outline='blue', fill='', width=2)
            self.points_left = []

    def add_point_right(self, event):
        x, y = event.x, event.y
        self.points_right.append((x, y))
        self.canvas_right.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')

        if len(self.points_right) >= 4:
            polygon_coords = self.points_right.copy()
            self.polygons_right.append(polygon_coords)
            self.canvas_right.create_polygon(
                polygon_coords, outline='blue', fill='', width=2)
            self.points_right = []

    def clear_polygons_left(self, event):
        self.canvas_left.delete("all")
        self.polygons_left = []
        self.points_left = []

    def clear_polygons_right(self, event):
        self.canvas_right.delete("all")
        self.polygons_right = []
        self.points_right = []

    def process_left(self):
        count = 0
        count_cannot_detect = 0
        self.nguoi_dungs = self.nguoi_dung_dal.get()
        self.cap_left = cv2.VideoCapture(self.video_source_left)
        while self.running_left:
            with self.lock_left:
                ret, frame = self.cap_left.read()
            if ret:
                count+=1
                frame = cv2.resize(frame, (680, 480))
                if self.mode == "START_CHECKIN":
                    cv2.putText(frame, f"DANG CHECKIN",
                                    (320, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                if self.mode == "START_CHECKOUT":
                    cv2.putText(frame, f"DANG CHECKOUT",
                                    (320, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                
                
                predict = self.face_detector.detect(frame)
                boxes = predict['boxes']
                faces = predict['faces']

                for idx, (x, y, w, h) in enumerate(boxes):
                    cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                    face = faces[idx]
                    nguoi_dung = self.face_recognition.search_face(
                        face, self.nguoi_dungs)

                    if nguoi_dung is not None:
                        cv2.putText(frame, f"ID:{nguoi_dung.Id} {unidecode.unidecode(nguoi_dung.HoTen)}",
                                    (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                        if self.mode == 'START_CHECKIN':
                            checkIn = Checkin()
                            checkIn.IdNguoiDung = nguoi_dung.Id
                            checkIn.HoTen = nguoi_dung.HoTen
                            self.checkin_dal.checkIn(checkIn)
                        if self.mode == 'START_CHECKOUT':
                            self.checkin_dal.checkOut(nguoi_dung.Id)
                    else:
                        cv2.putText(frame, f"QUAY MAT VAO CAMERA",
                                    (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                        if self.mode == 'START_CHECKIN' or self.mode == 'START_CHECKOUT':
                            count_cannot_detect+=1
                            count+=1
                            if count_cannot_detect>=60 and count%100==0:
                                t1 = threading.Thread(target=self.send_telegram_photo, args=[frame])
                                t1.start()
                            

                self.display_frame_thread_safe(
                    frame, self.canvas_left, self.points_left, self.polygons_left)

                self.frame_count_left += 1
                elapsed_time = time.time() - self.fps_start_time_left
                if elapsed_time > 1:
                    fps = self.frame_count_left / elapsed_time
                    self.fps_start_time_left = time.time()
                    self.frame_count_left = 0
                    self.update_fps_display(self.canvas_left, round(fps))
            else:
                break
        with self.lock_left:
            self.cap_left.release()

    def process_video_left(self, video_path):
        self.nguoi_dungs = self.nguoi_dung_dal.get()
        self.cap_left = cv2.VideoCapture(video_path)
        while self.cap_left.isOpened():
            with self.lock_left:
                ret, frame = self.cap_left.read()
            if ret:
                frame = cv2.resize(frame, (680, 480))
                if self.mode == "START_CHECKIN":
                    cv2.putText(frame, f"DANG CHECKIN",
                                    (320, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                if self.mode == "START_CHECKOUT":
                    cv2.putText(frame, f"DANG CHECKOUT",
                                    (320, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                predict = self.face_detector.detect(frame)
                boxes = predict['boxes']
                faces = predict['faces']

                for idx, (x, y, w, h) in enumerate(boxes):
                    cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                    face = faces[idx]
                    nguoi_dung = self.face_recognition.search_face(
                        face, self.nguoi_dungs)
                    if nguoi_dung is not None:
                        cv2.putText(frame, f"ID:{nguoi_dung.Id} {unidecode.unidecode(nguoi_dung.HoTen)}",
                                    (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                        if self.mode == 'START_CHECKIN':
                            checkIn = Checkin()
                            checkIn.IdNguoiDung = nguoi_dung.Id
                            checkIn.HoTen = nguoi_dung.HoTen
                            self.checkin_dal.checkIn(checkIn)
                        if self.mode == 'START_CHECKOUT':
                            self.checkin_dal.checkOut(nguoi_dung.Id)
                    else:
                        cv2.putText(frame, f"QUAY MAT VAO CAMERA",
                                    (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                        if self.mode == 'START_CHECKIN' or self.mode == 'START_CHECKOUT':
                            count_cannot_detect+=1
                            count+=1
                            if count_cannot_detect>=60 and count%100==0:
                                t1 = threading.Thread(target=self.send_telegram_photo, args=[frame])
                                t1.start()
                self.display_frame_thread_safe(
                    frame, self.canvas_left, self.points_left, self.polygons_left)

                self.frame_count_left += 1
                elapsed_time = time.time() - self.fps_start_time_left
                if elapsed_time > 1:
                    fps = self.frame_count_left / elapsed_time
                    self.fps_start_time_left = time.time()
                    self.frame_count_left = 0
                    self.update_fps_display(self.canvas_left, round(fps))
            else:
                break
        with self.lock_left:
            self.cap_left.release()

    def process_right(self):

        self.cap_right = cv2.VideoCapture(self.video_source_right)
        while self.running_right:
            with self.lock_right:
                ret, frame = self.cap_right.read()
            if ret:
                frame = cv2.resize(frame, (680, 480))
                frame, xyxys, confidences, class_ids = self.object_detection.detect_objects(
                    frame)
                self.check_alert(xyxys, confidences, class_ids, frame)
                self.display_frame_thread_safe(
                    frame, self.canvas_right, self.points_right, self.polygons_right)

                self.frame_count_right += 1
                elapsed_time = time.time() - self.fps_start_time_right
                if elapsed_time > 1:
                    fps = self.frame_count_right / elapsed_time
                    self.fps_start_time_right = time.time()
                    self.frame_count_right = 0
                    self.update_fps_display(self.canvas_right, round(fps))
            else:
                break
        with self.lock_right:
            self.cap_right.release()

    def process_video_right(self, video_path):
        self.cap_right = cv2.VideoCapture(video_path)
        while self.cap_right.isOpened():
            with self.lock_right:
                ret, frame = self.cap_right.read()
            if ret:
                frame = cv2.resize(frame, (680, 480))
                frame, xyxys, confidences, class_ids = self.object_detection.detect_objects(
                    frame)
                self.check_alert(xyxys, confidences, class_ids, frame)
                self.display_frame_thread_safe(
                    frame, self.canvas_right, self.points_right, self.polygons_right)

                self.frame_count_right += 1
                elapsed_time = time.time() - self.fps_start_time_right
                if elapsed_time > 1:
                    fps = self.frame_count_right / elapsed_time
                    self.fps_start_time_right = time.time()
                    self.frame_count_right = 0
                    self.update_fps_display(self.canvas_right, round(fps))
            else:
                break
        with self.lock_right:
            self.cap_right.release()

    def check_alert(self, xyxys, confidences, class_ids, frame):
        objects_in_polygons = [0] * len(self.polygons_right)
        object_detected = False

        for (xyxy, confidence, class_id) in zip(xyxys, confidences, class_ids):
            if xyxy.size == 4:
                x1, y1, x2, y2 = map(int, xyxy)
                x_center = (x1 + x2) // 2
                y_center = (y1 + y2) // 2
                point = (x_center, y_center)
                object_detected = True

                for i, polygon in enumerate(self.polygons_right):
                    if self.is_point_in_polygon(point, polygon):
                        objects_in_polygons[i] += 1

        if len(self.polygons_right) >= 2 and objects_in_polygons[1] == 1 and all(count == 0 for i, count in enumerate(objects_in_polygons) if i != 1):
            threading.Thread(target=self.alert, args=(
                frame,), daemon=True).start()
        elif not object_detected:
            pygame.mixer.music.stop()

    def is_point_in_polygon(self, point, polygon):
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / \
                                (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def alert(self, frame):
        # Phát cảnh báo âm thanh và gửi thông báo trong thread riêng
        self.play_alert_sound()
        message = "Alert: Object detected within the designated area."
        self.send_telegram_message(message)
        self.send_telegram_photo(frame)

    def play_alert_sound(self):
        pygame.mixer.music.load("Alarm/alarm.wav")
        pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 3000)

    def send_telegram_message(self, message):
        data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        requests.post(TELEGRAM_API_URL, data=data)

    def send_telegram_photo(self, frame):
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'photo': ('image.jpg', img_encoded.tobytes())}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        requests.post(TELEGRAM_PHOTO_URL, data=data, files=files)
        print('send telegram')

    def display_frame_thread_safe(self, frame, canvas, points, polygons):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (680, 480))
        img = tk.PhotoImage(
            master=canvas, data=cv2.imencode('.png', img)[1].tobytes())
        canvas.after(0, self.update_canvas, canvas, img, points, polygons)

    def update_canvas(self, canvas, img, points, polygons):
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
        canvas.img = img

        for point in points:
            x, y = point
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')
        for polygon in polygons:
            canvas.create_polygon(polygon, outline='blue', fill='', width=2)

    def update_fps_display(self, canvas, fps):
        canvas.delete("fps")
        canvas.create_text(
            10, 10, anchor=tk.NW, text=f"FPS: {fps}", fill="red", font=self.font_small, tag="fps")

    def startCheckin(self):
        self.mode = 'START_CHECKIN'

    def endCheckin(self):
        self.mode = 'NONE'
        list_hoc_sinh = self.nguoi_dung_dal.get()
        list_checkin = self.checkin_dal.get()
        list_id_checkin = [i.IdNguoiDung for i in list_checkin]
        for hocSinh in list_hoc_sinh:
            if hocSinh.Id not in list_id_checkin:
                text = f'Bạn: {hocSinh.HoTen} ID: {hocSinh.Id} vắng'
                self.send_telegram_message(text)
        
    def startCheckout(self):
        self.mode = 'START_CHECKOUT'

    def endCheckout(self):
        self.mode = 'NONE'
        list_hoc_sinh = self.nguoi_dung_dal.get()
        list_checkin = self.checkin_dal.get()
        id_chua_checkout = [i.IdNguoiDung for i in list_checkin if i.GioCheckout == '']
        for hocSinh in list_hoc_sinh:
            if hocSinh.Id in id_chua_checkout:
                text = f'Bạn: {hocSinh.HoTen} ID: {hocSinh.Id} chưa checkout'
                self.send_telegram_message(text)

    def quit(self):
        self.running_left = False
        self.running_right = False
        if self.cap_left is not None:
            with self.lock_left:
                self.cap_left.release()
        if self.cap_right is not None:
            with self.lock_right:
                self.cap_right.release()
        cv2.destroyAllWindows()
        self.destroy()


if __name__ == "__main__":
    app = CameraApp()

    def handle_pygame_events():
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                pygame.mixer.music.stop()
                pygame.time.set_timer(pygame.USEREVENT, 0)

    def pygame_loop():
        while True:
            handle_pygame_events()
            time.sleep(0.1)

    threading.Thread(target=pygame_loop, daemon=True).start()
    app.mainloop()
