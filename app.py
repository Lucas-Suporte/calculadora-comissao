import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# =========================
# ESTILO PROFISSIONAL
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; }

.kpi {
    background: linear-gradient(135deg, #0B0F6D, #1B75BC);
    color: white;
    padding: 40px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.20);
    margin-bottom: 30px;
}

.meta-box {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    font-size: 14px;
}

.progress-bar {
    height: 10px;
    background-color: #E6E6E6;
    border-radius: 6px;
    margin-top: 5px;
}

.progress-fill {
    height: 10px;
    border-radius: 6px;
    background: linear-gradient(90deg, #1B75BC, #0B0F6D);
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
if os.path.exists("logo.png"):
    st.image("logo.png", width=300)

st.title("Relatório Oficial de Comissão")

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
# CONFIG METAS E CATEGORIAS
# =========================
CATEGORIAS = {
    "BANHO": ["BANHO"],
    "TOSA HIGIENICA": ["HIGIENICA"],
    "TOSA MAQUINA": ["MAQUINA"],
    "TOSA TESOURA": ["TESOURA"],
    "TRATAMENTOS": ["HIDRAT", "TRAT"]
}

META_CONFIG = {
    "BANHO": 200,
    "TOSA HIGIENICA": 120,
    "TOSA MAQUINA": 100,
    "TOSA TESOURA": 70,
    "TRATAMENTOS": 70
}

uploaded_file = st.file_uploader("Envie a planilha CSV extraida do Tecpet", type=["csv"])

if uploaded_file and funcionario and mes_referencia:

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

        # Limpeza segura
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

        resultados = []
        total_comissao = 0
        total_faturamento = 0

        for categoria, palavras in CATEGORIAS.items():

            filtro = df["SERVICO"].apply(
                lambda x: any(p in x for p in palavras)
            )

            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # comissão fixa exemplo 5%
            pct = 0.05
            comissao = faturamento * pct

            total_comissao += comissao
            total_faturamento += faturamento

            progresso = min((qtd / META_CONFIG[categoria]) * 100, 100)

            resultados.append({
                "Categoria": categoria,
                "Quantidade": qtd,
                "Faturamento": faturamento,
                "Comissão": comissao,
                "Meta": META_CONFIG[categoria],
                "Progresso": progresso
            })

        # =========================
        # KPI CENTRAL
        # =========================
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
            <p>Total de Comissão</p>
        </div>
        """, unsafe_allow_html=True)

        # =========================
        # LAYOUT PRINCIPAL
        # =========================
        col_meta, col_relatorio = st.columns([0.2, 0.8])

        # =========================
        # METAS (20%)
        # =========================
        with col_meta:
            st.subheader("Metas")

            for categoria in META_CONFIG:
                st.markdown(f"""
                <div class="meta-box">
                    <b>{categoria}</b><br>
                    Meta Ouro: {META_CONFIG[categoria]} serviços
                </div>
                """, unsafe_allow_html=True)

        # =========================
        # RELATÓRIO GERAL
        # =========================
        with col_relatorio:
            st.subheader("Relatório Geral de Serviços")

            relatorio_df = pd.DataFrame(resultados)[
                ["Categoria", "Quantidade", "Faturamento", "Comissão"]
            ]

            st.dataframe(relatorio_df, use_container_width=True)

            st.markdown(f"""
            **Faturamento Total:** R$ {total_faturamento:,.2f}  
            **Comissão Total:** R$ {total_comissao:,.2f}
            """)

        st.divider()

        # =========================
        # DASHBOARD DE PROGRESSÃO
        # =========================
        st.subheader("Progressão das Metas")

        for item in resultados:
            st.markdown(f"### {item['Categoria']}")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{item['Progresso']}%;"></div>
            </div>
            <small>{item['Progresso']:.1f}% da Meta</small>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
