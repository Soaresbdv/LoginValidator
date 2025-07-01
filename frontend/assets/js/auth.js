export const authApi = {
  async login(username, password) {
    const response = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return await response.json();
  },

  async verify2fa(username, code) {
    const response = await fetch('http://localhost:5000/verify-2fa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, code })
    });
    return await response.json();
  }
}