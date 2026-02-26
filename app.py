import streamlit as st
import pandas as pd
from database import criar_tabela_usuarios
from auth import cadastrar_usuario, login
from utils.comissao import calcular_comissao

st.set_page_config(page_title="Sistema PET247", layout="wide")

criar_tabela_usuarios()

# =========================
# CONTROLE DE SESSÃO
# =========================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# =========================
# TELA DE LOGIN
# =========================
if st.session_state.usuario is None:

    st.title("Login - Sistema PET247")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuario = login(email, senha)

        if usuario:
            st.session_state.usuario = usuario
            st.success("Login realizado com sucesso.")
            st.rerun()
        else:
            st.error("E-mail ou senha inválidos.")

    st.markdown("---")
    st.subheader("Cadastrar Usuário (primeiro acesso)")

    nome = st.text_input("Nome")
    novo_email = st.text_input("Novo E-mail")
    nova_senha = st.text_input("Nova Senha", type="password")

    if st.button("Cadastrar"):
        cadastrar_usuario(nome, novo_email, nova_senha, "admin")
        st.success("Usuário cadastrado com sucesso.")

# =========================
# ÁREA PROTEGIDA
# =========================
else:

    st.sidebar.title("Menu")
    st.sidebar.write(f"Usuário: {st.session_state.usuario['nome']}")

    if st.sidebar.button("Logout"):
        st.session_state.usuario = None
        st.rerun()

    st.title("Dashboard de Comissão PET247")

    funcionario = st.text_input("Nome do Funcionário")
    mes = st.text_input("Mês de Referência")
    uploaded_file = st.file_uploader("Enviar arquivo CSV", type=["csv"])

    if uploaded_file and funcionario and mes:

        try:
            df = pd.read_csv(uploaded_file)

            resultados, total_comissao, total_faturamento = calcular_comissao(df)

            st.markdown("---")
            st.subheader("Resumo Geral")

            col1, col2 = st.columns(2)
            col1.metric("Comissão Total", f"R$ {total_comissao:,.2f}")
            col2.metric("Faturamento Total", f"R$ {total_faturamento:,.2f}")

            st.markdown("---")
            st.subheader("Detalhamento por Serviço")

            for item in resultados:
                st.write(
                    f"**{item['categoria']}** | "
                    f"Qtd: {item['qtd']} | "
                    f"{item['meta']} ({item['percentual']}%) | "
                    f"Faturamento: R$ {item['faturamento']:,.2f} | "
                    f"Comissão: R$ {item['comissao']:,.2f}"
                )

        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")
