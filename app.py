import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

st.set_page_config(layout="wide")

# =========================
# CSS VISUAL MODERNO
# =========================
st.markdown("""
<style>
body { background-color: #F4F6F9; font-family: Arial, sans-serif; }

/* Card padrão */
.card {
    padding: 15px;
    border-radius: 12px;
    margin: 5px;
    background: linear-gradient(135deg, #0B0F6D, #1B75BC);
    color: white;
    text-align: center;
}
.card h4 { margin-bottom: 8px; }
.card .comissao { font-weight: bold; font-size: 16px; margin-top: 8px; }

/* Card resumo principal */
.card-resumo {
    background: linear-gradient(135deg, #0B0F6D, #1B75BC);
    color: white;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    width: 60%;
}

/* Inputs */
input[type="text"] {
    border: 2px solid #0B0F6D !important;
    border-radius: 8px;
    padding: 8px;
    font-size: 16px;
}

/* Botão upload */
div.stFileUploader>div>div>button {
    background-color: #0B0F6D;
    color: white;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
}
div.stFileUploader>div>div>button:hover {
    background-color: #1B75BC;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO CENTRALIZADA CORRETA
# =========================
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=400)
        st.markdown(
            "<div style='height:10px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2); border-radius:5px;'></div>",
            unsafe_allow_html=True
        )
else:
    st.warning("Arquivo logo.png não encontrado na pasta do projeto.")

# =========================
# TÍTULO
# =========================
st.markdown("<h1 style='text-align:center;'>Relatório de Comissão - Pet247</h1>", unsafe_allow_html=True)

# =========================
# INPUTS
# =========================
st.markdown("<b>Nome do Funcionário</b>", unsafe_allow_html=True)
funcionario = st.text_input("", placeholder="Digite o nome do funcionário")

st.markdown("<b>Mês de Referência</b>", unsafe_allow_html=True)
mes_referencia = st.text_input("", placeholder="Digite o mês de referência")

st.markdown("<b>Envie a planilha CSV</b>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"])

# =========================
# METAS
# =========================
META_CONFIG = {
    "BANHO": {"base":3,"meta":4,"super":5,"bronze":150,"prata":180,"ouro":200},
    "TOSA HIGIENICA": {"base":10,"meta":15,"super":20,"bronze":80,"prata":100,"ouro":120},
    "TOSA MAQUINA": {"base":10,"meta":15,"super":20,"bronze":60,"prata":80,"ouro":100},
    "TOSA TESOURA": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
    "TRATAMENTOS": {"base":15,"meta":20,"super":25,"bronze":40,"prata":55,"ouro":70},
}

SERVICE_MAP = {
    "BANHO": ["Banho", "Banho + Hidratação", "Banho + Tosa Higiênica"],
    "TOSA HIGIENICA": ["Tosa Higiênica", "Tosa de Acabamento"],
    "TOSA MAQUINA": ["Tosa à Máquina", "Tosa à Máquina (sb)"],
    "TOSA TESOURA": ["Tosa à Tesoura", "Tosa à Tesoura (sb)", "Tosa à Tesoura Gato"],
    "TRATAMENTOS": [
        "Hidratação","Remoção de Subpelos","Higiene Bucal","Corte de Unhas",
        "Desembaraço Leve (30min)","Desembaraço Médio (1h)",
        "Desembaraço Pesado (2h)","Corte de Unhas Gato"
    ]
}

# =========================
# PROCESSAMENTO
# =========================
if uploaded_file and funcionario and mes_referencia:
    try:
        df = pd.read_csv(uploaded_file)
        df["VALOR"] = (
            df["VALOR"].astype(str)
            .str.replace("R$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
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

            if qtd >= metas["ouro"]:
                pct = metas["super"]/100
                meta_nome = "Super Meta"
                pct_text = f"{metas['super']}%"
            elif qtd >= metas["prata"]:
                pct = metas["meta"]/100
                meta_nome = "Meta"
                pct_text = f"{metas['meta']}%"
            else:
                pct = metas["base"]/100
                meta_nome = "Base"
                pct_text = f"{metas['base']}%"

            comissao = faturamento * pct
            total_comissao += comissao

            resultados.append({
                "categoria": categoria,
                "qtd": qtd,
                "meta": meta_nome,
                "pct": pct_text,
                "comissao": comissao
            })

        # =========================
        # CARD CENTRAL RESUMO
        # =========================
        colA, colB, colC = st.columns([1,2,1])
        with colB:
            st.markdown(f"""
            <div class='card-resumo'>
                <h2>{funcionario}</h2>
                <h4>{mes_referencia}</h4>
                <h1>R$ {total_comissao:,.2f}</h1>
                <p>Comissão Total</p>
                <h3>Faturamento Total: R$ {total_faturamento:,.2f}</h3>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # CARDS INDIVIDUAIS
        # =========================
        st.subheader("Resumo por Serviço")
        cols = st.columns(5)
        for i, item in enumerate(resultados):
            with cols[i % 5]:
                st.markdown(f"""
                <div class='card'>
                    <h4>{item['categoria']}</h4>
                    <p>Qtd: {item['qtd']}</p>
                    <p>{item['meta']} ({item['pct']})</p>
                    <div class='comissao'>R$ {item['comissao']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

        # =========================
        # PDF (SEM FATURAMENTO TOTAL)
        # =========================
        st.subheader("Gerar Relatório em PDF")
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()

            if os.path.exists("logo.png"):
                pdf.image("logo.png", x=60, w=90)

            pdf.set_font("Arial", "B", 16)
            pdf.ln(50)
            pdf.cell(0, 10, "Relatório de Comissão - Pet247", 0, 1, "C")
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Funcionário: {funcionario}", 0, 1)
            pdf.cell(0, 8, f"Mês de Referência: {mes_referencia}", 0, 1)
            pdf.ln(10)

            for item in resultados:
                pdf.set_fill_color(11, 15, 109)
                pdf.set_text_color(255,255,255)
                pdf.cell(0, 10, item['categoria'], 0, 1, fill=True)
                pdf.set_text_color(0,0,0)
                pdf.cell(0, 8, f"Qtd: {item['qtd']} | {item['meta']} ({item['pct']}) | Comissão: R$ {item['comissao']:.2f}", 0, 1)
                pdf.ln(3)

            nome_pdf = f"Relatorio_{funcionario}.pdf"
            pdf.output(nome_pdf)
            st.success("PDF gerado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao processar CSV: {e}")

else:
    st.info("Preencha os campos e envie o CSV para gerar o relatório.")
