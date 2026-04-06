# subir servidor no terminal: uvicorn api:app --host 0.0.0.0 --port 8000

import cv2
import pickle
import numpy as np
import mediapipe as mp
from fastapi import FastAPI, UploadFile, File

# Inicializando Servidor API
app = FastAPI(title="Sinaliza API", description="API para tradução de Linguagem de Sinais")

# 1. Carregando o modelo treinado e mediapipe
try:
    with open('modelo.pkl', 'rb') as f:
        modelo_libras = pickle.load(f)
    print("Modelo de IA carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar modelo: {e}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

# 2. Reutilização da função de normalização do arquivo 1_extract_features.py
def normalize_landmarks(hand_landmarks):
    pulso_x = hand_landmarks.landmark[0].x
    pulso_y = hand_landmarks.landmark[0].y
    pontos_relativos = []

    for lm in hand_landmarks.landmark:
        pontos_relativos.append(lm.x - pulso_x)
        pontos_relativos.append(lm.y - pulso_y)

    valor_maximo = max(list(map(abs, pontos_relativos)))

    if valor_maximo > 0:
        return [ponto / valor_maximo for ponto in pontos_relativos]
    return pontos_relativos

# 3. Endpoint principal da API
@app.post("/traduzir")
async def predict_sign(file: UploadFile = File(...)):
    # Lê os dados (bytes) da imagem recebida do Flutter pela internet
    conteudo = await file.read()

    # Transforma os dados crus numa imagem que o OpenCV compreende
    nparr = np.frombuffer(conteudo, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_cv is None:
        return {"letra": "?"} # Volta nulo se o arquivo vier corrompido

    # Converter para a MediaPipe (RGB)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

    # Buscando a mão
    resultados = hands.process(img_rgb)

    if resultados.multi_hand_landmarks:
        mao = resultados.multi_hand_landmarks[0]
        pontos = normalize_landmarks(mao)

        previsao = modelo_libras.predict([pontos])
        letra_encontrada = str(previsao[0])

        return {"letra": letra_encontrada}

    return {"letra": "?"}

