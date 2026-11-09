FROM python:3.10-slim

WORKDIR /app

# Copia todo o projeto, mantendo a estrutura original
COPY . .

# Instala usando o caminho correto
RUN pip install --no-cache-dir -r backend/requirements.txt gunicorn

# Inicia o servidor chamando o módulo backend
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend:create_app()"]
