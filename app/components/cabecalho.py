import streamlit as st
from app.components.estilos import html_titulo_pagina, html_divider_laranja


def cabecalho(titulo: str, pagina_voltar: str | None = None):
    col_logo, _ = st.columns([1, 5])
    with col_logo:
        st.image("img/logo-forzy-branca.svg", use_container_width=True)

    col_titulo, col_acao = st.columns([5, 1])
    with col_titulo:
        st.markdown(html_titulo_pagina(titulo), unsafe_allow_html=True)
    if pagina_voltar:
        with col_acao:
            st.write("")
            if st.button("← Voltar", use_container_width=True):
                st.switch_page(pagina_voltar)

    st.markdown(html_divider_laranja(), unsafe_allow_html=True)
