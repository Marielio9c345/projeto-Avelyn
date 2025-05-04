# -*- PROJETO AVELYN -*-
"""
Avelyn IA é um assistente pessoal desenvolvido em Streamlit, com foco em interação via texto e voz.
A plataforma possui design dark, suporte a transcrição de áudio, geração de fala com edge-tts,
histórico de conversas e integração com modelos de linguagem via Together AI.
Criada para oferecer uma experiência fluida, visualmente impactante e funcional para quem busca
produtividade, análise e interações com IA em tempo real.

Este script Python utiliza a biblioteca Streamlit para criar uma interface web simples
que permite ao usuário inserir um texto e, em seguida, gerar um arquivo de áudio
desse texto utilizando a voz da Avelyn (padrão FranciscaNeural da Microsoft Edge TTS).
O áudio gerado é então exibido em um mini player de áudio na própria interface Streamlit.

Autor: Mariélio Fernandes
Data de Criação: 01 de Maio de 2025
Versão: 1.0
"""
import streamlit as st
import base64
import os
import asyncio
import edge_tts
from PIL import Image
from datetime import datetime
from db import criar_chat, salvar_mensagem, listar_chats, carregar_chat, deletar_chat, renomear_chat  # Importe renomear_chat
from ia import chamar_together
from voz import capturar_audio_e_transcrever
import numpy as np
import fitz
import pandas as pd
import requests
import re
import time  # Para medir o tempo de execução
from limpeza import limpar_formatacao


def limpar_formatacoes(texto):
    texto = re.sub(r"[*_`~]", "", texto)  # Remove *, _, `, ~
    texto = re.sub(r"\s{2,}", " ", texto)  # Remove espaços duplos
    return texto.strip()

# ===================================================
# Avelyn IA — Interface principal do assistente virtual
# ===================================================

# ======================================
# CONFIGURAÇÃO INICIAL E TEMA PERSONALIZADO
# ======================================
start_time = time.time()
st.set_page_config(
    page_title="Avelyn IA",
    page_icon="imagens/favicon_web.png",
    layout="wide"
)
end_time = time.time()
print(f"Tempo para set_page_config: {end_time - start_time:.4f} segundos")

start_time = time.time()
st.markdown("""
<style>
/* Cores de fundo e texto principais - TEMA DARK */
body {
    background-color: #1e1e1e; /* Cinza bem escuro */
    color: #d4d4d4; /* Cinza claro para o texto */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Estilo da barra lateral - TEMA DARK */
.sidebar .sidebar-content {
    background-color: #252525;
    color: #d4d4d4;
}
.sidebar h2 {
    color: #00c698; /* Verde azulado para destaque */
}
.sidebar button {
    background-color: transparent !important;
    color: #c5c5c5 !important;
    border: 1px solid #555 !important;
    border-radius: 5px !important;
    margin-bottom: 5px;
    padding: 8px 12px !important;
    font-size: 16px !important;
    font-weight: normal;
    display: block;
    width: 100%;
    text-align: left;
}
.sidebar button:hover {
    background-color: #3c3c3c !important;
    color: #00c698 !important;
}

/* Estilo das mensagens - TEMA DARK - REMOVENDO NEGRITO E ITALICO VISUALMENTE */
.user-message {
    background-color: #333333; /* Cinza escuro para o usuário */
    color: #d4d4d4;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    max-width: 70%;
    margin-left: auto;
    font-size: 16px;
    box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.3s ease-in-out;
}
.assistant-message {
    background-color: #444444; /* Cinza um pouco mais claro para o assistente */
    color: #d4d4d4;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    max-width: 70%;
    margin-right: auto;
    font-size: 16px;
    box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(5px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Estilo do chat input - TEMA DARK */
.stChatInputContainer {
    background-color: #252525;
    border-top: 1px solid #444;
    padding: 10px;
    border-radius: 8px;
    margin-top: 20px;
    box-shadow: 0 -1px 5px rgba(0, 0, 0, 0.1);
}
.stChatInputTextArea {
    background-color: #333;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 10px;
    font-size: 16px;
}
.stChatInputButton {
    background-color: #00c698 !important; /* Verde azulado para destaque */
    color: #222 !important; /* Texto escuro no botão */
    border: none !important;
    border-radius: 5px !important;
    padding: 10px 15px !important;
    font-size: 16px !important;
    font-weight: bold;
    cursor: pointer;
}
.stChatInputButton:hover {
    background-color: #00a37d !important; /* Tom mais escuro no hover */
}

/* Estilo do botão flutuante do microfone - TEMA DARK */
.mic-float {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #00c698;
    color: #222;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 24px;
    text-align: center;
    line-height: 45px;
    z-index: 9999;
    transition: 0.3s ease-in-out;
    cursor: pointer;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
}
.mic-float:hover {
    background-color: #00a37d;
}

/* Estilo do mini player de áudio - TEMA DARK */
audio {
    background-color: #333;
    color: #d4d4d4;
    border-radius: 5px;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)
end_time = time.time()
print(f"Tempo para markdown do tema: {end_time - start_time:.4f} segundos")

# =============================
# INICIALIZAÇÃO DO ESTADO
# =============================
start_time = time.time()
for key in ['chat_id', 'messages', 'memory', 'uploaded_file', 'gravar', 'conteudo_pdf', 'pagina', 'modo_resposta', 'debug_mode', 'grafico_gerado']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['messages', 'memory'] else None
end_time = time.time()
print(f"Tempo para inicialização do session_state: {end_time - start_time:.4f} segundos")

# =============================
# FUNÇÕES DE ÁUDIO COM EDGE TTS
# =============================

# Função assíncrona para gerar áudio com edge-tts
async def _gerar_audio_async(texto, voice="pt-BR-FranciscaNeural"):
    communicate = edge_tts.Communicate(text=texto or "Olá!", voice=voice)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)

# Geração de arquivo de áudio .mp3
def gerar_audio_edge(texto, nome_arquivo="fala_avelyn.mp3"):
    os.makedirs("audiotemp", exist_ok=True)
    caminho = os.path.join("audiotemp", nome_arquivo)
    audio = asyncio.run(_gerar_audio_async(texto))
    with open(caminho, "wb") as f:
        f.write(audio)
    return caminho

# Exibe o mini player com o áudio gerado
def exibir_mini_player_audio(caminho_audio):
    with open(caminho_audio, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""<audio controls style='width: 150px; height: 30px;'>
        <source src='data:audio/mp3;base64,{audio_base64}' type='audio/mpeg'>
    </audio>""", unsafe_allow_html=True)

