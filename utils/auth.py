import json
import os

ARQUIVO_USUARIOS = "usuarios.json"

ADMIN_FIXO = {
    "usuario": "pet247market",
    "senha": "1234",
    "tipo": "admin"
}


# ==============================
# BASE
# ==============================

def inicializar_admin():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)

    usuarios = carregar_usuarios()

    if ADMIN_FIXO["usuario"] not in usuarios:
        usuarios[ADMIN_FIXO["usuario"]] = {
            "senha": ADMIN_FIXO["senha"],
            "tipo": "admin"
        }
        salvar_usuarios(usuarios)


def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return {}
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)


# ==============================
# AUTENTICAÇÃO
# ==============================

def autenticar(usuario, senha):
    inicializar_admin()
    usuarios = carregar_usuarios()

    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        return {
            "usuario": usuario,
            "tipo": usuarios[usuario]["tipo"]
        }

    return None


# ==============================
# CADASTRO (sempre usuario comum)
# ==============================

def cadastrar_usuario(usuario, senha):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        return False

    usuarios[usuario] = {
        "senha": senha,
        "tipo": "usuario"
    }

    salvar_usuarios(usuarios)
    return True


# ==============================
# ADMIN
# ==============================

def atualizar_usuario(usuario, nova_senha=None, novo_tipo=None):
    usuarios = carregar_usuarios()

    if usuario in usuarios:
        if nova_senha:
            usuarios[usuario]["senha"] = nova_senha
        if novo_tipo:
            usuarios[usuario]["tipo"] = novo_tipo

        salvar_usuarios(usuarios)
        return True

    return False


def listar_usuarios():
    return carregar_usuarios()
