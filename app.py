import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(layout="wide")

# =========================
# ESTILO CORPORATIVO PREMIUM
# =========================
st.markdown("""
<style>
.logo-center {
    display: flex;
    justify-content: center;
    margin-top: 15px;
    margin-bottom: 10px;
}
.title-center {
    text-align: center;
    font-size: 34px;
    font-weight: 600;
    margin-bottom: 30px;
}
.kpi {
    background: linear-gradient(135deg, #0B0F6D, #17B3A3);
    color: white;
    padding: 45px;
    border-radius: 24px;
    text-align: center;
    box-shadow: 0 18px 40px rgba(0,0,0,0.25);
    margin-bottom: 35px;
}
.card-premium {
    background: #ffffff;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    margin-bottom: 22px;
}
.progress-bar {
    height: 10px;
    background-color: #E6E6E6;
    border-radius: 10px;
    margin-top: 8px;
}
.progress-fill {
    height: 10px;
    border-radius: 10px;
    background: linear-gradient(90deg, #17B3A3, #0B0F6D);
}
.meta-table {
    background: #ffffff;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.10);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-center">', unsafe_allow_html=True)
    st.image("logo.png", width=340)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="title-center">Calculadora Corporativa de Comissão</div>', unsafe_allow_html=True)

# =========================
# CAMPOS
# =========================
col1, col2 = st.columns(2)

with col1:
    funcionario = st.text_input("Nome do Funcionário")

with col2:
    mes_referencia = st.text_input("Mês de Referência (Ex: Janeiro/2026)")

st.divider()

# =========================
# CONFIG METAS
# =========================
META_CONFIG = {
    "BANHO": {"meta_qtd": 150, "super_qtd": 200, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA HIGIENICA": {"meta_qtd": 80, "super_qtd": 120, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA MAQUINA": {"meta_qtd": 60, "super_qtd": 100, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TOSA TESOURA": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
    "TRATAMENTOS": {"meta_qtd": 40, "super_qtd": 70, "base_pct": 0.05, "meta_pct": 0.07, "super_pct": 0.10},
}

uploaded_file = st.file_uploader("Envie a planilha CSV extraida do Tecpet", type=["csv"])

if uploaded_file and funcionario and mes_referencia:

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

        if "SERVICO" not in df.columns or "VALOR" not in df.columns:
            st.error("CSV fora do padrão Tecpet.")
            st.stop()

        # Conversão segura de VALOR
        df["VALOR"] = (
            df["VALOR"]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)
        df["SERVICO"] = df["SERVICO"].astype(str).str.upper()

        resumo = []
        total_comissao = 0

        for categoria, cfg in META_CONFIG.items():

            filtro = df["SERVICO"].str.contains(categoria)
            qtd = filtro.sum()
            fat = df.loc[filtro, "VALOR"].sum()

            if qtd >= cfg["super_qtd"]:
                pct = cfg["super_pct"]
                proxima_meta = 0
            elif qtd >= cfg["meta_qtd"]:
                pct = cfg["meta_pct"]
                proxima_meta = cfg["super_qtd"] - qtd
            else:
                pct = cfg["base_pct"]
                proxima_meta = cfg["meta_qtd"] - qtd

            comissao = fat * pct
            total_comissao += comissao
            progresso = min((qtd / cfg["super_qtd"]) * 100, 100)

            resumo.append({
                "categoria": categoria,
                "qtd": qtd,
                "fat": fat,
                "pct": pct,
                "comissao": comissao,
                "progresso": progresso,
                "faltam": proxima_meta
            })

        # =========================
        # KPI CENTRAL
        # =========================
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1.6])

        # =========================
        # LADO ESQUERDO — TABELA BASE DE METAS
        # =========================
        with col_left:
            st.markdown('<div class="meta-table">', unsafe_allow_html=True)
            st.subheader("Tabela Base de Metas")

            base_df = pd.DataFrame([
                [
                    cat,
                    cfg["meta_qtd"],
                    cfg["super_qtd"],
                    f"{cfg['base_pct']*100:.0f}%",
                    f"{cfg['meta_pct']*100:.0f}%",
                    f"{cfg['super_pct']*100:.0f}%"
                ]
                for cat, cfg in META_CONFIG.items()
            ], columns=[
                "Categoria",
                "Meta",
                "Super Meta",
                "% Base",
                "% Meta",
                "% Super"
            ])

            st.dataframe(base_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # =========================
        # LADO DIREITO — INDICADORES PREMIUM
        # =========================
        with col_right:
            st.subheader("Indicadores de Performance")

            for item in resumo:
                faltam_texto = (
                    f"Faltam {item['faltam']} serviços para próxima meta"
                    if item["faltam"] > 0
                    else "Meta Máxima Atingida"
                )

                st.markdown(f"""
                <div class="card-premium">
                    <b>{item['categoria']}</b><br>
                    Comissão Aplicada: {item['pct']*100:.0f}%<br>
                    Comissão: <b>R$ {item['comissao']:,.2f}</b><br>
                    {faltam_texto}

                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{item['progresso']}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
