# imagem base
FROM python:3.12-slim

# variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# criar diretório de trabalho
WORKDIR /app

# instalar dependências do sistema necessárias para psycopg2 e outros
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar arquivos e instalar dependências Python
# O requirements.txt deve estar na raiz do projeto (contexto)
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copiar o código do projeto 
COPY . /app/

# expor porta
EXPOSE 8000