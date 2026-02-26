import json
import os

ARQUIVO_USUARIOS = "usuarios.json"


# ==============================
# BASE DE DADOS
# ==============================

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)

    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)


# ==============================
# AUTENTICAÇÃO
# ==============================

def autenticar(usuario, senha):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        if usuarios[usuario]["senha"] == senha:
            return {
                "usuario": usuario,
                "tipo": usuarios[usuario].get("tipo", "usuario")
            }

    return None


# ==============================
# CADASTRO
# ==============================

def cadastrar_usuario(usuario, senha, tipo="usuario"):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        return False

    usuarios[usuario] = {
        "senha": senha,
        "tipo": tipo
    }

    salvar_usuarios(usuarios)
    return True


# ==============================
# ATUALIZAÇÃO DE SENHA
# ==============================

def atualizar_usuario(usuario, nova_senha):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        usuarios[usuario]["senha"] = nova_senha
        salvar_usuarios(usuarios)
        return True

    return False


# ==============================
# LISTAGEM (para admin)
# ==============================

def listar_usuarios():
    return carregar_usuarios()
