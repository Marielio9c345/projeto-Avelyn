# db.py — Gerenciamento de banco de dados SQLite da Avelyn IA

import sqlite3
from datetime import datetime

# Nome do banco de dados
DB_NAME = 'avelin.db'

# ========================
# 🔌 Conexão
# ========================

def conectar_banco():
    return sqlite3.connect(DB_NAME)

# ========================
# 📁 Inicialização
# ========================

def inicializar_db():
    conn = conectar_banco()
    cursor = conn.cursor()

    # Cria tabela de chats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data_hora TEXT
        )
    ''')

    # Cria tabela de mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_hora TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )
    ''')

    conn.commit()
    conn.close()

# ========================
# 💬 Chats
# ========================

def criar_chat(titulo):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chats (titulo, data_hora) VALUES (?, ?)',
        (titulo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def listar_chats():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo FROM chats ORDER BY id DESC')
    dados = cursor.fetchall()
    conn.close()
    return dados

def renomear_chat(chat_id, novo_titulo):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('UPDATE chats SET titulo = ? WHERE id = ?', (novo_titulo, chat_id))
    conn.commit()
    conn.close()

def deletar_chat(chat_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mensagens WHERE chat_id = ?', (chat_id,))
    cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    conn.commit()
    conn.close()

# ========================
# 🧠 Mensagens
# ========================

def salvar_mensagem(chat_id, role, conteudo):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO mensagens (chat_id, role, conteudo, data_hora) VALUES (?, ?, ?, ?)',
        (chat_id, role, conteudo, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def carregar_chat(chat_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT role, conteudo FROM mensagens WHERE chat_id = ? ORDER BY id',
        (chat_id,)
    )
    dados = cursor.fetchall()
    conn.close()
    return dados
