import streamlit as st
import pandas as pd
from utils.auth import autenticar

st.set_page_config(page_title="Calculadora de Comissão", layout="wide")

# ==============================
# CONTROLE DE SESSÃO
# ==============================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None


# ==============================
# LOGIN
# ==============================

def tela_login():
    st.title("Sistema de Comissão")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        dados = autenticar(usuario, senha)
        if dados:
            st.session_state.usuario_logado = dados
            st.rerun()
        else:
            st.error("Credenciais inválidas.")


# ==============================
# DASHBOARD
# ==============================

def dashboard():

    usuario = st.session_state.usuario_logado

    # Sidebar simples
    with st.sidebar:
        st.write(f"Usuário: {usuario['usuario']}")
        st.write(f"Tipo: {usuario['tipo']}")

        if st.button("Logout"):
            st.session_state.usuario_logado = None
            st.rerun()

    st.title("Calculadora de Comissão")

    st.subheader("Carregar arquivo CSV")

    arquivo = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

    if arquivo is not None:

        try:
            df = pd.read_csv(arquivo)

            st.subheader("Dados carregados")
            st.dataframe(df)

            st.subheader("Cálculo de Comissão")

            if all(col in df.columns for col in ["quantidade", "valor_unitario", "percentual"]):

                df["comissao"] = df["quantidade"] * df["valor_unitario"] * (df["percentual"] / 100)

                total_comissao = df["comissao"].sum()

                st.dataframe(df)

                st.metric("Comissão Total", f"R$ {total_comissao:,.2f}")

            else:
                st.error("O CSV precisa conter as colunas: quantidade, valor_unitario, percentual")

        except Exception as e:
            st.error("Erro ao processar o arquivo CSV.")


# ==============================
# CONTROLE PRINCIPAL
# ==============================

if st.session_state.usuario_logado:
    dashboard()
else:
    tela_login()
