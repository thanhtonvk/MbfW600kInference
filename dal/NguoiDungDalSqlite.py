import sqlite3
from objects.NguoiDung import NguoiDung
from config import config
import pickle
import numpy as np
class NguoiDungDal:
    def __init__(self):
        pass
        

    def insert(self, hoten,id,emb:np.ndarray):
        vector_blob = pickle.dumps(emb)
        try:
            conn = sqlite3.connect(config.DATABASE)
            conn.execute(
                "INSERT INTO NguoiDung(HoTen,Id,Emb) values(?,?,?)", (hoten,id,vector_blob))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def update(self, hoten, id,emb):
        vector_blob = pickle.dumps(emb)
        try:
            conn = sqlite3.connect(config.DATABASE)
            conn.execute(
                "UPDATE NguoiDung SET HoTen = ?,Emb = ?, where Id = ?", (hoten, id,vector_blob))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print('err ', e)
            return True

    def delete(self, id):
        try:
            conn = sqlite3.connect(config.DATABASE)
            conn.execute("DELETE FROM NguoiDung where Id = ?", (id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def get(self):
        nguoi_dungs = []
        try:
            conn = sqlite3.connect(config.DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT * FROM NguoiDung")
            rows = cur.fetchall()
            for row in rows:
                sv = NguoiDung()
                sv.Id = row[0]
                sv.HoTen = row[1]
                sv.Emb = pickle.loads(row[2])
                nguoi_dungs.append(sv)
            conn.close()
            return nguoi_dungs
        except Exception as e:
            print('err ',e)
            return nguoi_dungs
