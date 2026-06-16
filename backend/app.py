# =============================================================
# BMW Bayi Web Sitesi - Flask REST API
# Neden Flask? Hafif, hızlı kurulumu ve Python ekosistemiyle
# uyumu sayesinde üniversite projeleri için idealdir.
# =============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Frontend'in farklı port'tan istek atabilmesi için CORS açık

# ------------------------------------------------------------------
# VERİTABANI BAĞLANTI AYARLARI
# Gerçek projede bu değerleri .env dosyasından okuyun!
# ------------------------------------------------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',       # MySQL şifrenizi buraya yazın
    'database': 'bmw_bayi',
    'charset': 'utf8mb4'
}

def get_db():
    """
    Her istek için yeni bir veritabanı bağlantısı açar.
    Neden her seferinde yeni bağlantı? Basit projelerde
    connection pool yerine bu yöntem yeterlidir ve
    "stale connection" hatalarını önler.
    """
    return mysql.connector.connect(**DB_CONFIG)

def success(data, status=200):
    """Standart başarı yanıtı formatı"""
    return jsonify({"success": True, "data": data}), status

def error(message, status=400):
    """Standart hata yanıtı formatı"""
    return jsonify({"success": False, "error": message}), status

# ==================================================================
# ANA SAYFA - index.html'i serve eder
# ==================================================================
@app.route('/')
def index():
    return app.send_static_file('index.html')

# ==================================================================
# 1. SERİLER ENDPOINT'LERİ
# ==================================================================

@app.route('/api/seriler', methods=['GET'])
def get_seriler():
    """Tüm BMW serilerini listeler"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM seriler ORDER BY seri_kodu")
        seriler = cursor.fetchall()
        cursor.close()
        db.close()
        return success(seriler)
    except Exception as e:
        return error(f"Veritabanı hatası: {str(e)}", 500)

@app.route('/api/seriler/<int:seri_id>', methods=['GET'])
def get_seri(seri_id):
    """Belirli bir seriyi getirir"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM seriler WHERE id = %s", (seri_id,))
        seri = cursor.fetchone()
        cursor.close()
        db.close()
        if not seri:
            return error("Seri bulunamadı", 404)
        return success(seri)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/seriler', methods=['POST'])
def create_seri():
    """Yeni seri ekler"""
    try:
        data = request.get_json()
        # Validasyon: zorunlu alanları kontrol et
        if not data or not data.get('seri_adi') or not data.get('seri_kodu'):
            return error("seri_adi ve seri_kodu zorunludur", 400)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO seriler (seri_adi, seri_kodu, aciklama, resim_yolu) VALUES (%s, %s, %s, %s)",
            (data['seri_adi'], data['seri_kodu'], data.get('aciklama'), data.get('resim_yolu'))
        )
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return success({"id": new_id, "message": "Seri başarıyla eklendi"}, 201)
    except mysql.connector.IntegrityError:
        return error("Bu seri kodu zaten mevcut", 400)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/seriler/<int:seri_id>', methods=['PUT'])
