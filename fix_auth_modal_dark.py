import os

css_path = r"c:\Users\berkc\OneDrive\Desktop\All my Projects\Bwm-Website-2026\frontend\assets\css\style.css"
dark_modal_css = """
/* Auth Modal Dark Mode */
body.dark-mode .auth-modal-content {
    background: rgba(30, 30, 30, 0.95) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}
body.dark-mode .auth-modal-header .btn-close {
    filter: invert(1) opacity(0.8);
}
body.dark-mode .auth-modal-header .btn-close:hover {
    filter: invert(1) opacity(1);
}
body.dark-mode .auth-title {
    color: #e0e0e0 !important;
}
body.dark-mode .auth-input {
    background: #2a2a2a !important;
    border-color: #444 !important;
    color: #e0e0e0 !important;
}
body.dark-mode .auth-input:focus {
    background: #333 !important;
    border-color: #1c69d4 !important;
}
body.dark-mode .auth-input::placeholder {
    color: #888 !important;
}
body.dark-mode .auth-divider {
    color: #bbb !important;
}
body.dark-mode .auth-divider::before,
body.dark-mode .auth-divider::after {
    border-color: #444 !important;
}
body.dark-mode .auth-btn-google {
    background: #2a2a2a !important;
    color: #e0e0e0 !important;
    border-color: #444 !important;
}
body.dark-mode .auth-btn-google:hover {
    background: #333 !important;
    border-color: #555 !important;
}
body.dark-mode .auth-switch {
    color: #bbb !important;
}
"""

with open(css_path, "a", encoding="utf-8") as f:
    f.write(dark_modal_css)

print("Auth Modal dark mode fixes applied successfully.")
