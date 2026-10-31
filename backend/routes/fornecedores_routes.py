from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import Fornecedor
from backend.services.validadores import validar_cnpj

fornecedores_bp = Blueprint('fornecedores_bp', __name__)


@fornecedores_bp.route('/api/fornecedores', methods=['GET'])
def api_get_fornecedores():
    fornecedores = db.session.query(Fornecedor).all()

    resultado = [{
        'idFornecedores': f.idFornecedores,
        'nome_empresa': f.nome_empresa,
        'cnpj': f.cnpj,
        'contato': f.contato,
        'email': f.email,
        'celular': f.celular,
        'endereco': f.endereco
    } for f in fornecedores]

    return jsonify({
        'sucesso': True,
        'fornecedores': resultado
    }), 200


@fornecedores_bp.route('/api/fornecedores', methods=['POST'])
def api_create_fornecedor():
    dados = request.get_json() or {}

    cnpj_informado = (dados.get('cnpj') or '').strip()
    razao_social = (dados.get('nome_empresa') or '').strip()

    if not razao_social or not cnpj_informado:
        return jsonify({
            'sucesso': False,
            'erro': 'Razão Social e CNPJ são obrigatórios.'
        }), 400

    if not validar_cnpj(cnpj_informado):
        return jsonify({
            'sucesso': False,
            'erro': 'O CNPJ informado é inválido pelo cálculo da Receita Federal.'
        }), 400

    if db.session.query(Fornecedor).filter_by(cnpj=cnpj_informado).first():
        return jsonify({
            'sucesso': False,
            'erro': 'Este CNPJ já está cadastrado para outro fornecedor.'
        }), 400

    try:
        novo_f = Fornecedor(
            nome_empresa=razao_social,
            cnpj=cnpj_informado,
            contato=dados.get('contato', ''),
            email=dados.get('email', ''),
            celular=dados.get('celular', ''),
            endereco=dados.get('endereco', '')
        )

        db.session.add(novo_f)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Fornecedor cadastrado com sucesso!'
        }), 201

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500


@fornecedores_bp.route('/api/fornecedores/<int:id>', methods=['PUT'])
def api_update_fornecedor(id):
    fornecedor = db.session.get(Fornecedor, id)

    if not fornecedor:
        return jsonify({
            'sucesso': False,
            'erro': 'Fornecedor não encontrado.'
        }), 404

    dados = request.get_json() or {}

    cnpj_informado = (dados.get('cnpj') or '').strip()
    razao_social = (dados.get('nome_empresa') or '').strip()

    if not razao_social or not cnpj_informado:
        return jsonify({
            'sucesso': False,
            'erro': 'Razão Social e CNPJ são obrigatórios.'
        }), 400

    if not validar_cnpj(cnpj_informado):
        return jsonify({
            'sucesso': False,
            'erro': 'O CNPJ informado é inválido pelo cálculo da Receita Federal.'
        }), 400

    fornecedor_existente = db.session.query(Fornecedor).filter(
        Fornecedor.cnpj == cnpj_informado,
        Fornecedor.idFornecedores != id
    ).first()

    if fornecedor_existente:
        return jsonify({
            'sucesso': False,
            'erro': 'Este CNPJ já está cadastrado para outro fornecedor.'
        }), 400

    try:
        fornecedor.nome_empresa = razao_social
        fornecedor.cnpj = cnpj_informado
        fornecedor.contato = dados.get('contato', '')
        fornecedor.email = dados.get('email', '')
        fornecedor.celular = dados.get('celular', '')
        fornecedor.endereco = dados.get('endereco', '')

        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Fornecedor updated com sucesso!'
        }), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500


@fornecedores_bp.route('/api/fornecedores/<int:id>', methods=['DELETE'])
def api_delete_fornecedor(id):
    f = db.session.get(Fornecedor, id)

    if not f:
        return jsonify({
            'sucesso': False,
            'erro': 'Fornecedor não encontrado.'
        }), 404

    try:
        db.session.delete(f)
        db.session.commit()
        return jsonify({
            'sucesso': True,
            'mensagem': 'Fornecedor excluído com sucesso!'
        }), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500
