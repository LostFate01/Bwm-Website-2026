import sys
import re

with open(r'c:\Users\enest\Documents\GitHub\Bwm-website\frontend\admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Sidebar Button
if 'showSection(\'siparisler\')' not in content:
    content = content.replace(
        '<button class="nav-btn" onclick="showSection(\'modeller\')"><i class="bi bi-car-front me-2"></i> Modeller</button>',
        '<button class="nav-btn" onclick="showSection(\'modeller\')"><i class="bi bi-car-front me-2"></i> Modeller</button>\n      <button class="nav-btn" onclick="showSection(\'siparisler\')"><i class="bi bi-bag-check me-2"></i> Siparişler</button>'
    )

# 2. Add Section HTML
section_html = """
      <!-- SİPARİŞLER -->
      <div id="section-siparisler" class="section">
        <h3 class="mb-4"><i class="bi bi-bag-check"></i> Siparişler</h3>
        <div id="siparis-alert" class="alert-api"></div>
        <div class="card-admin">
          <div class="table-responsive">
            <table class="table table-dark table-hover" id="siparis-table">
              <thead>
                <tr>
                  <th>ID</th><th>Müşteri</th><th>E-Posta</th><th>Model / Paket</th>
                  <th>Tutar (₺)</th><th>Tarih</th><th>Durum</th>
                </tr>
              </thead>
              <tbody id="siparis-body"></tbody>
            </table>
          </div>
        </div>
      </div>
"""

if 'id="section-siparisler"' not in content:
    content = content.replace(
        '<!-- İLETİŞİM TALEPLERİ -->',
        section_html + '\n      <!-- İLETİŞİM TALEPLERİ -->'
    )

# 3. Add to loadAll
if 'loadSiparisler()' not in content:
    content = content.replace(
        'loadModeller();',
        'loadModeller();\n  loadSiparisler();'
    )

# 4. Add JS function
js_code = """
// ——— SİPARİŞLER ———
async function loadSiparisler() {
  try {
    const res = await fetch(`${API}/admin/siparisler`);
    const json = await res.json();
    const tbody = document.getElementById('siparis-body');
    tbody.innerHTML = '';
    if(json.data && json.data.length > 0) {
      json.data.forEach(s => {
        let badge = s.durum === 'Onaylandı' ? 'badge-tamamlandi' : 'badge-bekliyor';
        tbody.innerHTML += `<tr>
          <td>#${s.id}</td>
          <td>${s.ad_soyad}</td>
          <td>${s.email}</td>
          <td>${s.model_adi} - ${s.paket_adi}</td>
          <td>${s.tutar.toLocaleString('tr-TR')} ₺</td>
          <td>${s.siparis_tarihi}</td>
          <td><span class="${badge}">${s.durum}</span></td>
        </tr>`;
      });
    } else {
       tbody.innerHTML = '<tr><td colspan="7" class="text-center">Henüz sipariş bulunmuyor.</td></tr>';
    }
  } catch(e) { showAlert('siparis-alert', 'Siparişler yüklenemedi', 'error'); }
}
"""

if 'async function loadSiparisler()' not in content:
    content = content.replace(
        '// ——— İLETİŞİM TALEPLERİ ———',
        js_code + '\n// ——— İLETİŞİM TALEPLERİ ———'
    )

with open(r'c:\Users\enest\Documents\GitHub\Bwm-website\frontend\admin.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("admin.html updated successfully!")
