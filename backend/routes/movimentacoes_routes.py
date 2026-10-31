from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.extensions import db
from backend.models import Produto, MovimentacaoEstoque

estoque_movimentacoes_bp = Blueprint('estoque_movimentacoes_bp', __name__)


@estoque_movimentacoes_bp.route('/api/estoque/movimentacoes', methods=['POST'])
def registrar_movimentacao():
    dados = request.get_json() or {}

    produto_id = dados.get('produto_id')
    tipo = (dados.get('tipo') or '').strip().upper()
    quantidade = dados.get('quantidade')
    validade = dados.get('validade')
    motivo = (dados.get('motivo') or '').strip()
    observacao = (dados.get('observacao') or '').strip()

    if not produto_id:
        return jsonify({'sucesso': False, 'erro': 'O produto é obrigatório.'}), 400

    if tipo not in ['ENTRADA', 'SAIDA', 'QUEBRA']:
        return jsonify({'sucesso': False, 'erro': 'Tipo de movimentação inválido.'}), 400


    # REGRA DE NEGÓCIO: Exige Validade na Entrada

    if tipo == 'ENTRADA' and not validade:
        return jsonify({
            'sucesso': False,
            'erro': 'Ação Bloqueada: Para dar entrada no estoque, é obrigatório informar a Data de Validade do novo lote.'
        }), 400

    try:
        quantidade = float(quantidade)
        if quantidade <= 0:
            return jsonify({'sucesso': False, 'erro': 'A quantidade deve ser maior que zero.'}), 400
        produto_id = int(produto_id)
    except (TypeError, ValueError):
        return jsonify({'sucesso': False, 'erro': 'A quantidade ou o produto informado é inválido.'}), 400

    produto = db.session.get(Produto, produto_id)

    if not produto:
        return jsonify({'sucesso': False, 'erro': 'Produto não encontrado.'}), 404

    if tipo in ['SAIDA', 'QUEBRA'] and produto.quantidade < quantidade:
        return jsonify({'sucesso': False, 'erro': f'Estoque insuficiente. Estoque atual: {produto.quantidade:g}.'}), 400

    if tipo == 'QUEBRA' and not motivo:
        return jsonify({'sucesso': False, 'erro': 'Informe o motivo da quebra ou vencimento.'}), 400

    data_validade = None
    if validade:
        try:
            data_validade = datetime.strptime(validade, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'sucesso': False, 'erro': 'A data de validade é inválida.'}), 400

    try:
        if tipo == 'ENTRADA':
            produto.quantidade += quantidade

            produto.data_validade = data_validade
        else:
            produto.quantidade -= quantidade

        movimentacao = MovimentacaoEstoque(
            produto_id=produto.idProduto,
            tipo=tipo,
            quantidade=quantidade,
            validade=data_validade,
            motivo=motivo or None,
            observacao=observacao or None
        )

        db.session.add(movimentacao)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Movimentação registrada com sucesso.',
            'movimentacao': {
                'id': movimentacao.id,
                'produto_id': movimentacao.produto_id,
                'tipo': movimentacao.tipo,
                'quantidade': movimentacao.quantidade,
                'estoque_atual': produto.quantidade
            }
        }), 201

    except Exception as err:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(err)}), 500


@estoque_movimentacoes_bp.route('/api/estoque/movimentacoes', methods=['GET'])
def listar_movimentacoes():
    try:
        movimentacoes = db.session.query(MovimentacaoEstoque).order_by(MovimentacaoEstoque.data.desc()).all()
        produtos_map = {p.idProduto: p.nome for p in db.session.query(Produto.idProduto, Produto.nome).all()}

        resultado = [{
            'id': m.id,
            'produto_id': m.produto_id,
            'produto': produtos_map.get(m.produto_id, 'Produto removido'),
            'tipo': m.tipo,
            'quantidade': m.quantidade,
            'data': m.data.isoformat() if m.data else None,
            'validade': m.validade.isoformat() if m.validade else None,
            'motivo': m.motivo,
            'observacao': m.observacao
        } for m in movimentacoes]

        return jsonify({'sucesso': True, 'movimentacoes': resultado}), 200

    except Exception as err:
        return jsonify({'sucesso': False, 'erro': str(err)}), 500


@estoque_movimentacoes_bp.route('/api/estoque/giro', methods=['GET'])
def consultar_giro_estoque():
    try:
        data_inicio = datetime.now() - timedelta(days=30)
        totais = (
            db.session.query(
                MovimentacaoEstoque.produto_id,
                MovimentacaoEstoque.tipo,
                func.sum(MovimentacaoEstoque.quantidade).label('quantidade_total')
            )
            .filter(MovimentacaoEstoque.data >= data_inicio)
            .group_by(MovimentacaoEstoque.produto_id, MovimentacaoEstoque.tipo)
            .all()
        )

        totais_por_produto = {}
        for produto_id, tipo, quantidade_total in totais:
            if produto_id not in totais_por_produto:
                totais_por_produto[produto_id] = {'entradas_30_dias': 0, 'saidas_30_dias': 0, 'quebras_30_dias': 0}

            if tipo == 'ENTRADA':
                chave = 'entradas_30_dias'
            elif tipo == 'SAIDA':
                chave = 'saidas_30_dias'
            elif tipo == 'QUEBRA':
                chave = 'quebras_30_dias'
            else:
                continue

            totais_por_produto[produto_id][chave] = float(quantidade_total or 0)

        produtos = db.session.query(Produto).order_by(Produto.nome.asc()).all()
        giro = []

        for produto in produtos:
            totais_produto = totais_por_produto.get(
                produto.idProduto,
                {'entradas_30_dias': 0, 'saidas_30_dias': 0, 'quebras_30_dias': 0}
            )

            giro.append({
                'produto_id': produto.idProduto,
                'produto': produto.nome,
                'estoque_atual': produto.quantidade,
                'entradas_30_dias': totais_produto['entradas_30_dias'],
                'saidas_30_dias': totais_produto['saidas_30_dias'],
                'quebras_30_dias': totais_produto['quebras_30_dias']
            })

        return jsonify({'sucesso': True, 'periodo_dias': 30, 'giro': giro}), 200

    except Exception as err:
        return jsonify({'sucesso': False, 'erro': str(err)}), 500