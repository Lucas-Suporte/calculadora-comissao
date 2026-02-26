import streamlit as st
import pandas as pd
from utils.comissao import calcular_comissao

st.set_page_config(page_title="Relatório de Comissão", layout="wide")

st.markdown("""
<style>
body {
    background-color: #F8FAFC;
}

.main-title {
    text-align: center;
    color: #1E293B;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 30px;
}

.card {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.card h3 {
    color: #1E293B;
    font-size: 18px;
    margin-bottom: 10px;
}

.card p {
    color: #64748B;
    font-size: 14px;
}

.highlight {
    font-weight: bold;
    color: #059669;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Relatório de Comissão</div>', unsafe_allow_html=True)

nome = st.text_input("Nome do Funcionário")
mes = st.text_input("Mês de Referência")
arquivo = st.file_uploader("Envie a planilha CSV", type="csv")

if arquivo:

    try:
        df = pd.read_csv(arquivo, sep=None, engine="python")
        resultados, total_comissao, total_faturamento = calcular_comissao(df)

        st.markdown("## Resumo Geral")

        st.markdown(f"""
        <div class="card">
            <h3>{nome}</h3>
            <p>Mês: {mes}</p>
            <p>Faturamento Total: <span class="highlight">R$ {total_faturamento:,.2f}</span></p>
            <p>Comissão Final: <span class="highlight">R$ {total_comissao:,.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("## Detalhamento por Categoria")

        col1, col2, col3 = st.columns(3)

        for i, r in enumerate(resultados):

            card_html = f"""
            <div class="card">
                <h3>{r['categoria']}</h3>
                <p>Quantidade de Serviços: <span class="highlight">{r['qtd']}</span></p>
                <p>Meta Atingida: <span class="highlight">{r['meta']} ({r['percentual']}%)</span></p>
                <p>Comissão: <span class="highlight">R$ {r['comissao']:,.2f}</span></p>
            </div>
            """

            if i % 3 == 0:
                col1.markdown(card_html, unsafe_allow_html=True)
            elif i % 3 == 1:
                col2.markdown(card_html, unsafe_allow_html=True)
            else:
                col3.markdown(card_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")
