import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from datetime import datetime

st.set_page_config(page_title="Calculadora de Performance – Tosador", layout="wide")

st.title("🐾 Calculadora de Performance – Tosador")

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
nome_profissional = st.text_input("Nome do Profissional")

META_CONFIG = {
    "BANHO": {"base": 129, "meta": 130, "super": 176, "perc": [0.03, 0.04, 0.05]},
    "TOSA HIGIENICA": {"base": 19, "meta": 20, "super": 40, "perc": [0.10, 0.15, 0.20]},
    "TOSA MAQUINA": {"base": 14, "meta": 15, "super": 30, "perc": [0.10, 0.15, 0.20]},
    "TOSA TESOURA": {"base": 14, "meta": 15, "super": 30, "perc": [0.15, 0.20, 0.25]},
    "TRATAMENTOS": {"base": 14, "meta": 15, "super": 30, "perc": [0.15, 0.20, 0.25]},
}

TRATAMENTOS_LISTA = [
    "REMOCAO DE SUBPELO",
    "HIDRATACAO",
    "CORTE DE UNHAS",
    "HIGIENE BUCAL",
    "DESEMBARACO LEVE",
    "DESEMBARACO MEDIO",
    "DESEMBARACO PESADO",
]

def classificar_servico(servico):
    servico = servico.upper().strip()
    if "BANHO" in servico:
        return "BANHO"
    if "HIGIENICA" in servico:
        return "TOSA HIGIENICA"
    if "MAQUINA" in servico:
        return "TOSA MAQUINA"
    if "TESOURA" in servico:
        return "TOSA TESOURA"
    for t in TRATAMENTOS_LISTA:
        if t in servico:
            return "TRATAMENTOS"
    return None

def calcular_percentual(qtd, config):
    if qtd >= config["super"]:
        return config["perc"][2]
    elif qtd >= config["meta"]:
        return config["perc"][1]
    else:
        return config["perc"][0]

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        st.error("A planilha precisa conter as colunas SERVICO e VALOR.")
    else:
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
            servicos = str(row["SERVICO"]).upper().split("+")
            valor = row["VALOR"]
            for s in servicos:
                categoria = classificar_servico(s.strip())
                if categoria:
                    registros.append({"CATEGORIA": categoria, "VALOR": valor})

        df_final = pd.DataFrame(registros)

        resumo = df_final.groupby("CATEGORIA").agg(
            QUANTIDADE=("VALOR", "count"),
            FATURAMENTO=("VALOR", "sum")
        ).reset_index()

        resultados = []

        for _, row in resumo.iterrows():
            categoria = row["CATEGORIA"]
            qtd = row["QUANTIDADE"]
            faturamento = row["FATURAMENTO"]

            config = META_CONFIG[categoria]
            perc = calcular_percentual(qtd, config)
            comissao = faturamento * perc

            resultados.append([
                categoria,
                qtd,
                f"R$ {faturamento:.2f}",
                f"{int(perc*100)}%",
                f"R$ {comissao:.2f}"
            ])

        total_comissao = sum(
            float(r[4].replace("R$ ", "")) for r in resultados
        )

        st.subheader("📊 Resultado")
        st.table(resultados)
        st.subheader(f"💰 Comissão Total: R$ {total_comissao:.2f}")

        if st.button("📄 Gerar PDF"):

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            doc = SimpleDocTemplate(temp_file.name, pagesize=pagesizes.A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Comissão", styles["Heading1"]))
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(Paragraph(f"Profissional: {nome_profissional}", styles["Normal"]))
            elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            table_data = [["Categoria", "Qtde", "Faturamento", "%", "Comissão"]]
            table_data += resultados

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph(f"Comissão Total: R$ {total_comissao:.2f}", styles["Heading2"]))

            doc.build(elements)

            with open(temp_file.name, "rb") as f:
                st.download_button(
                    label="📥 Baixar PDF",
                    data=f,
                    file_name="relatorio_comissao.pdf",
                    mime="application/pdf"
                )
