import streamlit as st
from database import criar_tabela_usuarios
from auth import cadastrar_usuario, login

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
            st.success("Login realizado com sucesso")
            st.rerun()
        else:
            st.error("E-mail ou senha inválidos")

    st.markdown("---")
    st.subheader("Cadastrar Usuário (Admin Inicial)")
    nome = st.text_input("Nome")
    novo_email = st.text_input("Novo E-mail")
    nova_senha = st.text_input("Nova Senha", type="password")

    if st.button("Cadastrar"):
        cadastrar_usuario(nome, novo_email, nova_senha, "admin")
        st.success("Usuário cadastrado")

# =========================
# SISTEMA PRINCIPAL
# =========================
else:

    st.sidebar.title("Menu")
    st.sidebar.write(f"Usuário: {st.session_state.usuario['nome']}")
    if st.sidebar.button("Gerar PDF"):
        st.sidebar.success("Função PDF será executada aqui")

    if st.sidebar.button("Logout"):
        st.session_state.usuario = None
        st.rerun()

    st.title("Dashboard PET247")
    st.write("Sistema protegido e autenticado com sucesso.")
