import os
import streamlit as st
from app.services.equipamentos import tag_existe, adicionar_equipamento, listar_plantas, listar_areas
from app.services.ocr_placa import extrair as ocr_extrair, CAMPOS as OCR_CAMPOS
from app.services.db import PLACAS_DIR
from app.components.cabecalho import cabecalho
from app.components.estilos import html_linha_check, html_linha_alerta

cabecalho("Novo Equipamento", pagina_voltar="app/pages/consulta_equipamentos.py")
st.caption("Faça upload da placa do motor para extração automática via IA (Gemini), ou preencha manualmente.")

for k in ("ocr_tag", "ocr_modelo", "ocr_fab", "ocr_pot", "ocr_tensao"):
    st.session_state.setdefault(k, "")

st.session_state.setdefault("ocr_extraidos", set())
st.session_state.setdefault("ocr_faltando", set())
st.session_state.setdefault("ocr_texto_bruto", "")

st.markdown("### 1. Placa do motor (opcional)")

col_up, col_btn = st.columns([3, 1])

with col_up:
    arquivo = st.file_uploader("Imagem da placa (jpg/png/webp)", type=["jpg", "jpeg", "png", "webp"], key="placa_upload")
with col_btn:
    st.write("")
    st.write("")
    run_ocr = st.button("Extrair via IA", type="primary", use_container_width=True, disabled=arquivo is None)

img_bytes = None
img_ext = None
if arquivo is not None:
    img_bytes = arquivo.getvalue()
    img_ext = os.path.splitext(arquivo.name)[1].lower() or ".jpg"
    st.image(img_bytes, caption=arquivo.name, width=320)

if run_ocr and img_bytes:
    with st.spinner("Analisando placa com Gemini 2.5 Flash..."):
        try:
            res = ocr_extrair(img_bytes)
        except Exception as exc:
            st.error(f"Falha na extração: {exc}")
            res = None

    if res is not None:
        extraidos = set()
        if "TAG" in res:
            st.session_state["ocr_tag"] = res["TAG"]; extraidos.add("TAG")
        if "Modelo" in res:
            st.session_state["ocr_modelo"] = res["Modelo"]; extraidos.add("Modelo")
        if "Fabricante" in res:
            st.session_state["ocr_fab"] = res["Fabricante"]; extraidos.add("Fabricante")
        if "Potência (W)" in res:
            st.session_state["ocr_pot"] = int(res["Potência (W)"]); extraidos.add("Potência (W)")
        if "Tensão (V)" in res:
            st.session_state["ocr_tensao"] = int(res["Tensão (V)"]); extraidos.add("Tensão (V)")

        st.session_state["ocr_extraidos"]   = extraidos
        st.session_state["ocr_faltando"]    = set(res.get("_faltando", []))
        st.session_state["ocr_texto_bruto"] = res.get("_texto_bruto", "")

        if extraidos:
            st.success(f"Extraídos {len(extraidos)} de {len(OCR_CAMPOS)} campos. Revise abaixo e ajuste se necessário.")
        else:
            st.warning("Nenhum campo pôde ser extraído. Preencha manualmente.")

if st.session_state["ocr_extraidos"] or st.session_state["ocr_faltando"]:
    col_ok, col_falta = st.columns(2)
    with col_ok:
        st.markdown("**Detectados pela IA**")
        if st.session_state["ocr_extraidos"]:
            for c in OCR_CAMPOS:
                if c in st.session_state["ocr_extraidos"]:
                    st.markdown(html_linha_check(c), unsafe_allow_html=True)
        else:
            st.caption("Nenhum")
    with col_falta:
        st.markdown("**Faltando — preencha manualmente**")
        if st.session_state["ocr_faltando"]:
            for c in OCR_CAMPOS:
                if c in st.session_state["ocr_faltando"]:
                    st.markdown(html_linha_alerta(c), unsafe_allow_html=True)
        else:
            st.caption("Nenhum")
    if st.session_state["ocr_texto_bruto"]:
        with st.expander("Texto bruto detectado", expanded=False):
            st.code(st.session_state["ocr_texto_bruto"])

st.divider()

st.markdown("### 2. Localização do ativo")
plantas = listar_plantas()
nomes_plantas = [p["nome"] for p in plantas]
planta_nome = st.selectbox("Planta *", nomes_plantas, key="cad_planta") if plantas else None
planta_sel = next((p for p in plantas if p["nome"] == planta_nome), None) if planta_nome else None

