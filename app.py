import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

st.set_page_config(page_title="Dashboard Performance – PET247", layout="wide")

# CORES DA MARCA
AZUL = "#0B0F6D"
VERDE = "#17B3A3"

st.markdown(f"<h1 style='color:{AZUL}'>🐾 Dashboard Performance - PET247</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
nome_profissional = st.text_input("Nome do Profissional")
mes_referencia = st.text_input("Mês de Referência")

META_CONFIG = {
    "BANHO": 130,
    "TOSA HIGIENICA": 20,
    "TOSA MAQUINA": 15,
    "TOSA TESOURA": 15,
    "TRATAMENTOS": 15,
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

    # LEITURA
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.upper().str.strip()

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        st.error("A planilha precisa conter SERVICO e VALOR.")
        st.write("Colunas encontradas:", df.columns.tolist())
        st.stop()

    df = df[["SERVICO", "VALOR"]].dropna()

    df["VALOR"] = (
        df["VALOR"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("-", "", regex=False)
    )

    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    df = df.dropna()

    registros = []

    for _, row in df.iterrows():
        servicos = str(row["SERVICO"]).split("+")
        for s in servicos:
            registros.append({
                "SERVICO": s.strip().upper(),
                "CATEGORIA": classificar(s.strip()),
                "VALOR": row["VALOR"]
            })

    df_final = pd.DataFrame(registros)

    if df_final.empty:
        st.error("Nenhum serviço identificado.")
        st.stop()

    # RESUMO POR CATEGORIA
    resumo = df_final.groupby("CATEGORIA").agg(
        QUANTIDADE=("VALOR", "count"),
        FATURAMENTO=("VALOR", "sum")
    ).reset_index()

    # RESUMO POR SERVIÇO INDIVIDUAL
    servicos_individuais = df_final.groupby("SERVICO").agg(
        QUANTIDADE=("VALOR", "count"),
        FATURAMENTO=("VALOR", "sum")
    ).reset_index()

    # DASHBOARD EM COLUNAS
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Performance por Categoria")

        for _, row in resumo.iterrows():
            categoria = row["CATEGORIA"]
            qtd = row["QUANTIDADE"]
            meta = META_CONFIG.get(categoria, 1)

            progresso = min(qtd / meta, 1.0)
            falta = max(meta - qtd, 0)

            st.markdown(f"### {categoria}")
            st.progress(progresso)

            if falta > 0:
                st.markdown(f"🔴 Faltam **{falta} serviços** para atingir a meta.")
            else:
                st.markdown("🟢 Meta atingida.")

            st.markdown(f"Total realizado: **{qtd}**")
            st.markdown("---")

    with col2:
        st.subheader("Gráfico Resumido")

        fig = plt.figure(figsize=(4,3))
        plt.bar(resumo["CATEGORIA"], resumo["QUANTIDADE"])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.subheader("Serviços Discriminados Individualmente")
    st.dataframe(servicos_individuais, use_container_width=True)

    # EXPORTAR PDF
    if st.button("Exportar Relatório em PDF"):

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        try:
            elements.append(Image("logo.png", width=3*inch, height=1*inch))
            elements.append(Spacer(1, 0.3 * inch))
        except:
            pass

        elements.append(Paragraph(f"Relatório de Performance - {mes_referencia}", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(f"Profissional: {nome_profissional}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

        tabela = [["Serviço", "Qtd", "Faturamento"]]

        for _, row in servicos_individuais.iterrows():
            tabela.append([
                row["SERVICO"],
                row["QUANTIDADE"],
                f"R$ {row['FATURAMENTO']:.2f}"
            ])

        table = Table(tabela)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(AZUL)),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ]))

        elements.append(table)
        doc.build(elements)

        with open(temp_file.name, "rb") as f:
            st.download_button(
                "Baixar PDF",
                f,
                file_name="Relatorio_Performance_PET247.pdf",
                mime="application/pdf"
            )
