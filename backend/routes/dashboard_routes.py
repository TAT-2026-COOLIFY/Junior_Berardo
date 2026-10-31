from flask import Blueprint, jsonify, request, send_file
from datetime import datetime, timedelta
from backend.models import Venda, Produto, Categoria
from backend.extensions import db
from backend.services.pdf_service import gerar_pdf_vendas
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)



# PAINEL GERAL E ALERTAS DE ESTOQUE


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def obter_dashboard():
    try:
        produtos_baixo_estoque = (
            db.session.query(Produto, Categoria)
            .join(Categoria, Produto.categoria_id == Categoria.idCategoria)
            .filter(
                Produto.tipo_item == 'ESTOQUE',
                Categoria.tipo == 'ESTOQUE',
                Produto.quantidade <= Produto.estoque_minimo
            )
            .order_by(Produto.quantidade.asc())
            .all()
        )

        itens_estoque_baixo = [
            {
                'id': produto.idProduto,
                'nome': produto.nome,
                'quantidade': produto.quantidade,
                'estoque_minimo': produto.estoque_minimo,
                'categoria': categoria.nome
            }
            for produto, categoria in produtos_baixo_estoque
        ]

        return jsonify({
            'sucesso': True,
            'resumo': {
                'itens_estoque_baixo': itens_estoque_baixo
            }
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao carregar o dashboard: {str(e)}'
        }), 500



# PAINEL FINANCEIRO - ÚLTIMAS 24 HORAS


@dashboard_bp.route('/api/dashboard/financeiro-24h', methods=['GET'])
def obter_painel_24h():
    try:
        limite_24h = datetime.now() - timedelta(hours=24)

        vendas = (
            Venda.query
            .filter(Venda.data >= limite_24h)
            .order_by(Venda.data.desc())
            .all()
        )

        resumo = db.session.query(
            func.sum(Venda.valor_total),
            func.count(Venda.id)
        ).filter(
            Venda.data >= limite_24h
        ).first()

        faturamento = resumo[0] if resumo and resumo[0] else 0.0
        total_vendas = resumo[1] if resumo and resumo[1] else 0

        return jsonify({
            'resumo': {
                'faturamento_ultimas_24h': faturamento,
                'total_vendas_ultimas_24h': total_vendas,
                'ticket_medio_24h': (
                    round(faturamento / total_vendas, 2)
                    if total_vendas > 0 else 0.0
                )
            },
            'vendas': [
                {
                    'id': v.id,
                    'data': v.data.strftime('%d/%m/%Y %H:%M'),
                    'valor_total': v.valor_total,
                    'metodo_pagamento': v.metodo_pagamento,
                    'cliente': v.cliente.nome if v.cliente else 'Consumidor'
                }
                for v in vendas
            ]
        }), 200

    except Exception as e:
        return jsonify({
            'erro': f'Erro no servidor: {str(e)}'
        }), 500


# EXPORTAÇÃO DE RELATÓRIOS EM PDF


@dashboard_bp.route('/api/relatorios/vendas/pdf', methods=['GET'])
@dashboard_bp.route('/relatorios/vendas/pdf', methods=['GET'])
def exportar_relatorio_pdf():
    try:
        periodo = request.args.get('periodo', 'geral').lower()
        agora = datetime.now()

        if 'semana' in periodo:
            data_limite = agora - timedelta(days=7)
            titulo = 'Relatório Financeiro Semanal (Últimos 7 dias)'
            query_vendas = Venda.query.filter(Venda.data >= data_limite)

        elif 'mes' in periodo or 'mês' in periodo:
            data_limite = agora - timedelta(days=30)
            titulo = 'Relatório Financeiro Mensal (Últimos 30 dias)'
            query_vendas = Venda.query.filter(Venda.data >= data_limite)

        else:
            titulo = 'Relatório Financeiro Geral Consolidado'
            query_vendas = Venda.query

        vendas_filtradas = query_vendas.order_by(Venda.data.desc()).all()
        pdf_stream = gerar_pdf_vendas(vendas_filtradas, titulo)

        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'relatorio_vendas_{periodo}.pdf'
        )

    except Exception as e:
        return jsonify({
            'erro': f'Falha ao emitir documento em PDF: {str(e)}'
        }), 500