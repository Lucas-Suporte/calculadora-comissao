import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Performance – Tosador", layout="wide")

st.title("🐾 Calculadora de Performance – Tosador")

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])

# ----------------------------
# CONFIGURAÇÃO DE METAS FIXAS
# ----------------------------

META_CONFIG = {
    "BANHO": {"base": 129, "meta": 130, "super": 176, "perc": [0.03, 0.04, 0.05]},
    "TOSA HIGIENICA": {"base": 19, "meta": 20, "super": 40, "perc": [0.10, 0.15, 0.20]},
    "TOSA MAQUINA": {"base": 14, "meta": 15, "super": 30, "perc": [0.10, 0.15, 0.20]},
    "TOSA TESOURA": {"base": 14, "meta": 15, "super": 30, "perc": [0.15, 0.20, 0.25]},
    "TRATAMENTOS": {"base": 14, "meta": 15, "super": 30, "perc": [0.15, 0.20, 0.25]},
}

TRATAMENTOS_LISTA = [
    "REMOCAO DE SUBPELO",
    "HIDRATACAO",
    "CORTE DE UNHAS",
    "HIGIENE BUCAL",
    "DESEMBARACO LEVE (30MIN)",
    "DESEMBARACO MEDIO (1H)",
    "DESEMBARACO PESADO (2H)",
]

def classificar_servico(servico):
    servico = servico.upper().strip()

    if "BANHO" in servico:
        return "BANHO"
    if "HIGIENICA" in servico:
        return "TOSA HIGIENICA"
    if "MAQUINA" in servico:
        return "TOSA MAQUINA"
    if "TESOURA" in servico:
        return "TOSA TESOURA"

    for t in TRATAMENTOS_LISTA:
        if t in servico:
            return "TRATAMENTOS"

    return None

def calcular_percentual(qtd, config):
    if qtd >= config["super"]:
        return config["perc"][2]
    elif qtd >= config["meta"]:
        return config["perc"][1]
    else:
        return config["perc"][0]

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        st.error("A planilha precisa conter as colunas SERVICO e VALOR.")
    else:
        df = df[["SERVICO", "VALOR"]].dropna()

        # Limpeza do valor
        df["VALOR"] = (
            df["VALOR"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace("-", "", regex=False)
        )
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
        df = df.dropna()

        registros = []

        for _, row in df.iterrows():
            servicos = str(row["SERVICO"]).upper().split("+")
            valor = row["VALOR"]

            for s in servicos:
                categoria = classificar_servico(s.strip())
                if categoria:
                    registros.append({"CATEGORIA": categoria, "VALOR": valor})

        df_final = pd.DataFrame(registros)

        if df_final.empty:
            st.warning("Nenhum serviço reconhecido encontrado.")
        else:
            resumo = df_final.groupby("CATEGORIA").agg(
                QUANTIDADE=("VALOR", "count"),
                FATURAMENTO=("VALOR", "sum")
            ).reset_index()

            resultados = []

            for _, row in resumo.iterrows():
                categoria = row["CATEGORIA"]
                qtd = row["QUANTIDADE"]
                faturamento = row["FATURAMENTO"]

                config = META_CONFIG[categoria]
                perc = calcular_percentual(qtd, config)
                comissao = faturamento * perc

                resultados.append({
                    "Categoria": categoria,
                    "Quantidade": qtd,
                    "Faturamento": round(faturamento, 2),
                    "% Aplicado": f"{int(perc*100)}%",
                    "Comissão": round(comissao, 2)
                })

            df_resultado = pd.DataFrame(resultados)
            total_comissao = df_resultado["Comissão"].sum()

            st.subheader("📊 Resultado por Categoria")
            st.dataframe(df_resultado, use_container_width=True)

            st.markdown("---")
            st.subheader(f"💰 Comissão Total: R$ {round(total_comissao, 2)}")
