import sqlite3

def conectar():
    return sqlite3.connect("database.db", check_same_thread=False)

def criar_tabela_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
