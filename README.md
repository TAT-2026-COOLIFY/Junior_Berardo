Markdown
# 🍦 Sistema de Gestão para Comércio Alimentício (TCC)

Trabalho de Conclusão de Curso (TCC) desenvolvido para a Gestão e Controle Operacional, estruturado com arquitetura moderna baseada em microsserviços conteinerizados.

## 🚀 Tecnologias Utilizadas

O projeto está dividido entre Front-end, Back-end e Banco de Dados:
* **Front-end:** Angular, TypeScript, HTML5, CSS3
* **Back-end:** Python, Flask, SQLAlchemy
* **Banco de Dados:** SQLite / PostgreSQL
* **Infraestrutura:** Docker e Docker Compose

---

## ⚙️ Como Executar o Projeto com Docker (Recomendado)

Certifique-se de ter o **Docker** e o **Docker Compose** instalados na sua máquina.

1. Clone o repositório:
bash
git clone https://github.com/JuniorBerardo/TCC.git
cd TCC

2. Suba os containers da aplicação:
bash
docker-compose up --build

3. Acesse a aplicação no seu navegador:
* **Front-end:** `http://localhost:4200`
* **Back-end API:** `http://localhost:5000`

---

## 📂 Estrutura do Projeto

* `backend/` - Código-fonte da API Flask e rotas do sistema.
* `frontend/` - Aplicação em Angular com as telas de gestão, estoque e vendas.
* `docker-compose.yml` - Orquestração dos serviços de container.
