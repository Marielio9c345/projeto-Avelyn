# audio_utils.py

import asyncio
import os
import base64
from edge_tts import Communicate
import streamlit as st

async def _gerar_audio_async(texto, voice="pt-BR-FranciscaNeural"):
    communicate = Communicate(text=texto or "Olá!", voice=voice)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)

def gerar_audio(texto, nome_arquivo="fala_avelyn.mp3"):
    os.makedirs("audiotemp", exist_ok=True)
    caminho = os.path.join("audiotemp", nome_arquivo)
    audio = asyncio.run(_gerar_audio_async(texto))
    with open(caminho, "wb") as f:
        f.write(audio)
    return caminho

def exibir_mini_player_audio(caminho_audio):
    with open(caminho_audio, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )
