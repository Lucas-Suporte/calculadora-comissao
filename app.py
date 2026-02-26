import streamlit as st
import os
from utils.auth import autenticar, cadastrar_usuario, carregar_usuarios
from utils.relatorio import gerar_pdf

st.set_page_config(page_title="Calculadora de Comissão", layout="wide")

# ==============================
# CONTROLE DE SESSÃO
# ==============================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# ==============================
# TELA DE LOGIN
# ==============================

def tela_login():
    st.title("Sistema de Comissão")

    opcao = st.radio("Escolha uma opção:", ["Login", "Primeiro Acesso"])

    if opcao == "Login":
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            usuario = autenticar(email, senha)
            if usuario:
                st.session_state.usuario_logado = usuario
                st.rerun()
            else:
                st.error("Login inválido.")

    else:
        st.subheader("Criar Primeiro Acesso")
        novo_email = st.text_input("Novo Email")
        nova_senha = st.text_input("Nova Senha", type="password")

        if st.button("Cadastrar"):
            sucesso = cadastrar_usuario(novo_email, nova_senha)
            if sucesso:
                st.success("Usuário cadastrado com sucesso.")
            else:
                st.error("Usuário já existe.")

# ==============================
# DASHBOARD PRINCIPAL
# ==============================

def dashboard():

    usuario = st.session_state.usuario_logado

    with st.sidebar:
        st.write(f"Usuário: {usuario['email']}")
        if st.button("Logout"):
            st.session_state.usuario_logado = None
            st.rerun()

    st.title("Calculadora de Comissão")

    nome = st.text_input("Nome do Funcionário")
    mes = st.text_input("Mês de Referência")

    st.divider()

    st.subheader("Serviços Realizados")

    categorias = [
        "Banho",
        "Tosa",
        "Hidratação",
        "Taxa Higiênica"
    ]

    resultados = []
    total_comissao = 0

    for categoria in categorias:

        st.markdown(f"### {categoria}")

        qtd = st.number_input(f"Quantidade - {categoria}", min_value=0, step=1, key=f"qtd_{categoria}")
        meta = st.number_input(f"Meta - {categoria}", min_value=0, step=1, key=f"meta_{categoria}")
        percentual = st.number_input(f"% Comissão - {categoria}", min_value=0.0, step=1.0, key=f"perc_{categoria}")

        valor_unitario = st.number_input(f"Valor Unitário - {categoria}", min_value=0.0, step=1.0, key=f"valor_{categoria}")

        comissao = qtd * valor_unitario * (percentual / 100)
        total_comissao += comissao

        resultados.append({
            "categoria": categoria,
            "qtd": qtd,
            "meta": meta,
            "percentual": percentual,
            "comissao": comissao
        })

        st.divider()

    st.subheader("Resumo")

    st.metric("Comissão Total", f"R$ {total_comissao:,.2f}")

    st.divider()

    # ==============================
    # GERAR RELATÓRIO
    # ==============================

    if st.button("Gerar Relatório em PDF"):

        caminho_pdf = gerar_pdf(nome, mes, resultados, total_comissao)

        with open(caminho_pdf, "rb") as f:
            st.download_button(
                label="Baixar Relatório",
                data=f,
                file_name=f"relatorio_{nome}_{mes}.pdf",
                mime="application/pdf"
            )

# ==============================
# CONTROLE PRINCIPAL
# ==============================

if st.session_state.usuario_logado:
    dashboard()
else:
    tela_login()
