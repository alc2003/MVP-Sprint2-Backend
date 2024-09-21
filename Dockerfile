# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale o virtualenv
RUN python -m venv /opt/venv

# Ative o virtualenv e instale as dependências
RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copie o conteúdo do projeto para o diretório de trabalho do container
COPY . .

# Defina o ambiente virtual no PATH
ENV PATH="/opt/venv/bin:$PATH"

# Defina a variável de ambiente para o Flask
ENV FLASK_APP=app.py

# Exponha a porta em que o Flask vai rodar
EXPOSE 5000

# Comando para rodar o Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
