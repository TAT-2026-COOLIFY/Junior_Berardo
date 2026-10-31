FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os ficheiros para dentro de uma subpasta 'backend'
COPY . ./backend

# Avisa o Flask qual é a pasta principal do sistema
ENV FLASK_APP=backend

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
