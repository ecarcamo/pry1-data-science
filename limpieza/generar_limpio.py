"""Orquestador integrador — genera el conjunto limpio consolidado (Actividad 9).

Aplica en orden todas las funciones de limpieza sobre el CSV unido crudo y
escribe el resultado en datos/clean/establecimientos_diversificado_limpio.csv.

Uso:
    python limpieza/generar_limpio.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

UNIDO_CSV  = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
LIMPIO_CSV = PROJECT_ROOT / "datos" / "clean" / "establecimientos_diversificado_limpio.csv"

# Columnas temporales generadas durante la limpieza que no van al limpio final
_COLS_TEMPORALES = ["_metodo_municipio"]


def _leer_unido() -> pd.DataFrame:
    return pd.read_csv(
        UNIDO_CSV, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[]
    )


def _aplicar_limpiezas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas las funciones de limpieza en el orden correcto."""
    # --- Esteban ---
    from limpieza.limpiar_establecimiento import clean_establecimiento
    from limpieza.limpiar_direccion import clean_direccion
    from limpieza.duplicados import detectar_duplicados

    # --- Ernesto ---
    from limpieza.limpiar_departamento import clean_departamento
    from limpieza.limpiar_municipio import clean_municipio
    from limpieza.limpiar_codigo import clean_codigo
    from limpieza.limpiar_distrito_departamental_nivel import clean_distrito_departamental_nivel

    print("Aplicando limpiezas de Esteban...")
    df = clean_establecimiento(df)
    df = clean_direccion(df)

    print("Aplicando limpiezas de Ernesto...")
    df = clean_departamento(df)
    df = clean_municipio(df)
    df = clean_codigo(df)
    df = clean_distrito_departamental_nivel(df)

    # --- Hugo ---
    from limpieza.limpiar_telefono import clean_telefono
    from limpieza.limpiar_personas import clean_director, clean_supervisor
    from limpieza.limpiar_categoricas import clean_categoricas

    print("Aplicando limpiezas de Hugo (telefono, personas, categóricas)...")
    df = clean_telefono(df)
    df = clean_director(df)
    df = clean_supervisor(df)
    df = clean_categoricas(df)

    # Reporte de duplicados parciales
    print("Generando reporte de duplicados...")
    detectar_duplicados(df)

    return df


def _remover_temporales(df: pd.DataFrame) -> pd.DataFrame:
    cols_a_drop = [c for c in _COLS_TEMPORALES if c in df.columns]
    return df.drop(columns=cols_a_drop)


def _correr_validaciones(df: pd.DataFrame) -> None:
    """Corre las validaciones básicas antes de escribir el limpio."""
    import re
    from limpieza.catalogos import DEPARTAMENTOS, normalizar_para_comparar

    patron = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")

    errores = []

    # Sin duplicados exactos
    cols = [c for c in df.columns if c not in ("id_registro", "archivo_origen")]
    n_dup = df[cols].duplicated().sum()
    if n_dup:
        errores.append(f"  {n_dup} duplicados exactos")

    # Sin espacios al inicio/fin
    for col in [c for c in df.columns if c not in ("id_registro",)]:
        n = (df[col] != df[col].str.strip()).sum()
        if n:
            errores.append(f"  {col}: {n} valores con espacios al inicio/fin")

    # nivel solo DIVERSIFICADO
    vals_nivel = df["nivel"].unique().tolist()
    if vals_nivel != ["DIVERSIFICADO"]:
        errores.append(f"  nivel tiene valores inesperados: {vals_nivel}")

    # códigos con patrón
    invalidos_cod = (~(df["codigo"].str.match(patron) | df["codigo"].str.startswith("REVISAR:"))).sum()
    if invalidos_cod:
        errores.append(f"  {invalidos_cod} códigos fuera de patrón")

    if errores:
        raise RuntimeError("Validaciones fallidas:\n" + "\n".join(errores))

    print(f"✓ Validaciones OK — {len(df):,} filas limpias.")


def main() -> None:
    assert UNIDO_CSV.exists(), (
        f"No se encontró {UNIDO_CSV}. "
        "Ejecutá primero: python automatizacion/unir_datos.py"
    )

    print(f"Leyendo: {UNIDO_CSV.name} …")
    df = _leer_unido()
    print(f"  {len(df):,} filas × {df.shape[1]} columnas cargadas.")

    df = _aplicar_limpiezas(df)
    df = _remover_temporales(df)

    _correr_validaciones(df)

    LIMPIO_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(LIMPIO_CSV, index=False, encoding="utf-8-sig")
    print(f"✓ Limpio guardado → {LIMPIO_CSV.relative_to(PROJECT_ROOT)}")
    print(f"  Columnas finales ({df.shape[1]}): {list(df.columns)}")


if __name__ == "__main__":
    main()
