import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(layout="wide")

# =========================
# CSS moderno
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: 'Arial', sans-serif; }
.kpi {background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;}
.card {background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 15px;}
.stDataFrame div.row_heading, .stDataFrame div.blank {background-color: #1B75BC !important; color: white !important;}
</style>
""", unsafe_allow_html=True)

# =========================
# Logo
# =========================
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)

st.title("Relatório de Comissão - Pet24🕒7")

# =========================
# Inputs
# =========================
col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

uploaded_file = st.file_uploader("Envie a planilha CSV", type=["csv"])

# =========================
# CONFIGURAÇÃO DE METAS
# =========================
META_CONFIG = {
    "BANHO": {"bronze":150,"prata":180,"ouro":200,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
    "TOSA HIGIENICA": {"bronze":80,"prata":100,"ouro":120,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
    "TOSA MAQUINA": {"bronze":60,"prata":80,"ouro":100,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
    "TOSA TESOURA": {"bronze":40,"prata":55,"ouro":70,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
    "TRATAMENTOS": {"bronze":40,"prata":55,"ouro":70,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
}

# =========================
# MAPA DE SERVIÇOS
# =========================
SERVICE_MAP = {
    "BANHO": ["Banho", "Banho + Hidratação", "Banho + Tosa Higiênica"],
    "TOSA HIGIENICA": ["Tosa Higiênica", "Tosa de Acabamento"],
    "TOSA MAQUINA": ["Tosa à Máquina", "Tosa à Máquina (sb)"],
    "TOSA TESOURA": ["Tosa à Tesoura", "Tosa à Tesoura (sb)", "Tosa à Tesoura Gato"],
    "TRATAMENTOS": [
        "Hidratação",
        "Remoção de Subpelos",
        "Higiene Bucal",
        "Corte de Unhas",
        "Desembaraço Leve (30min)",
        "Desembaraço Médio (1h)",
        "Desembaraço Pesado (2h)",
        "Corte de Unhas Gato"
    ]
}

# =========================
# Processamento
# =========================
if uploaded_file and funcionario and mes_referencia:
    try:
        df = pd.read_csv(uploaded_file, engine="python")
        df = df[df["SERVICO"].notna() & (df["SERVICO"].str.strip() != "")]
        df["VALOR"] = df["VALOR"].astype(str).str.replace("R$", "").str.replace(".", "").str.replace(",", ".").astype(float)
        df["SERVICO"] = df["SERVICO"].str.strip()

        resultados = []
        total_comissao = 0
        total_faturamento = 0

        for cat, metas in META_CONFIG.items():
            termos = SERVICE_MAP[cat]
            filtro = df["SERVICO"].isin(termos)
            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # Percentual aplicado conforme meta
            if qtd >= metas["ouro"]:
                pct = metas["percent_ouro"]
            elif qtd >= metas["prata"]:
                pct = metas["percent_prata"]
            elif qtd >= metas["bronze"]:
                pct = metas["percent_bronze"]
            else:
                pct = 0.03

            comissao = faturamento * pct
            total_comissao += comissao
            total_faturamento += faturamento

            resultados.append({
                "Serviço": cat,
                "Quantidade": qtd,
                "% Aplicada": f"{pct*100:.0f}%",
                "Comissão (R$)": comissao
            })

        # =========================
        # KPI
        # =========================
        st.markdown(f"<div class='kpi'><h2>{funcionario}</h2><h4>{mes_referencia}</h4><h1>R$ {total_comissao:,.2f}</h1><p>Comissão Total</p></div>", unsafe_allow_html=True)

        # =========================
        # Cards modernos por serviço
        # =========================
        st.subheader("Resumo por Serviço")
        for item in resultados:
            st.markdown(f"<div class='card'><h3>{item['Serviço']}</h3><p>Quantidade: {item['Quantidade']}<br>% Aplicada: {item['% Aplicada']}<br>Comissão: R$ {item['Comissão (R$)']:.2f}</p></div>", unsafe_allow_html=True)

        # =========================
        # PDF final
        # =========================
        class PDF(FPDF):
            def header(self):
                if os.path.exists("logo.png"):
                    self.image("logo.png", 10, 8, 50)
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, f'Relatório de Comissão - {funcionario}', ln=True, align='C')
                self.set_font('Arial', '', 12)
                self.cell(0, 8, f'Mês de Referência: {mes_referencia}', ln=True, align='C')
                self.ln(10)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", '', 12)
        pdf.cell(50,10,"Serviço",1)
        pdf.cell(30,10,"Qtd",1)
        pdf.cell(30,10,"% Aplicada",1)
        pdf.cell(40,10,"Comissão (R$)",1)
        pdf.ln()

        for item in resultados:
            pdf.cell(50,10,item["Serviço"],1)
            pdf.cell(30,10,str(item["Quantidade"]),1)
            pdf.cell(30,10,item["% Aplicada"],1)
            pdf.cell(40,10,f'{item["Comissão (R$)"]:.2f}',1)
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial",'B',12)
        pdf.cell(0,10,f"Faturamento Total: R$ {total_faturamento:.2f}",ln=True)
        pdf.cell(0,10,f"Comissão Total: R$ {total_comissao:.2f}",ln=True)

        output = BytesIO()
        pdf.output(output)
        st.download_button("📥 Baixar Relatório em PDF", output.getvalue(), f"Relatorio_{funcionario}.pdf", "application/pdf")

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")

else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
