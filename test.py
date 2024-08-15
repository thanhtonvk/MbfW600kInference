import sqlite3
# # from dal.CheckinDal import CheckinDal
# # dal = CheckinDal()
# # print(dal.get()[0].GioCheckout)

conn = sqlite3.connect('./database/database.sqlite')

# conn.execute("""CREATE TABLE IF NOT EXISTS NguoiDung(
#     Id integer primary key,
#     HoTen text not null,
#     Emb blob
# );""")
# conn.commit()



# conn.execute("""
#              CREATE TABLE IF NOT EXISTS CheckIn(
#                  IdNguoiDung integer,
#                  HoTen text,
#                  Ngay text,
#                  GioCheckin text,
#                  GioCheckout text
#              )
#              """)
# conn.commit()
conn.execute("""delete from Checkin""")
conn.commit()
conn.close()
# # # # from dal.NguoiDungDal import NguoiDungDal
# # # # dal = NguoiDungDal()

# # # # print(dal.get())
# # # import numpy as np

# # # # Create a 2D NumPy array
# # # arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# # # # Change the value of an element at row 1, column 2 to 10
# # # arr_2d[1, 2] = 10

# # # print(arr_2d)
# # # # Output:
# # # # [[ 1  2  3]
# # # #  [ 4  5 10]
# # # #  [ 7  8  9]]


# # # import cv2
# # # import matplotlib.pyplot as plt
# # # image = cv2.imread('test\qr4.png')

# # # qrCodeDetector = cv2.QRCodeDetector()
# # # decodedText, points, qr = qrCodeDetector.detectAndDecode(image)
# # # print('noi dung ', decodedText=='')
# # # print(points)

# # # x1, y1 = tuple(points[0][0].astype('int'))
# # # x2, y2 = tuple(points[0][1].astype('int'))
# # # x3, y3 = tuple(points[0][2].astype('int'))
# # # x4, y4 = tuple(points[0][3].astype('int'))

# # # x_min = min(x1, x2, x3, x4)
# # # y_min = min(y1, y2, y3, y4)
# # # x_max = max(x1, x2, x3, x4)
# # # y_max = max(y1, y2, y3, y4)

# # # # Define top-left and bottom-right corner coordinates
# # # pt1 = (x_min, y_min)  # Replace with your top-left coordinates
# # # pt2 = (x_max, y_max)  # Replace with your bottom-right coordinates

# # # # Define rectangle color (BGR format)
# # # color = (255, 0, 0)  # Blue color

# # # # Define rectangle thickness (in pixels)
# # # thickness = 2

# # # # Draw the rectangle on the image
# # # img = cv2.rectangle(image, pt1, pt2, color, thickness)

# # # plt.imshow(img)
# # # plt.show()
# # # # print(decodedText)
# # # # print(qr.shape)
# # import datetime
# # currentDate = str(datetime.datetime.now())
# # print(currentDate)