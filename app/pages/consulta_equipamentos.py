import streamlit as st
import pandas as pd
from app.services.equipamentos import (
    get_equipamentos, remover_equipamento, listar_plantas, listar_areas,
)
from app.services.telemetria import status_atual, get_limites
from app.components.cabecalho import cabecalho
from app.components.status_badge import CORES as STATUS_CORES


@st.dialog("Confirmar remoção")
def confirmar_remocao(equipamento: dict):
    st.warning(
        f"Tem certeza que deseja remover o equipamento **{equipamento['TAG']}** "
        f"({equipamento['Modelo']} / {equipamento['Fabricante']})?"
    )
    col1, col2 = st.columns(2)
    if col1.button("Remover", type="primary", use_container_width=True):
        remover_equipamento(equipamento["TAG"])
        st.session_state["remocao_sucesso"] = equipamento["TAG"]
        st.rerun()
    if col2.button("Cancelar", use_container_width=True):
        st.rerun()


cabecalho("Consulta de Equipamentos")

col_top1, col_top2 = st.columns([4, 1])
with col_top2:
    if st.button("+ Novo Equipamento", type="primary", use_container_width=True):
        st.switch_page("app/pages/cadastro_equipamento.py")

st.caption("Selecione um equipamento na tabela para acessar o Módulo Técnico ou o Dashboard.")

equipamentos = get_equipamentos()
if not equipamentos:
    st.info("Nenhum equipamento cadastrado.")
    st.stop()

# Enriquecer com status
limites = get_limites()
for eq in equipamentos:
    eq["Status"] = STATUS_CORES[status_atual(eq["TAG"], limites)]["label"]

df_base = pd.DataFrame(equipamentos)

# Filtros
plantas = ["Todas"] + sorted({eq["Planta"] for eq in equipamentos if eq.get("Planta")})
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    busca = st.text_input("Buscar por TAG ou Modelo", placeholder="Ex.: EQ-001 ou XR-200")
with col2:
    planta_sel = st.selectbox("Planta", plantas)
with col3:
    if planta_sel == "Todas":
        areas_disp = sorted({eq["Área"] for eq in equipamentos if eq.get("Área")})
    else:
        areas_disp = sorted({eq["Área"] for eq in equipamentos if eq.get("Planta") == planta_sel and eq.get("Área")})
    area_sel = st.selectbox("Área", ["Todas"] + areas_disp)
with col4:
    fabricantes = ["Todos"] + sorted(df_base["Fabricante"].unique().tolist())
    fab_sel = st.selectbox("Fabricante", fabricantes)

df = df_base.copy()
if busca:
    termo = busca.strip().upper()
    df = df[df["TAG"].str.upper().str.contains(termo) | df["Modelo"].str.upper().str.contains(termo)]
if planta_sel != "Todas":
    df = df[df["Planta"] == planta_sel]
if area_sel != "Todas":
    df = df[df["Área"] == area_sel]
if fab_sel != "Todos":
    df = df[df["Fabricante"] == fab_sel]

st.caption(f"{len(df)} equipamento(s) encontrado(s)")

colunas_exibir = ["TAG", "Modelo", "Fabricante", "Planta", "Área", "Potência (W)", "Tensão (V)", "Status"]
df_view = df[colunas_exibir].reset_index(drop=True)


def estilo_status(v):
    if v == "Crítico":
        return "color:#F44336; font-weight:700;"
    if v == "Atenção":
        return "color:#FFB300; font-weight:700;"
    if v == "OK":
        return "color:#4CAF50; font-weight:700;"
    return ""


evento = st.dataframe(
    df_view.style.map(estilo_status, subset=["Status"]),
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "TAG":          st.column_config.TextColumn("TAG",            width="small"),
        "Modelo":       st.column_config.TextColumn("Modelo",         width="medium"),
        "Fabricante":   st.column_config.TextColumn("Fabricante",     width="medium"),
        "Planta":       st.column_config.TextColumn("Planta",         width="medium"),
        "Área":         st.column_config.TextColumn("Área",           width="medium"),
        "Potência (W)": st.column_config.NumberColumn("Potência (W)", format="%d W", width="small"),
        "Tensão (V)":   st.column_config.NumberColumn("Tensão (V)",   format="%d V", width="small"),
        "Status":       st.column_config.TextColumn("Status",         width="small"),
    },
)

linhas = evento.selection.rows
if linhas:
    eq_view = df_view.iloc[linhas[0]].to_dict()
    eq = next(e for e in equipamentos if e["TAG"] == eq_view["TAG"])
    st.session_state["equipamento_selecionado"] = eq

    st.divider()
    col_info, col_acoes = st.columns([4, 1])
    with col_info:
        st.info(
            f"Selecionado: **{eq['TAG']}** — {eq['Modelo']} / {eq['Fabricante']} "
            f"· {eq.get('Planta','—')} › {eq.get('Área','—')}"
        )
    with col_acoes:
        if st.button("Dashboard", type="primary", use_container_width=True):
            st.switch_page("app/pages/dashboard_ativo.py")
        if st.button("Módulo Técnico", use_container_width=True):
            st.switch_page("app/pages/modulo_tecnico.py")
        if st.button("Dados Brutos", use_container_width=True):
            st.switch_page("app/pages/dados_brutos.py")
        if st.button("Remover", use_container_width=True):
            confirmar_remocao(eq)

if "cadastro_sucesso" in st.session_state:
    st.success(f"Equipamento **{st.session_state.pop('cadastro_sucesso')}** cadastrado com sucesso!")
if "remocao_sucesso" in st.session_state:
    st.success(f"Equipamento **{st.session_state.pop('remocao_sucesso')}** removido com sucesso!")
