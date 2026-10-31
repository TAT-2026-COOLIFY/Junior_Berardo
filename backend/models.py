from datetime import datetime
from backend.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Categoria(db.Model):
    __tablename__ = 'categoria'

    idCategoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column('NOME', db.String(100), nullable=False)
    tipo = db.Column('TIPO', db.String(20), default='VENDA')

    produtos = db.relationship('Produto', backref='cat', lazy=True)


class Produto(db.Model):
    __tablename__ = 'produto'

    idProduto = db.Column(db.Integer, primary_key=True)
    nome = db.Column('NOME', db.String(100), nullable=False)
    quantidade = db.Column('QUANTIDADE', db.Float, default=0.0)
    preco = db.Column('PRECO', db.Float, default=0.0)
    ingredientes = db.Column('INGREDIENTES', db.Text)
    imagem = db.Column('IMAGEM', db.String(500))
    tipo_item = db.Column('TIPO_ITEM', db.String(20), default='ESTOQUE')
    estoque_minimo = db.Column('ESTOQUE_MINIMO', db.Float, default=10.0)

    fornecedor_id = db.Column('FORNECEDOR_ID', db.Integer, db.ForeignKey('fornecedores.idFornecedores'), nullable=True)
    categoria_id = db.Column('Categoria_idCategoria', db.Integer, db.ForeignKey('categoria.idCategoria'),
                             nullable=False)
    data_validade = db.Column('data_validade', db.Date, nullable=True)


class Cliente(db.Model):
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(20), unique=True)
    telefone = db.Column(db.String(20))
    compras_realizadas = db.Column(db.Integer, default=0)
    premiacao = db.Column(db.String(200), default='Sem Premiação')

    vendas_historico = db.relationship('Venda', backref='cliente', lazy=True)


class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'

    idFornecedores = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column('NOME', db.String(150), nullable=False)
    cnpj = db.Column('CNPJ', db.String(18), unique=True)
    contato = db.Column('TELEFONE', db.String(100))
    email = db.Column('EMAIL', db.String(100))
    celular = db.Column('CELULAR', db.String(20))
    endereco = db.Column(db.String(200))


class Venda(db.Model):
    __tablename__ = 'venda'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.now)
    valor_total = db.Column(db.Float, nullable=False)
    metodo_pagamento = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)

    itens = db.relationship('VendaItem', backref='venda', lazy=True, cascade='all, delete-orphan')


class VendaItem(db.Model):
    __tablename__ = 'venda_item'

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.idProduto'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


class FichaTecnica(db.Model):
    __tablename__ = 'ficha_tecnica'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.idProduto'), nullable=False)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('produto.idProduto'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=1.0)


class MovimentacaoEstoque(db.Model):
    __tablename__ = 'movimentacao_estoque'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.idProduto'), nullable=False)
    venda_id = db.Column(db.Integer, nullable=True)
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now, nullable=False)
    validade = db.Column(db.Date, nullable=True)
    motivo = db.Column(db.String(255), nullable=True)
    observacao = db.Column(db.Text, nullable=True)