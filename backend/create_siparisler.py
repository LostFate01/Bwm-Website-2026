import mysql.connector

db = mysql.connector.connect(host='localhost', user='root', password='', database='bmw_bayi')
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS siparisler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    musteri_id INT NOT NULL,
    donanim_id INT NOT NULL,
    tutar DECIMAL(15,2) NOT NULL,
    siparis_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    durum VARCHAR(50) DEFAULT 'Onay Bekliyor',
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE CASCADE,
    FOREIGN KEY (donanim_id) REFERENCES donanim_paketleri(id) ON DELETE CASCADE
) ENGINE=InnoDB;
""")

db.commit()
print("siparisler tablosu olusturuldu.")
cursor.close()
db.close()
