import streamlit as st
import base64
import os
from utils.auth import autenticar, cadastrar_usuario, listar_usuarios, atualizar_usuario
from utils.relatorio import gerar_pdf

st.set_page_config(page_title="Calculadora de Comissão", layout="wide")

# ==============================
# FUNÇÃO BASE64
# ==============================

def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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

    opcao = st.radio("Escolha uma opção:", ["Login", "Primeiro Acesso"])

    if opcao == "Login":
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
        novo_usuario = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Nova Senha", type="password")

        if st.button("Cadastrar"):
            sucesso = cadastrar_usuario(novo_usuario, nova_senha)
            if sucesso:
                st.success("Usuário criado com sucesso.")
            else:
                st.error("Usuário já existe.")


# ==============================
# ÁREA ADMIN
# ==============================

def area_admin():
    st.subheader("Gerenciar Usuários")

    usuarios = listar_usuarios()

    for user, dados in usuarios.items():
        st.markdown(f"### {user}")
        st.write(f"Tipo: {dados['tipo']}")

        nova_senha = st.text_input(f"Nova senha para {user}", key=f"senha_{user}")

        novo_tipo = st.selectbox(
            f"Tipo de usuário {user}",
            ["usuario", "admin"],
            index=0 if dados["tipo"] == "usuario" else 1,
            key=f"tipo_{user}"
        )

        if st.button(f"Atualizar {user}"):
            atualizar_usuario(user, nova_senha, novo_tipo)
            st.success("Atualizado com sucesso.")
            st.rerun()

        st.divider()


# ==============================
# DASHBOARD
# ==============================

def dashboard():

    usuario = st.session_state.usuario_logado

    # ==============================
    # LOGO DE FUNDO (50% OPACIDADE)
    # Só aparece após login
    # ==============================

    if os.path.exists("assets/logo_fundo.png"):
        logo_fundo_base64 = get_base64_image("assets/logo_fundo.png")

        st.markdown(
            f"""
            <style>
            .stApp {{
                position: relative;
            }}

            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url("data:image/png;base64,{logo_fundo_base64}");
                background-size: 40%;
                background-repeat: no-repeat;
                background-position: center;
                opacity: 0.5;
                z-index: -1;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    # ==============================
    # SIDEBAR
    # ==============================

    with st.sidebar:

        if os.path.exists("assets/logo_sidebar.png"):
            st.image("assets/logo_sidebar.png", use_container_width=True)

        st.markdown("---")
        st.write(f"Usuário: {usuario['usuario']}")
        st.write(f"Tipo: {usuario['tipo']}")

        if usuario["tipo"] == "admin":
            menu = st.radio("Navegação", ["Comissão", "Administrador"])
        else:
            menu = "Comissão"

        if st.button("Logout"):
            st.session_state.usuario_logado = None
            st.rerun()

    if usuario["tipo"] == "admin" and menu == "Administrador":
        area_admin()
        return

    # ==============================
    # ÁREA COMISSÃO
    # ==============================

    st.title("Calculadora de Comissão")

    nome = st.text_input("Nome do Funcionário")
    mes = st.text_input("Mês de Referência")

    st.divider()

    categorias = ["Banho", "Tosa", "Hidratação", "Taxa Higiênica"]

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

    st.metric("Comissão Total", f"R$ {total_comissao:,.2f}")

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
