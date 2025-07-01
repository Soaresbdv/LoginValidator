import pyotp
from datetime import datetime

# Banco de dados simples em memória
users = {}

def setup_auth():
    # Usuário de exemplo
    secret = pyotp.random_base32()
    users['teste'] = {
        'password': '123',  # Em produção, usar bcrypt
        '2fa_enabled': True,
        '2fa_secret': secret
    }

def verify_user(username, password):
    user = users.get(username)
    if user and user['password'] == password:  # Comparação insegura - só para exemplo
        return user
    return None

def generate_2fa_secret(username):
    secret = pyotp.random_base32()
    users[username]['2fa_secret'] = secret
    return secret

def verify_2fa(username, code):
    user = users.get(username)
    if not user or not user['2fa_secret']:
        return False
    totp = pyotp.TOTP(user['2fa_secret'])
    return totp.verify(code)