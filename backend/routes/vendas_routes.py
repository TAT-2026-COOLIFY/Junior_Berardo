from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.extensions import db
from backend.models import Venda, VendaItem, Produto, FichaTecnica, MovimentacaoEstoque, Cliente, Categoria

vendas_bp = Blueprint('vendas', __name__)

BAIXA_POR_RECHEIO = 1.0


@vendas_bp.route('/api/recheios', methods=['GET'])
def listar_recheios():
    try:
        recheios = (
            db.session.query(Produto)
            .join(Categoria, Produto.categoria_id == Categoria.idCategoria)
            .filter(
                Produto.tipo_item == 'ESTOQUE',
                db.func.lower(Categoria.nome).like('%recheio%')
            )
            .order_by(Produto.nome)
            .all()
        )
        return jsonify({
            'sucesso': True,
            'recheios': [
                {
                    'id': p.idProduto,
                    'nome': p.nome,
                    'quantidade': p.quantidade,
                    'categoria_id': p.categoria_id
                }
                for p in recheios
            ]
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': f'Erro ao listar recheios: {str(e)}'}), 500


@vendas_bp.route('/api/vendas', methods=['POST'])
def registrar_venda():
    dados = request.get_json() or {}
    if not dados or 'valor_total' not in dados or 'itens' not in dados:
        return jsonify({'erro': 'Dados incompletos'}), 400

    try:
        baixas_necessarias = {}

        # --- 1. MAPEAMENTO E VALIDAÇÃO PRÉVIA DE ESTOQUE ---
        for item in dados['itens']:
            prod_id = item['produto_id']
            qtd_vendida = float(item['quantidade'])
            produto = db.session.get(Produto, prod_id)

            if not produto:
                return jsonify({'erro': f'Produto ID {prod_id} não encontrado.'}), 404

            nome_lower = produto.nome.lower()
            id_prod = getattr(produto, 'idProduto', getattr(produto, 'id', None))


            categoria = db.session.get(Categoria, produto.categoria_id) if getattr(produto, 'categoria_id', None) else None
            is_recheio = categoria and 'recheio' in categoria.nome.lower()

            # REGRA: Picolés e Sorvetes não descontam do estoque
            if 'picolé' in nome_lower or 'picole' in nome_lower or 'sorvete' in nome_lower:
                continue

            if is_recheio:
                if produto.tipo_item == 'ESTOQUE':
                    baixas_necessarias[id_prod] = baixas_necessarias.get(id_prod, 0) + (qtd_vendida * BAIXA_POR_RECHEIO)
                continue

            # REGRA AÇAÍ E MILKSHAKE: Desconta APENAS embalagens
            if 'açaí' in nome_lower or 'acai' in nome_lower or 'milkshake' in nome_lower:
                tamanho = "300ml" if "300" in nome_lower else "500ml" if "500" in nome_lower else "700ml"

                # Desconta sempre o copo correspondente
                copo = Produto.query.filter(Produto.nome.ilike(f"%Copo {tamanho}%"), Produto.tipo_item == 'ESTOQUE').first()
                if copo:
                    id_copo = getattr(copo, 'idProduto', getattr(copo, 'id', None))
                    baixas_necessarias[id_copo] = baixas_necessarias.get(id_copo, 0) + qtd_vendida

                if 'açaí' in nome_lower or 'acai' in nome_lower:
                    colher = Produto.query.filter(Produto.nome.ilike("%Colher%Plástic%"), Produto.tipo_item == 'ESTOQUE').first()
                    if colher:
                        id_colher = getattr(colher, 'idProduto', getattr(colher, 'id', None))
                        baixas_necessarias[id_colher] = baixas_necessarias.get(id_colher, 0) + qtd_vendida
                else:
                    canudo = Produto.query.filter(Produto.nome.ilike("%Canudo%"), Produto.tipo_item == 'ESTOQUE').first()
                    if canudo:
                        id_canudo = getattr(canudo, 'idProduto', getattr(canudo, 'id', None))
                        baixas_necessarias[id_canudo] = baixas_necessarias.get(id_canudo, 0) + qtd_vendida
                continue


            baixas_necessarias[id_prod] = baixas_necessarias.get(id_prod, 0) + qtd_vendida


            componentes = FichaTecnica.query.filter_by(produto_id=prod_id).all()
            if componentes:
                for comp in componentes:
                    baixas_necessarias[comp.ingrediente_id] = baixas_necessarias.get(comp.ingrediente_id, 0) + (comp.quantidade * qtd_vendida)

        # Validação final
        for insumo_id, qtd_necessaria in baixas_necessarias.items():
            ingrediente = db.session.get(Produto, insumo_id)
            if not ingrediente or ingrediente.quantidade < qtd_necessaria:
                saldo = ingrediente.quantidade if ingrediente else 0
                nome = ingrediente.nome if ingrediente else f"Item ID {insumo_id}"
                return jsonify({
                    'erro': f'Estoque insuficiente de "{nome}". Disponível: {saldo}. Necessário: {qtd_necessaria}. Venda bloqueada.'}), 400

        # --- REGRA DE NEGÓCIO: 2 RECHEIOS GRÁTIS POR AÇAÍ, DEMAIS R$ 2,00
        qtd_copos_acai = 0
        itens_recheio = []

        for item in dados['itens']:
            produto = db.session.get(Produto, item['produto_id'])
            if not produto:
                continue

            nome_lower = produto.nome.lower()
            categoria = db.session.get(Categoria, produto.categoria_id) if getattr(produto, 'categoria_id', None) else None

            if 'açaí' in nome_lower or 'acai' in nome_lower:
                qtd_copos_acai += int(float(item['quantidade']))

            elif categoria and 'recheio' in categoria.nome.lower():
                itens_recheio.append(item)

        # Calcula a cota de recheios gratuitos
        recheios_gratis_disponiveis = qtd_copos_acai * 2

        # Se houver açaí e recheios no pedido, aplica a matemática
        if qtd_copos_acai > 0 and itens_recheio:
            for req_item in itens_recheio:
                qtd_pedida = int(float(req_item['quantidade']))
                subtotal_calculado = 0.0

                for _ in range(qtd_pedida):
                    if recheios_gratis_disponiveis > 0:
                        recheios_gratis_disponiveis -= 1
                    else:
                        subtotal_calculado += 2.00

                req_item['subtotal'] = float(subtotal_calculado)
                req_item['preco_unitario'] = float(subtotal_calculado / qtd_pedida if qtd_pedida > 0 else 0.0)

            dados['valor_total'] = sum(float(i['subtotal']) for i in dados['itens'])

        # --- 2. REGISTRO DA VENDA ---
        nova_venda = Venda(
            valor_total=float(dados['valor_total']),
            metodo_pagamento=dados.get('metodo_pagamento', 'Dinheiro'),
            cliente_id=dados.get('cliente_id'),
            data=datetime.now()
        )
        db.session.add(nova_venda)
        db.session.flush()

        for item in dados['itens']:
            prod_id = item['produto_id']
            qtd_vendida = float(item['quantidade'])
            novo_item = VendaItem(
                venda_id=nova_venda.id,
                produto_id=prod_id,
                quantidade=qtd_vendida,
                preco_unitario=float(item['preco_unitario']),
                subtotal=float(item['subtotal'])
            )
            db.session.add(novo_item)

        # --- 3. ATUALIZAÇÃO DO ESTOQUE ---
        for insumo_id, qtd_reduzir in baixas_necessarias.items():
            ingrediente = db.session.get(Produto, insumo_id)
            ingrediente.quantidade -= qtd_reduzir
            db.session.add(MovimentacaoEstoque(
                produto_id=insumo_id,
                venda_id=nova_venda.id,
                tipo='SAIDA',
                quantidade=qtd_reduzir,
                motivo="Venda Frente de Caixa"
            ))

        # --- 4. FIDELIDADE ---
        if dados.get('cliente_id'):
            cliente = db.session.get(Cliente, dados['cliente_id'])
            if cliente:
                cliente.compras_realizadas += 1

        db.session.commit()
        return jsonify({'mensagem': 'Venda realizada com sucesso!', 'venda_id': nova_venda.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


# REVERTER / EXCLUIR VENDA
@vendas_bp.route('/api/vendas/<int:id>', methods=['DELETE'])
def excluir_venda(id):
    try:
        venda = db.session.get(Venda, id)
        if not venda:
            return jsonify({'sucesso': False, 'erro': 'Venda não encontrada.'}), 404

        # 1. Devolve ao estoque exatamente o que esta venda baixou.
        movimentacoes = MovimentacaoEstoque.query.filter_by(venda_id=id, tipo='SAIDA').all()
        for mov in movimentacoes:
            produto = db.session.get(Produto, mov.produto_id)
            if produto:
                produto.quantidade += mov.quantidade
            db.session.delete(mov)

        # 2. Estorna o programa de fidelidade do cliente
        if venda.cliente_id:
            cliente = db.session.get(Cliente, venda.cliente_id)
            if cliente and cliente.compras_realizadas > 0:
                cliente.compras_realizadas -= 1

        db.session.delete(venda)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Venda desfeita e estoque devolvido com sucesso!'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': f'Erro ao reverter venda: {str(e)}'}), 500


# --- ROTAS PARA SALVAR PRODUTOS E CATEGORIAS DO FRONTEND ---
@vendas_bp.route('/api/produtos', methods=['POST'])
def criar_produto_api():
    dados = request.get_json()
    try:
        novo_p = Produto(
            nome=dados.get('nome'),
            quantidade=float(dados.get('quantidade', 0.0)),
            preco=float(dados.get('preco', 0.0)),
            categoria_id=int(dados.get('categoria_id', 1)),
            ingredientes=dados.get('ingredientes', ''),
            imagem=dados.get('imagem', '')
        )
        db.session.add(novo_p)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Produto salvo permanentemente!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@vendas_bp.route('/api/categorias', methods=['POST'])
def criar_categoria_api():
    dados = request.get_json()
    try:
        nova_cat = Categoria(nome=dados.get('nome'))
        db.session.add(nova_cat)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Categoria salva permanentemente!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500