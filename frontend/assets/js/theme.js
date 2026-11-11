const root = document.documentElement;

function getStoredTheme() {
  return localStorage.getItem('theme') || 'light';
}

function applyTheme(theme) {
  root.className = theme + '-theme';
  localStorage.setItem('theme', theme);
  const toggle = document.getElementById('themeToggle');
  if (toggle) {
    const isDark = theme === 'dark';
    if (typeof t === 'function') {
      toggle.textContent = isDark ? t('theme_toggle_light') : t('theme_toggle_dark');
    } else {
      toggle.textContent = isDark ? '☀️ Light' : '🌙 Dark';
    }
  }
}

function toggleTheme() {
  const newTheme = root.className.includes('dark') ? 'light' : 'dark';
  applyTheme(newTheme);
}

function setLanguage(lang) {
  localStorage.setItem('language', lang);
}

function getStoredLanguage() {
  return localStorage.getItem('language') || 'en';
}

// Theme is applied here; translation is handled by translations.js
window.addEventListener('DOMContentLoaded', () => {
  applyTheme(getStoredTheme());
});
