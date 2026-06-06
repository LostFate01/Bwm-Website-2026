document.addEventListener("DOMContentLoaded", function() {
    const kesfedinDropdown = document.getElementById('kesfedinDropdown');
    const navbar = document.querySelector('.custom-navbar');
    const navLinks = document.querySelectorAll('.custom-navbar .nav-link');
    const logoImg = document.querySelector('.navbar-brand img');
    
    // Original state
    let originalNavClass = navbar.className;
    let originalLogoSrc = logoImg ? logoImg.getAttribute('src') : '';
    let isDarkNav = navbar.classList.contains('navbar-dark');

    if (kesfedinDropdown && navbar) {
        kesfedinDropdown.addEventListener('show.bs.dropdown', function () {
            // When menu starts opening: instantly prepare the navbar
            navbar.style.setProperty('background-color', '#ffffff', 'important');
            navbar.classList.remove('navbar-dark');
            navbar.classList.add('navbar-light');
            
            navLinks.forEach(link => {
                link.classList.remove('text-white');
                link.classList.add('text-dark');
            });

            if (isDarkNav && logoImg) {
                let basePath = originalLogoSrc.substring(0, originalLogoSrc.lastIndexOf('/') + 1);
                if (!basePath) basePath = 'images/';
                logoImg.setAttribute('src', basePath + 'BMW Logo.png');
                
                // Keep the visual size identical
                logoImg.style.width = '52px';
            }
            
            // Remove border on inner div
            const innerDiv = navbar.querySelector('div > div');
            if(innerDiv) innerDiv.style.borderBottom = 'none';
        });

        // We completely ignore 'hide.bs.dropdown' so the navbar stays solid white
        // while the menu gracefully animates closed. 
        // This prevents the transparent background from revealing the video 
        // behind the fading menu, which causes the messy overlap look.

        kesfedinDropdown.addEventListener('hidden.bs.dropdown', function () {
            // ONLY after the menu is completely closed and invisible, 
            // we instantly snap the navbar back to its original transparent/dark state.
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
            }
            
            // Revert border
            const innerDiv = navbar.querySelector('div > div');
            if(innerDiv) innerDiv.style.borderBottom = '1px solid rgba(255, 255, 255, 0.25)';
        });
    }
});
