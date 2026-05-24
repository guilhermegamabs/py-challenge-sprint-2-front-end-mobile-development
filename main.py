import streamlit as st
from app.services.db import init_db

st.set_page_config(
    page_title="Forzy — Monitoramento de Ativos",
    page_icon="img/forzy_logo.jpg",
    layout="wide",
)

init_db()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, label, p, div {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: #1A1A1A !important;
}


[data-testid="stSidebarNav"] a {
    border-left: 3px solid transparent;
    padding-left: 10px !important;
    transition: border-color 0.2s, color 0.2s, background-color 0.2s;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 0 6px 6px 0;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    border-left: 3px solid #FFB300 !important;
    color: #FFB300 !important;
    background-color: #2A2A2A !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    transition: opacity 0.2s;
}

.stButton > button:hover {
    opacity: 0.85;
}

[data-testid="baseButton-secondary"] {
    border: 1px solid #FFB300 !important;
    color: #FFB300 !important;
}

[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {
    border: 1px solid #FFB300 !important;
    border-radius: 6px !important;
    background-color: #1A1A1A !important;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    border: 1px solid #FFB300 !important;
    border-radius: 6px !important;
    background-color: #1A1A1A !important;
}

[data-testid="stDataFrame"] th {
    background-color: #2A2A2A !important;
    color: #FFB300 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #FFB300 !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background-color: rgba(255, 179, 0, 0.08) !important;
}


hr {
    border-color: #333333 !important;
}
</style>
""", unsafe_allow_html=True)

paginas = {
    "Operação": [
        st.Page("app/pages/navegacao_planta.py",     title="Navegação por Planta", default=True),
        st.Page("app/pages/dashboard_ativo.py",      title="Dashboard do Ativo"),
    ],
    "Cadastro": [
        st.Page("app/pages/consulta_equipamentos.py", title="Consulta de Equipamentos"),
        st.Page("app/pages/cadastro_equipamento.py",  title="Novo Equipamento"),
        st.Page("app/pages/modulo_tecnico.py",        title="Módulo Técnico"),
        st.Page("app/pages/dados_brutos.py",          title="Dados Brutos"),
    ],
}

with st.sidebar:
    st.markdown(
        '<p style="text-align:center; color:#888; font-size:0.8rem; margin:0;">Sprint 2 — Visualização Operacional</p>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Integrantes**")
    st.caption("Guilherme Gama · RM565293")
    st.caption("Bruno Fernandes · RM552574")
    st.caption("Edgar Lódula · RM565260")
    st.caption("Júlia Aben-Athar · RM566325")
    st.caption("Igor Nakajima · RM563632")
    st.divider()

pg = st.navigation(paginas, position="sidebar")
pg.run()