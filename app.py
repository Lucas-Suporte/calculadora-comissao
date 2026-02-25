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
    height: 20px;
    background-color: #E6E6E6;
    border-radius: 6px;
    margin-top: 4px;
    position: relative;
}

.progress-fill {
    height: 20px;
    border-radius: 6px;
    background: linear-gradient(90deg, #1B75BC, #0B0F6D);
    text-align: right;
    padding-right: 5px;
    color: white;
    font-weight: bold;
    line-height: 20px;
}
</style>
""", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=280)

st.title("Relatório Oficial de Comissão")

# =========================
# INPUTS
# =========================
col1, col2 = st.columns(2)
with col1:
    funcionario = st.text_input("Nome do Funcionário")
with col2:
    mes_referencia = st.text_input("Mês de Referência")

st.divider()

uploaded_file = st.file_uploader("Envie a planilha CSV extraída do Tecpet", type=["csv"])

if not uploaded_file:
    st.info("📄 Por favor, envie o CSV extraído do Tecpet para gerar o relatório.")
elif not funcionario or not mes_referencia:
    st.warning("⚠️ Preencha o nome do funcionário e o mês de referência antes de continuar.")
else:
    try:
        # =========================
        # LEITURA CSV
        # =========================
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

        # =========================
        # CONFIGURAÇÃO DE METAS
        # =========================
        META_CONFIG = {
            "BANHO": {"bronze":150,"prata":180,"ouro":200,"percent":0.05},
            "TOSA HIGIENICA": {"bronze":80,"prata":100,"ouro":120,"percent":0.07},
            "TOSA MAQUINA": {"bronze":60,"prata":80,"ouro":100,"percent":0.07},
            "TOSA TESOURA": {"bronze":40,"prata":55,"ouro":70,"percent":0.10},
            "TRATAMENTOS": {"bronze":40,"prata":55,"ouro":70,"percent":0.10},
        }

        total_comissao = 0
        total_faturamento = 0
        resultados = []

        # =========================
        # PROCESSAMENTO
        # =========================
        for categoria, metas in META_CONFIG.items():
            cat_norm = normalizar(categoria)
            if categoria == "TRATAMENTOS":
                filtro = df["SERVICO"].str.contains("HIDRAT|TRAT", regex=True)
            else:
                filtro = df["SERVICO"].str.contains(cat_norm, regex=False)

            qtd = filtro.sum()
            faturamento = df.loc[filtro, "VALOR"].sum()

            # Define nível e percentual aplicado
            if qtd >= metas["ouro"]:
                nivel = "OURO"
                pct = metas["percent"]
            elif qtd >= metas["prata"]:
                nivel = "PRATA"
                pct = metas["percent"]
            elif qtd >= metas["bronze"]:
                nivel = "BRONZE"
                pct = metas["percent"]
            else:
                nivel = "INICIAL"
                pct = 0.03

            comissao = faturamento * pct
            total_comissao += comissao
            total_faturamento += faturamento

            progresso = min(qtd / metas["ouro"], 1)  # usado para barra proporcional

            resultados.append({
                "Categoria": categoria,
                "Quantidade": qtd,
                "Meta Ouro": metas["ouro"],
                "Faturamento": faturamento,
                "Nível": nivel,
                "% Aplicado": f"{pct*100:.0f}%",
                "Comissão": comissao,
                "Progresso": progresso
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

        col_meta, col_rel = st.columns([0.25, 0.75])

        # =========================
        # METAS
        # =========================
        with col_meta:
            st.subheader("Metas por Categoria")
            for cat, metas in META_CONFIG.items():
                st.markdown(f"**{cat}**")
                st.markdown(f'<div class="meta-card bronze">🥉 Bronze: {metas["bronze"]} → 5%</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta-card prata">🥈 Prata: {metas["prata"]} → 7%</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta-card ouro">🥇 Ouro: {metas["ouro"]} → 10%</div>', unsafe_allow_html=True)
                st.markdown("---")

        # =========================
        # RELATÓRIO DETALHADO
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
        # DASHBOARD DE PROGRESSÃO
        # =========================
        st.subheader("Progressão das Metas (Quantidade Realizada)")

        for item in resultados:
            qtd_real = item["Quantidade"]
            meta = item["Meta Ouro"]
            st.markdown(f"### {item['Categoria']} ({qtd_real}/{meta})")
            cor = '#C6A700' if item['Nível']=='OURO' else '#BDC3C7' if item['Nível']=='PRATA' else '#B08D57' if item['Nível']=='BRONZE' else '#E6E6E6'
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{item['Progresso']*100}%; background:{cor}">{qtd_real}</div>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # DOWNLOAD RELATÓRIO
        # =========================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba resumo
            resumo_df = pd.DataFrame([{
                "Funcionário": funcionario,
                "Mês": mes_referencia,
                "Faturamento Total": total_faturamento,
                "Comissão Total": total_comissao
            }])
            resumo_df.to_excel(writer, index=False, sheet_name="Resumo")

            # Aba detalhado
            relatorio_df.to_excel(writer, index=False, sheet_name="Detalhado")

            # Aba dados brutos
            df.to_excel(writer, index=False, sheet_name="Dados Brutos")

        st.download_button(
            label="Baixar Relatório em Excel",
            data=output.getvalue(),
            file_name=f"Relatorio_Comissao_{funcionario}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
