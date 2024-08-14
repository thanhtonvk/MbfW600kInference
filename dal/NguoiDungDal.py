import mysql.connector
from objects.NguoiDung import NguoiDung
from config import config
import pickle
import numpy as np

class NguoiDungDal:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        self.cursor = self.conn.cursor()

    def insert(self, hoten, id, emb: np.ndarray):
        vector_blob = pickle.dumps(emb)
        try:
            print(f"Inserting embedding for {hoten}: {emb.shape}")
            sql = """
                INSERT INTO NguoiDung (HoTen, Id, Emb)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    HoTen = VALUES(HoTen),
                    Emb = VALUES(Emb)
            """
            self.cursor.execute(sql, (hoten, id, vector_blob))
            self.conn.commit()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def update(self, hoten, id, emb):
        vector_blob = pickle.dumps(emb)
        try:
            sql = "UPDATE NguoiDung SET HoTen = %s, Emb = %s WHERE Id = %s"
            self.cursor.execute(sql, (hoten, vector_blob, id))
            self.conn.commit()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def delete(self, id):
        try:
            sql = "DELETE FROM NguoiDung WHERE Id = %s"
            self.cursor.execute(sql, (id,))
            self.conn.commit()
            return True
        except Exception as e:
            print('err ', e)
            return False

    def get(self):
        nguoi_dungs = []
        try:
            sql = "SELECT * FROM NguoiDung"
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            for row in rows:
                sv = NguoiDung()
                sv.Id = row[0]
                sv.HoTen = row[1]
                sv.Emb = pickle.loads(row[2])
                print(f"Loaded embedding for {sv.HoTen}: {sv.Emb.shape}")
                nguoi_dungs.append(sv)
            return nguoi_dungs
        except Exception as e:
            print('err ', e)
            return nguoi_dungs
