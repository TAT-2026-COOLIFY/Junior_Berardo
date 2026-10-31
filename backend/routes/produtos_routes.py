from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import (
    Categoria,
    Produto,
    VendaItem,
    FichaTecnica,
    MovimentacaoEstoque
)

produtos_bp = Blueprint('produtos_bp', __name__)



# GESTÃO DE CATEGORIAS


@produtos_bp.route('/api/categorias', methods=['GET'])
def api_get_categorias():
    tipo = request.args.get('tipo', '').upper()
    query = db.session.query(Categoria)

    if tipo in ['VENDA', 'ESTOQUE']:
        query = query.filter_by(tipo=tipo)

    cats = query.all()

    return jsonify({
        'sucesso': True,
        'categorias': [
            {
                'id': c.idCategoria,
                'nome': c.nome,
                'tipo': c.tipo
            }
            for c in cats
        ]
    }), 200


@produtos_bp.route('/api/categorias', methods=['POST'])
def api_create_categoria():
    dados = request.get_json() or {}
    nome = dados.get('nome', '').strip()
    tipo = dados.get('tipo', 'ESTOQUE').upper()

    if not nome:
        return jsonify({
            'sucesso': False,
            'erro': 'O nome da categoria é obrigatório.'
        }), 400

    if tipo not in ['VENDA', 'ESTOQUE']:
        return jsonify({
            'sucesso': False,
            'erro': 'O tipo da categoria deve ser VENDA ou ESTOQUE.'
        }), 400

    try:
        nova_cat = Categoria(nome=nome, tipo=tipo)
        db.session.add(nova_cat)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Categoria adicionada com sucesso!',
            'id': nova_cat.idCategoria
        }), 201

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao salvar no banco de dados: {str(err)}'
        }), 500


@produtos_bp.route('/api/categorias/<int:id>', methods=['DELETE'])
def api_delete_categoria(id):
    categoria = db.session.get(Categoria, id)

    if not categoria:
        return jsonify({
            'sucesso': False,
            'erro': 'Categoria não encontrada.'
        }), 404

    try:
        produtos = Produto.query.filter_by(
            categoria_id=categoria.idCategoria
        ).all()

        produtos_com_vinculos = []

        for produto in produtos:
            possui_vendas = VendaItem.query.filter_by(
                produto_id=produto.idProduto
            ).first() is not None

            possui_ficha_como_produto = FichaTecnica.query.filter_by(
                produto_id=produto.idProduto
            ).first() is not None

            possui_ficha_como_ingrediente = FichaTecnica.query.filter_by(
                ingrediente_id=produto.idProduto
            ).first() is not None

            possui_movimentacoes = MovimentacaoEstoque.query.filter_by(
                produto_id=produto.idProduto
            ).first() is not None

            if (
                possui_vendas
                or possui_ficha_como_produto
                or possui_ficha_como_ingrediente
                or possui_movimentacoes
            ):
                produtos_com_vinculos.append(produto.nome)

        if produtos_com_vinculos:
            return jsonify({
                'sucesso': False,
                'erro': (
                    'Não foi possível excluir a categoria porque existem '
                    'produtos vinculados ao histórico de vendas, às fichas '
                    'técnicas ou às movimentações de estoque.'
                ),
                'produtos_vinculados': produtos_com_vinculos
            }), 409

        for produto in produtos:
            db.session.delete(produto)

        db.session.delete(categoria)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': (
                f'Categoria "{categoria.nome}" e seus produtos '
                'foram excluídos com sucesso.'
            )
        }), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao excluir categoria: {str(err)}'
        }), 500


# CARDÁPIO E PRODUTOS


@produtos_bp.route('/api/cardapio', methods=['GET'])
def api_get_cardapio():
    produtos = db.session.query(Produto).filter_by(
        tipo_item='CARDAPIO'
    ).all()

    return jsonify({
        'sucesso': True,
        'produtos': [
            {
                'id': p.idProduto,
                'nome': p.nome,
                'preco': p.preco,
                'ingredientes': p.ingredientes,
                'imagem': p.imagem,
                'categoria_id': p.categoria_id,
                'categoria': p.cat.nome if p.cat else ''
            }
            for p in produtos
        ]
    }), 200


