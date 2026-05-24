import streamlit as st

CORES = {
    "ok":   {"bg": "#1B5E20", "fg": "#A5D6A7", "border": "#2E7D32", "label": "OK",       "ponto": "#4CAF50"},
    "warn": {"bg": "#5D4037", "fg": "#FFD180", "border": "#FFB300", "label": "Atenção",  "ponto": "#FFB300"},
    "crit": {"bg": "#5C1A1A", "fg": "#FFCDD2", "border": "#EF5350", "label": "Crítico",  "ponto": "#F44336"},
}


def html_badge(status: str, texto: str | None = None) -> str:
    c = CORES.get(status, CORES["ok"])
    label = texto or c["label"]
    return (
        f'<span style="display:inline-flex; align-items:center; gap:6px; '
        f'padding:3px 10px; border-radius:999px; border:1px solid {c["border"]}; '
        f'background:{c["bg"]}; color:{c["fg"]}; font-size:0.78rem; font-weight:600; '
        f"font-family:Inter,sans-serif;\">"
        f'<span style="width:8px; height:8px; border-radius:50%; background:{c["ponto"]};"></span>'
        f"{label}</span>"
    )


def render(status: str, texto: str | None = None):
    st.markdown(html_badge(status, texto), unsafe_allow_html=True)


COR_PLOTLY = {
    "ok":   "#4CAF50",
    "warn": "#FFB300",
    "crit": "#F44336",
}
