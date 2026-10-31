from flask import Blueprint, request, jsonify, flash, redirect, url_for
from backend.extensions import db
from backend.models import Cliente
import re

clientes_bp = Blueprint('clientes_bp', __name__)


def aplicar_mascara_cpf(cpf_bruto):

    if not cpf_bruto:
        return ""

    numeros = re.sub(r'\D', '', str(cpf_bruto))

    if len(numeros) >= 11:
        numeros = numeros[:11]
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"

    return cpf_bruto


def aplicar_mascara_telefone(tel_bruto):

    if not tel_bruto:
        return ""

    numeros = re.sub(r'\D', '', str(tel_bruto))

    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

    return tel_bruto



# LISTAR CLIENTES

@clientes_bp.route('/api/clientes', methods=['GET'])
def api_get_clientes():
    try:
        clientes = db.session.query(Cliente).all()

        resultado = [
            {
                'id': c.id,
                'nome': c.nome,
                'cpf': aplicar_mascara_cpf(c.cpf),
                'telefone': aplicar_mascara_telefone(c.telefone),
                'premiacao': c.premiacao,
                'compras_realizadas': c.compras_realizadas or 0
            }
            for c in clientes
        ]

        return jsonify({
            'sucesso': True,
            'clientes': resultado
        }), 200

    except Exception as err:
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500



# CADASTRAR CLIENTE

@clientes_bp.route('/api/clientes', methods=['POST'])
@clientes_bp.route('/clientes/cadastrar', methods=['POST'])
def api_create_cliente():
    is_api = request.path.startswith('/api/')
    dados = request.get_json() if request.is_json else request.form

    nome = (dados.get('nome') or '').strip().title()
    cpf = (dados.get('cpf') or '').strip()
    telefone = (dados.get('telefone') or '').strip()
    premiacao = dados.get('premiacao', 'Sem Premiação')

    if not nome or not cpf or not telefone:
        if is_api:
            return jsonify({'sucesso': False, 'erro': 'Nome, CPF e Telefone/Celular são obrigatórios.'}), 400
        flash('Nome, CPF e Telefone são obrigatórios.')
        return redirect(url_for('clientes'))

    cpf_numeros = re.sub(r'\D', '', cpf)
    telefone_numeros = re.sub(r'\D', '', telefone)

    if len(cpf_numeros) > 11: cpf_numeros = cpf_numeros[:11]
    if len(telefone_numeros) > 11: telefone_numeros = telefone_numeros[:11]

    if len(cpf_numeros) < 11:
        msg = 'O CPF deve conter os 11 números.'
        if is_api: return jsonify({'sucesso': False, 'erro': msg}), 400
        flash(msg)
        return redirect(url_for('clientes'))

    if len(telefone_numeros) < 10:
        msg = 'O número de celular digitado está incompleto.'
        if is_api: return jsonify({'sucesso': False, 'erro': msg}), 400
        flash(msg)
        return redirect(url_for('clientes'))

    cpf_formatado = f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"

    try:
        novo_c = Cliente(
            nome=nome,
            cpf=cpf_formatado,
            telefone=telefone_numeros,
            premiacao=premiacao,
            compras_realizadas=0
        )

        db.session.add(novo_c)
        db.session.commit()

        if is_api:
            return jsonify({'sucesso': True, 'mensagem': 'Cliente cadastrado com sucesso!'}), 201
        flash('Cliente cadastrado com sucesso!')
        return redirect(url_for('clientes'))

    except Exception as err:
        db.session.rollback()
        msg_erro = f'Erro ao salvar cliente: {str(err)}'
        if is_api:
            return jsonify({'sucesso': False, 'erro': msg_erro}), 500
        flash(msg_erro)
        return redirect(url_for('clientes'))



# ATUALIZAR CLIENTE

