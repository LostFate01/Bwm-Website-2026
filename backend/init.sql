-- ============================================================
-- BMW Bayi Projesi - Veritabanı Başlangıç Scripti (init.sql)
-- Kullanım: mysql -u root -p < init.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS bmw_bayi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_turkish_ci;
USE bmw_bayi;

-- Geliştirme ortamında temiz başlangıç için tabloları sıfırla
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fiyat_listesi;
DROP TABLE IF EXISTS donanim_paketleri;
DROP TABLE IF EXISTS modeller;
DROP TABLE IF EXISTS seriler;
DROP TABLE IF EXISTS iletisim_talepleri;
DROP TABLE IF EXISTS geri_cagirmalar;
DROP TABLE IF EXISTS kampanyalar;
DROP TABLE IF EXISTS kullanicilar;
DROP TABLE IF EXISTS bayiler;
DROP TABLE IF EXISTS siparisler;
DROP TABLE IF EXISTS sepet;
DROP TABLE IF EXISTS favoriler;
DROP TABLE IF EXISTS musteriler;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- TABLO 1: seriler
-- BMW ana seri grupları (2S, 3S, X Serisi vb.)
-- Tasarım: modeller tablosu bu tabloya FK ile bağlanır → 1-to-N
-- ============================================================
CREATE TABLE seriler (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    seri_adi         VARCHAR(50)  NOT NULL UNIQUE,
    seri_kodu        VARCHAR(10)  NOT NULL UNIQUE,
    aciklama         TEXT,
    olusturma_tarihi DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLO 2: modeller
-- Bir seriye bağlı spesifik araç modelleri (1-N: seriler→modeller)
-- ============================================================
CREATE TABLE modeller (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    seri_id          INT          NOT NULL,
    model_adi        VARCHAR(100) NOT NULL,
    yakit_tipi       ENUM('Benzin','Dizel','Elektrik','Hibrit') NOT NULL DEFAULT 'Benzin',
    kasa_tipi        VARCHAR(50),
    resim_yolu       VARCHAR(255),
    aktif            TINYINT(1)   NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME     DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_modeller_seriler
        FOREIGN KEY (seri_id) REFERENCES seriler(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLO 3: donanim_paketleri
-- Modele ait donanım/motor paketleri (1-N: modeller→donanim)
-- ============================================================
CREATE TABLE donanim_paketleri (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    model_id    INT          NOT NULL,
    paket_adi   VARCHAR(100) NOT NULL,
    motor       VARCHAR(100),
    sanziman    VARCHAR(100),
    motor_gucu  VARCHAR(20),
    hiz_0_100   VARCHAR(20),
    ozellikler  TEXT,
    CONSTRAINT fk_donanim_modeller
        FOREIGN KEY (model_id) REFERENCES modeller(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLO 4: fiyat_listesi
-- Donanım paketine bağlı fiyat (1-1: donanim→fiyat)
-- Ayrı tablo: fiyatlar model bilgisinden bağımsız güncellenebilir
-- ============================================================
CREATE TABLE fiyat_listesi (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    donanim_id        INT            NOT NULL UNIQUE,
    fiyat             DECIMAL(15,2)  NOT NULL,
    gecerlilik_tarihi DATE,
    para_birimi       VARCHAR(10)    NOT NULL DEFAULT 'TRY',
    CONSTRAINT fk_fiyat_donanim
        FOREIGN KEY (donanim_id) REFERENCES donanim_paketleri(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLO 5: iletisim_talepleri
-- iletisim.html formundan gelen müşteri talepleri
-- ============================================================
CREATE TABLE iletisim_talepleri (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    ad               VARCHAR(50)  NOT NULL,
    soyad            VARCHAR(50)  NOT NULL,
    email            VARCHAR(150) NOT NULL,
    gsm              VARCHAR(20)  NOT NULL,
    kvkk_onay        TINYINT(1)   NOT NULL DEFAULT 0,
    ileti_izni       TINYINT(1)   NOT NULL DEFAULT 0,
    durum            ENUM('Bekliyor','Arandı','Tamamlandı') DEFAULT 'Bekliyor',
    olusturma_tarihi DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLO 6: geri_cagirmalar
-- geri-cagirma.html formundan gelen arama talepleri
-- ============================================================
CREATE TABLE geri_cagirmalar (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    ad               VARCHAR(50)  NOT NULL,
    soyad            VARCHAR(50)  NOT NULL,
    gsm              VARCHAR(20)  NOT NULL,
    tercih_saat      VARCHAR(50),
    konu             VARCHAR(255),
    durum            ENUM('Bekliyor','Arandı','Ulaşılamadı') DEFAULT 'Bekliyor',
    olusturma_tarihi DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLO 7: kampanyalar
-- kampanya.html'deki promosyonlar; model_id opsiyonel FK
-- ============================================================
CREATE TABLE kampanyalar (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    baslik           VARCHAR(255)   NOT NULL,
    aciklama         TEXT,
    model_id         INT            DEFAULT NULL,
    baslangic_tarihi DATE           NOT NULL,
    bitis_tarihi     DATE           NOT NULL,
    faiz_orani       DECIMAL(5,2),
    vade_ay          INT,
    takas_destegi    DECIMAL(15,2),
    aktif            TINYINT(1)     NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME       DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_kampanya_modeller
        FOREIGN KEY (model_id) REFERENCES modeller(id) ON DELETE SET NULL
);

-- ============================================================
-- TABLO 8: kullanicilar
-- Admin paneli erişimi; şifre hash olarak saklanır
-- ============================================================
CREATE TABLE kullanicilar (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    kullanici_adi    VARCHAR(50)  NOT NULL UNIQUE,
    sifre_hash       VARCHAR(255) NOT NULL,
    ad_soyad         VARCHAR(100),
    rol              ENUM('admin','editor') NOT NULL DEFAULT 'editor',
    aktif            TINYINT(1)   NOT NULL DEFAULT 1,
    son_giris        DATETIME,
    olusturma_tarihi DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SEED: seriler
-- ============================================================
INSERT INTO seriler (seri_adi, seri_kodu, aciklama) VALUES
('2 Serisi', '2S', 'Kompakt sedan ve coupe. Sportif dinamikler, uygun segment.'),
('3 Serisi', '3S', 'BMW ikonik sedan serisi. Performans ve konforun dengesi.'),
('4 Serisi', '4S', 'Coupe odaklı sportif tasarım. Zarif ve güçlü.'),
('5 Serisi', '5S', 'Üst segment yönetici sedanı. Lüks, teknoloji, konfor.'),
('7 Serisi', '7S', 'BMW amiral gemisi. En yüksek lüks ve elektrikli i7 modelleri.'),
('8 Serisi', '8S', 'Gran Turismo ve yüksek performanslı coupe/cabrio.'),
('X Serisi', 'XS', 'BMW SAV ailesi: X1\'den X6\'ya tüm SUV modeller.');

-- ============================================================
-- SEED: modeller
-- ============================================================
INSERT INTO modeller (seri_id, model_adi, yakit_tipi, kasa_tipi, resim_yolu) VALUES
(1, 'BMW 2 Serisi Sedan',       'Benzin',   'Sedan',  '../assets/images/2 serisi.png'),
(2, 'BMW 3 Serisi M Sport',     'Benzin',   'Sedan',  '../assets/images/3 serisi.png'),
(2, 'BMW M3 Competition',       'Benzin',   'Sedan',  '../assets/images/BMW M3.jpg'),
(2, 'BMW 3 Serisi Touring',     'Benzin',   'Touring','../assets/images/3 serisi touring.png'),
(3, 'BMW 4 Serisi Coupe',       'Benzin',   'Coupe',  '../assets/images/4 serisi coupe.png'),
(3, 'BMW M4 Competition Coupe', 'Benzin',   'Coupe',  '../assets/images/4 serisi.agresif.png'),
(4, 'BMW 5 Serisi M Sport',     'Benzin',   'Sedan',  '../assets/images/5 serisi.png'),
(4, 'BMW i5 xDrive M Sport',    'Elektrik', 'Sedan',  '../assets/images/5 serisi i5M60.png'),
(5, 'BMW i7 M70 xDrive',        'Elektrik', 'Sedan',  '../assets/images/7 serisi elektrik.png'),
(5, 'BMW i7 xDrive M Sport',    'Elektrik', 'Sedan',  '../assets/images/i7-sedan.png'),
(5, 'BMW i7 M650 xDrive',       'Elektrik', 'Sedan',  '../assets/images/yeni i7.png'),
(6, 'BMW 8 Serisi Coupe',       'Benzin',   'Coupe',  '../assets/images/8-serisi-coupe.png'),
(6, 'BMW M8 Competition',       'Benzin',   'Coupe',  '../assets/images/m8-grann-coupe.siyah.png'),
(6, 'BMW 8 Serisi Cabrio',      'Benzin',   'Cabrio', '../assets/images/8 serisi cabrio.png'),
(7, 'BMW X1',                   'Benzin',   'SUV',    '../assets/images/X1.jpg'),
(7, 'BMW X2',                   'Benzin',   'SUV',    '../assets/images/x2 serisi.png'),
(7, 'BMW X3 M Sport',           'Benzin',   'SUV',    '../assets/images/x3 serisi.png'),
(7, 'BMW X4 M Sport',           'Benzin',   'SUV',    '../assets/images/x4 serisi.png'),
(7, 'BMW X5 M Sport',           'Benzin',   'SUV',    '../assets/images/x5 serisi.png'),
(7, 'BMW X6 M Sport',           'Benzin',   'SUV',    '../assets/images/x6 serisi.png');

-- ============================================================
-- SEED: donanim_paketleri
-- ============================================================
INSERT INTO donanim_paketleri (model_id, paket_adi, motor, sanziman, motor_gucu, hiz_0_100, ozellikler) VALUES
-- 2 Serisi (model_id=1)
(1,'M Sport 220i','2.0L Benzinli','8 İleri Otomatik','184 HP','7.9 saniye','LED farlar, Deri döşeme, iDrive 7.0, Anahtarsız giriş'),
(1,'M Sport 230i','2.0L Benzinli','8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(1,'M Sport 240i','3.0L Benzinli','8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(1,'M Sport M250i xDrive','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- 3 Serisi (model_id=2)
(2,'M Sport 320i','2.0L Benzinli','8 İleri Otomatik','184 HP','7.9 saniye','LED farlar, Deri döşeme, iDrive 7.0, Anahtarsız giriş'),
(2,'M Sport 330i','2.0L Benzinli','8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(2,'M Sport 340i','3.0L Benzinli','8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(2,'M Sport M350i xDrive','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- 4 Serisi (model_id=5)
(5,'M Sport 420i','2.0L Benzinli','8 İleri Otomatik','184 HP','7.9 saniye','LED farlar, Deri döşeme, iDrive 7.0, Anahtarsız giriş'),
(5,'M Sport 430i','2.0L Benzinli','8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(5,'M Sport 440i','3.0L Benzinli','8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(5,'M Sport M450i xDrive','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- 5 Serisi (model_id=7)
(7,'M Sport 520i','2.0L Benzinli','8 İleri Otomatik','184 HP','7.9 saniye','LED farlar, Deri döşeme, iDrive 7.0, Anahtarsız giriş'),
(7,'M Sport 530i','2.0L Benzinli','8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(7,'M Sport 540i','3.0L Benzinli','8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(7,'M Sport M550i xDrive','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- 7 Serisi (model_id=9,10,11)
(9, 'M Sport i7 M70',       '2.0L Benzinli',      '8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(10,'M Sport i7 xDrive',    '3.0L Benzinli',      '8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(11,'M Sport i7 M650 xDrive','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- 8 Serisi (model_id=12,13)
(12,'M Sport 840i','3.0L Benzinli',      '8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(12,'M Sport 850i','3.0L Benzinli',      '8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(13,'M Sport M8 Competition','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera'),
-- X1 (model_id=15)
(15,'X-Line sDrive20i', '2.0L Benzinli',      '8 İleri Otomatik','252 HP','6.0 saniye','LED farlar, 19" jantlar, Apple CarPlay, Adaptif cruise'),
(15,'M Sport sDrive20i','3.0L Benzinli',      '8 İleri Otomatik','340 HP','4.9 saniye','Laser farlar, Harman Kardon, M Sport frenler'),
(15,'M Sport xDrive28i','4.4L V8 Twin-Turbo','8 İleri Otomatik','462 HP','3.8 saniye','Laser ışık, M Sport paket, 360 derece kamera');

-- ============================================================
-- SEED: fiyat_listesi (kaynak: fiyat-listesi.html 27.12.2024)
-- ============================================================
INSERT INTO fiyat_listesi (donanim_id, fiyat, gecerlilik_tarihi) VALUES
(1,1150000.00,'2024-12-27'),(2,1300000.00,'2024-12-27'),
(3,1500000.00,'2024-12-27'),(4,2000000.00,'2024-12-27'),
(5,1150000.00,'2024-12-27'),(6,1300000.00,'2024-12-27'),
(7,1500000.00,'2024-12-27'),(8,2000000.00,'2024-12-27'),
(9,1150000.00,'2024-12-27'),(10,1300000.00,'2024-12-27'),
(11,1500000.00,'2024-12-27'),(12,2000000.00,'2024-12-27'),
(13,1150000.00,'2024-12-27'),(14,1300000.00,'2024-12-27'),
(15,1500000.00,'2024-12-27'),(16,2000000.00,'2024-12-27'),
(17,1300000.00,'2024-12-27'),(18,1500000.00,'2024-12-27'),
(19,2000000.00,'2024-12-27'),(20,1300000.00,'2024-12-27'),
(21,1500000.00,'2024-12-27'),(22,2000000.00,'2024-12-27'),
(23,1300000.00,'2024-12-27'),(24,1500000.00,'2024-12-27'),
(25,2000000.00,'2024-12-27');

-- ============================================================
-- SEED: kampanyalar (kaynak: kampanya.html - BMW 3 Serisi)
-- ============================================================
INSERT INTO kampanyalar (baslik, aciklama, model_id, baslangic_tarihi, bitis_tarihi, faiz_orani, vade_ay, takas_destegi) VALUES
('BMW 3 Serisi - %0 Faiz 6 Ay', 'BMW 320i Sedan için 6 aya kadar %0 faizli kredi imkânı.', 2, '2024-12-01','2024-12-31', 0.00, 6,  500000.00),
('BMW 3 Serisi - 12 Ay Kredi',  'BMW 3 Serisi için 12 ay vadeli özel kredi fırsatı.',      2, '2024-12-01','2024-12-31', 1.99,12, NULL),
('BMW 3 Serisi - 24 Ay Kredi',  'BMW 3 Serisi için 24 ay vadeli özel kredi fırsatı.',      2, '2024-12-01','2024-12-31', 3.19,24, NULL),
('BMW Yaz Kampanyası',          'Tüm X Serisi modellerinde özel yaz dönemi fırsatları.',   NULL,'2025-06-01','2025-08-31',2.49,24, 750000.00);

-- ============================================================
-- SEED: iletisim_talepleri (örnek kayıtlar)
-- ============================================================
INSERT INTO iletisim_talepleri (ad, soyad, email, gsm, kvkk_onay, ileti_izni, durum) VALUES
('Ahmet','Yılmaz','ahmet.yilmaz@email.com','+905321234567',1,1,'Tamamlandı'),
('Elif', 'Kaya',  'elif.kaya@email.com',   '+905339876543',1,0,'Bekliyor');

-- ============================================================
-- SEED: geri_cagirmalar (örnek kayıtlar)
-- ============================================================
INSERT INTO geri_cagirmalar (ad, soyad, gsm, tercih_saat, konu, durum) VALUES
('Murat', 'Demir', '+905554443322','10:00 - 12:00','Test sürüşü talebi','Bekliyor'),
('Zeynep','Çelik', '+905461112233','14:00 - 16:00','Fiyat bilgisi',     'Arandı');

-- ============================================================
-- SEED: kullanicilar
-- Şifre "admin123" SHA2 ile hashlendi. Üretimde bcrypt kullanın!
-- ============================================================
INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, rol) VALUES
('admin',  SHA2('admin123',  256), 'Site Yöneticisi', 'admin'),
('editor', SHA2('editor123', 256), 'İçerik Editörü',  'editor');

-- ============================================================
-- Doğrulama: Her tablodaki kayıt sayısını göster
-- ============================================================
SELECT 'seriler'            AS tablo, COUNT(*) AS kayit FROM seriler
UNION ALL SELECT 'modeller',            COUNT(*) FROM modeller
UNION ALL SELECT 'donanim_paketleri',   COUNT(*) FROM donanim_paketleri
UNION ALL SELECT 'fiyat_listesi',       COUNT(*) FROM fiyat_listesi
UNION ALL SELECT 'iletisim_talepleri',  COUNT(*) FROM iletisim_talepleri
UNION ALL SELECT 'geri_cagirmalar',     COUNT(*) FROM geri_cagirmalar
UNION ALL SELECT 'kullanicilar',        COUNT(*) FROM kullanicilar;

-- ============================================================
-- YENI TABLOLAR (Bayiler, Sepet, Favoriler)
-- ============================================================
CREATE TABLE IF NOT EXISTS bayiler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bayi_adi VARCHAR(150) NOT NULL,
    sehir VARCHAR(50) NOT NULL,
    adres TEXT NOT NULL,
    telefon VARCHAR(20) NOT NULL
);

INSERT INTO bayiler (bayi_adi, sehir, adres, telefon) VALUES 
('Borusan Oto Avcılar', 'İstanbul', 'Avcılar E-5 Yanyol', '0212 412 00 00'),
('Borusan Oto İstinye', 'İstanbul', 'İstinye Mah. Sarıyer', '0212 359 33 33'),
('Borusan Oto Ankara', 'Ankara', 'Balgat, Çankaya', '0312 204 80 00'),
('Borusan Oto İzmir', 'İzmir', 'Bornova', '0232 400 11 22');

CREATE TABLE IF NOT EXISTS musteriler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad_soyad VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    sifre_hash VARCHAR(255) NOT NULL,
    kayit_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favoriler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    musteri_id INT DEFAULT NULL,
    model_id INT NOT NULL,
    olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES modeller(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLO: siparisler
-- Müşterilerin sepetten onaylayıp aldıkları araçlar
-- ============================================================
CREATE TABLE siparisler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    musteri_id INT NOT NULL,
    donanim_id INT NOT NULL,
    tutar DECIMAL(15,2) NOT NULL,
    siparis_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    durum VARCHAR(50) DEFAULT 'Onay Bekliyor',
    FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE CASCADE,
    FOREIGN KEY (donanim_id) REFERENCES donanim_paketleri(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sepet (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NULL,
    musteri_id INT NULL,
    donanim_id INT NOT NULL,
    olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sep_donanim FOREIGN KEY (donanim_id) REFERENCES donanim_paketleri(id) ON DELETE CASCADE,
    CONSTRAINT fk_sep_musteriler FOREIGN KEY (musteri_id) REFERENCES musteriler(id) ON DELETE CASCADE
);