areas = listar_areas(planta_sel["id"]) if planta_sel else []
nomes_areas = [a["nome"] for a in areas]
area_nome = st.selectbox("Área *", nomes_areas, key="cad_area") if nomes_areas else None
area_sel = next((a for a in areas if a["nome"] == area_nome), None) if area_nome else None

st.divider()

st.markdown("### 3. Dados do equipamento")
st.caption("Campos pré-preenchidos pela IA podem ser editados livremente.")

extraidos = st.session_state["ocr_extraidos"]

def rotulo(campo: str) -> str:
    if campo in extraidos:
        return f"{campo} *  ·  ✓ IA"
    if campo in st.session_state["ocr_faltando"]:
        return f"{campo} *  ·  ⚠ não detectado"
    return f"{campo} *"

with st.form("form_cadastro", border=True):
    col1, col2 = st.columns(2)
    with col1:
        tag = st.text_input(
            rotulo("TAG"),
            value=st.session_state.get("ocr_tag", ""),
            placeholder="Ex.: EQ-009",
        )
        modelo = st.text_input(
            rotulo("Modelo"),
            value=st.session_state.get("ocr_modelo", ""),
            placeholder="Ex.: XR-200",
        )
        fab = st.text_input(
            rotulo("Fabricante"),
            value=st.session_state.get("ocr_fab", ""),
            placeholder="Ex.: Siemens",
        )
    with col2:
        pot_val = st.session_state.get("ocr_pot") or None
        ten_val = st.session_state.get("ocr_tensao") or None
        potencia = st.number_input(
            rotulo("Potência (W)"),
            min_value=0, step=50,
            value=int(pot_val) if pot_val else None,
            placeholder="Ex.: 1500",
        )
        tensao = st.number_input(
            rotulo("Tensão (V)"),
            min_value=0, step=1,
            value=int(ten_val) if ten_val else None,
            placeholder="Ex.: 220",
        )

    st.write("")
    col_salvar, col_cancelar = st.columns(2)
    salvar   = col_salvar.form_submit_button("Cadastrar", type="primary", use_container_width=True)
    cancelar = col_cancelar.form_submit_button("Cancelar",                  use_container_width=True)


def _reset_ocr_state():
    for k in ("ocr_tag", "ocr_modelo", "ocr_fab", "ocr_pot", "ocr_tensao", "ocr_texto_bruto"):
        st.session_state[k] = ""
    st.session_state["ocr_extraidos"] = set()
    st.session_state["ocr_faltando"]  = set()


if cancelar:
    _reset_ocr_state()
    st.switch_page("app/pages/consulta_equipamentos.py")

if salvar:
    erros = []
    if not tag.strip():
        erros.append("TAG é obrigatória.")
    elif tag_existe(tag.strip()):
        erros.append(f"Já existe um equipamento com a TAG **{tag.strip().upper()}**.")
    if not modelo.strip():
        erros.append("Modelo é obrigatório.")
    if not fab.strip():
        erros.append("Fabricante é obrigatório.")
    if potencia is None:
        erros.append("Potência é obrigatória.")
    if tensao is None:
        erros.append("Tensão é obrigatória.")
    if area_sel is None:
        erros.append("Selecione Planta e Área.")

    if erros:
        for e in erros:
            st.error(e)
    else:
        img_path = None
        if img_bytes:
            os.makedirs(PLACAS_DIR, exist_ok=True)
            safe_tag = tag.strip().upper().replace("/", "_").replace("\\", "_")
            img_path = os.path.join(PLACAS_DIR, f"{safe_tag}{img_ext or '.jpg'}")
            with open(img_path, "wb") as f:
                f.write(img_bytes)

        adicionar_equipamento({
            "TAG":          tag.strip().upper(),
            "Modelo":       modelo.strip(),
            "Fabricante":   fab.strip(),
            "Potência (W)": int(potencia),
            "Tensão (V)":   int(tensao),
            "area_id":      area_sel["id"],
            "img_placa_path": img_path,
        })
        _reset_ocr_state()
        st.session_state["cadastro_sucesso"] = tag.strip().upper()
        st.switch_page("app/pages/consulta_equipamentos.py")
