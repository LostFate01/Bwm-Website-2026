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
});