@clientes_bp.route('/api/clientes/<int:id>', methods=['PUT', 'POST'])
def api_update_cliente(id):
    is_api = request.path.startswith('/api/')
    cliente = db.session.get(Cliente, id)

    if not cliente:
        if is_api: return jsonify({'sucesso': False, 'erro': 'Cliente não encontrado.'}), 404
        return redirect(url_for('clientes'))

    dados = request.get_json() if request.is_json else request.form

    nome = (dados.get('nome') or '').strip().title()
    telefone = (dados.get('telefone') or '').strip()

    if not nome or not telefone:
        if is_api: return jsonify({'sucesso': False, 'erro': 'Nome e Telefone são obrigatórios para atualização.'}), 400
        return redirect(url_for('clientes'))

    telefone_numeros = re.sub(r'\D', '', telefone)
    if len(telefone_numeros) > 11: telefone_numeros = telefone_numeros[:11]

    try:
        cliente.nome = nome
        cliente.telefone = telefone_numeros
        db.session.commit()

        if is_api: return jsonify({'sucesso': True, 'mensagem': 'Cliente atualizado com sucesso!'}), 200
        return redirect(url_for('clientes'))

    except Exception as err:
        db.session.rollback()
        if is_api: return jsonify({'sucesso': False, 'erro': str(err)}), 500
        return redirect(url_for('clientes'))



# ATUALIZAR PREMIAÇÃO

@clientes_bp.route('/api/clientes/<int:id>/premiacao', methods=['PUT'])
def api_atualizar_premiacao(id):
    cliente = db.session.get(Cliente, id)
    if not cliente:
        return jsonify({'sucesso': False, 'erro': 'Cliente não encontrado.'}), 404

    try:
        dados = request.get_json() if request.is_json else request.form
        premiacao = (dados.get('premiacao') or '').strip()

        if not premiacao:
            return jsonify({'sucesso': False, 'erro': 'A premiação deve ser informada.'}), 400

        cliente.premiacao = premiacao
        db.session.commit()
        return jsonify(
            {'sucesso': True, 'mensagem': 'Premiação salva com sucesso!', 'premiacao': cliente.premiacao}), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao salvar premiação: {str(err)}'}), 500



# RESGATAR PREMIAÇÃO

@clientes_bp.route('/api/clientes/<int:id>/resgatar-premiacao', methods=['POST'])
def api_resgatar_premiacao(id):
    cliente = db.session.get(Cliente, id)
    if not cliente:
        return jsonify({'sucesso': False, 'erro': 'Cliente não encontrado.'}), 404

    try:
        cliente.premiacao = 'Sem Premiação'
        cliente.compras_realizadas = 0
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Premiação resgatada com sucesso!'}), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao processar resgate: {str(err)}'}), 500



# EXCLUIR CLIENTE

@clientes_bp.route('/api/clientes/<int:id>', methods=['DELETE'])
@clientes_bp.route('/clientes/deletar/<int:id>', methods=['GET', 'POST', 'DELETE'])
def api_excluir_cliente(id):
    is_api = request.path.startswith('/api/')
    cliente = db.session.get(Cliente, id)

    if not cliente:
        if is_api:
            return jsonify({'sucesso': False, 'erro': 'Cliente não encontrado.'}), 404
        flash('Cliente não encontrado.')
        return redirect(url_for('clientes'))

    try:
        # Tratamento seguro para desvincular o cliente de vendas antigas
        if hasattr(cliente, 'vendas_historico'):
            for venda in cliente.vendas_historico:
                venda.cliente_id = None
        elif hasattr(cliente, 'vendas'):
            for venda in cliente.vendas:
                venda.cliente_id = None

        # Exclusão definitiva do cliente
        db.session.delete(cliente)
        db.session.commit()

        if is_api:
            return jsonify({'sucesso': True, 'mensagem': 'Cliente excluído com sucesso!'}), 200
        flash('Cliente excluído com sucesso!')
        return redirect(url_for('clientes'))

    except Exception as err:
        db.session.rollback()

        msg_erro = f"O banco de dados bloqueou a exclusão. Detalhe: {str(err)}"

        if is_api:
            return jsonify({'sucesso': False, 'erro': msg_erro}), 500
        flash(msg_erro)
        return redirect(url_for('clientes'))