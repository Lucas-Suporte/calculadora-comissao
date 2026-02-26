import streamlit as st
import pandas as pd
from utils.comissao import calcular_comissao
from utils.auth import autenticar, cadastrar_usuario, carregar_usuarios, atualizar_usuario

st.set_page_config(page_title="Sistema de Comissão", layout="wide")

# ==========================
# CONTROLE DE SESSÃO
# ==========================

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "tipo" not in st.session_state:
    st.session_state.tipo = ""

# ==========================
# TELA DE LOGIN
# ==========================

def tela_login():
    st.title("Acesso ao Sistema")

    aba = st.radio("Escolha:", ["Login", "Primeiro Acesso"])

    if aba == "Login":
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            ok, tipo = autenticar(email, senha)
            if ok:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.tipo = tipo
                st.rerun()
            else:
                st.error("E-mail ou senha inválidos")

    if aba == "Primeiro Acesso":
        email = st.text_input("Novo E-mail")
        senha = st.text_input("Nova Senha", type="password")

        if st.button("Criar Conta"):
            ok, msg = cadastrar_usuario(email, senha)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

if not st.session_state.logado:
    tela_login()
    st.stop()

# ==========================
# SIDEBAR
# ==========================

with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("---")
    st.markdown(f"**Usuário:** {st.session_state.usuario}")
    st.markdown(f"**Perfil:** {st.session_state.tipo}")
    st.markdown("---")

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

# ==========================
# PAINEL ADMIN
# ==========================

if st.session_state.tipo == "admin":

    st.header("Painel Administrativo")

    usuarios = carregar_usuarios()

    for email in usuarios:
        with st.expander(email):
            nova_senha = st.text_input(
                f"Nova senha para {email}",
                type="password",
                key=email
            )

            if st.button(f"Atualizar {email}"):
                ok, msg = atualizar_usuario(email, nova_senha)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.divider()

# ==========================
# DASHBOARD DE COMISSÃO
# ==========================

st.title("Relatório de Comissão")

nome = st.text_input("Nome do Funcionário")
mes = st.text_input("Mês de Referência")
arquivo = st.file_uploader("Envie a planilha CSV", type="csv")

if arquivo:
    try:
        df = pd.read_csv(arquivo, sep=None, engine="python")
        resultados, total_comissao, total_faturamento = calcular_comissao(df)

        st.subheader("Resumo Geral")
        st.write("Faturamento Total:", f"R$ {total_faturamento:,.2f}")
        st.write("Comissão Final:", f"R$ {total_comissao:,.2f}")

        st.subheader("Detalhamento")

        for r in resultados:
            st.write(
                r["categoria"],
                "| Qtde:", r["qtd"],
                "| Meta:", r["meta"],
                "| Comissão:", f"R$ {r['comissao']:,.2f}"
            )

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
