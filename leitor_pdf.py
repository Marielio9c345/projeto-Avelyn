# leitor_pdf.py

import streamlit as st
import fitz  # PyMuPDF
import base64
import os
import asyncio
import edge_tts
import re

# ==========
# Funções auxiliares
# ==========
def limpar_formatacoes(texto):
    texto = re.sub(r"[*_`~]", "", texto)  # Remove *, _, `, ~
    texto = re.sub(r"\s{2,}", " ", texto)  # Remove espaços duplicados
    return texto.strip()

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
    st.markdown(f"""
        <audio controls style="width:150px; height:30px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# ==========
# Função principal do leitor
# ==========
def ler_pdf():
    st.title("📖 Leitor de PDF com Narração da Avelyn")
    uploaded_file = st.file_uploader("Envie um arquivo PDF", type="pdf")

    if uploaded_file:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            total_paginas = len(doc)
            st.success(f"PDF carregado com sucesso! Total de páginas: {total_paginas}")

            if "pagina_atual" not in st.session_state:
                st.session_state["pagina_atual"] = 1

            with st.container():
                col_a, col_b = st.columns([9, 1])
                with col_b:
                    st.session_state["pagina_atual"] = st.number_input(
                        "Pág", min_value=1, max_value=total_paginas,
                        value=st.session_state["pagina_atual"], label_visibility="collapsed"
                    )

            texto = doc[st.session_state["pagina_atual"] - 1].get_text()
            texto_limpo = limpar_formatacoes(texto)

            st.subheader("📘 Conteúdo da Página Selecionada")
            st.text_area("Texto da Página", value=texto_limpo, height=300, label_visibility="collapsed")

            st.session_state["conteudo_pdf"] = texto_limpo

            if st.button("🔊 Narrar esta página"):
                caminho_audio = gerar_audio_edge(texto_limpo, nome_arquivo=f"pagina_{st.session_state['pagina_atual']}.mp3")
                exibir_mini_player_audio(caminho_audio)