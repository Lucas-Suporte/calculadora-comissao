import pandas as pd

# ==============================
# CONFIGURAÇÃO DE METAS
# ==============================

META_CONFIG = {
    "Banho": {"base": 3, "meta": 4, "super": 5},
    "Tosa Higiênica": {"base": 10, "meta": 15, "super": 20},
    "Tosa à Máquina": {"base": 10, "meta": 15, "super": 20},
    "Tosa à Tesoura": {"base": 15, "meta": 20, "super": 25},
    "Tratamentos": {"base": 15, "meta": 20, "super": 25},
}

# ==============================
# MAPEAMENTO DE SERVIÇOS
# ==============================

SERVICE_MAP = {
    "Banho": [
        "Banho",
        "Banho + Tosa Higiênica",
        "Banho + Hidratação",
    ],
    "Tosa Higiênica": [
        "Tosa Higiênica",
        "Banho + Tosa Higiênica",
    ],
    "Tosa à Máquina": [
        "Tosa à Máquina",
        "Tosa à Máquina (sb)",
    ],
    "Tosa à Tesoura": [
        "Tosa à Tesoura",
        "Tosa à Tesoura (sb)",
        "Tosa à Tesoura Gato",
    ],
    "Tratamentos": [
        "Hidratação",
        "Banho + Hidratação",
        "Remoção de Subpelos",
        "Desembaraço Leve (30min)",
        "Desembaraço Médio (1h)",
        "Desembaraço Pesado (2h)",
        "Corte de Unhas",
        "Corte de Unhas Gato",
    ],
}

# ==============================
# FUNÇÃO PRINCIPAL
# ==============================

def calcular_comissao(df):

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        raise ValueError("O CSV precisa conter as colunas SERVICO e VALOR.")

    df["VALOR"] = (
        df["VALOR"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

    resultados = []
    total_comissao = 0
    total_faturamento = 0

    categoria_data = {
        categoria: {"qtd": 0, "faturamento": 0}
        for categoria in META_CONFIG.keys()
    }

    for _, row in df.iterrows():

        servico = row["SERVICO"]
        valor = row["VALOR"]

        if servico == "Banho + Tosa Higiênica":
            categoria_data["Banho"]["qtd"] += 1
            categoria_data["Banho"]["faturamento"] += valor
            categoria_data["Tosa Higiênica"]["qtd"] += 1

        elif servico == "Banho + Hidratação":
            categoria_data["Banho"]["qtd"] += 1
            categoria_data["Banho"]["faturamento"] += valor
            categoria_data["Tratamentos"]["qtd"] += 1

        else:
            for categoria, servicos in SERVICE_MAP.items():
                if servico in servicos:
                    categoria_data[categoria]["qtd"] += 1
                    categoria_data[categoria]["faturamento"] += valor
                    break

    for categoria, metas in META_CONFIG.items():

        qtd = categoria_data[categoria]["qtd"]
        faturamento = categoria_data[categoria]["faturamento"]

        if qtd >= metas["super"]:
            percentual = metas["super"]
            nome_meta = "Super Meta"
        elif qtd >= metas["meta"]:
            percentual = metas["meta"]
            nome_meta = "Meta"
        else:
            percentual = metas["base"]
            nome_meta = "Base"

        comissao = faturamento * (percentual / 100)

        total_comissao += comissao
        total_faturamento += faturamento

        resultados.append({
            "categoria": categoria,
            "qtd": qtd,
            "meta": nome_meta,
            "percentual": percentual,
            "faturamento": faturamento,
            "comissao": comissao,
        })

    return resultados, total_comissao, total_faturamento
