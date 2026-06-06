from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from typing import List, Optional

# Akademik Savunma: Neden FastAPI kullanıldı?
# FastAPI, asenkron yapısı sayesinde yüksek performans sağlar ve otomatik Swagger UI dokümantasyonu üretir.
# Bu sayede hem RESTful standartlarına uymak hem de frontend tarafında API entegrasyonunu test etmek çok daha kolaydır.

app = FastAPI(title="BMW Bayi API")

# CORS ayarları - Frontend'in API'ye erişebilmesi için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantı fonksiyonu
# Akademik Savunma: Neden her istekte yeni bağlantı açılıyor?
# Basit bir mimari sunmak ve veritabanı kilitlenmelerini (deadlock) önlemek için her işlem kendi bağlantısını açıp kapatır.
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # XAMPP varsayılan şifresi boştur
            database="bmw_bayi"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı.")

# Pydantic Modelleri (Veri Doğrulama / Validation)
class IletisimTalebi(BaseModel):
    ad: str
    soyad: str
    email: str
    gsm: str
    kvkk_onay: bool

class Kampanya(BaseModel):
    kampanya_adi: str
    aciklama: str
    baslangic_tarihi: str
    bitis_tarihi: str
    aktif: bool
    resim_yolu: Optional[str] = None

# ==========================================
# ENDPOINT'LER (RESTful API Uç Noktaları)
# ==========================================

# 1. Modelleri Getir (GET)
@app.get("/api/modeller")
def get_modeller():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # JOIN kullanarak seri adını da getiriyoruz
    query = """
        SELECT m.*, s.seri_adi 
        FROM modeller m 
        JOIN seriler s ON m.seri_id = s.id 
        WHERE m.aktif = 1
    """
    cursor.execute(query)
    modeller = cursor.fetchall()
    cursor.close()
    conn.close()
    return modeller

# 2. Fiyat Listesini Getir (GET)
@app.get("/api/fiyat-listesi")
def get_fiyat_listesi():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 3 Tabloyu JOIN ile birleştiriyoruz: modeller + donanim_paketleri + fiyat_listesi
    # Akademik Savunma: İlişkisel veritabanı kullanmanın en büyük avantajı bu tür sorgularda veri tekrarını önlemesidir.
    query = """
        SELECT m.model_adi, dp.paket_adi, fl.fiyat, fl.gecerlilik_tarihi
        FROM fiyat_listesi fl
        JOIN donanim_paketleri dp ON fl.donanim_id = dp.id
        JOIN modeller m ON dp.model_id = m.id
        ORDER BY m.model_adi, fl.fiyat ASC
    """
    cursor.execute(query)
    fiyatlar = cursor.fetchall()
    cursor.close()
    conn.close()
    return fiyatlar

# 3. İletişim Talebi Oluştur (POST)
@app.post("/api/iletisim", status_code=201)
def create_iletisim(talep: IletisimTalebi):
    if not talep.kvkk_onay:
        raise HTTPException(status_code=400, detail="KVKK onayı zorunludur.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO iletisim_talepleri (ad, soyad, email, gsm, kvkk_onay) VALUES (%s, %s, %s, %s, %s)"
    values = (talep.ad, talep.soyad, talep.email, talep.gsm, 1 if talep.kvkk_onay else 0)
    
    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Talep kaydedilemedi.")
    finally:
        cursor.close()
        conn.close()
        
    return {"message": "Talebiniz başarıyla alındı."}

# 4. Kampanyalar (GET)
@app.get("/api/kampanyalar")
def get_kampanyalar():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM kampanyalar ORDER BY baslangic_tarihi DESC"
    cursor.execute(query)
    kampanyalar = cursor.fetchall()
    cursor.close()
    conn.close()
    return kampanyalar

class KampanyaBasvuru(BaseModel):
    ad: str
    soyad: str
    email: str
    telefon: str
    kampanya_adi: str

# 4.5 Kampanya Başvurusu (POST)
@app.post("/api/kampanyalar/basvuru", status_code=201)
def create_kampanya_basvuru(basvuru: KampanyaBasvuru):
    # Veritabanında kampanya başvurusu tablosu yok, iletişim tablosuna kaydediyoruz.
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO iletisim_talepleri (ad, soyad, email, gsm, kvkk_onay, durum) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (basvuru.ad, basvuru.soyad, basvuru.email, basvuru.telefon, 1, 'Bekliyor')
    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Talep kaydedilemedi.")
    finally:
        cursor.close()
        conn.close()
    return {"message": "Başvurunuz alındı."}

# --- ADMIN PANELİ İÇİN CRUD İŞLEMLERİ ---

# 5. Model Sil (DELETE)
@app.delete("/api/modeller/{model_id}")
def delete_model(model_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM modeller WHERE id = %s", (model_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Model bulunamadı.")
        
    cursor.execute("DELETE FROM modeller WHERE id = %s", (model_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Model silindi."}

if __name__ == "__main__":
    import uvicorn
    # Akademik Savunma: Uygulama yerel ağda 8000 portunda çalışacak şekilde ayarlandı.
    uvicorn.run(app, host="127.0.0.1", port=8000)
