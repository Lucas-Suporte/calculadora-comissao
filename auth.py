import streamlit as st
import bcrypt
from database import conectar

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

def verificar_senha(senha_digitada, senha_hash):
    return bcrypt.checkpw(senha_digitada.encode(), senha_hash)

def cadastrar_usuario(nome, email, senha, perfil="funcionario"):
    conn = conectar()
    cursor = conn.cursor()

    senha_hash = hash_senha(senha)

    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, perfil) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, perfil)
        )
        conn.commit()
    except:
        pass

    conn.close()

def login(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, senha, perfil FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        if verificar_senha(senha, usuario[2]):
            return {
                "id": usuario[0],
                "nome": usuario[1],
                "perfil": usuario[3]
            }

    return None
