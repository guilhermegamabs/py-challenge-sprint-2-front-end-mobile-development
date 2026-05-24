import os
import streamlit as st
from app.components.cabecalho import cabecalho
from app.services.equipamentos import (
    get_equipamento, atualizar_equipamento, listar_plantas, listar_areas,
)

if "editando" not in st.session_state:
    st.session_state["editando"] = False

if "equipamento_selecionado" not in st.session_state:
    st.warning("Nenhum equipamento selecionado. Volte para a consulta.")
    if st.button("← Voltar à Consulta"):
        st.switch_page("app/pages/consulta_equipamentos.py")
    st.stop()

tag = st.session_state["equipamento_selecionado"]["TAG"]
eq = get_equipamento(tag)
if not eq:
    st.error(f"Equipamento {tag} não encontrado.")
    st.stop()

cabecalho(f'Módulo Técnico — {eq["TAG"]}', pagina_voltar="app/pages/consulta_equipamentos.py")

if not st.session_state["editando"]:
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.markdown("**TAG de Identificação**"); st.text(eq["TAG"])
        st.markdown("**Modelo**");                st.text(eq["Modelo"])
        st.markdown("**Fabricante**");            st.text(eq["Fabricante"])

    with col2:
        st.markdown("**Potência**"); st.text(f"{eq['Potência (W)']} W")
        st.markdown("**Tensão**");   st.text(f"{eq['Tensão (V)']} V")
        st.markdown("**Planta**");   st.text(eq.get("Planta") or "—")
        st.markdown("**Área**");     st.text(eq.get("Área") or "—")

    with col3:
        st.markdown("**Placa do motor**")
        img_path = eq.get("img_placa_path")
        if img_path and os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.markdown(
                '<div style="border:1px dashed #444; border-radius:6px; padding:18px;'
                ' text-align:center; color:#666; font-size:0.85rem;">Sem imagem cadastrada</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    if st.button("Editar", type="primary"):
        st.session_state["editando"] = True
        st.rerun()

else:
    st.subheader("Editar Equipamento")
    plantas = listar_plantas()
    nomes_plantas = [p["nome"] for p in plantas]
    idx_planta = nomes_plantas.index(eq["Planta"]) if eq.get("Planta") in nomes_plantas else 0
    planta_nome = st.selectbox("Planta", nomes_plantas, index=idx_planta) if nomes_plantas else None
    planta_sel = next((p for p in plantas if p["nome"] == planta_nome), None) if planta_nome else None
    areas = listar_areas(planta_sel["id"]) if planta_sel else []
    nomes_areas = [a["nome"] for a in areas]
    idx_area = nomes_areas.index(eq["Área"]) if eq.get("Área") in nomes_areas else 0
    area_nome = st.selectbox("Área", nomes_areas, index=idx_area) if nomes_areas else None
    area_sel = next((a for a in areas if a["nome"] == area_nome), None) if area_nome else None

    with st.form("form_edicao"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("TAG", value=eq["TAG"], disabled=True)
            modelo = st.text_input("Modelo",     value=eq["Modelo"])
            fab    = st.text_input("Fabricante", value=eq["Fabricante"])
        with col2:
            potencia = st.number_input("Potência (W)", value=int(eq["Potência (W)"]), min_value=0, step=50)
            tensao   = st.number_input("Tensão (V)",   value=int(eq["Tensão (V)"]),   min_value=0, step=1)

        col_s, col_c = st.columns(2)
        salvar   = col_s.form_submit_button("Salvar", type="primary", use_container_width=True)
        cancelar = col_c.form_submit_button("Cancelar",                use_container_width=True)

    if salvar:
        atualizar_equipamento(tag, {
            "Modelo":       modelo,
            "Fabricante":   fab,
            "Potência (W)": int(potencia),
            "Tensão (V)":   int(tensao),
            "area_id":      area_sel["id"] if area_sel else None,
        })
        st.session_state["equipamento_selecionado"] = get_equipamento(tag)
        st.session_state["editando"] = False
        st.success("Dados atualizados com sucesso!")
        st.rerun()
    if cancelar:
        st.session_state["editando"] = False
        st.rerun()
