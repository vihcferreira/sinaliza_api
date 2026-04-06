FROM python:3.11

# Instala as dependências de sistema para o OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Cria o diretório de trabalho
WORKDIR /code

# Copia os arquivos necessários
COPY requirements.txt .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código (A API e o modelo)
COPY . .

# A porta obrigatória do Hugging Face Spaces é a 7860
EXPOSE 7860

# Comando para iniciar o servidor
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
