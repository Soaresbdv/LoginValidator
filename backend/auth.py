from datetime import datetime
from flask import request
from jwt_utils import verify_token
import pyotp
import bcrypt

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

def get_authenticated_user(req):
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
        
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    # Consulte seu banco de dados ou dicionário users
    for username, user in users.items():
        if username == user_id:  # Adapte conforme sua lógica
            return user
    return None

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