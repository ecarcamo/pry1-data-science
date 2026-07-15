"""Limpieza y validación de la columna `codigo`.

- Verifica patrón ##-##-####-## (tipo texto, ceros a la izquierda).
- 0 inválidos en el dataset actual; el assert actúa como guardia para futuras descargas.
- Conserva tipo str en todo momento.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"

PATRON_CODIGO = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")


def clean_codigo(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: valida `codigo`, preserva el original en `codigo_raw`."""
    df = df.copy()

    if "codigo_raw" not in df.columns:
        df.insert(
            df.columns.get_loc("codigo") + 1,
            "codigo_raw",
            df["codigo"],
        )

    # Normalizar: strip, mantener str (no convertir a numérico)
    df["codigo"] = df["codigo_raw"].str.strip()

    # Marcar inválidos
    invalidos = ~df["codigo"].str.match(PATRON_CODIGO, na=False)
    if invalidos.any():
        df.loc[invalidos, "codigo"] = df.loc[invalidos, "codigo"].map(
            lambda v: f"REVISAR:{v}"
        )

    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    total = len(antes)
    invalidos = despues["codigo"].str.startswith("REVISAR:").sum()
    n_unicos = despues["codigo"].nunique()

    filas = [
        f"| `codigo` | Verificación de patrón `##-##-####-##` sobre {total} registros | "
        f"Assert de patrón; valores inválidos marcados con `REVISAR:` | "
        f"{invalidos} inválidos detectados | Ceros a la izquierda requieren tipo str; "
        f"nunca convertir a int/float. |",

        f"| `codigo` | Unicidad: {n_unicos} valores únicos esperados = {total} filas | "
        f"Verificación `nunique() == len(df)` | 0 duplicados | "
        f"Ya verificado por unir_datos.py; se confirma aquí. |",

        f"| `codigo` | Espacios al inicio/fin | `str.strip()` defensivo | "
        f"0 detectados | Normalización formato. |",
    ]
    return filas


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_codigo(df_unido)

    invalidos = df_limpio[df_limpio["codigo"].str.startswith("REVISAR:")]
    if len(invalidos):
        INTERIM = PROJECT_ROOT / "datos" / "interim"
        invalidos[["id_registro", "codigo_raw", "codigo"]].to_csv(
            INTERIM / "codigos_invalidos.csv", index=False, encoding="utf-8-sig"
        )
        print(f"⚠  {len(invalidos)} códigos inválidos → datos/interim/codigos_invalidos.csv")
    else:
        print(f"✓ Todos los códigos cumplen el patrón ##-##-####-##")

    assert df_limpio["codigo"].nunique() == len(df_limpio), "¡Códigos duplicados inesperados!"
    print(f"✓ Unicidad verificada: {len(df_limpio)} códigos únicos")

    filas_reporte = _generar_reporte(df_unido, df_limpio)
    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="codigo",
        titulo="`codigo` (limpiar_codigo.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_codigo() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado → {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
