import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# =========================
# ESTILO PREMIUM CORPORATIVO
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; }

.logo-center {
    display: flex;
    justify-content: center;
    margin-top: 15px;
}

.title-center {
    text-align: center;
    font-size: 34px;
    font-weight: 600;
    margin-bottom: 25px;
}

.kpi {
    background: linear-gradient(135deg, #0B0F6D, #1B75BC);
    color: white;
    padding: 50px;
    border-radius: 25px;
    text-align: center;
    box-shadow: 0 20px 50px rgba(0,0,0,0.25);
    margin-bottom: 40px;
}

.medal-card {
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: white;
    font-weight: 500;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

.bronze { background: linear-gradient(135deg, #8C6239, #B08D57); }
.prata { background: linear-gradient(135deg, #8E9EAB, #BDC3C7); }
.ouro { background: linear-gradient(135deg, #C6A700, #FFD700); }

.indicador-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.10);
    margin-bottom: 25px;
}

.progress-bar {
    height: 14px;
    background-color: #E6E6E6;
    border-radius: 10px;
    margin-top: 8px;
}

.progress-fill {
    height: 14px;
    border-radius: 10px;
    background: linear-gradient(90deg, #1B75BC, #0B0F6D);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-center">', unsafe_allow_html=True)
    st.image("logo.png", width=360)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="title-center">Dashboard Executivo de Comissões</div>', unsafe_allow_html=True)

# =========================
# CAMPOS
# =========================
col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

st.divider()

# =========================
# METAS
# =========================
META_CONFIG = {
    "BANHO": {"bronze": 150, "prata": 180, "ouro": 200},
    "TOSA HIGIENICA": {"bronze": 80, "prata": 100, "ouro": 120},
    "TOSA MAQUINA": {"bronze": 60, "prata": 80, "ouro": 100},
    "TOSA TESOURA": {"bronze": 40, "prata": 55, "ouro": 70},
    "TRATAMENTOS": {"bronze": 40, "prata": 55, "ouro": 70},
}

uploaded_file = st.file_uploader("Envie a planilha CSV extraida do Tecpet", type=["csv"])

if uploaded_file and funcionario and mes_referencia:

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

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

        total_comissao = 0
        resultados = []

        for categoria, metas in META_CONFIG.items():

            filtro = df["SERVICO"].str.contains(categoria)
            qtd = filtro.sum()
            fat = df.loc[filtro, "VALOR"].sum()

            if qtd >= metas["ouro"]:
                pct = 0.10
                nivel = "OURO"
                faltam = 0
            elif qtd >= metas["prata"]:
                pct = 0.07
                nivel = "PRATA"
                faltam = metas["ouro"] - qtd
            elif qtd >= metas["bronze"]:
                pct = 0.05
                nivel = "BRONZE"
                faltam = metas["prata"] - qtd
            else:
                pct = 0.03
                nivel = "INICIAL"
                faltam = metas["bronze"] - qtd

            comissao = fat * pct
            total_comissao += comissao
            progresso = min((qtd / metas["ouro"]) * 100, 100)

            resultados.append({
                "categoria": categoria,
                "qtd": qtd,
                "fat": fat,
                "pct": pct,
                "nivel": nivel,
                "faltam": faltam,
                "progresso": progresso,
                "metas": metas
            })

        # KPI PRINCIPAL
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
            <p>Total de Comissão do Período</p>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2])

        # =========================
        # METAS VERTICAIS
        # =========================
        with col_left:
            st.subheader("Metas por Categoria")

            for cat, metas in META_CONFIG.items():
                st.markdown(f"### {cat}")
                st.markdown(f'<div class="medal-card bronze">🥉 Bronze: {metas["bronze"]} serviços</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="medal-card prata">🥈 Prata: {metas["prata"]} serviços</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="medal-card ouro">🥇 Ouro: {metas["ouro"]} serviços</div>', unsafe_allow_html=True)
                st.markdown("---")

        # =========================
        # INDICADORES
        # =========================
        with col_right:
            st.subheader("Indicadores de Performance")

            for item in resultados:

                st.markdown('<div class="indicador-card">', unsafe_allow_html=True)

                st.markdown(f"### {item['categoria']}")
                st.markdown(f"Serviços realizados: **{item['qtd']}**")
                st.markdown(f"Nível atual: **{item['nivel']}**")
                st.markdown(f"Comissão aplicada: **{item['pct']*100:.0f}%**")
                st.markdown(f"Comissão gerada: **R$ {item['fat'] * item['pct']:,.2f}**")

                if item["faltam"] > 0:
                    st.markdown(f"Faltam **{item['faltam']} serviços** para próxima meta")
                else:
                    st.markdown("Meta máxima atingida")

                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{item['progresso']}%;"></div>
                </div>
                <small>{item['progresso']:.1f}% da meta Ouro</small>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
