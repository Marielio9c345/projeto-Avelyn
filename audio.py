# Imports principais
import streamlit as st
import base64
import tempfile
import edge_tts
import asyncio
import os

# 🔊 Geração de áudio com voz da Avelyn
async def _gerar_audio_async(texto, voice="pt-BR-FranciscaNeural"):
    communicate = edge_tts.Communicate(text=texto or "Olá!", voice=voice)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)

def gerar_audio_edge(texto, nome_arquivo="fala_avelyn.mp3"):
    os.makedirs("audiotemp", exist_ok=True)
    caminho = os.path.join("audiotemp", nome_arquivo)
    audio = asyncio.run(_gerar_audio_async(texto))
    with open(caminho, "wb") as f:
        f.write(audio)
    return caminho

def exibir_mini_player_audio(caminho_audio):
    with open(caminho_audio, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    audio_html = f"""
    <audio controls style="width: 150px; height: 30px; margin-top: 5px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
