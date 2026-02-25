import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

st.set_page_config(layout="wide")

# =========================
# CSS moderno
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: 'Arial', sans-serif; }
.card {padding: 15px; border-radius: 12px; margin: 5px; background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; text-align: center; font-size: 14px;}
.card h4 {margin-bottom: 8px; font-size: 16px;}
.card p {margin: 2px; font-size: 14px;}
.card .comissao {margin-top: 8px; font-weight: bold; font-size: 16px;}
input[type="text"] {border: 2px solid #0B0F6D !important; border-radius: 8px; padding: 8px; font-size: 16px;}
div.stFileUploader>div>div>button {background-color: #0B0F6D; color: white; border-radius: 8px; padding: 8px 20px; font-weight: bold; font-size: 14px;}
div.stFileUploader>div>div>button:hover {background-color: #1B75BC;}
.stDataFrame th {background-color: #0B0F6D !important; color: white !important; text-align: center;}
.stDataFrame td {text-align: center;}
</style>
""", unsafe_allow_html=True)

# =========================
# Logo centralizado - tamanho original
# =========================
if os.path.exists("logo.png"):
    st.markdown(
        f"<div style='text-align:center; margin-bottom:20px;'><img src='logo.png' style='max-width:100%; height:auto;'></div>",
        unsafe_allow_html=True
    )

# =========================
# Título principal
# =========================
st.markdown("<h1 style='text-align:center;'>Relatório de Comissão - Pet247</h1>", unsafe_allow_html=True)

# =========================
# Inputs em negrito
# =========================
st.markdown("<b>Nome do Funcionário</b>", unsafe_allow_html=True)
funcionario = st.text_input("", placeholder="Digite o nome do funcionário")

st.markdown("<b>Mês de Referência</b>", unsafe_allow_html=True)
mes_referencia = st.text_input("", placeholder="Digite o mês de referência")

st.markdown("<b>Envie a planilha CSV</b>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"])

# =========================
# Configuração de metas
# =========================
META_CONFIG = {
    "BANHO": {"base":3,"meta":4,"super":5,"bronze":150,"prata":180,"ouro":200},
    "TOSA HIGIENICA": {"base":10,"meta":15,"super":20,"bronze":80,"prata":100,"ouro":120},
    "TOSA MAQUINA": {"base":10,"meta":15,"super":20,"bronze":60,"prata":80,"ouro":100},
    "TOSA TESOURA": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
    "TRATAMENTOS": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
}

SERVICE_MAP = {
    "BANHO": ["Banho", "Banho + Hidratação", "Banho + Tosa Higiênica"],
    "TOSA HIGIENICA": ["Tosa Higiênica", "Tosa de Acabamento"],
    "TOSA MAQUINA": ["Tosa à Máquina", "Tosa à Máquina (sb)"],
    "TOSA TESOURA": ["Tosa à Tesoura", "Tosa à Tesoura (sb)", "Tosa à Tesoura Gato"],
    "TRATAMENTOS": ["Hidratação","Remoção de Subpelos","Higiene Bucal","Corte de Unhas",
                     "Desembaraço Leve (30min)","Desembaraço Médio (1h)","Desembaraço Pesado (2h)",
                     "Corte de Unhas Gato"]
}

# =========================
# Processamento CSV
# =========================
if uploaded_file and funcionario and mes_referencia:
    try:
        df = pd.read_csv(uploaded_file, engine="python")
        df = df[df["SERVICO"].notna() & (df["SERVICO"].str.strip() != "")]
        df["VALOR"] = (
            df["VALOR"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
        df["SERVICO"] = df["SERVICO"].str.strip()

        resultados = []
        total_comissao = 0
        total_faturamento = 0

        for cat, metas in META_CONFIG.items():
            termos = SERVICE_MAP[cat]
            filtro = df["SERVICO"].isin(termos)
            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()
            total_faturamento += faturamento

            # Definir meta alcançada e % aplicada
            if qtd >= metas["ouro"]:
                pct = metas["super"]/100
                nome_meta = "Super Meta"
                pct_text = f"{metas['super']}%"
            elif qtd >= metas["prata"]:
                pct = metas["meta"]/100
                nome_meta = "Meta"
                pct_text = f"{metas['meta']}%"
            elif qtd >= metas["bronze"]:
                pct = metas["base"]/100
                nome_meta = "Base"
                pct_text = f"{metas['base']}%"
            else:
                pct = metas["base"]/100
                nome_meta = "Base"
                pct_text = f"{metas['base']}%"

            comissao = faturamento * pct
            total_comissao += comissao

            resultados.append({
                "Serviço": cat,
                "Quantidade": qtd,
                "Meta Alcançada": nome_meta,
                "Porcentagem": pct_text,
                "Comissão": comissao
            })

        # =========================
        # Card centralizado com resumo
        # =========================
        st.markdown(f"""
        <div style='display:flex; justify-content:center; margin-bottom:20px;'>
            <div style='background: linear-gradient(135deg, #0B0F6D, #1B75BC); color:white; border-radius: 20px; padding: 30px; text-align:center; width:60%;'>
                <h2>{funcionario}</h2>
                <h4>{mes_referencia}</h4>
                <h1>R$ {total_comissao:,.2f}</h1>
                <p>Comissão Total</p>
                <h3>Faturamento Total: R$ {total_faturamento:,.2f}</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # Cards individuais lado a lado
        # =========================
        st.subheader("Resumo por Serviço")
        col1, col2, col3, col4, col5 = st.columns(5)
        card_columns = [col1, col2, col3, col4, col5]
        for i, item in enumerate(resultados):
            col = card_columns[i % 5]
            col.markdown(
                f"<div class='card'><h4>{item['Serviço']}</h4>"
                f"<p>Qtd: {item['Quantidade']}<br>Meta: {item['Meta Alcançada']} ({item['Porcentagem']})</p>"
                f"<p class='comissao'>R$ {item['Comissão']:.2f}</p></div>",
                unsafe_allow_html=True
            )

        # =========================
        # Opção de gerar PDF
        # =========================
        st.subheader("Gerar Relatório em PDF")
        if st.button("📄 Gerar PDF"):
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()

            # Logo
            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=80, w=50)

            pdf.set_font("Arial", "B", 16)
            pdf.ln(15)
            pdf.cell(0, 10, f"Relatório de Comissão - Pet247", 0, 1, "C")
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Funcionário: {funcionario}", 0, 1)
            pdf.cell(0, 8, f"Mês de Referência: {mes_referencia}", 0, 1)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 12)
            for item in resultados:
                pdf.set_fill_color(11, 15, 109)  # azul da marca
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 10, f"{item['Serviço']}", 0, 1, fill=True)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 8, f"Qtd: {item['Quantidade']}   |   Meta: {item['Meta Alcançada']} ({item['Porcentagem']})   |   Comissão: R$ {item['Comissão']:.2f}", 0, 1)
                pdf.ln(2)

            pdf_output = f"Relatorio_Comissao_{funcionario}.pdf"
            pdf.output(pdf_output)
            st.success(f"PDF gerado: {pdf_output}")

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")

else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
