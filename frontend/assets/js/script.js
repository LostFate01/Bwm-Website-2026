const API_BASE_URL = 'http://localhost:5000/api'; // Varsayılan backend adresi

document.addEventListener('DOMContentLoaded', () => {
    // 1. Fiyat Listesi Yükleme
    const fiyatListesiContainer = document.getElementById('fiyat-listesi-container');
    if (fiyatListesiContainer) {
        fetchFiyatListesi();
    }

    // 2. Modeller Yükleme
    const modellerContainer = document.getElementById('modeller-container');
    if (modellerContainer) {
        fetchModeller();
    }

    // 3. İletişim Formu Gönderimi
    const iletisimForm = document.getElementById('iletisim-form');
    if (iletisimForm) {
        iletisimForm.addEventListener('submit', handleIletisimSubmit);
    }
    
    // 4. Kampanya Formu Gönderimi
    const kampanyaForm = document.getElementById('kampanya-form');
    if (kampanyaForm) {
        kampanyaForm.addEventListener('submit', handleKampanyaSubmit);
    }

    // 5. Admin Verilerini Yükleme
    const adminPanel = document.getElementById('admin-panel');
    if (adminPanel) {
        fetchAdminData();
    }
});

// Fiyat Listesi Fetch
async function fetchFiyatListesi() {
    try {
        const response = await fetch(`${API_BASE_URL}/fiyat-listesi`);
        if (!response.ok) throw new Error('Veri çekilemedi.');
        const data = await response.json();
        renderFiyatListesi(data);
    } catch (error) {
        console.error('Fiyat listesi hatası:', error);
        document.getElementById('fiyat-listesi-container').innerHTML = '<p class="text-danger text-center">Fiyat listesi yüklenirken bir hata oluştu.</p>';
    }
}

