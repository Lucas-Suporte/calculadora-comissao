from fpdf import FPDF
import streamlit as st
import pandas as pd
import os
import unicodedata
from io import BytesIO

st.set_page_config(layout="wide")

# =========================
# FUNÇÃO NORMALIZAÇÃO TEXTO
# =========================
def normalizar(texto):
    texto = str(texto).upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto

# =========================
# INPUTS
# =========================
col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

uploaded_file = st.file_uploader("Envie a planilha CSV extraída do Tecpet", type=["csv"])

if uploaded_file and funcionario and mes_referencia:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
        # remover linhas com serviço vazio
        df = df[df["SERVICO"].notna() & (df["SERVICO"].str.strip() != "")]
        df["VALOR"] = (
            df["VALOR"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
        df["SERVICO"] = df["SERVICO"].apply(normalizar)

        META_CONFIG = {
            "BANHO": {"bronze":150,"prata":180,"ouro":200,"percent":0.05},
            "TOSA HIGIENICA": {"bronze":80,"prata":100,"ouro":120,"percent":0.07},
            "TOSA MAQUINA": {"bronze":60,"prata":80,"ouro":100,"percent":0.07},
            "TOSA TESOURA": {"bronze":40,"prata":55,"ouro":70,"percent":0.10},
            "TRATAMENTOS": {"bronze":40,"prata":55,"ouro":70,"percent":0.10},
        }

        resultados = []
        total_faturamento = 0
        total_comissao = 0

        for categoria, metas in META_CONFIG.items():
            cat_norm = normalizar(categoria)
            if categoria == "TRATAMENTOS":
                filtro = df["SERVICO"].str.contains("HIDRAT|TRAT", regex=True)
            else:
                filtro = df["SERVICO"].str.contains(cat_norm, regex=False)

            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # definir % aplicada
            if qtd >= metas["ouro"]:
                pct = metas["percent"]
            elif qtd >= metas["prata"]:
                pct = metas["percent"]
            elif qtd >= metas["bronze"]:
                pct = metas["percent"]
            else:
                pct = 0.03

            comissao = faturamento * pct
            total_comissao += comissao
            total_faturamento += faturamento

            resultados.append({
                "Serviço": categoria,
                "Quantidade": qtd,
                "Meta Ouro": metas["ouro"],
                "% Aplicada": f"{pct*100:.0f}%",
                "Comissão": comissao
            })

        # =========================
        # GERAR PDF
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

        # tabela de serviços
        pdf.cell(50, 10, "Serviço", 1)
        pdf.cell(30, 10, "Qtd", 1)
        pdf.cell(30, 10, "Meta Ouro", 1)
        pdf.cell(30, 10, "% Aplicada", 1)
        pdf.cell(40, 10, "Comissão (R$)", 1)
        pdf.ln()

        for item in resultados:
            pdf.cell(50, 10, item["Serviço"], 1)
            pdf.cell(30, 10, str(item["Quantidade"]), 1)
            pdf.cell(30, 10, str(item["Meta Ouro"]), 1)
            pdf.cell(30, 10, item["% Aplicada"], 1)
            pdf.cell(40, 10, f'{item["Comissão"]:.2f}', 1)
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Faturamento Total: R$ {total_faturamento:.2f}", ln=True)
        pdf.cell(0, 10, f"Comissão Total: R$ {total_comissao:.2f}", ln=True)

        output = BytesIO()
        pdf.output(output)
        st.download_button(
            label="Baixar Relatório em PDF",
            data=output.getvalue(),
            file_name=f"Relatorio_Comissao_{funcionario}.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
