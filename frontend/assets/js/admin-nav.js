// Shared: inject Admin nav link if logged-in user is admin
(async () => {
  const token = localStorage.getItem('token');
  if (!token) return;
  try {
    const res = await fetch('http://127.0.0.1:8000/profile', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    if (data.is_admin === 'true') {
      const item = document.getElementById('adminNavItem');
      if (item) item.style.display = 'block';
    }
  } catch {}
})();
