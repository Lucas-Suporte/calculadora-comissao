import streamlit as st
import pandas as pd
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

st.set_page_config(page_title="Dashboard Performance – PET247", layout="wide")

AZUL = "#0B0F6D"
VERDE = "#17B3A3"
logo_path = "logo.png"

# =========================
# BASE FIXA DE VALORES
# =========================

VALORES = {
    1: {"BANHO":65,"TOSA HIGIENICA":100,"TOSA MAQUINA":130,"TOSA TESOURA":150,"REMOCAO SUBPELO":105},
    2: {"BANHO":75,"TOSA HIGIENICA":110,"TOSA MAQUINA":140,"TOSA TESOURA":160},
    3: {"BANHO":90,"TOSA HIGIENICA":125,"TOSA MAQUINA":155,"TOSA TESOURA":175,"REMOCAO SUBPELO":135},
    4: {"BANHO":135,"TOSA HIGIENICA":175,"TOSA MAQUINA":200,"TOSA TESOURA":220},
    5: {"BANHO":180,"TOSA HIGIENICA":225,"TOSA MAQUINA":245,"TOSA TESOURA":300},
}

TRATAMENTOS_VALORES = {
    "HIDRATACAO":35,
    "HIGIENE BUCAL":25,
    "CORTE DE UNHAS":25,
    "REMOCAO SUBPELO":105
}

# =========================
# METAS
# =========================

META_CONFIG = {
    "BANHO":{"base":129,"meta":130,"super":176,"pct":[0.03,0.04,0.05]},
    "TOSA HIGIENICA":{"base":19,"meta":20,"super":40,"pct":[0.10,0.15,0.20]},
    "TOSA MAQUINA":{"base":14,"meta":15,"super":30,"pct":[0.10,0.15,0.20]},
    "TOSA TESOURA":{"base":14,"meta":15,"super":30,"pct":[0.15,0.20,0.25]},
    "TRATAMENTOS":{"base":14,"meta":15,"super":30,"pct":[0.15,0.20,0.25]},
}

# =========================
# HEADER
# =========================

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
if os.path.exists(logo_path):
    st.image(logo_path, width=250)
st.markdown(f"<h1 style='color:{AZUL};'>Dashboard Performance</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{VERDE};'>PET247 Market</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

grupo = st.selectbox("Grupo do Pet (1 a 5)", [1,2,3,4,5])

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx","csv"])
nome = st.text_input("Nome do Profissional")
mes = st.text_input("Mês de Referência")

def classificar(servico):
    s = servico.upper()
    if "BANHO" in s: return "BANHO"
    if "HIGIENICA" in s: return "TOSA HIGIENICA"
    if "MAQUINA" in s: return "TOSA MAQUINA"
    if "TESOURA" in s: return "TOSA TESOURA"
    return "TRATAMENTOS"

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.upper().str.strip()
    df = df[["SERVICO"]].dropna()

    registros = []

    for _, row in df.iterrows():
        servicos = [s.strip().upper() for s in row["SERVICO"].split("+")]

        for s in servicos:
            categoria = classificar(s)

            if categoria == "TRATAMENTOS":
                valor = TRATAMENTOS_VALORES.get(s,0)
            else:
                valor = VALORES[grupo].get(categoria,0)

            registros.append({
                "SERVICO":s,
                "CATEGORIA":categoria,
                "VALOR":valor
            })

    df_final = pd.DataFrame(registros)

    resumo = df_final.groupby("CATEGORIA").agg(
        QUANTIDADE=("VALOR","count"),
        FATURAMENTO=("VALOR","sum")
    ).reset_index()

    total_comissao = 0
    linhas = []

    for _, row in resumo.iterrows():
        cat = row["CATEGORIA"]
        qtd = row["QUANTIDADE"]
        fat = row["FATURAMENTO"]
        meta = META_CONFIG[cat]

        if qtd >= meta["super"]:
            pct = meta["pct"][2]; faixa="SUPER META"
        elif qtd >= meta["meta"]:
            pct = meta["pct"][1]; faixa="META"
        else:
            pct = meta["pct"][0]; faixa="BASE"

        comissao = fat * pct
        total_comissao += comissao

        linhas.append([
            cat,
            qtd,
            f"R$ {fat:,.2f}",
            f"{pct*100:.0f}%",
            f"R$ {comissao:,.2f}",
            faixa
        ])

    tabela = pd.DataFrame(linhas, columns=[
        "Categoria","Qtd","Faturamento",
        "% Aplicada","Comissão","Faixa"
    ])

    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Resumo Geral")
        st.dataframe(tabela, use_container_width=True)

    with col2:
        st.subheader("Dashboard")
        st.success(f"Comissão Total\nR$ {total_comissao:,.2f}")

    # PDF
    if st.button("Exportar PDF"):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp.name, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=3*inch, height=1*inch))
            elements.append(Spacer(1,12))

        elements.append(Paragraph("Relatório de Performance", styles["Heading1"]))
        elements.append(Spacer(1,12))
        elements.append(Paragraph(f"Profissional: {nome}", styles["Normal"]))
        elements.append(Paragraph(f"Mês: {mes}", styles["Normal"]))
        elements.append(Spacer(1,12))

        tabela_pdf = Table([tabela.columns.tolist()] + tabela.values.tolist())
        tabela_pdf.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(AZUL)),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ]))

        elements.append(tabela_pdf)
        elements.append(Spacer(1,12))
        elements.append(Paragraph(f"Comissão Total: R$ {total_comissao:,.2f}", styles["Heading2"]))

        doc.build(elements)

        with open(temp.name,"rb") as f:
            st.download_button("Baixar PDF", f, file_name="Relatorio_PET247.pdf")
