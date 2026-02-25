import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# =========================
# CSS moderno para cards lado a lado
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: 'Arial', sans-serif; }
.kpi {background: linear-gradient(135deg, #0B0F6D, #1B75BC); color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;}
.card {padding: 12px; border-radius: 12px; margin: 5px; color: white; text-align: center; font-size: 14px;}
.banho {background: linear-gradient(135deg, #0B0F6D, #1B75BC);}
.tosa_higienica {background: linear-gradient(135deg, #C6A700, #FFD700);}
.tosa_maquina {background: linear-gradient(135deg, #7B1FA2, #9C27B0);}
.tosa_tesoura {background: linear-gradient(135deg, #FF5722, #FF7043);}
.tratamentos {background: linear-gradient(135deg, #4CAF50, #81C784);}
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
# CONFIGURAÇÃO DE METAS E PORCENTAGENS
# =========================
META_CONFIG = {
    "BANHO": {"base":3,"meta":4,"super":5,"bronze":150,"prata":180,"ouro":200},
    "TOSA HIGIENICA": {"base":10,"meta":15,"super":20,"bronze":80,"prata":100,"ouro":120},
    "TOSA MAQUINA": {"base":10,"meta":15,"super":20,"bronze":60,"prata":80,"ouro":100},
    "TOSA TESOURA": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
    "TRATAMENTOS": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
}

# =========================
# MAPA DE SERVIÇOS (nomes revisados)
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

        # Limpa e converte VALOR
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

            # Determina nome da meta atingida
            if qtd >= metas["ouro"]:
                pct = metas["super"]/100
                nome_meta = "Super Meta"
            elif qtd >= metas["prata"]:
                pct = metas["meta"]/100
                nome_meta = "Meta"
            elif qtd >= metas["bronze"]:
                pct = metas["base"]/100
                nome_meta = "Base"
            else:
                pct = metas["base"]/100
                nome_meta = "Base"

            comissao = faturamento * pct
            total_comissao += comissao
            total_faturamento += faturamento

            resultados.append({
                "Serviço": cat,
                "Quantidade": qtd,
                "Meta Alcançada": nome_meta,
                "Comissão (R$)": comissao
            })

        # =========================
        # KPI
        # =========================
        st.markdown(f"<div class='kpi'><h2>{funcionario}</h2><h4>{mes_referencia}</h4><h1>R$ {total_comissao:,.2f}</h1><p>Comissão Total</p></div>", unsafe_allow_html=True)

        # =========================
        # Cards menores lado a lado com cores
        # =========================
        st.subheader("Resumo por Serviço")
        col1, col2, col3, col4, col5 = st.columns(5)
        card_columns = [col1, col2, col3, col4, col5]
        color_classes = {
            "BANHO": "banho",
            "TOSA HIGIENICA": "tosa_higienica",
            "TOSA MAQUINA": "tosa_maquina",
            "TOSA TESOURA": "tosa_tesoura",
            "TRATAMENTOS": "tratamentos"
        }

        for i, item in enumerate(resultados):
            col = card_columns[i % 5]
            color = color_classes[item["Serviço"]]
            col.markdown(
                f"<div class='card {color}'><h4>{item['Serviço']}</h4><p>Qtd: {item['Quantidade']}<br>Meta: {item['Meta Alcançada']}</p></div>",
                unsafe_allow_html=True
            )

        # =========================
        # Comissões detalhadas ao final
        # =========================
        st.subheader("Comissões Aplicadas por Serviço")
        for item in resultados:
            st.write(f"{item['Serviço']}: R$ {item['Comissão (R$)']:.2f}")

        # =========================
        # Total
        # =========================
        st.subheader("Resumo Geral")
        st.write(f"**Faturamento Total:** R$ {total_faturamento:,.2f}")
        st.write(f"**Comissão Total:** R$ {total_comissao:,.2f}")

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")

else:
    st.info("📄 Preencha todos os campos e envie o CSV para gerar o relatório.")
