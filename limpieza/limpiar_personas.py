"""Limpieza de nombres de personas (`director`, `supervisor`): normaliza formato, no altera el nombre."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"

MARCADOR_VALOR_FALTANTE = "NA"
_ESPACIOS_MULTIPLES = re.compile(r"\s+")
_SOLO_PUNTUACION = re.compile(r"^[.\-_/\\|*]+$")
PLACEHOLDERS_EXACTOS = {
    "SIN DATO", "SIN DATOS", "SIN DIRECTOR", "SIN SUPERVISOR", "SIN NOMBRE",
    "NO TIENE", "PENDIENTE", "N/A", "NA", "NULL", "XX", "XXX", "XXXX", "XXXXX",
}


def _es_no_informativo(texto: str) -> bool:
    return (
        texto == ""
        or texto.upper() in PLACEHOLDERS_EXACTOS
        or bool(_SOLO_PUNTUACION.fullmatch(texto))
    )


def _normalizar_persona(valor: str) -> str:
    if valor is None:
        return MARCADOR_VALOR_FALTANTE

    texto = unicodedata.normalize("NFC", valor)
    texto = texto.replace("\u00a0", " ")  # espacio no separable → espacio normal
    texto = "".join(c for c in texto if unicodedata.category(c) not in ("Cc", "Cf"))
    texto = _ESPACIOS_MULTIPLES.sub(" ", texto).strip()

    if _es_no_informativo(texto):
        return MARCADOR_VALOR_FALTANTE

    return texto.upper()


def _clean_persona(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    df = df.copy()
    raw = f"{columna}_raw"
    if raw not in df.columns:
        df.insert(df.columns.get_loc(columna) + 1, raw, df[columna])
    df[columna] = df[raw].map(_normalizar_persona)
    return df


def clean_director(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza formato de `director`, preserva el original en `director_raw`."""
    return _clean_persona(df, "director")


def clean_supervisor(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza formato de `supervisor`, preserva el original en `supervisor_raw`."""
    return _clean_persona(df, "supervisor")


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _filas_columna(antes: pd.DataFrame, despues: pd.DataFrame, columna: str) -> list[str]:
    espacios_dobles = int(antes[columna].str.contains("  ", regex=False).sum())
    na_final = despues[columna] == MARCADOR_VALOR_FALTANTE
    vacios_originales = int((antes[columna].str.strip() == "").sum())
    no_informativos = int(na_final.sum())
    placeholders = no_informativos - vacios_originales

    return [
        f"| `{columna}` | {espacios_dobles} registros con espacios múltiples internos | "
        f"`strip()` + colapsar espacios múltiples a uno solo | {espacios_dobles} | "
        "Formato: no cambia las letras del nombre, solo normaliza separadores. |",
        f"| `{columna}` | {vacios_originales} vacíos y {placeholders} placeholders no "
        f"informativos (`-`, `.`, `SIN DATO`, `XXX`, etc.) | Se marcan como "
        f"`\"{MARCADOR_VALOR_FALTANTE}\"` | {no_informativos} | No aportan un nombre real; "
        "el original queda en la columna `_raw`. |",
        f"| `{columna}` | Casing y caracteres invisibles (`\\u00a0`, zero-width) | Se quitan "
        "invisibles + NFC + MAYÚSCULAS (decisión del proyecto), sin cambiar las letras del "
        f"nombre | 0 cambios de caja (ya venía en MAYÚSCULAS) | Consistencia con el resto de "
        "columnas de texto; se conserva la ortografía real del nombre. |",
    ]


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_supervisor(clean_director(df_unido))

    filas_reporte = _filas_columna(df_unido, df_limpio, "director") + _filas_columna(
        df_unido, df_limpio, "supervisor"
    )
    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="personas",
        titulo="`director`, `supervisor` (limpiar_personas.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_director()/clean_supervisor() aplicados sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
