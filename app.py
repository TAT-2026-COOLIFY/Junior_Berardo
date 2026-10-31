import os
import logging
from flask import send_from_directory, jsonify
from backend import create_app
from backend.config import DIST_FOLDER

app = create_app()


logging.getLogger('werkzeug').setLevel(logging.ERROR)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_angular(path):
    if path.startswith('api/'):
        return jsonify({
            'sucesso': False,
            'erro': 'Endpoint da API não encontrado'
        }), 404

    arquivo_solicitado = os.path.join(DIST_FOLDER, path)

    if path != "" and os.path.exists(arquivo_solicitado):
        return send_from_directory(DIST_FOLDER, path)

    index_path = os.path.join(DIST_FOLDER, 'index.html')

    if os.path.exists(index_path):
        return send_from_directory(DIST_FOLDER, 'index.html')

    return (
        f"<h3>Erro: index.html não encontrado em {DIST_FOLDER}. "
        f"Execute 'ng build' dentro da pasta frontend!</h3>",
        404
    )


if __name__ == '__main__':
    # use_reloader=False impede que o Flask duplique as mensagens de log no terminal ao iniciar
    app.run(debug=True, use_reloader=False)
