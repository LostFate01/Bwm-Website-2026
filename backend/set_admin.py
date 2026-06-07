import mysql.connector
import bcrypt

db = mysql.connector.connect(host='localhost', user='root', password='', database='bmw_bayi')
cursor = db.cursor()

sifre = b'admin123'
hashed = bcrypt.hashpw(sifre, bcrypt.gensalt(12))

cursor.execute(
    "UPDATE kullanicilar SET sifre_hash=%s WHERE kullanici_adi='admin'",
    (hashed.decode('utf-8'),)
)
db.commit()
print("Admin sifresi guncellendi.")
cursor.close()
db.close()
