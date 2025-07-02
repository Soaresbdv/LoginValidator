from datetime import datetime
from flask import request
from jwt_utils import verify_token
import pyotp
import bcrypt
import smtplib
from email.message import EmailMessage
import secrets
import sqlite3
from datetime import datetime, timedelta

# Banco de dados simples em memória
users = {}

# Modifique setup_auth()
def setup_auth():
    secret = pyotp.random_base32()
    hashed_pw = bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt())
    users['teste'] = {
        'id': 1,
        'username': 'teste',
        'password': hashed_pw.decode('utf-8'),
        '2fa_enabled': True,
        '2fa_secret': secret
    }

# Atualize verify_user()
def verify_user(username, password):
    user = users.get(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
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

def update_user_2fa(user_id, secret, enabled):
    for username, user in users.items():
        if user.get('id') == user_id:
            user['2fa_secret'] = secret
            user['2fa_enabled'] = enabled
            return True
    return False

def get_authenticated_user(req):
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
        
    token = auth_header.split(' ')[1]
    username = verify_token(token)
    return users.get(username)

def send_verification_email(email, verification_code):
    msg = EmailMessage()
    msg['Subject'] = 'Seu Código de Verificação'
    msg['From'] = 'seu_email@gmail.com'
    msg['To'] = email
    msg.set_content(f'''
        Seu código de verificação é: {verification_code}
        Este código expira em 10 minutos.
    ''')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('seu_email@gmail.com', 'sua_senha_app')  # Use App Password
        smtp.send_message(msg)

def generate_verification_code():
    """Gera um código numérico de 6 dígitos"""
    import random
    return str(random.randint(100000, 999999))

def store_2fa_code(user_id, code):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    # Cria tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS twofa_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Insere o código (expira em 10 minutos)
    expires_at = datetime.now() + timedelta(minutes=10)
    cursor.execute(
        'INSERT INTO twofa_codes (user_id, code, expires_at) VALUES (?, ?, ?)',
        (user_id, code, expires_at)
    )
    conn.commit()
    conn.close()

# Função para verificar códigos 2FA
def verify_2fa_code(email, code):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    # Busca o código não expirado
    cursor.execute('''
        SELECT u.id FROM users u
        JOIN twofa_codes t ON u.id = t.user_id
        WHERE u.email = ? AND t.code = ? AND t.expires_at > ?
    ''', (email, code, datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Função para obter usuário por email
def get_user_by_email(email):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'username': user[2],
            'twofa_enabled': bool(user[5])
        }
    return None

def user_exists(email):
    """Verifica se um email já está cadastrado"""
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE email = ?', (email,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def create_user(email, password, verification_code):
    """Cria um novo usuário no banco de dados"""
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (email, username, password_hash, verified)
            VALUES (?, ?, ?, ?)
        ''', (email, email.split('@')[0], hashed_pw.decode('utf-8'), False))
        
        user_id = cursor.lastrowid
        store_2fa_code(user_id, verification_code)
        conn.commit()
    finally:
        conn.close()

def verify_user_code(email, code):
    """Verifica se o código de verificação é válido"""
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id FROM users u
        JOIN twofa_codes t ON u.id = t.user_id
        WHERE u.email = ? AND t.code = ? AND t.expires_at > ?
    ''', (email, code, datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Marca o usuário como verificado
        conn = sqlite3.connect('auth.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET verified = 1 WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        return True
    
    return False

def send_verification_email(email, code):
    """Envia email com código de verificação"""
    msg = EmailMessage()
    msg['Subject'] = 'Seu Código de Verificação'
    msg['From'] = 'seu_email@exemplo.com'  # Substitua pelo seu email
    msg['To'] = email
    
    msg.set_content(f'''
        Seu código de verificação é: {code}
        Use este código para completar seu cadastro.
        O código expira em 10 minutos.
    ''')
    
    # Configuração do servidor SMTP (exemplo para Gmail)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('seu_email@exemplo.com', 'sua_senha')  # Use App Password
        smtp.send_message(msg)