from flask import Flask, jsonify, request
from flask_cors import CORS
from auth import get_authenticated_user
import pyotp
from jwt_utils import generate_token
from auth import (
    users,
    setup_auth,
    verify_user,
    verify_2fa,
    get_authenticated_user,
    update_user_2fa
)

app = Flask(__name__)
CORS(app)

# Configuração básica
app.config['SECRET_KEY'] = '993969'

# Rota raiz para teste
@app.route('/')
def home():
    return "Servidor Flask funcionando! Acesse /login via POST"

# Rotas
@app.route('/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
        
    user = verify_user(data.get('username'), data.get('password'))
    
    if user:
        if user['2fa_enabled']:
            return jsonify({'success': True, 'requires_2fa': True})
        token = generate_token(user['username'])
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        })
    return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401

@app.route('/verify-2fa', methods=['POST'])  # Note o hífen e o método POST
def verify_2fa_route():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
        
    if verify_2fa(data.get('username'), data.get('code')):
        user = users.get(data.get('username'))
        token = generate_token(user['username'])
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        })
    return jsonify({'success': False, 'error': 'Código 2FA inválido'}), 401

@app.route('/get-2fa-secret/<username>', methods=['GET'])
def get_2fa_secret(username):
    user = users.get(username)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
        
    # Se o usuário não tiver um secret, gera um novo
    if not user.get('2fa_secret'):
        user['2fa_secret'] = pyotp.random_base32()
    
    # Gera URL para QR Code
    otpauth_url = pyotp.totp.TOTP(user['2fa_secret']).provisioning_uri(
        name=username,
        issuer_name="Taskify App"
    )
    
    return jsonify({
        'secret': user['2fa_secret'],
        'otpauth_url': otpauth_url
    })

@app.route('/enable-2fa', methods=['POST'])
def enable_2fa():
    user = get_authenticated_user(request)
    if not user:
        return jsonify({'error': 'Não autorizado'}), 401
        
    secret = pyotp.random_base32()
    update_user_2fa(user['id'], secret, True)
    
    otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user['username'],
        issuer_name="Taskify App"
    )
    
    return jsonify({
        'success': True,
        'secret': secret,
        'otpauth_url': otpauth_url
    })

if __name__ == '__main__':
    setup_auth()  # Configura usuários iniciais
    app.run(debug=True, port=5000)