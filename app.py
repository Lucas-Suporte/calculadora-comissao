import streamlit as st
import json
import os
from utils.relatorio import gerar_pdf

st.set_page_config(page_title="Sistema de Comissão", layout="wide")

ARQUIVO_USUARIOS = "usuarios.json"

# =========================
# GARANTE ADMIN FIXO
# =========================

def inicializar_admin():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)

    with open(ARQUIVO_USUARIOS, "r") as f:
        usuarios = json.load(f)

    if "pet247market" not in usuarios:
        usuarios["pet247market"] = {
            "senha": "1234",
            "tipo": "admin"
        }

        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump(usuarios, f)

inicializar_admin()

# =========================
# FUNÇÕES USUÁRIO
# =========================

def carregar_usuarios():
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f)

def autenticar(usuario, senha):
    usuarios = carregar_usuarios()
    if usuario in usuarios and usuarios[usuario]["senha"] == senha:
        return {"usuario": usuario, "tipo": usuarios[usuario]["tipo"]}
    return None

def cadastrar_usuario(usuario, senha):
    usuarios = carregar_usuarios()
    if usuario in usuarios:
        return False
    usuarios[usuario] = {"senha": senha, "tipo": "usuario"}
    salvar_usuarios(usuarios)
    return True

def excluir_usuario(usuario):
    usuarios = carregar_usuarios()
    if usuario != "pet247market":
        usuarios.pop(usuario)
        salvar_usuarios(usuarios)

# =========================
# SESSÃO
# =========================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# =========================
# LOGIN
# =========================

def tela_login():
    st.title("Sistema de Comissão PET247")

    aba = st.radio("Selecione:", ["Login", "Cadastrar"])

    if aba == "Login":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            dados = autenticar(usuario, senha)
            if dados:
                st.session_state.usuario_logado = dados
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

    else:
        novo = st.text_input("Novo Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if cadastrar_usuario(novo, senha):
                st.success("Usuário criado com sucesso.")
            else:
                st.error("Usuário já existe.")

# =========================
# ADMIN
# =========================

def area_admin():
    st.header("Painel Administrativo")

    usuarios = carregar_usuarios()

    for user, dados in usuarios.items():
        st.subheader(user)

        col1, col2, col3 = st.columns(3)

        nova_senha = col1.text_input("Nova senha", key=f"senha_{user}")

        novo_tipo = col2.selectbox(
            "Tipo",
            ["usuario", "admin"],
            index=0 if dados["tipo"] == "usuario" else 1,
            key=f"tipo_{user}"
        )

        if col3.button("Excluir", key=f"del_{user}"):
            excluir_usuario(user)
            st.success("Usuário excluído.")
            st.rerun()

        if st.button(f"Atualizar {user}", key=f"update_{user}"):
            usuarios[user]["tipo"] = novo_tipo
            if nova_senha:
                usuarios[user]["senha"] = nova_senha
            salvar_usuarios(usuarios)
            st.success("Atualizado com sucesso.")
            st.rerun()

        st.divider()

# =========================
# DASHBOARD
# =========================

def dashboard():

    usuario = st.session_state.usuario_logado

    with st.sidebar:
        st.write(f"Usuário: {usuario['usuario']}")
        st.write(f"Tipo: {usuario['tipo']}")

        if usuario["tipo"] == "admin":
            menu = st.radio("Menu", ["Comissão", "Administrador"])
        else:
            menu = "Comissão"

        if st.button("Logout"):
            st.session_state.usuario_logado = None
            st.rerun()

    if usuario["tipo"] == "admin" and menu == "Administrador":
        area_admin()
        return

    st.title("Dashboard de Comissão")

    nome = st.text_input("Nome do Funcionário")
    mes = st.text_input("Mês de Referência")

    categorias = {
        "Banho": 0,
        "Tosa": 0,
        "Hidratação": 0,
        "Taxa Higiênica": 0
    }

    resultados = []
    total = 0

    for categoria in categorias:

        st.subheader(categoria)

        col1, col2, col3 = st.columns(3)

        qtd = col1.number_input("Quantidade", min_value=0, key=f"qtd_{categoria}")
        meta = col2.number_input("Meta", min_value=0, key=f"meta_{categoria}")
        perc = col3.number_input("% Comissão", min_value=0.0, key=f"perc_{categoria}")

        progresso = (qtd / meta) if meta > 0 else 0

        st.progress(min(progresso, 1.0))

        valor_unitario = st.number_input("Valor Unitário", min_value=0.0, key=f"valor_{categoria}")

        comissao = qtd * valor_unitario * (perc / 100)
        total += comissao

        st.metric("Comissão", f"R$ {comissao:,.2f}")

        resultados.append({
            "categoria": categoria,
            "qtd": qtd,
            "meta": meta,
            "percentual": perc,
            "comissao": comissao
        })

        st.divider()

    st.success(f"Comissão Total: R$ {total:,.2f}")

    if st.button("Gerar PDF"):
        caminho = gerar_pdf(nome, mes, resultados, total)

        with open(caminho, "rb") as f:
            st.download_button(
                "Baixar Relatório",
                f,
                file_name=f"relatorio_{nome}_{mes}.pdf",
                mime="application/pdf"
            )

# =========================
# CONTROLE
# =========================

if st.session_state.usuario_logado:
    dashboard()
else:
    tela_login()
