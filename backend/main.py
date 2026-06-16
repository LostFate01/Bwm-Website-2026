from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from typing import List, Optional

app = FastAPI(title="BMW Bayi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bmw_bayi"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Veritabanı bağlantı hatası: {err}")
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı.")

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

@app.get("/api/modeller")
def get_modeller():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT m.*, s.seri_adi, s.seri_kodu
        FROM modeller m
        JOIN seriler s ON m.seri_id = s.id
        WHERE m.aktif = 1
        ORDER BY s.seri_kodu, m.model_adi
    """
    cursor.execute(query)
    modeller = cursor.fetchall()
    cursor.close()
    conn.close()
    return modeller

@app.get("/api/fiyat-listesi")
def get_fiyat_listesi():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
        ORDER BY s.seri_kodu, m.model_adi, fl.fiyat
    """
    cursor.execute(query)
    fiyatlar = cursor.fetchall()
    for row in fiyatlar:
        if row.get('fiyat'):
            row['fiyat'] = float(row['fiyat'])
    cursor.close()
    conn.close()
    return fiyatlar

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

@app.post("/api/kampanyalar/basvuru", status_code=201)
def create_kampanya_basvuru(basvuru: KampanyaBasvuru):
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
