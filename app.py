import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard Performance – PET247", layout="wide")

# CORES INSTITUCIONAIS
AZUL = "#0B0F6D"
VERDE = "#17B3A3"

# HEADER COM LOGO
logo_path = "logo.png"

col_logo, col_titulo = st.columns([1,3])

with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

with col_titulo:
    st.markdown(
        f"<h1 style='color:{AZUL}; margin-bottom:0;'>Dashboard Performance</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h3 style='color:{VERDE}; margin-top:0;'>PET247 Market</h3>",
        unsafe_allow_html=True
    )

st.markdown("---")

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
nome_profissional = st.text_input("Nome do Profissional")
mes_referencia = st.text_input("Mês de Referência")

# CONFIG COMPLETA DE METAS + PERCENTUAIS
META_CONFIG = {
    "BANHO": {
        "base_qtd": 129, "meta_qtd": 130, "super_qtd": 176,
        "base_pct": 0.03, "meta_pct": 0.04, "super_pct": 0.05
    },
    "TOSA HIGIENICA": {
        "base_qtd": 19, "meta_qtd": 20, "super_qtd": 40,
        "base_pct": 0.10, "meta_pct": 0.15, "super_pct": 0.20
    },
    "TOSA MAQUINA": {
        "base_qtd": 14, "meta_qtd": 15, "super_qtd": 30,
        "base_pct": 0.10, "meta_pct": 0.15, "super_pct": 0.20
    },
    "TOSA TESOURA": {
        "base_qtd": 14, "meta_qtd": 15, "super_qtd": 30,
        "base_pct": 0.15, "meta_pct": 0.20, "super_pct": 0.25
    },
    "TRATAMENTOS": {
        "base_qtd": 14, "meta_qtd": 15, "super_qtd": 30,
        "base_pct": 0.15, "meta_pct": 0.20, "super_pct": 0.25
    },
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

    # LEITURA DO ARQUIVO
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.upper().str.strip()

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        st.error("A planilha precisa conter as colunas SERVICO e VALOR.")
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

    resumo = df_final.groupby("CATEGORIA").agg(
        QUANTIDADE=("VALOR", "count"),
        FATURAMENTO=("VALOR", "sum")
    ).reset_index()

    servicos_individuais = df_final.groupby("SERVICO").agg(
        QUANTIDADE=("VALOR", "count"),
        FATURAMENTO=("VALOR", "sum")
    ).reset_index()

    st.subheader("📊 Performance e Comissão")

    total_comissao = 0
    relatorio_melhoria = []

    for _, row in resumo.iterrows():
        categoria = row["CATEGORIA"]
        qtd = row["QUANTIDADE"]
        faturamento = row["FATURAMENTO"]

        config = META_CONFIG[categoria]

        if qtd >= config["super_qtd"]:
            faixa = "SUPER META"
            pct = config["super_pct"]
            proxima_meta = None
            indicador = "🟢"
        elif qtd >= config["meta_qtd"]:
            faixa = "META"
            pct = config["meta_pct"]
            proxima_meta = config["super_qtd"]
            indicador = "🟡"
        else:
            faixa = "BASE"
            pct = config["base_pct"]
            proxima_meta = config["meta_qtd"]
            indicador = "🔴"

        comissao = faturamento * pct
        total_comissao += comissao

        st.markdown(f"### {categoria}")
        st.markdown(f"{indicador} Faixa: **{faixa}**")
        st.markdown(f"Percentual aplicado: **{pct*100:.0f}%**")
        st.markdown(f"Comissão gerada: **R$ {comissao:.2f}**")

        progresso = min(qtd / config["super_qtd"], 1.0)
        st.progress(progresso)

        if proxima_meta:
            falta = proxima_meta - qtd
            st.markdown(f"Faltam **{falta} serviços** para atingir o próximo nível.")
            relatorio_melhoria.append(
                f"- {categoria}: aumentar {falta} serviços para subir de faixa."
            )
        else:
            st.markdown("Nível máximo atingido.")

        st.markdown("---")

    st.subheader("💰 Comissão Total")
    st.success(f"Total de comissão no mês: R$ {total_comissao:.2f}")

    st.subheader("📈 Relatório de Melhoria")

    if relatorio_melhoria:
        for item in relatorio_melhoria:
            st.markdown(item)
    else:
        st.success("Todas as categorias atingiram o nível máximo.")

    st.subheader("📋 Serviços Discriminados Individualmente")
    st.dataframe(servicos_individuais, use_container_width=True)

    # EXPORTAR PDF
    if st.button("Exportar Relatório em PDF"):

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=3*inch, height=1*inch))
            elements.append(Spacer(1, 0.3 * inch))

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
