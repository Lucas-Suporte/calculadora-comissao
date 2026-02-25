import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.platypus import HRFlowable
import os

st.set_page_config(layout="wide")

# =====================================
# ESTILO VISUAL
# =====================================
st.markdown("""
<style>
.logo-center {
    display: flex;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 10px;
}
.title-center {
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    margin-bottom: 30px;
}
.kpi {
    background: linear-gradient(135deg, #0B0F6D, #17B3A3);
    color: white;
    padding: 35px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    margin-bottom: 30px;
}
.card3d {
    background: linear-gradient(145deg, #ffffff, #e6e6e6);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 6px 6px 15px rgba(0,0,0,0.15),
                -6px -6px 15px rgba(255,255,255,0.7);
    margin-bottom: 20px;
}
.progress-bar {
    height: 10px;
    background-color: #ddd;
    border-radius: 10px;
    margin-top: 8px;
}
.progress-fill {
    height: 10px;
    border-radius: 10px;
    background: linear-gradient(90deg, #17B3A3, #0B0F6D);
}
</style>
""", unsafe_allow_html=True)

# =====================================
# LOGO CENTRALIZADA
# =====================================
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-center">', unsafe_allow_html=True)
    st.image("logo.png", width=320)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="title-center">📊 Calculadora de Comissão</div>', unsafe_allow_html=True)

# =====================================
# CAMPOS MANUAIS
# =====================================
col1, col2 = st.columns(2)

with col1:
    funcionario = st.text_input("Nome do Funcionário")

with col2:
    mes_referencia = st.text_input("Mês de Referência (Ex: Janeiro/2026)")

st.divider()

# =====================================
# CONFIG METAS
# =====================================
META_CONFIG = {
    "BANHO": {"meta_qtd": 150, "super_qtd": 200, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA HIGIENICA": {"meta_qtd": 80, "super_qtd": 120, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA MAQUINA": {"meta_qtd": 60, "super_qtd": 100, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA TESOURA": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TRATAMENTOS": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
}

uploaded_file = st.file_uploader("Envie a planilha em CSV", type=["csv"])

if uploaded_file and funcionario and mes_referencia:

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
        df.columns = df.columns.str.upper().str.strip()

        col_serv = [c for c in df.columns if "SERV" in c][0]
        col_valor = [c for c in df.columns if "VALOR" in c][0]

        df[col_serv] = df[col_serv].astype(str).str.upper()

        resumo = []
        total_comissao = 0

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
            total_comissao += comissao

            progresso = min((qtd / cfg["super_qtd"]) * 100, 100)

            resumo.append({
                "categoria": categoria,
                "qtd": qtd,
                "fat": fat,
                "pct": pct,
                "comissao": comissao,
                "nivel": nivel,
                "progresso": progresso
            })

        # =====================================
        # KPI PRINCIPAL
        # =====================================
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1.4])

        # =====================================
        # INDICADORES 3D LADO ESQUERDO
        # =====================================
        with col_left:
            st.subheader("Indicadores de Comissão")

            for item in resumo:
                st.markdown(f"""
                <div class="card3d">
                    <b>{item['categoria']}</b><br>
                    {item['pct']*100:.0f}% aplicada<br>
                    Comissão: <b>R$ {item['comissao']:,.2f}</b>

                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{item['progresso']}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # =====================================
        # TABELA LADO DIREITO
        # =====================================
        with col_right:
            st.subheader("Resumo Financeiro")

            tabela_df = pd.DataFrame([
                [
                    i["categoria"],
                    i["qtd"],
                    f"R$ {i['fat']:,.2f}",
                    f"{i['pct']*100:.0f}%",
                    f"R$ {i['comissao']:,.2f}",
                    i["nivel"]
                ]
                for i in resumo
            ], columns=["Categoria", "Qtd", "Faturamento", "% Comissão", "Comissão", "Nível"])

            st.dataframe(tabela_df, use_container_width=True)

        # =====================================
        # PDF
        # =====================================
        if st.button("📄 Gerar PDF"):

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=pagesizes.A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Comissão", styles["Title"]))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Funcionário: {funcionario}", styles["Normal"]))
            elements.append(Paragraph(f"Mês de Referência: {mes_referencia}", styles["Normal"]))
            elements.append(Paragraph(f"Comissão Total: R$ {total_comissao:,.2f}", styles["Normal"]))
            elements.append(Spacer(1, 20))
            elements.append(HRFlowable(width="100%"))
            elements.append(Spacer(1, 20))

            tabela_dados = [tabela_df.columns.tolist()] + tabela_df.values.tolist()
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

    except Exception:
        st.error("Erro ao ler o CSV. Verifique se contém colunas de Serviço e Valor.")