@produtos_bp.route('/api/cardapio', methods=['POST'])
def api_create_cardapio():
    dados = request.get_json() or {}
    nome = ' '.join(
        p.capitalize()
        for p in (dados.get('nome') or '').split()
    ).strip()

    if not nome:
        return jsonify({
            'sucesso': False,
            'erro': 'Nome do produto é obrigatório.'
        }), 400

    try:
        novo_p = Produto(
            nome=nome,
            preco=float(dados.get('preco', 0.0)),
            ingredientes=dados.get('ingredientes', ''),
            imagem=dados.get('imagem', ''),
            tipo_item='CARDAPIO',
            quantidade=99.0,
            categoria_id=int(dados.get('categoria_id', 1))
        )

        db.session.add(novo_p)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Produto adicionado com sucesso!',
            'id': novo_p.idProduto
        }), 201

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500



# ATUALIZAÇÃO E REMOÇÃO DE PRODUTOS


@produtos_bp.route('/api/cardapio/<int:id>/preco', methods=['PUT'])
def api_alterar_preco_cardapio(id):
    produto = db.session.get(Produto, id)

    if not produto or produto.tipo_item != 'CARDAPIO':
        return jsonify({
            'sucesso': False,
            'erro': 'Produto não encontrado no cardápio.'
        }), 404

    dados = request.get_json() or {}

    try:
        preco = float(dados.get('preco'))

        if preco < 0:
            return jsonify({
                'sucesso': False,
                'erro': 'O preço não pode ser negativo.'
            }), 400

        produto.preco = preco
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Preço atualizado!',
            'produto': {
                'id': produto.idProduto,
                'nome': produto.nome,
                'preco': produto.preco
            }
        }), 200

    except (TypeError, ValueError):
        return jsonify({
            'sucesso': False,
            'erro': 'O preço informado é inválido.'
        }), 400

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500


@produtos_bp.route('/api/cardapio/<int:id>/ingredientes', methods=['PUT'])
def api_alterar_ingredientes_cardapio(id):
    produto = db.session.get(Produto, id)

    if not produto or produto.tipo_item != 'CARDAPIO':
        return jsonify({
            'sucesso': False,
            'erro': 'Produto não encontrado no cardápio.'
        }), 404

    dados = request.get_json() or {}
    ingredientes = dados.get('ingredientes', '')

    if not isinstance(ingredientes, str):
        return jsonify({
            'sucesso': False,
            'erro': 'A descrição deve ser um texto válido.'
        }), 400

    try:
        produto.ingredientes = ingredientes.strip()
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Descrição atualizada!',
            'produto': {
                'id': produto.idProduto,
                'nome': produto.nome,
                'ingredientes': produto.ingredientes
            }
        }), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500


@produtos_bp.route('/api/cardapio/<int:id>', methods=['DELETE'])
def api_delete_cardapio(id):
    p = db.session.get(Produto, id)

    if not p or p.tipo_item != 'CARDAPIO':
        return jsonify({
            'sucesso': False,
            'erro': 'Produto não encontrado no cardápio.'
        }), 404

    try:
        db.session.delete(p)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Produto retirado de venda com sucesso!'
        }), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500



# AUDITORIA E INTEGRIDADE DE ESTOQUE


@produtos_bp.route(
    '/api/estoque/verificar-categorias-removidas',
    methods=['GET']
)
def verificar_categorias_removidas():
    nomes_categorias = ['Essência', 'Bebidas']

    try:
        categorias = db.session.query(Categoria).filter(
            db.func.lower(Categoria.nome).in_(
                [n.lower() for n in nomes_categorias]
            ),
            Categoria.tipo == 'ESTOQUE'
        ).all()

        resultado = []

        for cat in categorias:
            produtos = db.session.query(Produto).filter_by(
                categoria_id=cat.idCategoria,
                tipo_item='ESTOQUE'
            ).all()

            for prod in produtos:
                qtd_vendas = db.session.query(VendaItem).filter_by(
                    produto_id=prod.idProduto
                ).count()

                em_ficha = db.session.query(FichaTecnica).filter(
                    db.or_(
                        FichaTecnica.produto_id == prod.idProduto,
                        FichaTecnica.ingrediente_id == prod.idProduto
                    )
                ).count()

                resultado.append({
                    'id': prod.idProduto,
                    'nome': prod.nome,
                    'categoria': cat.nome,
                    'vendas_vinculadas': qtd_vendas,
                    'fichas_tecnicas_vinculadas': em_ficha,
                    'seguro_deletar': (
                        qtd_vendas == 0 and em_ficha == 0
                    )
                })

        return jsonify({
            'sucesso': True,
            'produtos_analisados': resultado
        }), 200

    except Exception as err:
        return jsonify({
            'sucesso': False,
            'erro': str(err)
        }), 500