# =====================
# RENDERIZAÇÃO DO CHAT
# =====================
def renderizar_chat():
    start_time = time.time()
    for idx, msg in enumerate(st.session_state['messages'][-50:]):
        if msg['role'] == 'user':
            st.markdown(f"<div class='user-message'>🧑‍💻 <b>Você:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-message'>🤖 <b>Avelyn:</b><br>{msg['content'].replace('*', '').replace('_', '')}</div>", unsafe_allow_html=True)
            # Otimização: Gera áudio apenas para a última mensagem do assistente
            if idx == len(st.session_state['messages'][-50:]) - 1 and msg['role'] == 'assistant':
                texto_limpo = limpar_formatacoes(msg['content'])
                caminho_audio = gerar_audio_edge(texto_limpo, nome_arquivo="fala_avelyn_last.mp3")
                if caminho_audio:
                    exibir_mini_player_audio(caminho_audio)
    end_time = time.time()
    print(f"Tempo para renderizar o chat: {end_time - start_time:.4f} segundos")

# =====================
# SISTEMA DE MENU
# =====================
with st.sidebar:
    start_time_sidebar = time.time()  # Inicializa start_time_sidebar aqui
    start_time_logo = time.time()
    st.image(Image.open("imagens/logo.png"), width=200)
    end_time_logo = time.time()
    print(f"Tempo para carregar logo: {end_time_logo - start_time_logo:.4f} segundos")

    st.markdown("---")
    st.markdown("### 💬 Nova Conversa")
    if st.button("➕ Iniciar Novo Chat", help="Cria um novo chat e limpa o histórico atual"):
        for key in ['chat_id', 'messages', 'memory', 'uploaded_file', 'conteudo_pdf', 'pagina', 'grafico_gerado']:
            st.session_state[key] = [] if key in ['messages', 'memory'] else None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📜 Histórico")

    start_time_db_list = time.time()
    chats = listar_chats()
    end_time_db_list = time.time()
    print(f"Tempo para listar chats do DB: {end_time_db_list - start_time_db_list:.4f} segundos")
    chats_dict = {titulo: chat_id for chat_id, titulo in chats}

    if not chats:
        st.info("Nenhuma conversa salva.")
    else:
        # Estilo para organização dos controles
        st.markdown("""
        <style>
        .chat-box {
            background-color: #1f1f1f;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .chat-buttons {
            display: flex;
            justify-content: space-between;
            gap: 6px;
            margin-top: 8px;
        }
        .rename-row {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 6px;
        }
        .stTextInput > div > input {
            background-color: #2a2a2a;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            termo_busca = st.text_input("🔍 Buscar conversa:", "", key="busca_chat").lower()
            chats_filtrados = {titulo: cid for titulo, cid in chats_dict.items() if termo_busca in titulo.lower()}

            if not chats_filtrados:
                st.warning("Nenhum resultado encontrado.")
            else:
                titulo_selecionado = st.selectbox("Selecione uma conversa:", list(chats_filtrados.keys()), key="chat_select")
                chat_id_selecionado = chats_filtrados[titulo_selecionado]

                st.markdown('<div class="chat-buttons">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📂 Abrir", key="abrir_chat"):
                        start_time_db_load = time.time()
                        st.session_state['chat_id'] = chat_id_selecionado
                        st.session_state['messages'] = [{"role": r, "content": c} for r, c in carregar_chat(chat_id_selecionado)]
                        end_time_db_load = time.time()
                        print(f"Tempo para carregar chat do DB: {end_time_db_load - start_time_db_load:.4f} segundos")
                        st.rerun()
                with col2:
                    if st.button("❌ Deletar", key="deletar_chat"):
                        start_time_db_delete = time.time()
                        deletar_chat(chat_id_selecionado)
                        end_time_db_delete = time.time()
                        print(f"Tempo para deletar chat do DB: {end_time_db_delete - start_time_db_delete:.4f} segundos")
                        if st.session_state.get('chat_id') == chat_id_selecionado:
                            st.session_state['chat_id'] = None
                            st.session_state['messages'] = []
                        st.success("Conversa deletada.")
                        st.rerun()
                with col3:
                    st.write("")  # Preenchimento visual
                st.markdown('</div>', unsafe_allow_html=True)

                # Renomear
                st.markdown('<div class="rename-row">', unsafe_allow_html=True)
                novo_titulo = st.text_input("✏️ Novo título:", value=titulo_selecionado, key="novo_titulo_input")
                if st.button("💾 Salvar Nome", key="salvar_nome_btn"):
                    start_time_db_rename = time.time()
                    renomear_chat(chat_id_selecionado, novo_titulo)
                    end_time_db_rename = time.time()
                    print(f"Tempo para renomear chat no DB: {end_time_db_rename - start_time_db_rename:.4f} segundos")
                    st.success("Título atualizado.")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 Utilitários")
    if st.button("📚 Leitor de PDF", use_container_width=True):
        st.session_state["pagina"] = "leitor_pdf"
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Configurações da Avelyn")
    with st.expander("Controles", expanded=True):
        st.markdown("### 🧠 Preferências de Análise")

        # Forçar sempre resposta longa
        modo_resposta = st.radio(
            "Formato da resposta:",
            ["Longa e detalhada", "Curta e direta"],
            horizontal=True,
            index=0,
            help="Respostas longas trazem contexto, insights e explicações completas."
        )
        st.session_state["modo_resposta"] = modo_resposta

        nivel_analise = st.selectbox(
            "Nível da análise de dados:",
            ["Estratégica (com insights e recomendações)", "Avançada (estatísticas e padrões)", "Básica (descrições simples)"],
            index=0,
            help="Escolha o nível de profundidade que Avelyn deve aplicar nas análises."
        )
        st.session_state["nivel_analise"] = nivel_analise

        # Reset de memória
        if st.button("♻️ Resetar Memória", help="Limpa a memória de contexto atual (não apaga o histórico do chat)."):
            st.session_state["memory"] = []
            st.success("Memória limpa com sucesso!")

        st.markdown("---")
        st.markdown("### 📊 Estatísticas da Sessão")
        if st.session_state.get("messages"):
            total_mensagens = len(st.session_state["messages"])
            total_tokens = sum(len(m["content"].split()) for m in st.session_state["messages"])
            st.write(f"📨 Mensagens trocadas: **{total_mensagens}**")
            st.write(f"🔢 Estimativa de tokens: **{total_tokens:,}**")
        else:
            st.info("Nenhuma conversa iniciada ainda.")

        st.markdown("---")
        st.markdown("### 🧪 Modo Desenvolvedor")
        st.session_state["debug_mode"] = st.checkbox("Ativar modo desenvolvedor", value=st.session_state.get("debug_mode", False))


    if st.button("📝 Exportar para PDF"):
        if st.session_state.get("messages"):
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for m in st.session_state["messages"]:
                pdf.multi_cell(0, 10, f"{m['role'].upper()}: {m['content']}\n")
            caminho = "conversa_exportada.pdf"
            pdf.output(caminho)
            with open(caminho, "rb") as f:
                st.download_button("📥 Baixar PDF", f, file_name="conversa_avelyn.pdf")

    # Estilo opcional para barra lateral mais clean
    st.markdown("""
        <style>
        .sidebar-content {
            overflow-y: auto;
            scrollbar-width: thin;
        }
        .stButton > button {
            width: 100%;
            border-radius: 0.5rem;
            margin-bottom: 0.25rem;
        }
        </style>
    """, unsafe_allow_html=True)
    end_time_sidebar = time.time()
    print(f"Tempo total para renderizar a sidebar: {end_time_sidebar - start_time_sidebar:.4f} segundos")


# ======================
# CHAT E MENSAGENS TEXTO
# ======================
renderizar_chat()

# ==========================
# CAPTURA DE ÁUDIO POR MICROFONE
# ==========================
if st.button("🎤", key="gravar_audio", help="Clique para gravar"):
    st.session_state['gravar'] = True

if st.session_state.get("gravar"):
    with st.spinner("🎤 Gravando por 7 segundos..."):
        texto_voz = capturar_audio_e_transcrever(duracao=7)

    st.success("📝 Transcrição detectada!")
    st.markdown(f"**Você disse:** {texto_voz}")

    st.session_state['messages'].append({"role": "user", "content": texto_voz})
    if not st.session_state['chat_id']:
        st.session_state['chat_id'] = criar_chat("Chat por Voz")
    salvar_mensagem(st.session_state['chat_id'], "user", texto_voz)

    with st.spinner("🤖 Avelyn está respondendo..."):
        start_time_ia = time.time()
        historico_limitado = st.session_state['messages'][-12:]  # mantém só as 12 últimas trocas
        resposta = chamar_together(historico_limitado)
        end_time_ia = time.time()
        print(f"Tempo para chamar Together AI: {end_time_ia - start_time_ia:.4f} segundos")

    st.session_state['messages'].append({"role": "assistant", "content": resposta})
    st.session_state['memory'].append(resposta)
    salvar_mensagem(st.session_state['chat_id'], "assistant", resposta)
    st.session_state['gravar'] = None
    st.rerun()

# ===============================
# IMPORTAÇÕES E FUNÇÕES DE LIMPEZA
# ===============================
from limpeza import limpar_formatacao  # <- certifique-se que o arquivo limpeza.py está na raiz ou no mesmo diretório

# ===============================
# ENTRADA DE TEXTO E ARQUIVOS
# ===============================
prompt = st.chat_input("Digite algo e/ou envie uma imagem, PDF ou planilha", accept_file=True, file_type=["jpg", "jpeg", "png", "pdf", "xlsx", "xls"])

if prompt:
    user_input = prompt.text if prompt.text else ""
    uploaded_file = prompt.get("files")[0] if prompt.get("files") else None

    if not st.session_state['chat_id'] and (user_input or uploaded_file):
        titulo_chat = user_input[:50] if user_input else "Novo Chat com Arquivo"
        st.session_state['chat_id'] = criar_chat(titulo_chat)

    if user_input:
        st.session_state['messages'].append({"role": "user", "content": user_input})
        salvar_mensagem(st.session_state['chat_id'], "user", user_input)

    if uploaded_file:
        st.session_state['uploaded_file'] = uploaded_file

        try:
            mensagem = ""

            if uploaded_file.name.endswith(".pdf"):
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    texto_inicial = ""
                    for i in range(doc.page_count):  # <-- Lê o PDF completo
                        texto_inicial += doc.load_page(i).get_text("text", sort=True) + "\n"
                    st.session_state['conteudo_pdf_inicial'] = texto_inicial
                    mensagem = f"📄 O documento **{uploaded_file.name}** foi carregado. Todo o conteúdo está disponível."

            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
                linhas, colunas = df.shape
                tipos = df.dtypes

                mensagem = f"📈 Avelyn analisou a planilha **{uploaded_file.name}**.\n"
                mensagem += f"Ela possui **{linhas} registros** e **{colunas} colunas**.\n"
                mensagem += "\n🔍 **Leitura das colunas:**\n"

                for coluna in df.columns:
                    serie = df[coluna].dropna()
                    tipo = tipos[coluna]

                    if pd.api.types.is_numeric_dtype(tipo) and not serie.empty:
                        media = serie.mean()
                        mediana = serie.median()
                        minimo = serie.min()
                        maximo = serie.max()
                        desvio = serie.std()
                        dispersao = "alta" if desvio > media * 0.5 else "moderada" if desvio > media * 0.2 else "baixa"
                        simetria = "simétrica" if abs(media - mediana) < media * 0.1 else "assimétrica"

                        mensagem += (
                            f"\n📁 **{coluna}**: valores numéricos.\n"
                            f"   Média: {media:.2f}, Mediana: {mediana:.2f}, de {minimo:.2f} a {maximo:.2f}.\n"
                            f"   Variabilidade: {dispersao}, distribuição: {simetria}.\n"
                        )

                    elif pd.api.types.is_object_dtype(tipo) or pd.api.types.is_categorical_dtype(tipo):
                        total_unicos = serie.nunique()
                        exemplos = serie.unique()[:5]
                        mensagem += (
                            f"\n🏷️ **{coluna}**: dados categóricos ou descritivos.\n"
                            f"   {total_unicos} categorias únicas. Exemplos: {', '.join(map(str, exemplos))}\n"
                        )

                tabela_completa = df.to_markdown(index=False)
                st.session_state["dados_excel_brutos"] = (
                    f"📈 Abaixo está o conteúdo integral da planilha **{uploaded_file.name}**, formatado como tabela Markdown:\n\n"
                    f"{tabela_completa}\n\n"
                    "Interprete esses dados diretamente. Apresente uma análise clara, contextualizada, didática e estratégica. "
                    "Considere padrões, anomalias, variações relevantes e possíveis interpretações do conjunto como um todo."
                )

            elif uploaded_file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                mensagem = f"🖼️ A imagem **{uploaded_file.name}** foi carregada. Diga o que deseja analisar."

            else:
                mensagem = f"📋 O arquivo **{uploaded_file.name}** foi carregado com sucesso."

            st.session_state['messages'].append({"role": "assistant", "content": mensagem})
            salvar_mensagem(st.session_state['chat_id'], "assistant", mensagem)

            with st.spinner("🤖 Avelyn está interpretando os dados..."):
                contexto = list(st.session_state['messages'])

                if st.session_state.get("dados_excel_brutos"):
                    contexto.append({
                        "role": "user",
                        "content": st.session_state["dados_excel_brutos"]
                    })

                if st.session_state.get("conteudo_pdf_inicial") and st.session_state.get("pagina") != "leitor_pdf":
                    contexto.append({
                        "role": "user",
                        "content": f"\n\nConteúdo completo do PDF carregado:\n{st.session_state['conteudo_pdf_inicial'][:3000]}"
                    })

                resposta = chamar_together(contexto[-12:])

                resposta_simulada = ""
                placeholder = st.empty()
                with st.chat_message("assistant"):
                    for char in resposta:
                        resposta_simulada += char
                        placeholder.markdown(resposta_simulada + "▌")
                        time.sleep(0.012)

            resposta_limpa = limpar_formatacao(resposta_simulada)
            st.session_state['messages'].append({"role": "assistant", "content": resposta_simulada})
            st.session_state['memory'].append(resposta_simulada)
            salvar_mensagem(st.session_state['chat_id'], "assistant", resposta_simulada)
            st.rerun()

        except Exception as e:
            erro_msg = f"❌ Erro ao processar o arquivo **{uploaded_file.name}**:\n\n`{e}`"
            st.session_state['messages'].append({"role": "assistant", "content": erro_msg})
            salvar_mensagem(st.session_state['chat_id'], "assistant", erro_msg)
            st.error(erro_msg)

    elif user_input:
        with st.spinner("🤖 Avelyn está digitando..."):
            resposta = chamar_together(st.session_state['messages'][-12:])

            resposta_simulada = ""
            placeholder = st.empty()
            with st.chat_message("assistant"):
                for char in resposta:
                    resposta_simulada += char
                    placeholder.markdown(resposta_simulada + "▌")
                    time.sleep(0.012)

        resposta_limpa = limpar_formatacao(resposta_simulada)
        st.session_state['messages'].append({"role": "assistant", "content": resposta_simulada})
        st.session_state['memory'].append(resposta_simulada)
        salvar_mensagem(st.session_state['chat_id'], "assistant", resposta_simulada)
        st.rerun()

# ===============================
# MANUTENÇÃO DO HISTÓRICO
# ===============================
if len(st.session_state['messages']) > 500:
    st.session_state['messages'] = st.session_state['messages'][-500:]

# ===============================
# PÁGINA DE LEITOR DE PDF
# ===============================
if st.session_state.get("pagina") == "leitor_pdf":
    from leitor_pdf import ler_pdf
    ler_pdf()
    st.stop()

