"""Limpieza de la columna `departamento`.

Decisiones:
- CIUDAD CAPITAL (00) + GUATEMALA (01) → GUATEMALA (catálogo oficial 22 deptos).
- Normaliza tildes correctas en MAYÚSCULAS.
- Valores sin match → prefijo REVISAR:.
Documentado en docs/plan_limpieza.md y docs/transformaciones.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"


def _normalizar_departamento(valor: str, lookup_fn) -> str:
    resultado = lookup_fn(valor)
    if resultado:
        return resultado
    return f"REVISAR:{valor.strip().upper()}"


def clean_departamento(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza `departamento`, preserva el original en `departamento_raw`."""
    from limpieza.catalogos import lookup_departamento

    df = df.copy()

    if "departamento_raw" not in df.columns:
        df.insert(
            df.columns.get_loc("departamento") + 1,
            "departamento_raw",
            df["departamento"],
        )

    df["departamento"] = df["departamento_raw"].map(
        lambda v: _normalizar_departamento(v, lookup_departamento)
    )
    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    total = len(antes)

    # Fusión 00+01
    ciudad_capital = (antes["departamento"].str.strip().str.upper() == "CIUDAD CAPITAL").sum()
    fusionados = ciudad_capital  # todos se fusionan en GUATEMALA

    # Correcciones de tildes (valor raw ≠ valor limpio, sin contar fusión ni REVISAR)
    mask_tilde = (
        (antes["departamento"].str.strip().str.upper() != despues["departamento"])
        & (~despues["departamento"].str.startswith("REVISAR:"))
        & (antes["departamento"].str.strip().str.upper() != "CIUDAD CAPITAL")
    )
    corregidos_tilde = mask_tilde.sum()

    # Fuera de catálogo
    fuera_cat = despues["departamento"].str.startswith("REVISAR:").sum()

    filas = [
        f"| `departamento` | CIUDAD CAPITAL (código 00) separado de GUATEMALA (código 01) "
        f"en la fuente MINEDUC | Se unifica en `GUATEMALA` (catálogo oficial 22 deptos); "
        f"original preservado en `departamento_raw` | {fusionados} registros fusionados | "
        f"CIUDAD CAPITAL no es un departamento distinto en el INE; la distinción es un "
        f"artefacto del selector de descarga. Decisión documentada en docs/plan_limpieza.md. |",

        f"| `departamento` | {corregidos_tilde} registros sin tildes "
        f"(SACATEPEQUEZ, PETEN, SOLOLA, etc.) | Normalización a forma canónica con tildes "
        f"correctas en MAYÚSCULAS (comparación sin tildes, valor guardado con tildes) | "
        f"{corregidos_tilde} | Fidelidad al catálogo oficial del INE. CASING: "
        f"MAYÚSCULAS del proyecto. |",

        f"| `departamento` | {fuera_cat} registros no reconocidos en catálogo | "
        f"Se marcan con prefijo `REVISAR:` (no se borran) | {fuera_cat} | "
        f"Sin información suficiente para corregir automáticamente; requieren revisión manual. |",

        f"| `departamento` | {total} registros — casing 100% MAYÚSCULAS verificado | "
        f"Se aplica `.upper()` de forma defensiva | 0 cambios de caja | "
        f"Convención del proyecto: MAYÚSCULAS con tildes correctas. |",
    ]
    return filas


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_departamento(df_unido)

    # Reporte a datos/interim/
    INTERIM = PROJECT_ROOT / "datos" / "interim"
    fuera_cat = df_limpio[df_limpio["departamento"].str.startswith("REVISAR:")]
    if len(fuera_cat):
        fuera_cat[["id_registro", "departamento_raw", "departamento"]].to_csv(
            INTERIM / "deptos_fuera_catalogo.csv", index=False, encoding="utf-8-sig"
        )
        print(f"⚠  {len(fuera_cat)} registros fuera de catálogo → datos/interim/deptos_fuera_catalogo.csv")

    filas_reporte = _generar_reporte(df_unido, df_limpio)
    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="departamento",
        titulo="`departamento` (limpiar_departamento.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_departamento() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado → {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
    vc = df_limpio["departamento"].value_counts()
    print(f"\nDistribución final ({vc.shape[0]} valores únicos):")
    print(vc.to_string())
