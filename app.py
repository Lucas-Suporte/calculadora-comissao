import streamlit as st
import pandas as pd
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

st.set_page_config(page_title="Dashboard Performance – PET247", layout="wide")

AZUL = "#0B0F6D"
VERDE = "#17B3A3"
logo_path = "logo.png"

# =========================
# ESTILO EXECUTIVO
# =========================
st.markdown("""
<style>
body { background-color: #f4f6f9; }

.kpi {
    background: linear-gradient(135deg, #0B0F6D, #17B3A3);
    color: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    margin-bottom: 25px;
    transition: all 0.25s ease-in-out;
}
.card:hover { transform: translateY(-6px); }

.card-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; }

.progress-bar {
    height: 8px;
    border-radius: 10px;
    background-color: #ddd;
    margin-top: 8px;
}

.progress-fill {
    height: 8px;
    border-radius: 10px;
}

.bronze { border-left: 8px solid #cd7f32; }
.prata { border-left: 8px solid #C0C0C0; }
.ouro { border-left: 8px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# =========================
# METAS
# =========================
META_CONFIG = {
    "BANHO": {"base_qtd":129,"meta_qtd":130,"super_qtd":176,"pct":[0.03,0.04,0.05]},
    "TOSA HIGIENICA": {"base_qtd":19,"meta_qtd":20,"super_qtd":40,"pct":[0.10,0.15,0.20]},
    "TOSA MAQUINA": {"base_qtd":14,"meta_qtd":15,"super_qtd":30,"pct":[0.10,0.15,0.20]},
    "TOSA TESOURA": {"base_qtd":14,"meta_qtd":15,"super_qtd":30,"pct":[0.15,0.20,0.25]},
    "TRATAMENTOS": {"base_qtd":14,"meta_qtd":15,"super_qtd":30,"pct":[0.15,0.20,0.25]},
}

# =========================
# HEADER
# =========================
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
if os.path.exists(logo_path):
    st.image(logo_path, width=250)
st.markdown(f"<h1 style='color:{AZUL};'>Dashboard Performance</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{VERDE};'>PET247 Market</h3>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx","csv"])
nome = st.text_input("Nome do Profissional")
mes = st.text_input("Mês de Referência")

def classificar(servico):
    s = servico.upper()
    if "BANHO" in s: return "BANHO"
    if "HIGIENICA" in s: return "TOSA HIGIENICA"
    if "MAQUINA" in s: return "TOSA MAQUINA"
    if "TESOURA" in s: return "TOSA TESOURA"
    return "TRATAMENTOS"

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.upper().str.strip()

    if "SERVICO" not in df.columns or "VALOR" not in df.columns:
        st.error("A planilha precisa conter SERVICO e VALOR.")
        st.stop()

    df = df[["SERVICO","VALOR"]].dropna()
    df["VALOR"] = pd.to_numeric(df["VALOR"].astype(str).str.replace(",", "."), errors="coerce")
    df = df.dropna()

    registros = []

    for _, row in df.iterrows():
        servicos = [s.strip().upper() for s in str(row["SERVICO"]).split("+")]
        valor_total = row["VALOR"]

        # Serviço único mantém valor original
        if len(servicos) == 1:
            s = servicos[0]
            registros.append({
                "SERVICO": s,
                "CATEGORIA": classificar(s),
                "VALOR": valor_total
            })

        else:
            valor_restante = valor_total

            # Valores fixos quando compostos
            for s in servicos:
                if "HIGIENICA" in s:
                    valor = 20
                    valor_restante -= 20
                    registros.append({
                        "SERVICO": s,
                        "CATEGORIA": classificar(s),
                        "VALOR": valor
                    })

                elif "HIDRATACAO" in s:
                    valor = 30
                    valor_restante -= 30
                    registros.append({
                        "SERVICO": s,
                        "CATEGORIA": classificar(s),
                        "VALOR": valor
                    })

            # Serviço principal recebe restante
            for s in servicos:
                if "HIGIENICA" not in s and "HIDRATACAO" not in s:
                    registros.append({
                        "SERVICO": s,
                        "CATEGORIA": classificar(s),
                        "VALOR": valor_restante
                    })

    df_final = pd.DataFrame(registros)

    resumo = df_final.groupby("CATEGORIA").agg(
        QUANTIDADE=("VALOR","count"),
        FATURAMENTO=("VALOR","sum")
    ).reset_index()

    total_comissao = 0
    linhas_resumo = []

    nomes_formatados = {
        "BANHO": "Banho",
        "TOSA HIGIENICA": "Tosa Higiênica",
        "TOSA MAQUINA": "Tosa à Máquina",
        "TOSA TESOURA": "Tosa à Tesoura",
        "TRATAMENTOS": "Tratamentos"
    }

    for _, row in resumo.iterrows():
        categoria = row["CATEGORIA"]
        qtd = row["QUANTIDADE"]
        fat = row["FATURAMENTO"]
        cfg = META_CONFIG[categoria]

        if qtd >= cfg["super_qtd"]:
            pct = cfg["pct"][2]; faixa="SUPER META"
        elif qtd >= cfg["meta_qtd"]:
            pct = cfg["pct"][1]; faixa="META"
        else:
            pct = cfg["pct"][0]; faixa="BASE"

        comissao = fat * pct
        total_comissao += comissao

        linhas_resumo.append([
            nomes_formatados[categoria],
            qtd,
            f"R$ {fat:,.2f}",
            f"{pct*100:.0f}%",
            f"R$ {comissao:,.2f}",
            faixa
        ])

    tabela_resumo = pd.DataFrame(linhas_resumo, columns=[
        "Categoria","Quantidade","Faturamento",
        "% Aplicada","Comissão","Faixa"
    ])

    # KPI
    st.markdown(f"""
    <div class="kpi">
        <h3>Comissão Total do Mês</h3>
        <h1>R$ {total_comissao:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Dashboard Cards
    st.subheader("Performance por Categoria")

    col1, col2 = st.columns(2)

    for i, row in resumo.iterrows():
        categoria = row["CATEGORIA"]
        qtd = row["QUANTIDADE"]
        fat = row["FATURAMENTO"]
        cfg = META_CONFIG[categoria]

        if qtd >= cfg["super_qtd"]:
            pct = cfg["pct"][2]; classe="ouro"; medalha="🥇 Ouro"
        elif qtd >= cfg["meta_qtd"]:
            pct = cfg["pct"][1]; classe="prata"; medalha="🥈 Prata"
        else:
            pct = cfg["pct"][0]; classe="bronze"; medalha="🥉 Bronze"

        comissao = fat * pct
        progresso = min((qtd / cfg["super_qtd"]) * 100, 100)

        card_html = f"""
        <div class="card {classe}">
            <div class="card-title">{nomes_formatados[categoria]} — {medalha}</div>
            <div>Quantidade: <b>{qtd}</b></div>
            <div>Faturamento: <b>R$ {fat:,.2f}</b></div>
            <div>% Aplicada: <b>{pct*100:.0f}%</b></div>
            <div>Comissão: <b>R$ {comissao:,.2f}</b></div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:{progresso}%; background:#17B3A3;"></div>
            </div>
        </div>
        """

        if i % 2 == 0:
            with col1:
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2:
                st.markdown(card_html, unsafe_allow_html=True)

    st.subheader("Resumo Geral")
    st.dataframe(tabela_resumo, use_container_width=True)

    # PDF
    if st.button("Exportar PDF"):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp.name, pagesize=pagesizes.A4)
        elements = []
        styles = getSampleStyleSheet()

        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=3*inch, height=1*inch))
            elements.append(Spacer(1,12))

        elements.append(Paragraph("Relatório de Performance", styles["Heading1"]))
        elements.append(Spacer(1,12))
        elements.append(Paragraph(f"Profissional: {nome}", styles["Normal"]))
        elements.append(Paragraph(f"Mês: {mes}", styles["Normal"]))
        elements.append(Spacer(1,12))

        tabela_pdf = Table([tabela_resumo.columns.tolist()] + tabela_resumo.values.tolist())
        tabela_pdf.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(AZUL)),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ]))

        elements.append(tabela_pdf)
        elements.append(Spacer(1,12))
        elements.append(Paragraph(f"Comissão Total: R$ {total_comissao:,.2f}", styles["Heading2"]))

        doc.build(elements)

        with open(temp.name,"rb") as f:
            st.download_button("Baixar PDF", f, file_name="Relatorio_PET247.pdf")
