import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

st.set_page_config(layout="wide")

# =========================
# CONFIGURAÇÃO DE METAS
# =========================
META_CONFIG = {
    "BANHO": {"meta_qtd": 150, "super_qtd": 200, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA HIGIENICA": {"meta_qtd": 80, "super_qtd": 120, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA MAQUINA": {"meta_qtd": 60, "super_qtd": 100, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA TESOURA": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TRATAMENTOS": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
}

# =========================
# TÍTULO
# =========================
st.title("📊 Calculadora de Comissão")

uploaded_file = st.file_uploader("Envie a planilha de vendas (.xlsx)", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # =========================
    # IDENTIFICAÇÕES AUTOMÁTICAS
    # =========================
    df["DATA"] = pd.to_datetime(df["DATA"])
    data_inicio = df["DATA"].min().strftime("%d/%m/%Y")
    data_fim = df["DATA"].max().strftime("%d/%m/%Y")

    funcionario = df["FUNCIONARIO"].iloc[0]

    # =========================
    # TRATAMENTO SERVIÇOS
    # =========================
    df["SERVICO"] = df["SERVICO"].str.upper()

    resumo = []

    for categoria in META_CONFIG.keys():
        filtro = df["SERVICO"].str.contains(categoria)
        qtd = filtro.sum()
        fat = df.loc[filtro, "VALOR"].sum()

        cfg = META_CONFIG[categoria]

        if qtd >= cfg["super_qtd"]:
            pct = cfg["super_pct"]
        elif qtd >= cfg["meta_qtd"]:
            pct = cfg["meta_pct"]
        else:
            pct = cfg["base_pct"]

        comissao = fat * pct

        resumo.append([
            categoria,
            qtd,
            fat,
            pct,
            comissao
        ])

    resumo_df = pd.DataFrame(resumo, columns=[
        "Categoria",
        "Quantidade",
        "Faturamento",
        "% Comissão",
        "Comissão"
    ])

    total_comissao = resumo_df["Comissão"].sum()

    # =========================
    # DASHBOARD
    # =========================
    st.subheader("Resumo Geral")
    st.markdown(f"""
    **Funcionário:** {funcionario}  
    **Período:** {data_inicio} até {data_fim}  
    **Comissão Total:** R$ {total_comissao:,.2f}
    """)

    st.dataframe(resumo_df.style.format({
        "Faturamento": "R$ {:,.2f}",
        "% Comissão": "{:.0%}",
        "Comissão": "R$ {:,.2f}"
    }), use_container_width=True)

    # =========================
    # GERAR PDF
    # =========================
    if st.button("📄 Gerar Relatório PDF"):

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
        elements = []

        styles = getSampleStyleSheet()

        elements.append(Paragraph("<b>Relatório de Comissão</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Funcionário: {funcionario}", styles["Normal"]))
        elements.append(Paragraph(f"Período: {data_inicio} até {data_fim}", styles["Normal"]))
        elements.append(Paragraph(f"Comissão Total: R$ {total_comissao:,.2f}", styles["Normal"]))

        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%"))
        elements.append(Spacer(1, 20))

        tabela_dados = [resumo_df.columns.tolist()] + resumo_df.values.tolist()

        tabela = Table(tabela_dados)
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT")
        ]))

        elements.append(tabela)

        doc.build(elements)

        st.download_button(
            "⬇️ Baixar PDF",
            buffer.getvalue(),
            file_name="relatorio_comissao.pdf",
            mime="application/pdf"
        )
