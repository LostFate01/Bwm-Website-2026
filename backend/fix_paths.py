import mysql.connector

db = mysql.connector.connect(host='localhost', user='root', password='', database='bmw_bayi')
cursor = db.cursor()
cursor.execute("UPDATE modeller SET resim_yolu = REPLACE(resim_yolu, '../images/', '../assets/images/')")
db.commit()
print("Updated rows:", cursor.rowcount)
cursor.close()
db.close()
