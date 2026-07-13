"""Detección de duplicados exactos y candidatos a duplicado parcial. No modifica ni elimina filas."""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from limpieza.limpiar_establecimiento import MARCADOR_VALOR_FALTANTE
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"
REPORTE_CSV = PROJECT_ROOT / "datos" / "interim" / "duplicados_parciales_revisar.csv"
REPORTE_README = PROJECT_ROOT / "datos" / "interim" / "README.md"

COLUMNAS_ORIGINALES = [
    "codigo", "distrito", "departamento", "municipio", "establecimiento",
    "direccion", "telefono", "supervisor", "director", "nivel", "sector",
    "area", "status", "modalidad", "jornada", "plan", "departamental",
]
COLUMNAS_REPORTE = [
    "id_registro_a", "id_registro_b", "codigo_a", "codigo_b",
    "establecimiento_a", "establecimiento_b", "jornada_a", "jornada_b",
    "plan_a", "plan_b", "score", "decision",
]

UMBRAL_MINIMO = 88
UMBRAL_MAXIMO = 100  # exclusivo: 100 (mismo nombre exacto) se considera aparte, no se reporta aquí


def _clave_comparacion(texto: str) -> str:
    # No se quitan tildes: si "AMERICA" y "AMÉRICA" quedaran idénticas, el score
    # sería 100 y el par se excluiría por UMBRAL_MAXIMO, justo lo contrario de lo
    # que se busca (son el caso típico que este reporte debe capturar).
    return unicodedata.normalize("NFC", texto).upper().strip()


def contar_duplicados_exactos(df: pd.DataFrame) -> int:
    return int(df.duplicated(subset=COLUMNAS_ORIGINALES).sum())


def _candidatos_de_bloque(grupo: pd.DataFrame, umbral_min: int, umbral_max: int) -> list[dict]:
    grupo = grupo[grupo["establecimiento"] != MARCADOR_VALOR_FALTANTE].reset_index(drop=True)
    if len(grupo) < 2:
        return []

    claves = grupo["establecimiento"].map(_clave_comparacion).tolist()
    matriz = process.cdist(claves, claves, scorer=fuzz.token_sort_ratio)

    n = len(claves)
    i_idx, j_idx = np.triu_indices(n, k=1)
    scores = matriz[i_idx, j_idx]
    mascara = (scores >= umbral_min) & (scores < umbral_max)

    candidatos = []
    for i, j, score in zip(i_idx[mascara], j_idx[mascara], scores[mascara]):
        a, b = grupo.iloc[int(i)], grupo.iloc[int(j)]
        candidatos.append({
            "id_registro_a": a["id_registro"], "id_registro_b": b["id_registro"],
            "codigo_a": a["codigo"], "codigo_b": b["codigo"],
            "establecimiento_a": a["establecimiento"], "establecimiento_b": b["establecimiento"],
            "jornada_a": a["jornada"], "jornada_b": b["jornada"],
            "plan_a": a["plan"], "plan_b": b["plan"],
            "score": round(float(score), 1), "decision": "",
        })
    return candidatos


def detectar_duplicados(
    df: pd.DataFrame, umbral_min: int = UMBRAL_MINIMO, umbral_max: int = UMBRAL_MAXIMO
) -> pd.DataFrame:
    columnas = ["id_registro", "codigo", "establecimiento", "departamento", "municipio", "jornada", "plan"]
    candidatos = []
    for _, grupo in df[columnas].groupby(["departamento", "municipio"]):
        candidatos.extend(_candidatos_de_bloque(grupo, umbral_min, umbral_max))

    reporte = pd.DataFrame(candidatos, columns=COLUMNAS_REPORTE)
    if not reporte.empty:
        reporte = reporte.sort_values("score", ascending=False).reset_index(drop=True)
    return reporte


GUIA_INTERPRETACION = """# Reporte de duplicados parciales

`duplicados_parciales_revisar.csv` contiene pares de registros cuyo `establecimiento`
(ya limpio) tiene una similitud (RapidFuzz `token_sort_ratio`) entre 88 y 100 (sin
incluir 100), dentro del mismo `departamento` + `municipio`. Las tildes NO se quitan
para la comparación (a propósito: diferencias de tildes, como "AMERICA" vs "AMÉRICA",
son justo el tipo de caso casi-idéntico que este reporte debe capturar). No incluye
pares con nombre idéntico (score 100): esos son mayoritariamente el mismo centro con
varios códigos (jornada/plan/modalidad distintos) y no ameritan revisión caso por caso.

Este script **no decide ni borra nada**. Ordena los pares por `score` descendente
para que alguien los revise a mano y llene la columna `decision` con uno de:
`conservar` (son establecimientos distintos), `fusionar` o `revisar`.

Guía orientativa:
- Nombre casi igual + códigos distintos + jornada/plan distintos → probablemente
  **legítimo** (mismo centro, varios códigos) → `conservar`.
- Nombre casi igual + mismo municipio + misma jornada y mismo plan → **sospechoso** →
  `revisar`.
"""


if __name__ == "__main__":
    from limpieza.limpiar_direccion import clean_direccion
    from limpieza.limpiar_establecimiento import clean_establecimiento
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = pd.read_csv(UNIDO_CSV, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])
    df_limpio = clean_direccion(clean_establecimiento(df_unido))

    exactos = contar_duplicados_exactos(df_limpio)
    reporte = detectar_duplicados(df_limpio)

    REPORTE_CSV.parent.mkdir(parents=True, exist_ok=True)
    reporte.to_csv(REPORTE_CSV, index=False, encoding="utf-8-sig")
    REPORTE_README.write_text(GUIA_INTERPRETACION, encoding="utf-8")

    filas_doc = [
        f"| (todas) | Duplicados exactos (17 columnas originales) | Ninguna: se cuentan y "
        f"documentan, no se eliminan | {exactos} | El `codigo` ya es único por diseño del "
        "sitio del MINEDUC; se confirma que no hay filas 100% idénticas. |",
        f"| `establecimiento` | {len(reporte)} pares candidatos a duplicado parcial "
        "(similitud 88-99 dentro del mismo departamento+municipio, RapidFuzz "
        "`token_sort_ratio`) | Se generan en `datos/interim/duplicados_parciales_revisar.csv` "
        f"para revisión manual (columna `decision`) | {len(reporte)} | No se fusionan ni "
        "eliminan automáticamente: nombres muy parecidos suelen ser el mismo centro con "
        "varios códigos (jornada/plan distinto), y una fusión automática podría borrar "
        "establecimientos reales que solo coinciden en nombre. |",
    ]
    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="duplicados",
        titulo="Duplicados exactos y parciales (duplicados.py)",
        filas_tabla=filas_doc,
    )

    print(f"Duplicados exactos: {exactos}")
    print(f"Candidatos a duplicado parcial: {len(reporte)}")
    print(f"Reporte -> {REPORTE_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
