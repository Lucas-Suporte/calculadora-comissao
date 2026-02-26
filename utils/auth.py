import json
import os

CAMINHO_USUARIOS = "data/usuarios.json"


def carregar_usuarios():
    if not os.path.exists(CAMINHO_USUARIOS):
        return {}
    with open(CAMINHO_USUARIOS, "r") as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(CAMINHO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)


def autenticar(email, senha):
    usuarios = carregar_usuarios()
    if email in usuarios and usuarios[email]["senha"] == senha:
        return True, usuarios[email]["tipo"]
    return False, None


def cadastrar_usuario(email, senha, tipo="user"):
    usuarios = carregar_usuarios()

    if email in usuarios:
        return False, "Usuário já existe."

    usuarios[email] = {
        "senha": senha,
        "tipo": tipo
    }

    salvar_usuarios(usuarios)
    return True, "Usuário criado com sucesso."


def atualizar_usuario(email, nova_senha=None, novo_email=None):
    usuarios = carregar_usuarios()

    if email not in usuarios:
        return False, "Usuário não encontrado."

    dados = usuarios[email]

    if nova_senha:
        dados["senha"] = nova_senha

    if novo_email:
        usuarios[novo_email] = dados
        del usuarios[email]

    salvar_usuarios(usuarios)
    return True, "Usuário atualizado com sucesso."
