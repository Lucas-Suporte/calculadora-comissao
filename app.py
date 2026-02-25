import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.platypus import HRFlowable
from datetime import datetime
import os

st.set_page_config(layout="wide")

# ===============================
# ESTILO MODERNO
# ===============================
st.markdown("""
<style>
.kpi {
    background: linear-gradient(135deg, #0B0F6D, #17B3A3);
    color: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    margin-bottom: 30px;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    margin-bottom: 25px;
}
.logo-center {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOGO NO TOPO
# ===============================
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-center">', unsafe_allow_html=True)
    st.image("logo.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("📊 Calculadora de Comissão")

# ===============================
# CONFIG METAS
# ===============================
META_CONFIG = {
    "BANHO": {"meta_qtd": 150, "super_qtd": 200, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA HIGIENICA": {"meta_qtd": 80, "super_qtd": 120, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA MAQUINA": {"meta_qtd": 60, "super_qtd": 100, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA TESOURA": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TRATAMENTOS": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
}

uploaded_file = st.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])

if uploaded_file:

    try:
        df = pd.read_excel(uploaded_file)

        # Padronizar nomes de colunas
        df.columns = df.columns.str.upper().str.strip()

        # Mapear possíveis nomes
        col_data = [c for c in df.columns if "DATA" in c][0]
        col_func = [c for c in df.columns if "FUNC" in c][0]
        col_serv = [c for c in df.columns if "SERV" in c][0]
        col_valor = [c for c in df.columns if "VALOR" in c][0]

        df[col_data] = pd.to_datetime(df[col_data])

        data_inicio = df[col_data].min().strftime("%d/%m/%Y")
        data_fim = df[col_data].max().strftime("%d/%m/%Y")
        funcionario = df[col_func].iloc[0]

        df[col_serv] = df[col_serv].astype(str).str.upper()

        resumo = []

        for categoria in META_CONFIG.keys():

            filtro = df[col_serv].str.contains(categoria)
            qtd = filtro.sum()
            fat = df.loc[filtro, col_valor].sum()

            cfg = META_CONFIG[categoria]

            if qtd >= cfg["super_qtd"]:
                pct = cfg["super_pct"]
                nivel = "SUPER META"
            elif qtd >= cfg["meta_qtd"]:
                pct = cfg["meta_pct"]
                nivel = "META"
            else:
                pct = cfg["base_pct"]
                nivel = "BASE"

            comissao = fat * pct

            resumo.append([
                categoria,
                qtd,
                f"R$ {fat:,.2f}",
                f"{pct*100:.0f}%",
                f"R$ {comissao:,.2f}",
                nivel
            ])

        resumo_df = pd.DataFrame(resumo, columns=[
            "Categoria",
            "Qtd",
            "Faturamento",
            "% Aplicada",
            "Comissão",
            "Nível"
        ])

        total_comissao = sum(
            float(x.replace("R$ ", "").replace(",", "")) 
            for x in resumo_df["Comissão"]
        )

        # KPI
        st.markdown(f"""
        <div class="kpi">
            <h3>{funcionario}</h3>
            <h4>{data_inicio} até {data_fim}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.subheader("Resumo Detalhado")
            st.dataframe(resumo_df, use_container_width=True)

        with col2:
            st.subheader("Indicadores")
            for row in resumo:
                st.info(f"{row[0]} → {row[5]}")

        # ===============================
        # PDF
        # ===============================
        if st.button("📄 Gerar PDF"):

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Comissão", styles["Title"]))
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
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            elements.append(tabela)
            doc.build(elements)

            st.download_button(
                "⬇️ Baixar PDF",
                buffer.getvalue(),
                file_name="relatorio_comissao.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error("Erro ao ler a planilha. Verifique se ela contém colunas de Data, Funcionário, Serviço e Valor.")