def update_seri(seri_id):
    """Mevcut seriyi günceller"""
    try:
        data = request.get_json()
        if not data:
            return error("Güncellenecek veri gönderilmedi", 400)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE seriler SET seri_adi=%s, seri_kodu=%s, aciklama=%s, resim_yolu=%s WHERE id=%s",
            (data.get('seri_adi'), data.get('seri_kodu'), data.get('aciklama'), data.get('resim_yolu'), seri_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            return error("Seri bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Seri güncellendi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/seriler/<int:seri_id>', methods=['DELETE'])
def delete_seri(seri_id):
    """Seriyi siler (CASCADE ile ilişkili modeller de silinir)"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM seriler WHERE id = %s", (seri_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error("Seri bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Seri silindi"})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 2. MODELLER ENDPOINT'LERİ
# ==================================================================

@app.route('/api/modeller', methods=['GET'])
def get_modeller():
    """
    Tüm modelleri getirir. Opsiyonel: ?seri_id=1 ile filtrele.
    JOIN kullanarak seri adını da dahil ediyoruz.
    """
    try:
        seri_id = request.args.get('seri_id')
        db = get_db()
        cursor = db.cursor(dictionary=True)

        if seri_id:
            cursor.execute("""
                SELECT m.*, s.seri_adi, s.seri_kodu
                FROM modeller m
                JOIN seriler s ON m.seri_id = s.id
                WHERE m.seri_id = %s AND m.aktif = 1
                ORDER BY m.model_adi
            """, (seri_id,))
        else:
            cursor.execute("""
                SELECT m.*, s.seri_adi, s.seri_kodu
                FROM modeller m
                JOIN seriler s ON m.seri_id = s.id
                WHERE m.aktif = 1
                ORDER BY s.seri_kodu, m.model_adi
            """)

        modeller = cursor.fetchall()
        cursor.close()
        db.close()
        return success(modeller)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/modeller/<int:model_id>', methods=['GET'])
def get_model(model_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, s.seri_adi
            FROM modeller m
            JOIN seriler s ON m.seri_id = s.id
            WHERE m.id = %s
        """, (model_id,))
        model = cursor.fetchone()
        cursor.close()
        db.close()
        if not model:
            return error("Model bulunamadı", 404)
        return success(model)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/modeller', methods=['POST'])
def create_model():
    try:
        data = request.get_json()
        if not data or not data.get('seri_id') or not data.get('model_adi'):
            return error("seri_id ve model_adi zorunludur", 400)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO modeller (seri_id, model_adi, yakit_tipi, motor_bilgisi, motor_gucu, hiz_0_100, resim_yolu)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['seri_id'], data['model_adi'],
            data.get('yakit_tipi', 'Benzin'), data.get('motor_bilgisi'),
            data.get('motor_gucu'), data.get('hiz_0_100'), data.get('resim_yolu')
        ))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return success({"id": new_id, "message": "Model eklendi"}, 201)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/modeller/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    try:
        data = request.get_json()
        if not data:
            return error("Veri gönderilmedi", 400)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE modeller SET seri_id=%s, model_adi=%s, yakit_tipi=%s,
            motor_bilgisi=%s, motor_gucu=%s, hiz_0_100=%s, resim_yolu=%s, aktif=%s
            WHERE id=%s
        """, (
            data.get('seri_id'), data.get('model_adi'), data.get('yakit_tipi'),
            data.get('motor_bilgisi'), data.get('motor_gucu'), data.get('hiz_0_100'),
            data.get('resim_yolu'), data.get('aktif', 1), model_id
        ))
        db.commit()
        if cursor.rowcount == 0:
            return error("Model bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Model güncellendi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/modeller/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM modeller WHERE id = %s", (model_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error("Model bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Model silindi"})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 3. FİYAT LİSTESİ ENDPOINT'LERİ
# (Tüm tabloları JOIN'leyen ana sorgu)
# ==================================================================

@app.route('/api/fiyat-listesi', methods=['GET'])
def get_fiyat_listesi():
    """
    Fiyat listesini tam JOIN ile getirir.
    Neden 4 tabloyu JOIN'liyoruz? Frontend'in tek istekte
    tüm tabloyu render edebilmesi için gereksiz ek istek yapmak istemiyoruz.
    """
    try:
        seri_id = request.args.get('seri_id')
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT
                fl.id, fl.fiyat, fl.gecerlilik_tarihi,
                m.id AS model_id, m.model_adi, m.yakit_tipi, m.kasa_tipi,
                m.resim_yolu,
                dp.id AS donanim_id, dp.paket_adi, dp.motor AS motor_bilgisi, dp.motor_gucu, dp.hiz_0_100, dp.sanziman, dp.ozellikler,
                s.id AS seri_id, s.seri_adi, s.seri_kodu
            FROM fiyat_listesi fl
            JOIN donanim_paketleri dp ON fl.donanim_id = dp.id
            JOIN modeller m ON dp.model_id = m.id
            JOIN seriler s ON m.seri_id = s.id
            WHERE m.aktif = 1
        """
        params = []
        if seri_id:
            query += " AND s.id = %s"
            params.append(seri_id)
        query += " ORDER BY s.seri_kodu, m.model_adi, fl.fiyat"

        cursor.execute(query, params)
        fiyatlar = cursor.fetchall()
        # Decimal tipini float'a çevir (JSON serializable)
        for row in fiyatlar:
            row['fiyat'] = float(row['fiyat'])
        cursor.close()
        db.close()
        return success(fiyatlar)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/fiyat-listesi/<int:fiyat_id>', methods=['PUT'])
