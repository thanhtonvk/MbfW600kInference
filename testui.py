import pygame
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
pygame.init()
import threading
from PIL import Image
import time
class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Camera Interface")
        # self.geometry("1920x1080")

        # # Load and set the background image
        # self.background_image = Image.open("hugo.jpg")
        # self.background_image = self.background_image.resize(
        #     (self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
        # self.background_photo = ImageTk.PhotoImage(self.background_image)

        # self.background_label = tk.Label(self, image=self.background_photo)
        # self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

    #     # Add logo at the top left
    #     self.logo_image = Image.open("logo.png")
    #     self.logo_image = self.logo_image.resize(
    #         (100, 100), Image.Resampling.LANCZOS)
    #     self.logo_photo = ImageTk.PhotoImage(self.logo_image)
    #     self.logo_label = tk.Label(self, image=self.logo_photo, bg="#2c3e50")
    #     self.logo_label.place(x=20, y=10)

    #    # Create a title frame with an inner red border
    #     self.title_frame = tk.Frame(self, bg="#00BFFF", bd=10, relief="ridge")
    #     self.title_frame.place(x=320, y=20, width=900, height=90)

    #     self.title_label = tk.Label(self.title_frame, text="HỆ THỐNG THÔNG MINH TRÊN XE ĐƯA ĐÓN HỌC SINH", font=(
    #         "Helvetica", 24, "bold"), fg="#FF0000", bg="#F5F5F5")
    #     self.title_label.pack(padx=20, pady=20)

    #     self.video_source_left = 0
    #     self.video_source_right = 0
    #     self.cap_left = None
    #     self.cap_right = None
    #     self.running_left = False
    #     self.running_right = False
    #     self.lock_left = threading.Lock()
    #     self.lock_right = threading.Lock()

    #     self.font_large = ("Helvetica", 16, "bold")
    #     self.font_small = ("Helvetica", 12)

    #     button_width = 15
    #     button_height = 2

    #     # Camera frame 1
    #     self.frame_camera1 = tk.Frame(self, width=700, height=500, bg="#00BFFF", bd=10, relief="solid",
    #                                   highlightbackground="#00BFFF", highlightcolor="#00BFFF", highlightthickness=4)
    #     self.frame_camera1.place(x=45, y=140)

    #     # Camera frame 2
    #     self.frame_camera2 = tk.Frame(self, width=700, height=500, bg="#00BFFF", bd=10, relief="solid",
    #                                   highlightbackground="#00BFFF", highlightcolor="#00BFFF", highlightthickness=4)
    #     self.frame_camera2.place(x=775, y=140)

    #     # Buttons frame 1
    #     self.frame_buttons1 = tk.Frame(self, bg="#2c3e50")
    #     self.frame_buttons1.place(x=73, y=680)

    #     self.button_camera1 = tk.Button(self.frame_buttons1, text="Camera", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                     width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_camera1.pack(side=tk.LEFT, padx=10)

    #     self.button_video1 = tk.Button(self.frame_buttons1, text="Video", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                    width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_video1.pack(side=tk.LEFT, padx=10)

    #     self.button_connect1 = tk.Button(self.frame_buttons1, text="Kết nối", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                      width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_connect1.pack(side=tk.LEFT, padx=10)

    #     self.button_exit1 = tk.Button(self.frame_buttons1, text="Exit", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                   width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.quit)
    #     self.button_exit1.pack(side=tk.LEFT, padx=10)

    #     self.frame_buttons3 = tk.Frame(self, bg="#2c3e50")
    #     self.frame_buttons3.place(x=73, y=780)

    #     self.button_camera1 = tk.Button(self.frame_buttons3, text="Bắt đầu checkin", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                     width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_camera1.pack(side=tk.LEFT, padx=10)

    #     self.button_video1 = tk.Button(self.frame_buttons3, text="Kết thúc checkin", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                    width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_video1.pack(side=tk.LEFT, padx=10)

    #     self.button_camera1 = tk.Button(self.frame_buttons3, text="Bắt đầu checkout", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                     width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_camera1.pack(side=tk.LEFT, padx=10)

    #     self.button_video1 = tk.Button(self.frame_buttons3, text="Kết thúc checkout", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                    width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_video1.pack(side=tk.LEFT, padx=10)

    #     # Buttons frame 2
    #     self.frame_buttons2 = tk.Frame(self, bg="#2c3e50")
    #     self.frame_buttons2.place(x=800, y=680)

    #     self.button_camera2 = tk.Button(self.frame_buttons2, text="Camera", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                     width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_camera2.pack(side=tk.LEFT, padx=10)

    #     self.button_video2 = tk.Button(self.frame_buttons2, text="Video", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                    width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_video2.pack(side=tk.LEFT, padx=10)

    #     self.button_connect2 = tk.Button(self.frame_buttons2, text="Kết nối", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                      width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085")
    #     self.button_connect2.pack(side=tk.LEFT, padx=10)

    #     self.button_exit2 = tk.Button(self.frame_buttons2, text="Exit", font=self.font_small, bg="#1abc9c", fg="#ffffff",
    #                                   width=button_width, height=button_height, bd=2, relief="solid", highlightbackground="#16a085", command=self.quit)
    #     self.button_exit2.pack(side=tk.LEFT, padx=10)
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