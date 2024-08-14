import sqlite3
from objects.Checkin import Checkin
from config import config
import datetime


class CheckinDal:
    def __init__(self):
        pass

    def get(self):
        currentDate = str(datetime.datetime.now()).split(' ')
        ngayHienTai = currentDate[0]
        list_objects = []
        try:
            conn = sqlite3.connect(config.DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT * FROM Checkin WHERE Ngay = ?", (ngayHienTai,))
            rows = cur.fetchall()
            for row in rows:
                checkin = Checkin()
                checkin.IdNguoiDung = row[0]
                checkin.HoTen = row[1]
                checkin.Ngay = row[2]
                checkin.GioCheckin = row[3]
                checkin.GioCheckout = row[4]
                list_objects.append(checkin)
            conn.close()
        except Exception as e:
            print(e)
        return list_objects

    def delete(self, IdNguoiDung):
        try:
            conn = sqlite3.connect(config.DATABASE)
            conn.execute("DELETE FROM Checkin where Id = ?", (IdNguoiDung,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def checkIn(self, checkIn: Checkin):
        list_checkin = self.get()
        exist = [i for i in list_checkin if str(i.IdNguoiDung).strip() == str(checkIn.IdNguoiDung).strip()]
        if len(exist) == 0:
            currentDate = str(datetime.datetime.now()).split(' ')
            ngayHienTai = currentDate[0]
            gioHienTai = currentDate[1]
            checkIn.Ngay = ngayHienTai
            checkIn.GioCheckin = gioHienTai
            checkIn.GioCheckout = ''
            try:
                conn = sqlite3.connect(config.DATABASE)
                conn.execute(
                    "INSERT INTO CheckIn(IdNguoiDung,HoTen,Ngay,GioCheckin,GioCheckout) values(?,?,?,?,?)", (checkIn.IdNguoiDung, checkIn.HoTen, checkIn.Ngay, checkIn.GioCheckin, checkIn.GioCheckout))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print('err ', e)
                return False
        return False

    def checkOut(self, idNguoiDung):
        list_checkin = self.get()
        exist = [i for i in list_checkin if str(i.IdNguoiDung).strip() == str(idNguoiDung).strip() and i.GioCheckout=='']
        if len(exist)>0:
            currentDate = str(datetime.datetime.now()).split(' ')
            gioHienTai = currentDate[1]
            try:
                conn = sqlite3.connect(config.DATABASE)
                conn.execute(
                    "UPDATE CheckIn SET GioCheckout = ? where IdNguoiDung = ?", (gioHienTai, idNguoiDung))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print('err ', e)
                return False
        return False

