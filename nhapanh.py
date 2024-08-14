import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

from dal.NguoiDungDal import NguoiDungDal
from modules.face_detection import FaceDetection
from modules.face_recognition import FaceRecognition

# Khởi tạo các đối tượng xử lý
NguoiDungDal = NguoiDungDal()
faceDetector = FaceDetection()
faceRecognition = FaceRecognition()

# Hàm để tải ảnh lên và xử lý
def upload_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    
    ho_ten = ho_ten_entry.get()
    id_nguoi_dung = id_entry.get()

    if not ho_ten or not id_nguoi_dung:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ ID và Tên.")
        return

    try:
        # Sử dụng PIL để mở và lưu lại ảnh với một đường dẫn tạm thời
        image = Image.open(file_path)
        temp_save_path = f"static/faces/temp_image.png"
        image.save(temp_save_path)
        
        # Sau đó sử dụng OpenCV để đọc ảnh vừa lưu
        image_cv = cv2.imread(temp_save_path)
        result = faceDetector.save_face(id_nguoi_dung, image_cv)
        
        os.remove(temp_save_path)  # Xóa file tạm thời sau khi xử lý
        
        if result > 0:
            image_face_path = f"static/faces/{id_nguoi_dung}/face.png"
            image_face = cv2.imread(image_face_path)
            emb = faceRecognition.get_embed(image_face)
            NguoiDungDal.insert(ho_ten, id_nguoi_dung, emb)
            messagebox.showinfo("Thành công", "Đã thêm người dùng thành công")
        else:
            messagebox.showerror("Thất bại", "Không thể phát hiện khuôn mặt.")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


# Khởi tạo cửa sổ chính
root = tk.Tk()
root.title("Quản lý Người Dùng")

# Thiết lập kích thước cửa sổ
window_width = 600
window_height = 400

# Đặt kích thước và vị trí của cửa sổ
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

# Đặt background là hình ảnh
background_image = Image.open("hugo.jpg")
background_image = background_image.resize((window_width, window_height), Image.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# Tạo khung chứa các widget với viền màu xanh lá cây nhạt
frame = tk.Frame(root, bg="white", bd=2, relief="solid", highlightbackground="#90EE90", highlightthickness=3)
frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=350)

# Tiêu đề
title_label = tk.Label(frame, text="THÊM HỌC SINH", font=("Arial", 18, "bold"), bg="white", fg="green")
title_label.pack(pady=20)

# Khung con để chứa các input và nút, giúp căn giữa chúng
input_frame = tk.Frame(frame, bg="white")
input_frame.pack(pady=10)

# Nhập ID người dùng
id_entry = tk.Entry(input_frame, font=("Arial", 14), fg="green", bd=2, relief="groove", width=30)
id_entry.grid(row=0, column=0, padx=10, pady=10)
id_entry.insert(0, "Nhập ID")  # Placeholder text
id_entry.bind("<FocusIn>", lambda event: id_entry.delete(0, tk.END) if id_entry.get() == "Nhập ID" else None)

# Nhập Tên
ho_ten_entry = tk.Entry(input_frame, font=("Arial", 14), fg="green", bd=2, relief="groove", width=30)
ho_ten_entry.grid(row=1, column=0, padx=10, pady=10)
ho_ten_entry.insert(0, "Nhập Tên")  # Placeholder text
ho_ten_entry.bind("<FocusIn>", lambda event: ho_ten_entry.delete(0, tk.END) if ho_ten_entry.get() == "Nhập Tên" else None)

# Nút để tải ảnh khuôn mặt lên
upload_button = tk.Button(frame, text="Tải ảnh khuôn mặt lên", font=("Arial", 14), fg="white", bg="green", command=upload_image, bd=2, relief="raised")
upload_button.pack(pady=20)

# Khởi chạy giao diện
root.mainloop()