from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import pagesizes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import HRFlowable
from reportlab.lib.colors import HexColor
from reportlab.platypus import KeepTogether

import os

def gerar_pdf(nome, mes, resultados, total_comissao):

    caminho = "relatorio_comissao.pdf"
    doc = SimpleDocTemplate(
        caminho,
        pagesize=pagesizes.A4
    )

    elementos = []

    styles = getSampleStyleSheet()

    # ==========================
    # LOGO
    # ==========================

    if os.path.exists("assets/logo.png"):
        logo = Image("assets/logo.png", width=2*inch, height=1*inch)
        elementos.append(logo)
        elementos.append(Spacer(1, 20))

    # ==========================
    # TÍTULO
    # ==========================

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor("#1E293B"),
        spaceAfter=15
    )

    elementos.append(Paragraph("Relatório de Comissão", titulo_style))
    elementos.append(Spacer(1, 10))

    # ==========================
    # INFORMAÇÕES
    # ==========================

    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor("#334155")
    )

    elementos.append(Paragraph(f"<b>Funcionário:</b> {nome}", info_style))
    elementos.append(Paragraph(f"<b>Mês de Referência:</b> {mes}", info_style))
    elementos.append(Paragraph(f"<b>Comissão Total:</b> R$ {total_comissao:,.2f}", info_style))
    elementos.append(Spacer(1, 20))

    # ==========================
    # TABELA DE RESULTADOS
    # ==========================

    dados = [
        ["Categoria", "Qtd", "Meta", "%", "Comissão"]
    ]

    for r in resultados:
        dados.append([
            r["categoria"],
            r["qtd"],
            r["meta"],
            f"{r['percentual']}%",
            f"R$ {r['comissao']:,.2f}"
        ])

    tabela = Table(dados, repeatRows=1)

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#059669")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))

    elementos.append(tabela)
    elementos.append(Spacer(1, 40))

    # ==========================
    # ASSINATURA
    # ==========================

    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elementos.append(Spacer(1, 10))

    elementos.append(
        Paragraph(
            "Declaro que as informações acima refletem os serviços realizados no período informado.",
            info_style
        )
    )

    elementos.append(Spacer(1, 30))

    elementos.append(
        Paragraph(
            "__________________________________________",
            info_style
        )
    )

    elementos.append(
        Paragraph(
            "PET247 - Gestão",
            info_style
        )
    )

    doc.build(elementos)

    return caminho
