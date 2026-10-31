
import os
import secrets


# DIRETÓRIO PRINCIPAL E CAMINHOS DO ECOSSISTEMA

BASE_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)

DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')


# CONFIGURAÇÃO DE INFRAESTRUTURA DO FLASK ORM

class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY'
    ) or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# DISTRIBUIÇÃO DA CAMADA DE APRESENTAÇÃO (ANGULAR SPA)

DIST_FOLDER = os.path.join(
    BASE_DIR,
    'frontend',
    'dist',
    'frontend',
    'browser'
)

