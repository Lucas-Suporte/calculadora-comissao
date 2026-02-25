import streamlit as st
import pandas as pd
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

st.set_page_config(page_title="Performance Tosador – PET247", layout="wide")

# CORES DA MARCA
AZUL = colors.HexColor("#0B0F6D")
VERDE = colors.HexColor("#17B3A3")

st.markdown("<h1 style='color:#0B0F6D'>🐾 Performance – PET247 Market</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
nome_profissional = st.text_input("Nome do Profissional")
mes_referencia = st.text_input("Mês de Referência (ex: Janeiro/2026)")
periodo = st.text_input("Período Analisado (ex: 01/01/2026 a 31/01/2026)")
observacoes = st.text_area("Observações")
desmembrar = st.checkbox("Visualizar serviços desmembrados")

META_CONFIG = {
    "BANHO": {"base": 129, "meta": 130, "super": 176},
    "TOSA HIGIENICA": {"base": 19, "meta": 20, "super": 40},
    "TOSA MAQUINA": {"base": 14, "meta": 15, "super": 30},
    "TOSA TESOURA": {"base": 14, "meta": 15, "super": 30},
    "TRATAMENTOS": {"base": 14, "meta": 15, "super": 30},
}

def classificar(servico):
    s = servico.upper()
    if "BANHO" in s:
        return "BANHO"
    if "HIGIENICA" in s:
        return "TOSA HIGIENICA"
    if "MAQUINA" in s:
        return "TOSA MAQUINA"
    if "TESOURA" in s:
        return "TOSA TESOURA"
    return "TRATAMENTOS"

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df = df[["SERVICO", "VALOR"]].dropna()
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    df = df.dropna()

    registros = []

    for _, row in df.iterrows():
        servicos = row["SERVICO"].split("+")
        for s in servicos:
            registros.append({
                "CATEGORIA": classificar(s.strip()),
                "SERVICO_ORIGINAL": row["SERVICO"],
                "VALOR": row["VALOR"]
            })

    df_final = pd.DataFrame(registros)

    resumo = df_final.groupby("CATEGORIA").agg(
        QUANTIDADE=("VALOR", "count"),
        FATURAMENTO=("VALOR", "sum")
    ).reset_index()

    st.subheader("Resumo Geral")
    st.dataframe(resumo)

    if desmembrar:
        st.subheader("Serviços Desmembrados")
        st.dataframe(df_final)

    # MINI GRÁFICO
    fig = plt.figure()
    plt.bar(resumo["CATEGORIA"], resumo["QUANTIDADE"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # META
    st.subheader("Análise de Metas")
    for _, row in resumo.iterrows():
        categoria = row["CATEGORIA"]
        qtd = row["QUANTIDADE"]
        meta = META_CONFIG[categoria]["meta"]

        if qtd < meta:
            falta = meta - qtd
            st.warning(f"{categoria}: Faltam {falta} serviços para atingir a próxima meta.")
        else:
            st.success(f"{categoria}: Meta atingida ou superada.")

    # GERAR PDF
    if st.button("Gerar Relatório em PDF"):

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Image("logo.png", width=3*inch, height=1*inch))
        elements.append(Spacer(1, 0.3 * inch))

        titulo_style = ParagraphStyle(
            'titulo',
            parent=styles['Heading1'],
            textColor=AZUL
        )

        elements.append(Paragraph("Relatório de Performance", titulo_style))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(f"Profissional: {nome_profissional}", styles["Normal"]))
        elements.append(Paragraph(f"Mês de Referência: {mes_referencia}", styles["Normal"]))
        elements.append(Paragraph(f"Período: {periodo}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

        tabela = [["Categoria", "Qtd", "Faturamento"]]

        for _, row in resumo.iterrows():
            tabela.append([
                row["CATEGORIA"],
                row["QUANTIDADE"],
                f"R$ {row['FATURAMENTO']:.2f}"
            ])

        table = Table(tabela)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), AZUL),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(f"Observações:", styles["Heading2"]))
        elements.append(Paragraph(observacoes, styles["Normal"]))

        doc.build(elements)

        with open(temp_file.name, "rb") as f:
            st.download_button(
                "Baixar PDF",
                f,
                file_name="Relatorio_Performance_PET247.pdf",
                mime="application/pdf"
            )