def update_fiyat(fiyat_id):
    try:
        data = request.get_json()
        if not data or 'fiyat' not in data:
            return error("fiyat alanı zorunludur", 400)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE fiyat_listesi SET fiyat=%s, gecerlilik_tarihi=%s WHERE id=%s",
            (data['fiyat'], data.get('gecerlilik_tarihi'), fiyat_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            return error("Kayıt bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Fiyat güncellendi"})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 4. İLETİŞİM TALEPLERİ ENDPOINT'LERİ
# ==================================================================

@app.route('/api/iletisim', methods=['POST'])
def create_iletisim():
    """
    İletişim formunu veritabanına kaydeder.
    Sunucu taraflı validasyon yapıyoruz — frontend validasyonuna
    güvenmek tek başına yeterli değildir (güvenlik prensibi).
    """
    try:
        data = request.get_json()
        # Zorunlu alan kontrolü
        required = ['ad', 'soyad', 'email', 'gsm']
        for field in required:
            if not data or not data.get(field, '').strip():
                return error(f"'{field}' alanı zorunludur", 400)

        # E-posta basit format kontrolü
        if '@' not in data['email'] or '.' not in data['email']:
            return error("Geçerli bir e-posta adresi giriniz", 400)

        # GSM uzunluk kontrolü
        gsm = data['gsm'].strip()
        if len(gsm) < 10:
            return error("Geçerli bir GSM numarası giriniz", 400)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO iletisim_talepleri (ad, soyad, email, gsm, kvkk_onay, ileti_izin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['ad'].strip(), data['soyad'].strip(),
            data['email'].strip(), gsm,
            1 if data.get('kvkk_onay') else 0,
            1 if data.get('ileti_izin') else 0
        ))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return success({"id": new_id, "message": "Talebiniz alındı, ekibimiz en kısa sürede iletişime geçecek."}, 201)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/iletisim', methods=['GET'])
