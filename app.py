import streamlit as st
import pandas as pd
import json
import os
from utils.comissao import calcular_comissao
from utils.relatorio import gerar_pdf

st.set_page_config(page_title="Sistema de Comissão PET247", layout="wide")

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
    if usuario == "pet247market":
        return
    usuarios = carregar_usuarios()
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

    st.title("Dashboard Automático de Comissão")

    nome = st.text_input("Nome do Funcionário")
    mes = st.text_input("Mês de Referência")

    st.divider()

    st.subheader("Carregar CSV do Sistema")

    arquivo = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

    if arquivo:

        try:
            df = pd.read_csv(arquivo)

            resultados, total_comissao, total_faturamento = calcular_comissao(df)

            st.subheader("Resumo por Categoria")

            for item in resultados:

                if item["meta"] == "Super Meta":
                    progresso = 1.0
                    medalha = "🥇 Super Meta"
                elif item["meta"] == "Meta":
                    progresso = 0.7
                    medalha = "🥈 Meta"
                else:
                    progresso = 0.4
                    medalha = "🥉 Base"

                st.markdown(f"### {item['categoria']}")
                st.progress(progresso)
                st.metric(
                    medalha,
                    f"R$ {item['comissao']:,.2f}"
                )
                st.divider()

            st.success(f"Comissão Total: R$ {total_comissao:,.2f}")

            if st.button("Gerar PDF"):
                caminho = gerar_pdf(nome, mes, resultados, total_comissao)

                with open(caminho, "rb") as f:
                    st.download_button(
                        "Baixar Relatório",
                        f,
                        file_name=f"relatorio_{nome}_{mes}.pdf",
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

# =========================
# CONTROLE PRINCIPAL
# =========================

if st.session_state.usuario_logado:
    dashboard()
else:
    tela_login()
