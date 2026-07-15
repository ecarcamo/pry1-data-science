"""Limpieza de la columna `municipio`.

- Valida contra catálogo oficial por departamento ya limpio.
- Corrige typos con RapidFuzz (token_sort_ratio >= 90), documentando cada corrección.
- Valores sin match → prefijo REVISAR:.
- Fuera de catálogo → datos/interim/municipios_fuera_catalogo.csv.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"
UMBRAL_FUZZY = 90


def _municipios_de_depto(departamento: str) -> list[str]:
    from limpieza.catalogos import MUNICIPIOS_POR_DEPTO
    return MUNICIPIOS_POR_DEPTO.get(departamento, [])


def _match_municipio(municipio: str, departamento: str) -> tuple[str, str]:
    """Devuelve (canónico, metodo) donde metodo es 'exacto', 'fuzzy' o 'revisar'."""
    import re
    from limpieza.catalogos import lookup_municipio, normalizar_para_comparar
    from rapidfuzz import process, fuzz

    # 1. Match exacto (sin tildes)
    canon = lookup_municipio(municipio, departamento)
    if canon:
        return canon, "exacto"

    # 2. Para patrones "ZONA ##": NO aplicar fuzzy (evita ZONA 24 → ZONA 2)
    if re.match(r"^ZONA\s+\d+$", municipio.strip(), re.IGNORECASE):
        return f"REVISAR:{municipio.strip().upper()}", "revisar"

    # 3. Fuzzy dentro del departamento
    candidatos = _municipios_de_depto(departamento)
    if candidatos:
        resultado = process.extractOne(
            normalizar_para_comparar(municipio),
            [normalizar_para_comparar(c) for c in candidatos],
            scorer=fuzz.token_sort_ratio,
        )
        if resultado and resultado[1] >= UMBRAL_FUZZY:
            idx = resultado[2]
            return candidatos[idx], "fuzzy"

    # 4. Sin match
    return f"REVISAR:{municipio.strip().upper()}", "revisar"


def clean_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza `municipio`, preserva el original en `municipio_raw`.

    Requiere que la columna `departamento` ya esté limpia (clean_departamento primero).
    """
    df = df.copy()

    if "municipio_raw" not in df.columns:
        df.insert(
            df.columns.get_loc("municipio") + 1,
            "municipio_raw",
            df["municipio"],
        )

    resultados = [
        _match_municipio(row["municipio_raw"], row["departamento"])
        for _, row in df[["municipio_raw", "departamento"]].iterrows()
    ]
    df["municipio"] = [r[0] for r in resultados]
    # Columna temporal para el reporte — se elimina antes del limpio final en generar_limpio.py
    df["_metodo_municipio"] = [r[1] for r in resultados]
    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    total = len(antes)
    exactos = (despues["_metodo_municipio"] == "exacto").sum()
    fuzzy   = (despues["_metodo_municipio"] == "fuzzy").sum()
    revisar = (despues["_metodo_municipio"] == "revisar").sum()

    filas = [
        f"| `municipio` | {total} registros validados contra catálogo oficial (~340 municipios) "
        f"| Match exacto sin tildes contra catálogo por departamento | {exactos} correctos | "
        f"Catálogo oficial INE. Comparación normalizada (sin tildes/mayúsculas); valor canónico "
        f"guardado con tildes y MAYÚSCULAS. |",

        f"| `municipio` | {fuzzy} registros con typos (nombre casi correcto) | "
        f"Corrección con RapidFuzz `token_sort_ratio ≥ {UMBRAL_FUZZY}` dentro del mismo "
        f"departamento; original en `municipio_raw` | {fuzzy} | Umbral conservador para "
        f"minimizar correcciones incorrectas. Cada corrección es auditable via municipio_raw. |",

        f"| `municipio` | {revisar} registros sin match suficiente en catálogo | "
        f"Se marcan con prefijo `REVISAR:` (no se borran); exportados a "
        f"`datos/interim/municipios_fuera_catalogo.csv` | {revisar} | "
        f"Sin información suficiente para corregir automáticamente. |",
    ]
    return filas


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown
    from limpieza.limpiar_departamento import clean_departamento

    df_unido = _leer_unido(UNIDO_CSV)

    # Departamento debe ir primero
    df_con_depto = clean_departamento(df_unido)
    df_limpio = clean_municipio(df_con_depto)

    # Reporte de fuera de catálogo
    INTERIM = PROJECT_ROOT / "datos" / "interim"
    fuera = df_limpio[df_limpio["_metodo_municipio"] == "revisar"]
    if len(fuera):
        fuera[["id_registro", "departamento", "municipio_raw", "municipio"]].to_csv(
            INTERIM / "municipios_fuera_catalogo.csv", index=False, encoding="utf-8-sig"
        )
        print(f"⚠  {len(fuera)} municipios fuera de catálogo → datos/interim/municipios_fuera_catalogo.csv")

    # Correcciones fuzzy
    fuzzy_df = df_limpio[df_limpio["_metodo_municipio"] == "fuzzy"]
    if len(fuzzy_df):
        fuzzy_df[["id_registro", "departamento", "municipio_raw", "municipio"]].to_csv(
            INTERIM / "municipios_corregidos_fuzzy.csv", index=False, encoding="utf-8-sig"
        )
        print(f"✓  {len(fuzzy_df)} correcciones fuzzy → datos/interim/municipios_corregidos_fuzzy.csv")

    filas_reporte = _generar_reporte(df_unido, df_limpio)
    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="municipio",
        titulo="`municipio` (limpiar_municipio.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_municipio() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado → {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
    print(f"\nMétodos: exacto={( df_limpio['_metodo_municipio']=='exacto').sum()}, "
          f"fuzzy={( df_limpio['_metodo_municipio']=='fuzzy').sum()}, "
          f"revisar={( df_limpio['_metodo_municipio']=='revisar').sum()}")
