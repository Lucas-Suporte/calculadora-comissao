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
    margin-bottom: 30px;
}

.meta-card {
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    color: white;
    font-size: 13px;
}

.bronze { background: linear-gradient(135deg, #8C6239, #B08D57); }
.prata { background: linear-gradient(135deg, #8E9EAB, #BDC3C7); }
.ouro { background: linear-gradient(135deg, #C6A700, #FFD700); }

.progress-bar {
    height: 10px;
    background-color: #E6E6E6;
    border-radius: 6px;
    margin-top: 4px;
}

.progress-fill {
    height: 10px;
    border-radius: 6px;
    background: linear-gradient(90deg, #1B75BC, #0B0F6D);
}
</style>
""", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=280)

st.title("Relatório Oficial de Comissão")

col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

st.divider()

# =========================
# METAS E PORCENTAGENS
# =========================
META_CONFIG = {
    "BANHO": {"bronze":150,"prata":180,"ouro":200},
    "TOSA HIGIENICA": {"bronze":80,"prata":100,"ouro":120},
    "TOSA MAQUINA": {"bronze":60,"prata":80,"ouro":100},
    "TOSA TESOURA": {"bronze":40,"prata":55,"ouro":70},
    "TRATAMENTOS": {"bronze":40,"prata":55,"ouro":70},
}

PERCENTUAIS = {
    "INICIAL": 0.03,
    "BRONZE": 0.05,
    "PRATA": 0.07,
    "OURO": 0.10
}

uploaded_file = st.file_uploader("Envie a planilha CSV extraida do Tecpet", type=["csv"])

if uploaded_file and funcionario and mes_referencia:

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

        df["VALOR"] = (
            df["VALOR"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

        df["SERVICO"] = df["SERVICO"].apply(normalizar)

        total_comissao = 0
        total_faturamento = 0
        resultados = []

        for categoria, metas in META_CONFIG.items():

            cat_norm = normalizar(categoria)

            if categoria == "TRATAMENTOS":
                filtro = df["SERVICO"].str.contains("HIDRAT|TRAT", regex=True)
            else:
                filtro = df["SERVICO"].str.contains(cat_norm, regex=False)

            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # Define nível
            if qtd >= metas["ouro"]:
                nivel = "OURO"
            elif qtd >= metas["prata"]:
                nivel = "PRATA"
            elif qtd >= metas["bronze"]:
                nivel = "BRONZE"
            else:
                nivel = "INICIAL"

            pct = PERCENTUAIS[nivel]
            comissao = faturamento * pct

            total_comissao += comissao
            total_faturamento += faturamento

            progresso = min((qtd / metas["ouro"]) * 100, 100)

            resultados.append({
                "Categoria": categoria,
                "Quantidade": qtd,
                "Faturamento": faturamento,
                "Nível": nivel,
                "% Aplicado": f"{pct*100:.0f}%",
                "Comissão": comissao,
                "Progresso": progresso
            })

        # KPI
        st.markdown(f"""
        <div class="kpi">
            <h2>{funcionario}</h2>
            <h4>{mes_referencia}</h4>
            <h1>R$ {total_comissao:,.2f}</h1>
            <p>Comissão Total</p>
        </div>
        """, unsafe_allow_html=True)

        col_meta, col_rel = st.columns([0.2, 0.8])

        # =========================
        # METAS AGRUPADAS
        # =========================
        with col_meta:
            st.subheader("Metas")

            for cat, metas in META_CONFIG.items():
                st.markdown(f"**{cat}**")

                st.markdown(f'<div class="meta-card bronze">🥉 Bronze: {metas["bronze"]} → 5%</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta-card prata">🥈 Prata: {metas["prata"]} → 7%</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta-card ouro">🥇 Ouro: {metas["ouro"]} → 10%</div>', unsafe_allow_html=True)

                st.markdown("---")

        # =========================
        # RELATÓRIO COMPLETO
        # =========================
        with col_rel:
            st.subheader("Relatório Geral de Comissionamento")

            relatorio_df = pd.DataFrame(resultados)

            st.dataframe(relatorio_df, use_container_width=True)

            st.markdown(f"""
            **Faturamento Total:** R$ {total_faturamento:,.2f}  
            **Comissão Total:** R$ {total_comissao:,.2f}
            """)

        st.divider()

        # =========================
        # DASHBOARD PROGRESSÃO
        # =========================
        st.subheader("Progressão das Metas")

        for item in resultados:
            st.markdown(f"### {item['Categoria']}")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{item['Progresso']}%;"></div>
            </div>
            <small>{item['Progresso']:.1f}% da meta Ouro</small>
            """, unsafe_allow_html=True)

        # =========================
        # DOWNLOAD RELATÓRIO
        # =========================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            relatorio_df.to_excel(writer, index=False, sheet_name='Comissao')

        st.download_button(
            label="Baixar Relatório em Excel",
            data=output.getvalue(),
            file_name=f"Relatorio_Comissao_{funcionario}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
