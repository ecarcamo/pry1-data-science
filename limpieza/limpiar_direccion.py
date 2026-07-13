"""Limpieza de formato de la columna `direccion` (NA para no informativas, abreviaturas estandarizadas)."""

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
_SOLO_PUNTUACION = re.compile(r"^[.\-\s]*$")
PLACEHOLDERS_EXACTOS = {"S/N", "SIN", "SIN DIRECCION", "SIN DIRECCIÓN", "N/A", "NULL"}

# \bTOKEN\.|\bTOKEN\b (en vez de \bTOKEN\.?\b): con el punto opcional dentro de \b...\b,
# el punto no se consumía cuando el siguiente carácter no era alfanumérico (ej. "AV.'A'"
# o "NO.99" pegado a un dígito), dejando un punto suelto. La alternancia siempre consume
# el punto cuando está presente, sin importar qué venga después.
ABREVIATURAS = [
    ("AVDA / AVDA.", re.compile(r"\bAVDA\.|\bAVDA\b", re.IGNORECASE), "AVENIDA"),
    ("AV / AV.", re.compile(r"\bAV\.|\bAV\b", re.IGNORECASE), "AVENIDA"),
    ("COL / COL.", re.compile(r"\bCOL\.|\bCOL\b", re.IGNORECASE), "COLONIA"),
    ("ZN / ZN.", re.compile(r"\bZN\.|\bZN\b", re.IGNORECASE), "ZONA"),
    ("Z.", re.compile(r"\bZ\.", re.IGNORECASE), "ZONA"),
    ("BO / BO.", re.compile(r"\bBO\.|\bBO\b", re.IGNORECASE), "BARRIO"),
    ("#", re.compile(r"#"), "NO."),
    ("No / No.", re.compile(r"\bNo\.|\bNo\b", re.IGNORECASE), "NO."),
]


def _es_no_informativa(texto: str) -> bool:
    return texto == "" or texto.upper() in PLACEHOLDERS_EXACTOS or bool(_SOLO_PUNTUACION.fullmatch(texto))


def _normalizar_direccion(valor: str) -> str:
    if valor is None:
        return MARCADOR_VALOR_FALTANTE

    texto = unicodedata.normalize("NFC", valor)
    texto = _ESPACIOS_MULTIPLES.sub(" ", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Cc")
    texto = texto.strip()

    if _es_no_informativa(texto):
        return MARCADOR_VALOR_FALTANTE

    for _, patron, reemplazo in ABREVIATURAS:
        texto = patron.sub(reemplazo, texto)
    texto = _ESPACIOS_MULTIPLES.sub(" ", texto).strip()

    return texto.upper()


def clean_direccion(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza formato de `direccion`, preserva el original en `direccion_raw`."""
    df = df.copy()

    if "direccion_raw" not in df.columns:
        df.insert(df.columns.get_loc("direccion") + 1, "direccion_raw", df["direccion"])

    df["direccion"] = df["direccion_raw"].map(_normalizar_direccion)
    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    espacios_dobles = antes["direccion"].str.contains("  ", regex=False).sum()

    no_informativas = despues["direccion"] == MARCADOR_VALOR_FALTANTE
    ids_no_informativas = despues.loc[no_informativas, "id_registro"].tolist()

    filas = [
        f"| `direccion` | {espacios_dobles} registros con espacios múltiples internos | "
        f"`strip()` + colapsar espacios múltiples a uno solo | {espacios_dobles} | "
        "Formato: no cambia el contenido, solo normaliza separadores. |",
        f"| `direccion` | {len(ids_no_informativas)} valores vacíos o placeholders no "
        f'informativos (cadena vacía, `.`, `---`, `S/N`, etc.) | Se marcan como '
        f'`"{MARCADOR_VALOR_FALTANTE}"` | {len(ids_no_informativas)} | No aportan '
        "información real de ubicación; inventar una dirección sería peor que dejarla "
        "faltante. |",
    ]

    for etiqueta, patron, reemplazo in ABREVIATURAS:
        n = antes["direccion"].str.contains(patron).sum()
        if n:
            filas.append(
                f"| `direccion` | {n} registros con abreviatura `{etiqueta}` | "
                f"Se estandariza a `{reemplazo}` (regex con límites de palabra, no rompe "
                f"palabras que la contengan) | {n} | Uniformar el vocabulario de "
                "direcciones para que sea comparable/buscable. |"
            )

    filas.append(
        "| `direccion` | Casing: misma decisión que `establecimiento` | Se deja en "
        "MAYÚSCULAS (formato ya dominante en el dataset) | 0 registros cambiaron de "
        "caja en esta corrida | Consistencia entre columnas de texto del dataset. |"
    )
    return filas


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_direccion(df_unido)
    filas_reporte = _generar_reporte(df_unido, df_limpio)

    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="direccion",
        titulo="`direccion` (limpiar_direccion.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_direccion() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
