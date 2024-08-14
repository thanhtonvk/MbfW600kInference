import os
from flask import Flask, render_template, request, redirect
import cv2

from dal.NguoiDungDal import NguoiDungDal
from modules.face_detection import FaceDetection
from modules.face_recognition import FaceRecognition
app = Flask(__name__)

NguoiDungDal = NguoiDungDal()
faceDetector = FaceDetection()
faceRecognition = FaceRecognition()


@app.route('/nguoi-dung/them', methods=['GET', 'POST'])
def them_sv():
    if request.method == 'GET':
        return render_template('them_nguoi_dung.html')
    ho_ten = request.form['ho_ten']
    id = request.form['id']
    f = request.files['file']
    save_path = f'static/faces/image.png'
    try:
        f.save(save_path)
    except:
        os.remove(save_path)
        f.save(save_path)
    image = cv2.imread(save_path)
    result = faceDetector.save_face(id,image)
    os.remove(save_path)
    if result>0:
        image_face = cv2.imread(f"static/faces/{id}/face.png")
        emb = faceRecognition.get_embed(image_face)
        NguoiDungDal.insert(ho_ten, id,emb)
        return redirect('/') 
    return render_template('them_nguoi_dung.html')


@app.route('/nguoi-dung/xoa/<int:id>', methods=['GET'])
def xoa(id):
    NguoiDungDal.delete(id)
    return redirect('/')


@app.route('/', methods=['GET'])
def danh_sach_sv():
    NguoiDungs = NguoiDungDal.get()
    print(NguoiDungs)
    return render_template('danh_sach_nguoi_dung.html', NguoiDungs=NguoiDungs)


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
