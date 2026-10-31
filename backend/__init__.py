from flask import Flask
from flask_cors import CORS
from backend.config import Config, DIST_FOLDER
from backend.extensions import db
from backend.services.seeder import inicializar_banco


from backend.routes.login_routes import login_bp
from backend.routes.produtos_routes import produtos_bp
from backend.routes.vendas_routes import vendas_bp
from backend.routes.clientes_routes import clientes_bp
from backend.routes.fornecedores_routes import fornecedores_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.movimentacoes_routes import estoque_movimentacoes_bp
from backend.routes.estoque_routes import estoque_bp


def create_app():
    # Cria o servidor Flask acoplado à pasta de distribuição estática do Angular
    app = Flask(__name__, static_folder=DIST_FOLDER, static_url_path='')
    app.config.from_object(Config)

    # Configuração de segurança e comunicação cross-origin (CORS)
    CORS(app)

    # Inicialização do mapeador objeto-relacional SQLAlchemy
    db.init_app(app)

    # Registro de todas as rotas da API REST
    app.register_blueprint(estoque_bp)
    app.register_blueprint(estoque_movimentacoes_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(vendas_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(fornecedores_bp)
    app.register_blueprint(dashboard_bp)

    # Inicialização do banco de dados
    with app.app_context():
        inicializar_banco()

    return app