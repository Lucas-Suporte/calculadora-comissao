# =========================
# KPI centralizado - Faturamento e Comissão total
# =========================
st.markdown(f"""
<div style='display:flex; justify-content:center; margin-bottom:20px;'>
    <div style='background: linear-gradient(135deg, #0B0F6D, #1B75BC); color:white; border-radius: 20px; padding: 30px; text-align:center; width:60%;'>
        <h2>{funcionario}</h2>
        <h4>{mes_referencia}</h4>
        <h1>R$ {total_comissao:,.2f}</h1>
        <p>Comissão Total</p>
        <h3>Faturamento Total: R$ {total_faturamento:,.2f}</h3>
    </div>
</div>
""", unsafe_allow_html=True)
