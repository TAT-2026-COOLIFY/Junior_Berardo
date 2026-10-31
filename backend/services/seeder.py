import re
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text

# Ajuste os imports abaixo caso a estrutura de pastas do seu projeto exija
from backend.extensions import db
from backend.models import (
    User,
    Categoria,
    Produto,
    FichaTecnica,
    VendaItem
)

CATEGORIAS_ESTOQUE = [
    'Insumos',
    'Essência',
    'Recheio',
    'Bebidas lata',
    'Bebidas garrafas',
    'Embalagens',
    'Utensílios'
]


# ESTOQUE AUTOMÁTICO

DADOS_ESTOQUE = {
    'Insumos': [
        'Pão', 'Hambúrguer', 'Queijo', 'Alface', 'Tomate', 'Molho Especial',
        'Batata', 'Salsicha', 'Maionese', 'Ketchup', 'Mostarda', 'Bacon'
    ],
    'Bebidas lata': ['Coca-Cola 200 ml'],
    'Embalagens': ['Copo 300ml', 'Copo 500ml', 'Copo 700ml', 'Copo plástico'],
    'Utensílios': ['Colher Plástica', 'Canudo']
}


# TEXTOS EXATOS CONFORME AS SUAS REGRAS DE NEGÓCIO

DADOS_CARDAPIO = {
    'Açaí': [
        {'nome': 'Açaí 300 ml', 'preco': 12.00, 'ingredientes': 'Açaí',
         'imagem': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=500'},
        {'nome': 'Açaí 500 ml', 'preco': 15.00, 'ingredientes': 'Açaí',
         'imagem': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=500'},
        {'nome': 'Açaí 700 ml', 'preco': 20.00, 'ingredientes': 'Açaí',
         'imagem': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=500'}
    ],

    'Combos': [
        {
            'nome': 'Combo 1',
            'preco': 22.90,
            'ingredientes': 'Top Burguer Premium, Pão, 1 Hambúrguer, Queijo, Alface, Tomate, Molho Especial, Batata, Coca-Cola 200 ml',
            'imagem': 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500'
        },
        {
            'nome': 'Combo 2',
            'preco': 20.90,
            'ingredientes': 'Top Burguer, Pão, 1 Hambúrguer, Queijo, Alface, Tomate, Molho Especial, Batata',
            'imagem': 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f6?w=500'
        },
        {
            'nome': 'Combo 3',
            'preco': 25.00,
            'ingredientes': 'Duplo Burguer Premium, Pão, 2 Hambúrgueres, Queijo, Alface, Tomate, Molho Especial, Batata, Coca-Cola 200 ml',
            'imagem': 'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=500'
        },
        {
            'nome': 'Combo 4',
            'preco': 23.90,
            'ingredientes': 'Duplo Burguer, Pão, 2 Hambúrgueres, Queijo, Alface, Tomate, Molho Especial, Batata',
            'imagem': 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500'
        }
    ],

    'Lanches': [
        {
            'nome': 'Premier Burguer 1',
            'preco': 15.90,
            'ingredientes': 'Pão, 1 Hambúrguer, Alface, Tomate, Molho Especial',
            'imagem': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500'
        },
        {
            'nome': 'Premier Burguer 2',
            'preco': 21.90,
            'ingredientes': 'Pão, 2 Hambúrgueres, Alface, Tomate, Molho Especial',
            'imagem': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500'
        },
        {
            'nome': 'Hot Dog',
            'preco': 15.90,
            'ingredientes': 'Pão, 2 Salsichas, Alface, Tomate, Maionese, Ketchup, Mostarda',
            'imagem': 'https://images.unsplash.com/photo-1627054239404-51e604f38753?w=500'
        },
        {
            'nome': 'Hot Dog com Bacon',
            'preco': 18.90,
            'ingredientes': 'Pão, 2 Salsichas, Bacon, Alface, Tomate, Maionese, Ketchup, Mostarda',
            'imagem': 'https://images.unsplash.com/photo-1627054239404-51e604f38753?w=500'
        }
    ],

    'Sorvete de Massa': [
        {'nome': 'Sorvete de Massa Leite (1 Bola)', 'preco': 5.00, 'ingredientes': 'Leite',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'},
        {'nome': 'Sorvete de Massa Leite (2 Bolas)', 'preco': 8.00, 'ingredientes': 'Leite',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'},
        {'nome': 'Sorvete de Massa Fruta (1 Bola)', 'preco': 4.00, 'ingredientes': 'Fruta',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'},
        {'nome': 'Sorvete de Massa Fruta (2 Bolas)', 'preco': 7.00, 'ingredientes': 'Fruta',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'}
    ],

    'Picolés': [
        {'nome': 'Picolé de Fruta', 'preco': 1.00, 'ingredientes': 'Picolé',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'},
        {'nome': 'Picolé de Leite', 'preco': 1.50, 'ingredientes': 'Picolé',
         'imagem': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=500'}
    ],

    'Milkshakes': [
        {'nome': 'Milkshake 300ml', 'preco': 10.00, 'ingredientes': 'Milkshake',
         'imagem': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500'},
        {'nome': 'Milkshake 500ml', 'preco': 15.00, 'ingredientes': 'Milkshake',
         'imagem': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500'}
    ]
}


def migrar_banco():

    inspector = inspect(db.engine)
    tabelas = inspector.get_table_names()

    if 'produto' in tabelas:
        colunas_produto = {coluna['name'] for coluna in inspector.get_columns('produto')}

        if 'ESTOQUE_MINIMO' not in colunas_produto:
            with db.engine.begin() as conexao:
                conexao.execute(text('ALTER TABLE produto ADD COLUMN ESTOQUE_MINIMO FLOAT'))

        if 'FORNECEDOR_ID' not in colunas_produto:
            with db.engine.begin() as conexao:
                conexao.execute(text('ALTER TABLE produto ADD COLUMN FORNECEDOR_ID INTEGER'))


        # NOVA COLUNA: DATA DE VALIDADE

        if 'data_validade' not in colunas_produto:
            with db.engine.begin() as conexao:
                conexao.execute(text('ALTER TABLE produto ADD COLUMN data_validade DATE'))

    if 'movimentacao_estoque' in tabelas:
        colunas_movimentacao = {coluna['name'] for coluna in inspector.get_columns('movimentacao_estoque')}
        if 'venda_id' not in colunas_movimentacao:
            with db.engine.begin() as conexao:
                conexao.execute(text('ALTER TABLE movimentacao_estoque ADD COLUMN venda_id INTEGER'))

    db.create_all()


def inicializar_banco():

    print('BANCO EM USO:', db.engine.url)
    migrar_banco()

    if not db.session.query(User).filter_by(email='admin@premiarte.com').first():
        db.session.add(User(email='admin@premiarte.com', password=generate_password_hash('1234')))
        db.session.commit()


    for c_nome in DADOS_CARDAPIO.keys():
        if not db.session.query(Categoria).filter_by(nome=c_nome, tipo='VENDA').first():
            db.session.add(Categoria(nome=c_nome, tipo='VENDA'))
    db.session.commit()


    for c_nome in CATEGORIAS_ESTOQUE:
        if not db.session.query(Categoria).filter_by(nome=c_nome, tipo='ESTOQUE').first():
            db.session.add(Categoria(nome=c_nome, tipo='ESTOQUE'))
    db.session.commit()


    print('GERANDO ESTOQUE FÍSICO MÍNIMO PARA O TCC NÃO TRAVAR...')
    for cat_nome, insumos in DADOS_ESTOQUE.items():
        cat = db.session.query(Categoria).filter_by(nome=cat_nome, tipo='ESTOQUE').first()
        if not cat: continue

        for nome_insumo in insumos:
            prod_db = db.session.query(Produto).filter_by(nome=nome_insumo, tipo_item='ESTOQUE').first()
            if not prod_db:
                cat_id = getattr(cat, 'idCategoria', getattr(cat, 'id', None))
                db.session.add(Produto(
                    nome=nome_insumo, preco=0.0, quantidade=100.0,
                    tipo_item='ESTOQUE', categoria_id=cat_id
                ))
    db.session.commit()

    # 5. SINCRONIZA O CARDÁPIO VIRTUAL
    produtos_atualizados = {p['nome']: (c_nome, p) for c_nome, produtos in DADOS_CARDAPIO.items() for p in produtos}
    produtos_existentes = db.session.query(Produto).filter_by(tipo_item='CARDAPIO').all()
    nomes_atualizados = set(produtos_atualizados.keys())

    # Remove o que não existe mais no dicionário DADOS_CARDAPIO
    for produto in produtos_existentes:
        if produto.nome not in nomes_atualizados:
            db.session.delete(produto)
    db.session.flush()

    for nome, (c_nome, dados) in produtos_atualizados.items():
        cat = db.session.query(Categoria).filter_by(nome=c_nome, tipo='VENDA').first()
        if not cat: continue

        produto = db.session.query(Produto).filter_by(nome=nome, tipo_item='CARDAPIO').first()
        cat_id = getattr(cat, 'idCategoria', getattr(cat, 'id', None))

        if produto:
            produto.preco = dados['preco']
            produto.ingredientes = dados.get('ingredientes', '')
            produto.imagem = dados.get('imagem', '')
            produto.categoria_id = cat_id
        else:
            db.session.add(Produto(
                nome=dados['nome'], preco=dados['preco'],
                ingredientes=dados.get('ingredientes', ''),
                imagem=dados.get('imagem', ''),
                quantidade=99.0, tipo_item='CARDAPIO', categoria_id=cat_id
            ))
    db.session.commit()

    # 6. GARANTE INGREDIENTES ESPECÍFICOS DOS AÇAÍS
    ingredientes_acai = {'Açaí 300 ml': 'Açaí', 'Açaí 500 ml': 'Açaí', 'Açaí 700 ml': 'Açaí'}
    for nome_acai, ingredientes in ingredientes_acai.items():
        acai = db.session.query(Produto).filter_by(nome=nome_acai, tipo_item='CARDAPIO').first()
        if acai: acai.ingredientes = ingredientes
    db.session.commit()


    db.session.query(FichaTecnica).delete()

    for nome, (c_nome, dados) in produtos_atualizados.items():
        if c_nome in ['Lanches', 'Combos']:
            produto_db = db.session.query(Produto).filter_by(nome=nome, tipo_item='CARDAPIO').first()
            if produto_db and dados.get('ingredientes'):
                prod_id = getattr(produto_db, 'idProduto', getattr(produto_db, 'id', None))

                # Exemplo: ele lê "2 Hambúrgueres", acha o número 2 e o nome "Hambúrgueres"
                partes = dados['ingredientes'].split(',')
                for parte in partes:
                    parte = parte.strip()
                    match = re.match(r'^(\d+)\s+(.*)', parte)

                    if match:
                        qtd = float(match.group(1))
                        nome_ing = match.group(2).strip()

                        if nome_ing.lower() == 'hambúrgueres':
                            nome_ing = 'Hambúrguer'
                        elif nome_ing.lower() == 'salsichas':
                            nome_ing = 'Salsicha'
                    else:
                        qtd = 1.0
                        nome_ing = parte


                    insumo_db = db.session.query(Produto).filter(
                        Produto.nome.ilike(f"%{nome_ing}%"),
                        Produto.tipo_item == 'ESTOQUE'
                    ).first()

                    if insumo_db:
                        ing_id = getattr(insumo_db, 'idProduto', getattr(insumo_db, 'id', None))
                        db.session.add(FichaTecnica(
                            produto_id=prod_id,
                            ingrediente_id=ing_id,
                            quantidade=qtd
                        ))
    db.session.commit()




# PERMITE RODAR O SEEDER DIRETO PELO TERMINAL

if __name__ == '__main__':
    # Importa a fábrica que cria a aplicação Flask
    from backend import create_app

    # Cria uma instância temporária da aplicação
    app = create_app()

    # Roda a inicialização dentro do contexto correto
    with app.app_context():
        inicializar_banco()