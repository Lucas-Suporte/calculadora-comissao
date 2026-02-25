import streamlit as st
import pandas as pd
import unicodedata
from io import BytesIO
from fpdf import FPDF
import os

st.set_page_config(layout="wide")

# =========================
# FUNÇÃO PARA NORMALIZAR TEXTO
# =========================
def normalizar(texto):
    texto = str(texto).upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip()

# =========================
# ESTILO MODERNO
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: 'Arial', sans-serif; }
.kpi {background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;}
.table-container {background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
h2, h3 {color: #0B0F6D;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO E TÍTULO
# =========================
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)

st.title("Relatório de Comissão - Pet24🕒7")

# =========================
# INPUTS
# =========================
col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

uploaded_file = st.file_uploader("Envie a planilha CSV extraída do Tecpet", type=["csv"])

# =========================
# PROCESSAMENTO CSV
# =========================
if uploaded_file and funcionario and mes_referencia:
    try:
        df = pd.read_csv(uploaded_file, engine="python")
        # remover serviços vazios
        df = df[df["SERVICO"].notna() & (df["SERVICO"].str.strip() != "")]
        # tratar valores
        df["VALOR"] = (
            df["VALOR"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
        df["SERVICO"] = df["SERVICO"].apply(normalizar)

        # =========================
        # METAS COM PERCENTUAIS POR NÍVEL
        # =========================
        META_CONFIG = {
            "BANHO": {"bronze":150,"prata":180,"ouro":200,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
            "TOSA HIGIENICA": {"bronze":80,"prata":100,"ouro":120,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
            "TOSA MAQUINA": {"bronze":60,"prata":80,"ouro":100,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
            "TOSA TESOURA": {"bronze":40,"prata":55,"ouro":70,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
            "TRATAMENTOS": {"bronze":40,"prata":55,"ouro":70,"percent_bronze":0.05,"percent_prata":0.07,"percent_ouro":0.10},
        }

        resultados = []
        total_faturamento = 0
        total_comissao = 0

        for categoria, metas in META_CONFIG.items():
            cat_norm = normalizar(categoria)
            # filtro correto para cada serviço
            if categoria == "TRATAMENTOS":
                filtro = df["SERVICO"].str.contains("HIDRAT|TRAT", regex=True)
            else:
                filtro = df["SERVICO"].str.contains(cat_norm, regex=True)

            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # definir percentual aplicado
            if qtd >= metas["ouro"]:
                pct = metas["percent_ouro"]
            elif qtd >= metas["prata"]:
                pct = metas["percent_prata"]
            elif qtd >= metas["bronze"]:
                pct = metas["percent_bronze"]
            else:
                pct = 0.03  # percentual inicial

            comissao = faturamento * pct
            total_comissao += comissao
            total_faturamento += faturamento

            resultados.append({
                "Serviço": categoria,
                "Quantidade": qtd,
                "% Aplicada": f"{pct*100:.0f}%",
                "Comissão (R$)": comissao
            })

        # =========================
        # KPI
        # =========================
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
            <p>Comissão Total</p>
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # TABELA DE RESULTADOS
        # =========================
        st.subheader("Resumo por Serviço")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)

        # =========================
        # GERAR PDF
        # =========================
        class PDF(FPDF):
            def header(self):
                if os.path.exists("logo.png"):
                    temp_logo = "logo_temp.png"
                    with open(temp_logo, "wb") as f:
                        f.write(open("logo.png", "rb").read())
                    self.image(temp_logo, 10, 8, 50)
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, f'Relatório de Comissão - {funcionario}', ln=True, align='C')
                self.set_font('Arial', '', 12)
                self.cell(0, 8, f'Mês de Referência: {mes_referencia}', ln=True, align='C')
                self.ln(10)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", '', 12)

        pdf.cell(50, 10, "Serviço", 1)
        pdf.cell(30, 10, "Qtd", 1)
        pdf.cell(30, 10, "% Aplicada", 1)
        pdf.cell(40, 10, "Comissão (R$)", 1)
        pdf.ln()

        for item in resultados:
            pdf.cell(50, 10, item["Serviço"], 1)
            pdf.cell(30, 10, str(item["Quantidade"]), 1)
            pdf.cell(30, 10, item["% Aplicada"], 1)
            pdf.cell(40, 10, f'{item["Comissão (R$)"]:.2f}', 1)
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Faturamento Total: R$ {total_faturamento:.2f}", ln=True)
        pdf.cell(0, 10, f"Comissão Total: R$ {total_comissao:.2f}", ln=True)

        output = BytesIO()
        pdf.output(output)

        st.download_button(
            label="📥 Baixar Relatório em PDF",
            data=output.getvalue(),
            file_name=f"Relatorio_Comissao_{funcionario}.pdf",
            mime="application/pdf"
        )
        st.info("💡 Abra o PDF no seu computador para imprimir ou salvar.")

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