function renderFiyatListesi(fiyatlar) {
    const container = document.getElementById('fiyat-listesi-container');
    container.innerHTML = '';
    
    // Group by seri/model
    const groupedData = fiyatlar.reduce((acc, item) => {
        if (!acc[item.seri_adi]) acc[item.seri_adi] = [];
        acc[item.seri_adi].push(item);
        return acc;
    }, {});

    for (const [seri, modeller] of Object.entries(groupedData)) {
        let html = `
            <div class="table-respon mt-5">
                <h1 class="h11">${seri}</h1>
                <table class="table_ulan w-100">
                    <thead class="header1">
                        <tr class="tr1">
                            <th class="th1">Model</th>
                            <th class="th1">Tasarım Paketi</th>
                            <th class="th1">Şanzıman</th>
                            <th class="th1">Motor</th>
                            <th class="th1">Motor Gücü</th>
                            <th class="th1">Fiyat (₺)</th>
                        </tr>
                    </thead>
                    <tbody class="body1">
        `;

        modeller.forEach(model => {
            html += `
                <tr class="tr1">
                    <td class="td1">${model.model_adi}</td>
                    <td class="td1">${model.paket_adi || '-'}</td>
                    <td class="td1">${model.sanzisman || 'Otomatik'}</td>
                    <td class="td1">${model.motor_bilgisi || 'Benzinli'}</td>
                    <td class="td1">${model.motor_gucu || '-'}</td>
                    <td class="td1">${Number(model.fiyat).toLocaleString('tr-TR')} ₺</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
        container.innerHTML += html;
    }
}

// Modeller Fetch
async function fetchModeller() {
    try {
        const response = await fetch(`${API_BASE_URL}/modeller`);
        if (!response.ok) throw new Error('Veri çekilemedi.');
        const data = await response.json();
        renderModeller(data);
    } catch (error) {
        console.error('Modeller hatası:', error);
        document.getElementById('modeller-container').innerHTML = '<p class="text-danger text-center">Modeller yüklenirken bir hata oluştu.</p>';
    }
}

function renderModeller(modeller) {
    const container = document.getElementById('modeller-container');
    container.innerHTML = '';
    
    let html = '<div class="model-grid">';
    modeller.forEach(model => {
        html += `
            <div class="model-card">
                <a href="../pages/fiyat-listesi.html">
                    <img src="${model.gorsel_url || '../images/BMW Logo.png'}" alt="${model.model_adi}" style="max-width: 100%;">
                </a>
                <h3>${model.model_adi}</h3>
                <p style="color: #4d4d4d;">${model.motor_tipi || 'Benzin'}</p>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// Form Submit Handlers
async function handleIletisimSubmit(e) {
    e.preventDefault();
    const form = e.target;
    
    const ad = form.querySelector('#Ad').value;
    const soyad = form.querySelector('#Soyad').value;
    const email = form.querySelector('#Mail').value;
    const gsm = form.querySelector('#GSM').value;
    const onay1 = form.querySelector('#onayver').checked;

    if (!onay1) {
        alert("Lütfen kişisel verilerinizin işlenmesine onay verin.");
        return;
    }

    const formData = {
        ad: ad,
        soyad: soyad,
        email: email,
        gsm: gsm,
        kvkk_onay: true,
        ileti_izin: form.querySelector('#Evet')?.checked || false
    };

    try {
        const response = await fetch(`${API_BASE_URL}/iletisim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const json = await response.json();
        if (json.success) {
            // Başarı mesajını sayfada göster (alert yerine)
            const msg = document.createElement('div');
            msg.style.cssText = 'background:#1e4d2b;color:#2ecc71;border:1px solid #2ecc71;padding:15px;border-radius:8px;margin-top:15px;';
            msg.textContent = '✓ ' + json.data.message;
            form.appendChild(msg);
            form.querySelector('button[type=submit], .destek-form-button')?.remove();
        } else {
            alert('Hata: ' + (json.error || 'Gönderim başarısız.'));
        }
    } catch (error) {
        console.error('Hata:', error);
        alert('Sunucuya bağlanılamadı.');
    }
}

async function handleKampanyaSubmit(e) {
    e.preventDefault();
    const form = e.target;
    
    const ad = form.querySelector('#Ad').value;
    const soyad = form.querySelector('#Soyad').value;
    const email = form.querySelector('#Mail').value;
    const gsm = form.querySelector('#GSM').value;
    const onay1 = form.querySelector('#onayver').checked;

    if (!onay1) {
        alert("Lütfen kişisel verilerinizin işlenmesine onay verin.");
        return;
    }

    // Kampanya formu da iletisim tablosuna kaydedilir
    const formData = {
        ad: ad,
        soyad: soyad,
        email: email,
        gsm: gsm,
        kvkk_onay: true,
        ileti_izin: form.querySelector('#Evet')?.checked || false
    };

    try {
        const response = await fetch(`${API_BASE_URL}/iletisim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const json = await response.json();
        if (json.success) {
            const msg = document.createElement('div');
            msg.style.cssText = 'background:#1e4d2b;color:#2ecc71;border:1px solid #2ecc71;padding:15px;border-radius:8px;margin-top:15px;';
            msg.textContent = '✓ Bilgi ve teklif talebiniz alındı. Ekibimiz en kısa sürede sizinle iletişime geçecektir.';
            form.appendChild(msg);
            form.querySelector('button[type=submit], .destek-form-button')?.remove();
        } else {
            alert('Hata: ' + (json.error || 'Gönderim başarısız.'));
        }
    } catch (error) {
        console.error('Hata:', error);
        alert('Sunucuya bağlanılamadı.');
    }
}

// Admin İşlemleri
async function fetchAdminData() {
    try {
        const response = await fetch(`${API_BASE_URL}/modeller`);
        const result = await response.json();
        
        if(result.success) {
            const tbody = document.getElementById('admin-modeller-tbody');
            if(tbody) {
                tbody.innerHTML = '';
                result.data.forEach(model => {
                    // Motor tipi 'motor_bilgisi' veya 'yakit_tipi' olabilir
                    const motorTipi = model.motor_bilgisi || model.yakit_tipi || '-';
                    tbody.innerHTML += `
                        <tr>
                            <td>${model.id}</td>
                            <td>${model.model_adi}</td>
                            <td>${motorTipi}</td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="editModel(${model.id})">Düzenle</button>
                                <button class="btn btn-sm btn-danger" onclick="deleteModel(${model.id})">Sil</button>
                            </td>
                        </tr>
                    `;
                });
            }
        }

        // Sepet Özetlerini de yükle
        fetchAdminSepetData();
        // Siparişleri de yükle
        fetchAdminSiparislerData();
    } catch (error) {
        console.error('Admin veri yükleme hatası:', error);
    }
}

async function fetchAdminSepetData() {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/sepet_ozet`);
        const result = await response.json();
        if (result.success) {
            const tbody = document.getElementById('admin-sepet-tbody');
            if(tbody) {
                tbody.innerHTML = '';
                if(result.data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center">Henüz sepete eklenmiş ürün yok.</td></tr>';
                    return;
                }
                result.data.forEach(item => {
                    const musteriAdi = item.ad_soyad || '<span class="text-muted">Kayıtsız (Anonim)</span>';
                    const musteriMail = item.email || '-';
                    tbody.innerHTML += `
                        <tr>
                            <td>${item.olusturma_tarihi}</td>
                            <td>${musteriAdi}</td>
                            <td>${musteriMail}</td>
                            <td>${item.model_adi}</td>
                            <td>${item.paket_adi}</td>
                            <td>₺${item.fiyat.toLocaleString('tr-TR')}</td>
                        </tr>
                    `;
                });
            }
        }
    } catch (error) {
        console.error('Admin sepet veri yükleme hatası:', error);
    }
}

async function fetchAdminSiparislerData() {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/siparisler`);
        const result = await response.json();
        if (result.success) {
            const tbody = document.getElementById('admin-siparisler-tbody');
            if(tbody) {
                tbody.innerHTML = '';
                if(result.data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center">Henüz oluşturulmuş bir sipariş yok.</td></tr>';
                    return;
                }
                result.data.forEach(item => {
                    tbody.innerHTML += `
                        <tr>
                            <td>#${item.id}</td>
                            <td>${item.siparis_tarihi}</td>
                            <td>${item.ad_soyad}</td>
                            <td>${item.email}</td>
                            <td>${item.model_adi} - ${item.paket_adi}</td>
                            <td>₺${item.tutar.toLocaleString('tr-TR')}</td>
                            <td><span class="badge bg-warning text-dark">${item.durum}</span></td>
                        </tr>
                    `;
                });
            }
        }
    } catch (error) {
        console.error('Admin sipariş veri yükleme hatası:', error);
    }
}

async function deleteModel(id) {
    if (!confirm('Bu modeli silmek istediğinize emin misiniz?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/modeller/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Model başarıyla silindi!');
            fetchAdminData(); // Tabloyu yenile
        } else {
            alert('Silme işlemi başarısız oldu.');
        }
    } catch (error) {
        console.error('Hata:', error);
        alert('Sunucuya bağlanılamadı.');
    }
}

function editModel(id) {
    alert(`Model Güncelleme (ID: ${id}) işlevi backend entegrasyonu gerektiriyor.`);
    // İleride PUT / PATCH isteği yapılabilir
}
