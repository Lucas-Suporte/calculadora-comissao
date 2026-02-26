import pandas as pd

META_CONFIG = {
    "BANHO": {"base": 3, "meta": 4, "super": 5},
    "TOSA HIGIENICA": {"base": 10, "meta": 15, "super": 20},
    "TOSA MAQUINA": {"base": 10, "meta": 15, "super": 20},
    "TOSA TESOURA": {"base": 15, "meta": 20, "super": 25},
    "TRATAMENTOS": {"base": 15, "meta": 20, "super": 25},
}

SERVICE_MAP = {
    "BANHO": ["Banho", "Banho + Hidratação", "Banho + Tosa Higiênica"],
    "TOSA HIGIENICA": ["Tosa Higiênica", "Tosa de Acabamento"],
    "TOSA MAQUINA": ["Tosa à Máquina", "Tosa à Máquina (sb)"],
    "TOSA TESOURA": ["Tosa à Tesoura", "Tosa à Tesoura (sb)", "Tosa à Tesoura Gato"],
    "TRATAMENTOS": [
        "Hidratação", "Remoção de Subpelos", "Higiene Bucal",
        "Corte de Unhas", "Desembaraço Leve (30min)",
        "Desembaraço Médio (1h)", "Desembaraço Pesado (2h)",
        "Corte de Unhas Gato"
    ]
}

def calcular_comissao(df):
    if "VALOR" not in df.columns or "SERVICO" not in df.columns:
        raise ValueError("O CSV precisa conter as colunas SERVICO e VALOR.")

    df["VALOR"] = (
        df["VALOR"].astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

    resultados = []
    total_comissao = 0
    total_faturamento = 0

    for categoria, metas in META_CONFIG.items():
        filtro = df["SERVICO"].isin(SERVICE_MAP[categoria])
        qtd = filtro.sum()
        faturamento = df.loc[filtro, "VALOR"].sum()
        total_faturamento += faturamento

        if qtd >= metas["super"]:
            percentual = metas["super"]
            meta_nome = "Super Meta"
        elif qtd >= metas["meta"]:
            percentual = metas["meta"]
            meta_nome = "Meta"
        else:
            percentual = metas["base"]
            meta_nome = "Base"

        comissao = faturamento * (percentual / 100)
        total_comissao += comissao

        resultados.append({
            "categoria": categoria,
            "qtd": int(qtd),
            "meta": meta_nome,
            "percentual": percentual,
            "faturamento": faturamento,
            "comissao": comissao
        })

    return resultados, total_comissao, total_faturamento
