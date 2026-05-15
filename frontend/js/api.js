const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : '/api';

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearSession();
    window.location.href = '/login.html';
    return;
  }

  if (res.status === 204) return null;

  const data = await res.json();
  if (!res.ok) {
    const msg = data?.error?.message || '오류가 발생했습니다';
    const err = new Error(msg);
    err.code = data?.error?.code;
    err.status = res.status;
    throw err;
  }
  return data;
}
