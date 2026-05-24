from typing import Optional
from app.services.db import conexao


def _row_to_dict(row) -> dict:
    return {
        "TAG":          row["tag"],
        "Modelo":       row["modelo"],
        "Fabricante":   row["fabricante"],
        "Potência (W)": row["potencia_w"],
        "Tensão (V)":   row["tensao_v"],
        "Planta":       row["planta_nome"] if "planta_nome" in row.keys() else None,
        "Área":         row["area_nome"]   if "area_nome"   in row.keys() else None,
        "area_id":      row["area_id"],
        "img_placa_path": row["img_placa_path"],
    }


_SELECT_BASE = """
SELECT e.tag, e.modelo, e.fabricante, e.potencia_w, e.tensao_v,
       e.area_id, e.img_placa_path,
       a.nome AS area_nome, p.nome AS planta_nome
  FROM equipamentos e
  LEFT JOIN areas    a ON a.id = e.area_id
  LEFT JOIN plantas  p ON p.id = a.planta_id
"""


def get_equipamentos() -> list[dict]:
    with conexao() as con:
        rows = con.execute(_SELECT_BASE + " ORDER BY e.tag").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_equipamento(tag: str) -> Optional[dict]:
    with conexao() as con:
        row = con.execute(_SELECT_BASE + " WHERE e.tag = ?", (tag.upper(),)).fetchone()
    return _row_to_dict(row) if row else None


def listar_por_area(area_id: int) -> list[dict]:
    with conexao() as con:
        rows = con.execute(_SELECT_BASE + " WHERE e.area_id = ? ORDER BY e.tag", (area_id,)).fetchall()
    return [_row_to_dict(r) for r in rows]


def tag_existe(tag: str) -> bool:
    with conexao() as con:
        row = con.execute("SELECT 1 FROM equipamentos WHERE tag = ?", (tag.upper(),)).fetchone()
    return row is not None


def adicionar_equipamento(eq: dict):
    with conexao() as con:
        con.execute(
            """INSERT INTO equipamentos
               (tag, modelo, fabricante, potencia_w, tensao_v, area_id, img_placa_path)
               VALUES (?,?,?,?,?,?,?)""",
            (
                eq["TAG"].upper(),
                eq["Modelo"],
                eq["Fabricante"],
                int(eq["Potência (W)"]),
                int(eq["Tensão (V)"]),
                eq.get("area_id"),
                eq.get("img_placa_path"),
            ),
        )


def atualizar_equipamento(tag: str, campos: dict):
    mapa = {
        "Modelo":       "modelo",
        "Fabricante":   "fabricante",
        "Potência (W)": "potencia_w",
        "Tensão (V)":   "tensao_v",
        "area_id":      "area_id",
        "img_placa_path": "img_placa_path",
    }
    sets, vals = [], []
    for k, v in campos.items():
        col = mapa.get(k)
        if col:
            sets.append(f"{col} = ?")
            vals.append(v)
    if not sets:
        return
    vals.append(tag.upper())
    with conexao() as con:
        con.execute(f"UPDATE equipamentos SET {', '.join(sets)} WHERE tag = ?", vals)


def remover_equipamento(tag: str):
    with conexao() as con:
        con.execute("DELETE FROM equipamentos WHERE tag = ?", (tag.upper(),))


def listar_plantas() -> list[dict]:
    with conexao() as con:
        rows = con.execute("SELECT id, nome FROM plantas ORDER BY nome").fetchall()
    return [{"id": r["id"], "nome": r["nome"]} for r in rows]


def listar_areas(planta_id: Optional[int] = None) -> list[dict]:
    with conexao() as con:
        if planta_id is None:
            rows = con.execute(
                """SELECT a.id, a.nome, a.planta_id, p.nome AS planta_nome
                     FROM areas a JOIN plantas p ON p.id = a.planta_id
                    ORDER BY p.nome, a.nome"""
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT a.id, a.nome, a.planta_id, p.nome AS planta_nome
                     FROM areas a JOIN plantas p ON p.id = a.planta_id
                    WHERE a.planta_id = ?
                    ORDER BY a.nome""",
                (planta_id,),
            ).fetchall()
    return [
        {"id": r["id"], "nome": r["nome"], "planta_id": r["planta_id"], "planta_nome": r["planta_nome"]}
        for r in rows
    ]
