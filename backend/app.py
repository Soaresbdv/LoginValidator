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
    update_user_2fa,
    send_verification_email,
    store_2fa_code,
    get_user_by_email,
    user_exists,
    generate_verification_code,
    create_user,
    verify_user_code
)

app = Flask(__name__)
CORS(app)

# Configuração básica
app.config['SECRET_KEY'] = '993969'

# Rota raiz para teste
@app.route('/')
def home():
    return "Servidor Flask funcionando! Acesse /login via POST"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Dados inválidos'}), 400

    if user_exists(data['email']):
        return jsonify({'error': 'Email já registrado'}), 400

    verification_code = generate_verification_code()
    create_user(
        email=data['email'],
        password=data['password'],
        verification_code=verification_code
    )
    
    send_verification_email(data['email'], verification_code)
    return jsonify({'success': True})


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

@app.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    if verify_user_code(data['email'], data['code']):
        return jsonify({'success': True})
    return jsonify({'error': 'Código inválido'}), 400

@app.route('/send-2fa-email', methods=['POST'])
def send_2fa_email():
    data = request.get_json()
    user = get_user_by_email(data['email'])
    
    if user and user['twofa_enabled']:
        code = generate_verification_code()
        store_2fa_code(user['id'], code)
        send_verification_email(user['email'], code)
        return jsonify({'success': True})
    
    return jsonify({'error': 'Falha ao enviar código'}), 400

if __name__ == '__main__':
    setup_auth()
    app.run(debug=True, port=5000)