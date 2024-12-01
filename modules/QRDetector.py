import qrcode
import os
import cv2
def tao_qr(text):
    try:
        os.remove(f'static/qrs/{text}/qr.png')
    except:
        print('')
    os.makedirs(f'static/qrs/{text}', exist_ok=True)
    # Tạo mã QR
    qr = qrcode.QRCode(
        version=1,  # Kích thước QR Code (1 = nhỏ nhất, 40 = lớn nhất)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Mức sửa lỗi (L = thấp nhất)
        box_size=10,  # Kích thước mỗi ô trong QR Code
        border=4,  # Độ dày viền (tối thiểu là 4)
    )

    qr.add_data(text)
    qr.make(fit=True)

    # Tạo hình ảnh mã QR và lưu lại
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f'static/qrs/{text}/qr.png')
def doc_qr(image):
    detector = cv2.QRCodeDetector()
    data, vertices, _ = detector.detectAndDecode(image)
    return data,vertices
def search_person_qr(id, nguoiDungs):
    for nguoiDung in nguoiDungs:
        if str(id).strip() == str(nguoiDung.Id).strip():
            return nguoiDung
    return None
    

