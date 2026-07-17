"""Limpieza de categóricas (`sector`, `area`, `status`, `modalidad`, `jornada`, `plan`).

Normaliza formato (NFC, espacios, MAYÚSCULAS) y unifica cada valor a un set canónico
explícito. Los datos del MINEDUC ya vienen en MAYÚSCULAS y consistentes, así que el
mapeo actúa además como guardia documentada para futuras descargas.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"

_ESPACIOS_MULTIPLES = re.compile(r"\s+")

# Set canónico por columna (valores observados en el dataset, en MAYÚSCULAS).
CATEGORIAS_CANONICAS: dict[str, set[str]] = {
    "sector": {"PRIVADO", "OFICIAL", "COOPERATIVA", "MUNICIPAL"},
    "area": {"URBANA", "RURAL", "SIN ESPECIFICAR"},
    "status": {
        "ABIERTA", "CERRADA TEMPORALMENTE", "CERRADA DEFINITIVAMENTE",
        "TEMPORAL TITULOS", "TEMPORAL NOMBRAMIENTO",
    },
    "modalidad": {"MONOLINGUE", "BILINGUE"},
    "jornada": {"DOBLE", "VESPERTINA", "MATUTINA", "SIN JORNADA", "NOCTURNA", "INTERMEDIA"},
    "plan": {
        "DIARIO(REGULAR)", "FIN DE SEMANA", "SEMIPRESENCIAL (FIN DE SEMANA)",
        "SEMIPRESENCIAL (UN DÍA A LA SEMANA)", "A DISTANCIA", "SEMIPRESENCIAL",
        "VIRTUAL A DISTANCIA", "SEMIPRESENCIAL (DOS DÍAS A LA SEMANA)", "SABATINO",
        "DOMINICAL", "MIXTO", "IRREGULAR", "INTERCALADO",
    },
}

# Mapeo explícito variante -> canónico (además de la normalización de formato).
# Unifica diferencias de escritura que la normalización básica no cubre
# (el caso "Guatemala"/"GUATEMALA" aplicado a categóricas). Documentado y auditable.
MAPEOS: dict[str, dict[str, str]] = {
    "sector": {"PRIVADA": "PRIVADO", "OFICIALES": "OFICIAL"},
    "area": {"URBANO": "URBANA", "RURALES": "RURAL", "N/E": "SIN ESPECIFICAR"},
    "status": {"CERRADA TEMPORAL": "CERRADA TEMPORALMENTE"},
    "modalidad": {"MONOLINGÜE": "MONOLINGUE", "BILINGÜE": "BILINGUE"},
    "jornada": {"S/J": "SIN JORNADA"},
    "plan": {"DIARIO (REGULAR)": "DIARIO(REGULAR)", "REGULAR": "DIARIO(REGULAR)"},
}

COLUMNAS = list(CATEGORIAS_CANONICAS.keys())


def _normalizar_categoria(valor: str, columna: str) -> str:
    if valor is None:
        return "REVISAR:None"

    texto = unicodedata.normalize("NFC", valor)
    texto = "".join(c for c in texto if unicodedata.category(c) not in ("Cc", "Cf"))
    texto = _ESPACIOS_MULTIPLES.sub(" ", texto).strip().upper()

    texto = MAPEOS[columna].get(texto, texto)

    if texto in CATEGORIAS_CANONICAS[columna]:
        return texto
    return f"REVISAR:{texto}"


def clean_categoricas(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza y unifica cada categórica a su set canónico documentado."""
    df = df.copy()
    for columna in COLUMNAS:
        df[columna] = df[columna].map(lambda v, c=columna: _normalizar_categoria(v, c))
    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    filas = []
    for columna in COLUMNAS:
        unicos_antes = antes[columna].nunique()
        unicos_despues = despues[columna].nunique()
        remapeados = int((antes[columna].str.strip().str.upper() != despues[columna]).sum())
        revisar = int(despues[columna].str.startswith("REVISAR:").sum())
        canonicos = ", ".join(sorted(CATEGORIAS_CANONICAS[columna]))

        filas.append(
            f"| `{columna}` | {unicos_antes} variantes de escritura observadas | "
            f"Normalización (NFC, espacios, MAYÚSCULAS) + mapeo a set canónico "
            f"({unicos_despues} categorías): {{{canonicos}}}. Fuera de catálogo → "
            f"`REVISAR:` | {remapeados} valores normalizados/unificados, {revisar} marcados "
            "REVISAR | Elimina categorías duplicadas por diferencias de escritura; el set "
            "canónico documenta el dominio permitido. |"
        )
    return filas


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_categoricas(df_unido)
    filas_reporte = _generar_reporte(df_unido, df_limpio)

    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="categoricas",
        titulo="Categóricas: `sector`, `area`, `status`, `modalidad`, `jornada`, `plan` (limpiar_categoricas.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_categoricas() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
