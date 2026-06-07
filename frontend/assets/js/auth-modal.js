document.addEventListener("DOMContentLoaded", function() {
    const authModal = document.getElementById('authModal');
    if (!authModal) return;

    const loginView = document.getElementById('loginView');
    const registerView = document.getElementById('registerView');
    
    const showRegisterBtn = document.getElementById('showRegisterBtn');
    const showLoginBtn = document.getElementById('showLoginBtn');

    // Toggle to Register View
    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loginView.style.display = 'none';
            loginView.classList.remove('fade-in-active');
            
            registerView.style.display = 'block';
            setTimeout(() => {
                registerView.classList.add('fade-in-active');
            }, 50);
        });
    }

    // Toggle to Login View
    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            registerView.style.display = 'none';
            registerView.classList.remove('fade-in-active');
            
            loginView.style.display = 'block';
            setTimeout(() => {
                loginView.classList.add('fade-in-active');
            }, 50);
        });
    }

    // Reset to Login View when modal is closed
    authModal.addEventListener('hidden.bs.modal', function () {
        registerView.style.display = 'none';
        registerView.classList.remove('fade-in-active');
        
        loginView.style.display = 'block';
        loginView.classList.add('fade-in-active');
        
        // Clear all inputs
        const inputs = authModal.querySelectorAll('input');
        inputs.forEach(input => input.value = '');
    });

    // MÜŞTERİ KAYIT İŞLEMİ
    const regSubmitBtn = document.getElementById('regSubmitBtn');
    if(regSubmitBtn) {
        regSubmitBtn.addEventListener('click', function() {
            const adSoyad = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const sifre = document.getElementById('regPassword').value;

            if(!adSoyad || !email || !sifre) {
                alert("Lütfen tüm alanları doldurun.");
                return;
            }

            fetch('http://localhost:5000/api/auth/musteri-kayit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ad_soyad: adSoyad, email: email, sifre: sifre })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    alert("Kayıt başarılı! Şimdi giriş yapabilirsiniz.");
                    document.getElementById('showLoginBtn').click();
                } else {
                    alert("Hata: " + data.error);
                }
            })
            .catch(err => alert("Sunucu hatası."));
        });
    }

    // MÜŞTERİ GİRİŞ İŞLEMİ
    const loginSubmitBtn = document.getElementById('loginSubmitBtn');
    if(loginSubmitBtn) {
        loginSubmitBtn.addEventListener('click', function() {
            const email = document.getElementById('loginEmail').value;
            const sifre = document.getElementById('loginPassword').value;

            if(!email || !sifre) {
                alert("E-posta ve şifre zorunludur.");
                return;
            }

            fetch('http://localhost:5000/api/auth/musteri-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, sifre: sifre })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    alert(`Hoşgeldin, ${data.data.ad_soyad}!`);
                    localStorage.setItem('musteri_id', data.data.id);
                    localStorage.setItem('musteri_ad', data.data.ad_soyad);
                    window.location.reload();
                } else {
                    alert("Hata: " + data.error);
                }
            })
            .catch(err => alert("Sunucu hatası."));
        });
    }

    // Profil İkonu Kontrolü (Giriş yapılmışsa pop-up açma, çıkış yapma özelliği ekle)
    const musteriId = localStorage.getItem('musteri_id');
    const musteriAd = localStorage.getItem('musteri_ad');
    
    if (musteriId && musteriAd) {
        const profileIcons = document.querySelectorAll('.bi-person');
        profileIcons.forEach(icon => {
            const link = icon.closest('a');
            if (link) {
                link.removeAttribute('data-bs-toggle');
                link.removeAttribute('data-bs-target');
                link.title = `Hoşgeldin ${musteriAd} - Çıkış Yap`;
                
                // İkonu dolu yap
                icon.classList.remove('bi-person');
                icon.classList.add('bi-person-check-fill');

                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    if(confirm(`Hoşgeldin ${musteriAd}!\nHesabından çıkış yapmak istiyor musun?`)) {
                        localStorage.removeItem('musteri_id');
                        localStorage.removeItem('musteri_ad');
                        window.location.reload();
                    }
                });
            }
        });
    }
});
