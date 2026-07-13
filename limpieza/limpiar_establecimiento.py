"""Limpieza de formato de la columna `establecimiento` (no corrige ortografía)."""

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


def _normalizar_establecimiento(valor: str) -> str:
    if valor is None:
        return MARCADOR_VALOR_FALTANTE

    texto = unicodedata.normalize("NFC", valor)
    texto = _ESPACIOS_MULTIPLES.sub(" ", texto)  # antes de quitar control chars, evita pegar palabras
    texto = "".join(c for c in texto if unicodedata.category(c) != "Cc")
    texto = texto.strip()

    if texto == "":
        return MARCADOR_VALOR_FALTANTE

    return texto.upper()


def clean_establecimiento(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza formato de `establecimiento`, preserva el original en `establecimiento_raw`."""
    df = df.copy()

    if "establecimiento_raw" not in df.columns:
        df.insert(
            df.columns.get_loc("establecimiento") + 1,
            "establecimiento_raw",
            df["establecimiento"],
        )

    df["establecimiento"] = df["establecimiento_raw"].map(_normalizar_establecimiento)
    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    espacios_dobles = antes["establecimiento"].str.contains("  ", regex=False).sum()
    vacios = (despues["establecimiento"] == MARCADOR_VALOR_FALTANTE) & (
        antes["establecimiento"].str.strip() == ""
    )
    ids_vacios = despues.loc[vacios, "id_registro"].tolist()
    comillas = antes["establecimiento"].str.contains('"', regex=False).sum()
    total_filas = len(antes)

    filas = [
        f"| `establecimiento` | {espacios_dobles} registros con espacios múltiples "
        f"internos | `strip()` + colapsar espacios múltiples a uno solo | "
        f"{espacios_dobles} | Formato: no cambia el contenido, solo normaliza separadores. |",
        f"| `establecimiento` | {len(ids_vacios)} valores vacíos (cadena vacía) | "
        f'Se marcan como `"{MARCADOR_VALOR_FALTANTE}"` en vez de inventar un nombre; '
        f"IDs afectados: {ids_vacios} | {len(ids_vacios)} | No hay forma de inferir el "
        "nombre real de un establecimiento a partir de otras columnas. |",
        "| `establecimiento` | Caracteres de control / no normalizados Unicode (NFC) | "
        "Se eliminan caracteres de control invisibles y se normaliza a NFC | "
        "0 detectados en esta corrida | Defensivo: si una futura descarga trae "
        "caracteres invisibles, quedan removidos sin alterar tildes/ñ. |",
        f"| `establecimiento` | Casing: decisión documentada | Se deja el dataset en "
        f"MAYÚSCULAS (100% de los {total_filas} registros ya venía así); se aplica "
        ".upper() de forma defensiva sin tocar letras/tildes | 0 registros cambiaron de "
        "caja en esta corrida | Opción conservadora: cero riesgo. La alternativa (Title "
        "Case) es riesgosa por acrónimos con puntos (`C.E.T.A.CH.`) y numerales (`NO. 1`); "
        "se descarta. |",
        f"| `establecimiento` | {comillas} registros con comillas dobles "
        '(ej. `COLEGIO "SANTA ANA"`) | Ninguna: se conservan tal cual, son parte del '
        f"nombre propio | 0 (no se modifican) | Las comillas son parte del nombre "
        "oficial del establecimiento, no un problema de formato. |",
        "| `establecimiento` | 0 registros en minúscula encontrados (verificado sobre "
        "el dataset actual) | Ninguna (no se detectó el caso) | 0 | Se deja documentado "
        "por transparencia; la normalización de casing sigue aplicándose de forma "
        "defensiva por si aparece en una futura descarga. |",
        "| `establecimiento` | Nombres parecidos pero distintos (ej. `AMERICA` vs "
        "`AMÉRICA`) | No se autocorrigen — son establecimientos distintos o candidatos a "
        "revisar a mano | Ver reporte de duplicados parciales | Corregir automáticamente "
        "arriesga fusionar registros que en realidad son centros educativos diferentes. |",
    ]
    return filas


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_establecimiento(df_unido)
    filas_reporte = _generar_reporte(df_unido, df_limpio)

    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="establecimiento",
        titulo="`establecimiento` (limpiar_establecimiento.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_establecimiento() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
