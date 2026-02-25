import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# =========================
# CSS moderno para cards e tabela
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: 'Arial', sans-serif; }
.kpi {background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;}
.card {padding: 15px; border-radius: 12px; margin: 5px; background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; text-align: center; font-size: 14px;}
.card h4 {margin-bottom: 8px; font-size: 16px;}
.card p {margin: 2px; font-size: 14px;}
.card .comissao {margin-top: 8px; font-weight: bold; font-size: 16px;}
.stDataFrame th {background-color: #0B0F6D !important; color: white !important;}
.stDataFrame td {text-align: center;}
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
# Configuração de metas e porcentagens
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

            # Determina nome da meta e porcentagem aplicada
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
            total_faturamento += faturamento

            resultados.append({
                "Serviço": cat,
                "Quantidade": qtd,
                "Meta Alcançada": nome_meta,
                "Porcentagem": pct_text,
                "Comissão": comissao
            })

        # =========================
        # KPI
        # =========================
        st.markdown(f"<div class='kpi'><h2>{funcionario}</h2><h4>{mes_referencia}</h4><h1>R$ {total_comissao:,.2f}</h1><p>Comissão Total</p></div>", unsafe_allow_html=True)

        # =========================
        # Cards lado a lado
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
        # Resumo Geral
        # =========================
        st.subheader("Resumo Geral")
        st.write(f"**Faturamento Total:** R$ {total_faturamento:,.2f}")
        st.write(f"**Comissão Total:** R$ {total_comissao:,.2f}")

        # =========================
        # Tabela de metas padrão
        # =========================
        st.subheader("Tabela de Metas Base")
        metas_df = pd.DataFrame({
            "Serviço": ["Banho", "Tosa Higiênica", "Tosa à Máquina", "Tosa à Tesoura", "Tratamentos"],
            "Base (Qtd)": [META_CONFIG[s]["bronze"] for s in META_CONFIG],
            "Base (%)": [f"{META_CONFIG[s]['base']}%" for s in META_CONFIG],
            "Meta (Qtd)": [META_CONFIG[s]["prata"] for s in META_CONFIG],
            "Meta (%)": [f"{META_CONFIG[s]['meta']}%" for s in META_CONFIG],
            "Super Meta (Qtd)": [META_CONFIG[s]["ouro"] for s in META_CONFIG],
            "Super Meta (%)": [f"{META_CONFIG[s]['super']}%" for s in META_CONFIG],
        })
        st.dataframe(metas_df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")

else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
