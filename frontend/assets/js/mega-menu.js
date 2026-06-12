document.addEventListener("DOMContentLoaded", function() {
    const kesfedinDropdown = document.getElementById('kesfedinDropdown');
    const navbar = document.querySelector('.custom-navbar');
    const navLinks = document.querySelectorAll('.custom-navbar .nav-link');
    const logoImg = document.querySelector('.navbar-brand img');
    
    // Original state
    let originalNavClass = navbar ? navbar.className : '';
    let originalLogoSrc = logoImg ? logoImg.getAttribute('src') : '';
    let isDarkNav = navbar ? navbar.classList.contains('navbar-dark') : false;

    if (kesfedinDropdown && navbar) {
        kesfedinDropdown.addEventListener('show.bs.dropdown', function () {
            const isDarkMode = document.body.classList.contains('dark-mode');
            
            if (isDarkMode) {
                navbar.style.setProperty('background-color', '#1a1a1a', 'important');
                navbar.classList.remove('navbar-light');
                navbar.classList.add('navbar-dark');
                navLinks.forEach(link => {
                    link.classList.remove('text-dark');
                    link.classList.add('text-white');
                });
            } else {
                navbar.style.setProperty('background-color', '#ffffff', 'important');
                navbar.classList.remove('navbar-dark');
                navbar.classList.add('navbar-light');
                navLinks.forEach(link => {
                    link.classList.remove('text-white');
                    link.classList.add('text-dark');
                });
            }

            if (isDarkNav && logoImg) {
                let basePath = originalLogoSrc.substring(0, originalLogoSrc.lastIndexOf('/') + 1);
                if (!basePath) basePath = 'images/';
                
                if (isDarkMode) {
                    logoImg.setAttribute('src', originalLogoSrc); // Keep white logo in dark mode
                } else {
                    logoImg.setAttribute('src', basePath + 'BMW Logo.png');
                }
                logoImg.style.width = '52px';
            }
            
            const innerDiv = navbar.querySelector('div > div');
            if(innerDiv) innerDiv.style.borderBottom = 'none';
        });

        kesfedinDropdown.addEventListener('hidden.bs.dropdown', function () {
            navbar.style.setProperty('background-color', 'transparent', 'important');
            
            if (isDarkNav) {
                navbar.classList.remove('navbar-light');
                navbar.classList.add('navbar-dark');
                
                navLinks.forEach(link => {
                    link.classList.remove('text-dark');
                    link.classList.add('text-white');
                });

                if (logoImg) {
                    logoImg.setAttribute('src', originalLogoSrc);
                    logoImg.style.width = '52px';
                    logoImg.style.marginLeft = '0';
                    logoImg.style.marginRight = '0';
                }
            } else {
                // If original wasn't dark nav, restore properly
                const isDarkMode = document.body.classList.contains('dark-mode');
                if (isDarkMode) {
                    navbar.classList.remove('navbar-light');
                    navbar.classList.add('navbar-dark');
                    navLinks.forEach(link => {
                        link.classList.remove('text-dark');
                        link.classList.add('text-white');
                    });
                } else {
                    navbar.classList.add('navbar-light');
                    navbar.classList.remove('navbar-dark');
                    navLinks.forEach(link => {
                        link.classList.add('text-dark');
                        link.classList.remove('text-white');
                    });
                }
            }
            
            const innerDiv = navbar.querySelector('div > div');
            if(innerDiv) innerDiv.style.borderBottom = '1px solid rgba(255, 255, 255, 0.25)';
        });
    }
});