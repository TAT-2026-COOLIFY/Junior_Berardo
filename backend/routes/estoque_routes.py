from flask import Blueprint, request, jsonify
from sqlalchemy import func, or_  # func: forçar minúsculas | or_: filtro "ou" na exclusão de insumo
from backend.extensions import db
from backend.models import (
    Produto,
    Categoria,
    VendaItem,
    FichaTecnica,
    MovimentacaoEstoque
)
from datetime import datetime

estoque_bp = Blueprint('estoque_bp', __name__)


@estoque_bp.route('/api/estoque', methods=['GET', 'POST'])
def api_gerenciar_estoque():

    # 1. CADASTRO DE PRODUTO NO ESTOQUE (POST)

    if request.method == 'POST':
        dados_recebidos = request.get_json() or {}


        nome = (dados_recebidos.get('nome') or '').strip()

        preco_venda = float(dados_recebidos.get('preco_venda', 0.0) or dados_recebidos.get('preco', 0.0))
        estoque_minimo = float(dados_recebidos.get('estoque_minimo', 10.0))
        quantidade_inicial = float(dados_recebidos.get('quantidade', 0.0) or dados_recebidos.get('qtd_inicial', 0.0))
        categoria_id = int(dados_recebidos.get('categoria_id', 1))

        fornecedor_id = dados_recebidos.get('fornecedor_id')
        data_validade_str = dados_recebidos.get('data_validade')

        if not nome:
            return jsonify({'sucesso': False, 'erro': 'O nome do produto é obrigatório.'}), 400


        # TRAVAS DE SEGURANÇA

        if not fornecedor_id:
            return jsonify(
                {'sucesso': False, 'erro': 'Ação Bloqueada: É obrigatório vincular o produto a um Fornecedor.'}), 400


        produto_existente = db.session.query(Produto).filter(
            func.lower(Produto.nome) == func.lower(nome),
            Produto.tipo_item == 'ESTOQUE'
        ).first()

        if produto_existente:
            return jsonify({
                'sucesso': False,
                'erro': f'Ação Bloqueada: Já existe um insumo com o nome "{produto_existente.nome}" cadastrado no estoque!'
            }), 400

        try:

            data_validade_parsed = datetime.strptime(data_validade_str,
                                                     '%Y-%m-%d').date() if data_validade_str else None

            novo_produto = Produto(
                nome=nome,
                preco=preco_venda,
                quantidade=quantidade_inicial,
                tipo_item='ESTOQUE',
                estoque_minimo=estoque_minimo,
                categoria_id=categoria_id,
                fornecedor_id=fornecedor_id,
                data_validade=data_validade_parsed
            )

            db.session.add(novo_produto)
            db.session.commit()

            return jsonify({
                'sucesso': True,
                'mensagem': 'Produto cadastrado no estoque com sucesso!'
            }), 201

        except Exception as erro:
            db.session.rollback()
            return jsonify({'sucesso': False, 'erro': f'Erro ao salvar no banco: {str(erro)}'}), 500


    # 2. LISTAGEM DE PRODUTOS AGRUPADA POR CATEGORIA (GET)

    if request.method == 'GET':
        try:
            categorias_estoque = db.session.query(Categoria).filter_by(tipo='ESTOQUE').all()
            lista_final_agrupada = []

            for cat in categorias_estoque:
                id_cat = cat.idCategoria
                produtos_da_categoria = db.session.query(Produto).filter_by(categoria_id=id_cat,
                                                                            tipo_item='ESTOQUE').all()
                card_produtos = []

                for item in produtos_da_categoria:
                    card_produtos.append({
                        'id': item.idProduto,
                        'nome': item.nome,
                        'preco': item.preco,
                        'estoque_minimo': item.estoque_minimo,
                        'quantidade': item.quantidade,
                        'categoria_id': id_cat
                    })

                lista_final_agrupada.append({
                    'id': id_cat,
                    'categoria': cat.nome,
                    'produtos': card_produtos
                })

            return jsonify(lista_final_agrupada), 200

        except Exception as erro:
            return jsonify({'sucesso': False, 'erro': f'Erro ao buscar produtos do estoque: {str(erro)}'}), 500



# 3. EXCLUSÃO DE INSUMO

@estoque_bp.route('/api/estoque/<int:id>', methods=['DELETE'])
def api_excluir_produto_estoque(id):
    produto = db.session.get(Produto, id)

    if not produto or produto.tipo_item != 'ESTOQUE':
        return jsonify({'sucesso': False, 'erro': 'Insumo não encontrado no estoque.'}), 404

    try:
        qtd_vendas = VendaItem.query.filter_by(produto_id=produto.idProduto).count()

        qtd_fichas = FichaTecnica.query.filter(
            or_(
                FichaTecnica.produto_id == produto.idProduto,
                FichaTecnica.ingrediente_id == produto.idProduto
            )
        ).count()

        movimentacoes = MovimentacaoEstoque.query.filter_by(produto_id=produto.idProduto).all()

        # --- Bloqueios reais, com o motivo explicado ---
        if qtd_vendas > 0:
            return jsonify({
                'sucesso': False,
                'erro': (
                    f'Não foi possível excluir "{produto.nome}": ele aparece em '
                    f'{qtd_vendas} item(ns) de venda. Reverta essas vendas no '
                    'Painel Financeiro e tente novamente.'
                )
            }), 409

        if qtd_fichas > 0:
            return jsonify({
                'sucesso': False,
                'erro': (
                    f'Não foi possível excluir "{produto.nome}": ele faz parte de '
                    f'{qtd_fichas} ficha(s) técnica(s). Remova-o das fichas '
                    'antes de excluir.'
                )
            }), 409

        # --- Sem vendas e sem fichas: limpa o histórico de movimentações e exclui ---
        nome_produto = produto.nome
        qtd_movs = len(movimentacoes)

        for mov in movimentacoes:
            db.session.delete(mov)

        db.session.delete(produto)
        db.session.commit()

        complemento = (
            f' ({qtd_movs} movimentação(ões) de estoque removida(s) junto).'
            if qtd_movs else '.'
        )

        return jsonify({
            'sucesso': True,
            'mensagem': f'Insumo "{nome_produto}" excluído com sucesso{complemento}'
        }), 200

    except Exception as erro:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao excluir insumo: {str(erro)}'}), 500