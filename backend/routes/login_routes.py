from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db
from backend.models import User

from flask import Blueprint

login_bp = Blueprint('login_bp', __name__)



@login_bp.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json() or {}
    email = dados.get('email')
    senha = dados.get('senha', '')

    user = db.session.query(User).filter_by(email=email).first()

    if user and check_password_hash(user.password, senha):
        return jsonify({'sucesso': True, 'mensagem': 'Login com sucesso!'}), 200

    return jsonify({'sucesso': False, 'erro': 'E-mail ou senha incorretos.'}), 401


@login_bp.route('/api/redefinir-senha', methods=['POST'])
def api_redefinir_senha():
    dados = request.get_json() or {}
    email = (dados.get('email') or '').strip().lower()
    nova_senha = (dados.get('nova_senha') or '').strip()

    # Unifica validações de presença e tamanho mínimo da credencial
    if not email or not nova_senha:
        return jsonify({'sucesso': False, 'erro': 'E-mail e nova senha são obrigatórios.'}), 400

    if len(nova_senha) < 4:
        return jsonify({'sucesso': False, 'erro': 'A nova senha deve ter no mínimo 4 caracteres.'}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({'sucesso': False, 'erro': 'Nenhum usuário cadastrado com este e-mail.'}), 404

    try:
        user.password = generate_password_hash(nova_senha)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Senha redefinida com sucesso! Você já pode entrar.'}), 200
    except Exception as err:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(err)}), 500