def get_iletisim_talepleri():
    """Admin paneli için tüm iletişim taleplerini listeler"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM iletisim_talepleri ORDER BY olusturma_tarihi DESC")
        talepler = cursor.fetchall()
        for t in talepler:
            if t.get('olusturma_tarihi'):
                t['olusturma_tarihi'] = t['olusturma_tarihi'].strftime('%d.%m.%Y %H:%M')
        cursor.close()
        db.close()
        return success(talepler)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/iletisim/<int:talep_id>', methods=['PATCH'])
def update_iletisim_durum(talep_id):
    """Talebin durumunu günceller (Bekliyor/İşleniyor/Tamamlandı)"""
    try:
        data = request.get_json()
        durum = data.get('durum')
        if durum not in ['Bekliyor', 'İşleniyor', 'Tamamlandı']:
            return error("Geçersiz durum değeri", 400)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE iletisim_talepleri SET durum=%s WHERE id=%s", (durum, talep_id))
        db.commit()
        if cursor.rowcount == 0:
            return error("Talep bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Durum güncellendi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/iletisim/<int:talep_id>', methods=['DELETE'])
def delete_iletisim(talep_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM iletisim_talepleri WHERE id=%s", (talep_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error("Talep bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Talep silindi"})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 5. GERİ ÇAĞIRMA ENDPOINT'LERİ
# ==================================================================

@app.route('/api/geri-cagirma', methods=['POST'])
def sorgula_vin():
    """VIN numarasını kaydeder ve simüle edilmiş sorgu sonucu döner"""
    try:
        data = request.get_json()
        vin = data.get('vin_no', '').strip().upper()

        # VIN 17 karakter olmalı
        if len(vin) != 17:
            return error("Şasi numarası 17 karakter olmalıdır", 400)

        # Demo: Gerçek projede burada BMW API'sine istek atılır
        etkilendi = 0
        sonuc = "Aracınız için aktif bir gönüllü geri çağırma işlemi bulunmamaktadır."

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO geri_cagirmalar (vin_no, sorgu_sonucu, etkilendi) VALUES (%s, %s, %s)",
            (vin, sonuc, etkilendi)
        )
        db.commit()
        cursor.close()
        db.close()
        return success({"vin_no": vin, "etkilendi": etkilendi, "sonuc": sonuc})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 6. KAMPANYALAR ENDPOINT'LERİ
# ==================================================================

@app.route('/api/kampanyalar', methods=['GET'])
def get_kampanyalar():
    """Aktif kampanyaları getirir"""
    try:
        sadece_aktif = request.args.get('aktif', '1')
        db = get_db()
        cursor = db.cursor(dictionary=True)
        if sadece_aktif == '1':
            cursor.execute("SELECT *, baslik AS kampanya_adi FROM kampanyalar WHERE aktif=1 ORDER BY baslangic_tarihi DESC")
        else:
            cursor.execute("SELECT *, baslik AS kampanya_adi FROM kampanyalar ORDER BY baslangic_tarihi DESC")
        kampanyalar = cursor.fetchall()
        for k in kampanyalar:
            if k.get('baslangic_tarihi'):
                k['baslangic_tarihi'] = k['baslangic_tarihi'].strftime('%d.%m.%Y')
            if k.get('bitis_tarihi'):
                k['bitis_tarihi'] = k['bitis_tarihi'].strftime('%d.%m.%Y')
        cursor.close()
        db.close()
        return success(kampanyalar)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/kampanyalar', methods=['POST'])
def create_kampanya():
    try:
        data = request.get_json()
        required = ['kampanya_adi', 'baslangic_tarihi', 'bitis_tarihi']
        for f in required:
            if not data or not data.get(f):
                return error(f"'{f}' zorunludur", 400)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO kampanyalar (baslik, aciklama, baslangic_tarihi, bitis_tarihi, aktif, resim_yolu)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['kampanya_adi'], data.get('aciklama'),
            data['baslangic_tarihi'], data['bitis_tarihi'],
            1 if data.get('aktif', True) else 0, data.get('resim_yolu')
        ))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return success({"id": new_id, "message": "Kampanya eklendi"}, 201)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/kampanyalar/<int:kampanya_id>', methods=['PUT'])
def update_kampanya(kampanya_id):
    try:
        data = request.get_json()
        if not data:
            return error("Veri gönderilmedi", 400)
        db = get_db()
        cursor = db.cursor()
        
        # Dinamik SQL oluşturarak sadece gelen alanları güncelle
        fields = []
        params = []
        
        if 'kampanya_adi' in data:
            fields.append("baslik = %s")
            params.append(data['kampanya_adi'])
        elif 'baslik' in data:
            fields.append("baslik = %s")
            params.append(data['baslik'])
            
        if 'aciklama' in data:
            fields.append("aciklama = %s")
            params.append(data['aciklama'])
            
        if 'baslangic_tarihi' in data:
            fields.append("baslangic_tarihi = %s")
            params.append(data['baslangic_tarihi'])
            
        if 'bitis_tarihi' in data:
            fields.append("bitis_tarihi = %s")
            params.append(data['bitis_tarihi'])
            
        if 'aktif' in data:
            fields.append("aktif = %s")
            params.append(1 if data['aktif'] else 0)
            
        if 'resim_yolu' in data:
            fields.append("resim_yolu = %s")
            params.append(data['resim_yolu'])
            
        if not fields:
            return error("Güncellenecek geçerli alan bulunamadı", 400)
            
        params.append(kampanya_id)
        query = f"UPDATE kampanyalar SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, params)
        db.commit()
        if cursor.rowcount == 0:
            return error("Kampanya bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Kampanya güncellendi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/kampanyalar/<int:kampanya_id>', methods=['DELETE'])
def delete_kampanya(kampanya_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM kampanyalar WHERE id=%s", (kampanya_id,))
        db.commit()
        if cursor.rowcount == 0:
            return error("Kampanya bulunamadı", 404)
        cursor.close()
        db.close()
        return success({"message": "Kampanya silindi"})
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 7. KULLANICI / AUTH ENDPOINT'LERİ
# ==================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Admin girişi. bcrypt kullanıyoruz çünkü düz metin şifre
    saklamak güvenlik açığıdır. bcrypt otomatik salt ekler.
    """
    try:
        data = request.get_json()
        if not data or not data.get('kullanici_adi') or not data.get('sifre'):
            return error("Kullanıcı adı ve şifre zorunludur", 400)

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM kullanicilar WHERE kullanici_adi=%s",
            (data['kullanici_adi'],)
        )
        kullanici = cursor.fetchone()

        if not kullanici:
            return error("Kullanıcı adı veya şifre hatalı", 401)

        # bcrypt hash doğrulama
        sifre_bytes = data['sifre'].encode('utf-8')
        hash_bytes = kullanici['sifre_hash'].encode('utf-8')

        if not bcrypt.checkpw(sifre_bytes, hash_bytes):
            return error("Kullanıcı adı veya şifre hatalı", 401)

        # Son giriş zamanını güncelle
        cursor.execute(
            "UPDATE kullanicilar SET son_giris=NOW() WHERE id=%s",
            (kullanici['id'],)
        )
        db.commit()
        cursor.close()
        db.close()

        return success({
            "id": kullanici['id'],
            "kullanici_adi": kullanici['kullanici_adi'],
            "rol": kullanici['rol'],
            "message": "Giriş başarılı"
        })
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/auth/set-password', methods=['POST'])
def set_password():
    """
    Admin şifresini bcrypt ile hashleyip veritabanına yazar.
    İlk kurulumda kullanın: POST /api/auth/set-password
    Body: {"kullanici_adi": "admin", "sifre": "yenisifre"}
    """
    try:
        data = request.get_json()
        sifre = data.get('sifre', '').encode('utf-8')
        hashed = bcrypt.hashpw(sifre, bcrypt.gensalt(12))
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE kullanicilar SET sifre_hash=%s WHERE kullanici_adi=%s",
            (hashed.decode('utf-8'), data.get('kullanici_adi'))
        )
        db.commit()
        affected = cursor.rowcount
        cursor.close()
        db.close()
        if affected == 0:
            return error("Kullanıcı bulunamadı", 404)
        return success({"message": "Şifre güncellendi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/auth/musteri-kayit', methods=['POST'])
def musteri_kayit():
    try:
        data = request.get_json()
        if not data or not data.get('ad_soyad') or not data.get('email') or not data.get('sifre'):
            return error("Tüm alanlar zorunludur", 400)
        
        sifre = data['sifre'].encode('utf-8')
        hashed = bcrypt.hashpw(sifre, bcrypt.gensalt(12)).decode('utf-8')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO musteriler (ad_soyad, email, sifre_hash) VALUES (%s, %s, %s)",
            (data['ad_soyad'], data['email'], hashed)
        )
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return success({"id": new_id, "message": "Kayıt başarılı!"}, 201)
    except mysql.connector.IntegrityError:
        return error("Bu e-posta adresi zaten kullanılıyor", 400)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/auth/musteri-login', methods=['POST'])
def musteri_login():
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM musteriler WHERE email=%s", (data.get('email'),))
        musteri = cursor.fetchone()
        
        if not musteri:
            return error("E-posta veya şifre hatalı", 401)
            
        sifre_bytes = data.get('sifre', '').encode('utf-8')
        hash_bytes = musteri['sifre_hash'].encode('utf-8')
        
        if not bcrypt.checkpw(sifre_bytes, hash_bytes):
            return error("E-posta veya şifre hatalı", 401)
            
        cursor.close()
        db.close()
        return success({
            "id": musteri['id'],
            "ad_soyad": musteri['ad_soyad'],
            "email": musteri['email'],
            "message": "Giriş başarılı"
        })
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 8. SEPET, FAVORİLER VE BAYİLER ENDPOINT'LERİ (SESSION BAZLI)
# ==================================================================

@app.route('/api/bayiler', methods=['GET'])
def get_bayiler():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bayiler")
        bayiler = cursor.fetchall()
        cursor.close()
        db.close()
        return success(bayiler)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/favoriler', methods=['GET', 'POST', 'DELETE'])
def manage_favoriler():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        if request.method == 'GET':
            session_id = request.args.get('session_id')
            if not session_id: return error("session_id gerekli", 400)
            cursor.execute("""
                SELECT f.id as fav_id, m.*, s.seri_adi 
                FROM favoriler f
                JOIN modeller m ON f.model_id = m.id
                JOIN seriler s ON m.seri_id = s.id
                WHERE f.session_id = %s
            """, (session_id,))
            data = cursor.fetchall()
            return success(data)
        elif request.method == 'POST':
            data = request.get_json()
            session_id = data.get('session_id')
            musteri_id = data.get('musteri_id', None)
            cursor.execute(
                "INSERT INTO favoriler (session_id, musteri_id, model_id) VALUES (%s, %s, %s)",
                (session_id, musteri_id, data['model_id'])
            )
            db.commit()
            return success({"message": "Favorilere eklendi"})
        elif request.method == 'DELETE':
            fav_id = request.args.get('id')
            cursor.execute("DELETE FROM favoriler WHERE id = %s", (fav_id,))
            db.commit()
            return success({"message": "Favorilerden silindi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/sepet', methods=['GET', 'POST', 'DELETE'])
def manage_sepet():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        if request.method == 'GET':
            session_id = request.args.get('session_id')
            if not session_id: return error("session_id gerekli", 400)
            cursor.execute("""
                SELECT sp.id as sepet_id, m.model_adi, m.resim_yolu, dp.paket_adi, fl.fiyat
                FROM sepet sp
                JOIN donanim_paketleri dp ON sp.donanim_id = dp.id
                JOIN modeller m ON dp.model_id = m.id
                LEFT JOIN fiyat_listesi fl ON fl.donanim_id = dp.id
                WHERE sp.session_id = %s
            """, (session_id,))
            data = cursor.fetchall()
            return success(data)
        elif request.method == 'POST':
            data = request.get_json()
            session_id = data.get('session_id')
            musteri_id = data.get('musteri_id', None)
            cursor.execute(
                "INSERT INTO sepet (session_id, musteri_id, donanim_id) VALUES (%s, %s, %s)",
                (session_id, musteri_id, data['donanim_id'])
            )
            db.commit()
            return success({"message": "Sepete eklendi"})
        elif request.method == 'DELETE':
            sepet_id = request.args.get('id')
            cursor.execute("DELETE FROM sepet WHERE id = %s", (sepet_id,))
            db.commit()
            return success({"message": "Sepetten silindi"})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/admin/sepet_ozet', methods=['GET'])
def get_sepet_ozet():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT sp.id, sp.olusturma_tarihi, mus.ad_soyad, mus.email, m.model_adi, dp.paket_adi, fl.fiyat
            FROM sepet sp
            LEFT JOIN musteriler mus ON sp.musteri_id = mus.id
            JOIN donanim_paketleri dp ON sp.donanim_id = dp.id
            JOIN modeller m ON dp.model_id = m.id
            LEFT JOIN fiyat_listesi fl ON fl.donanim_id = dp.id
            ORDER BY sp.olusturma_tarihi DESC
        """)
        data = cursor.fetchall()
        for d in data:
            if d.get('olusturma_tarihi'):
                d['olusturma_tarihi'] = d['olusturma_tarihi'].strftime('%d.%m.%Y %H:%M')
            if d.get('fiyat'):
                d['fiyat'] = float(d['fiyat'])
        cursor.close()
        db.close()
        return success(data)
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/siparis_olustur', methods=['POST'])
def siparis_olustur():
    try:
        data = request.get_json()
        musteri_id = data.get('musteri_id')
        session_id = data.get('session_id')
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Sepetteki ürünleri al
        cursor.execute("""
            SELECT sp.id, sp.donanim_id, fl.fiyat 
            FROM sepet sp
            LEFT JOIN fiyat_listesi fl ON fl.donanim_id = sp.donanim_id
            WHERE sp.musteri_id = %s OR sp.session_id = %s
        """, (musteri_id, session_id))
        sepet_items = cursor.fetchall()
        
        if not sepet_items:
            return error("Sepetiniz boş.", 400)
            
        # Siparişler tablosuna taşı
        for item in sepet_items:
            tutar = item['fiyat'] if item['fiyat'] else 0
            # Müşteri girişi zorunlu, değilse siparişe kaydedemeyiz.
            if not musteri_id:
                return error("Sipariş oluşturmak için lütfen giriş yapın.", 401)
                
            cursor.execute("""
                INSERT INTO siparisler (musteri_id, donanim_id, tutar)
                VALUES (%s, %s, %s)
            """, (musteri_id, item['donanim_id'], tutar))
            
            # Sepetten sil
            cursor.execute("DELETE FROM sepet WHERE id = %s", (item['id'],))
            
        db.commit()
        cursor.close()
        db.close()
        return success({"message": "Siparişiniz başarıyla oluşturuldu."})
    except Exception as e:
        return error(str(e), 500)

@app.route('/api/admin/siparisler', methods=['GET'])
def get_admin_siparisler():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.siparis_tarihi, s.durum, s.tutar,
                   mus.ad_soyad, mus.email, m.model_adi, dp.paket_adi
            FROM siparisler s
            JOIN musteriler mus ON s.musteri_id = mus.id
            JOIN donanim_paketleri dp ON s.donanim_id = dp.id
            JOIN modeller m ON dp.model_id = m.id
            ORDER BY s.siparis_tarihi DESC
        """)
        data = cursor.fetchall()
        for d in data:
            if d.get('siparis_tarihi'):
                d['siparis_tarihi'] = d['siparis_tarihi'].strftime('%d.%m.%Y %H:%M')
            if d.get('tutar'):
                d['tutar'] = float(d['tutar'])
        cursor.close()
        db.close()
        return success(data)
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# 9. GÖSTERGE PANELİ (DASHBOARD) İSTATİSTİKLERİ
# ==================================================================

@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as sayi FROM siparisler")
        siparis_sayi = cursor.fetchone()['sayi']
        
        cursor.execute("SELECT COUNT(*) as sayi FROM sepet")
        sepet_sayi = cursor.fetchone()['sayi']
        
        cursor.execute("SELECT COUNT(*) as sayi FROM iletisim_talepleri")
        iletisim_sayi = cursor.fetchone()['sayi']
        
        cursor.execute("SELECT COUNT(*) as sayi FROM musteriler")
        musteri_sayi = cursor.fetchone()['sayi']
        
        cursor.execute("SELECT COUNT(*) as sayi FROM modeller")
        model_sayi = cursor.fetchone()['sayi']
        
        cursor.execute("SELECT COUNT(*) as sayi FROM kampanyalar WHERE aktif = 1")
        kampanya_sayi = cursor.fetchone()['sayi']
        
        cursor.close()
        db.close()
        return success({
            "siparis": siparis_sayi,
            "sepet": sepet_sayi,
            "iletisim": iletisim_sayi,
            "musteri": musteri_sayi,
            "model": model_sayi,
            "kampanya": kampanya_sayi
        })
    except Exception as e:
        return error(str(e), 500)

# ==================================================================
# UYGULAMA BAŞLATMA
# ==================================================================
if __name__ == '__main__':
    print("BMW Bayi API sunucusu başlatılıyor...")
    print("Adres: http://localhost:5000")
    print("Admin paneli: http://localhost:5000/admin.html")
    app.run(debug=True, host='0.0.0.0', port=5000)
