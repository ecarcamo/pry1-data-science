"""Pruebas automáticas de validación sobre el conjunto limpio (Actividad 7).

Ejecutar: pytest tests/test_validacion.py
Requiere: datos/clean/establecimientos_diversificado_limpio.csv
          (generado por limpieza/generar_limpio.py)
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIMPIO_CSV = PROJECT_ROOT / "datos" / "clean" / "establecimientos_diversificado_limpio.csv"
PATRON_CODIGO = re.compile(r"^\d{2}-\d{2}-\d{4}-\d{2}$")
PATRON_TELEFONO = re.compile(r"^\d{4}-\d{4}$")


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    assert LIMPIO_CSV.exists(), (
        f"No se encontró el CSV limpio en {LIMPIO_CSV}. "
        "Ejecutá primero: python limpieza/generar_limpio.py"
    )
    return pd.read_csv(
        LIMPIO_CSV, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[]
    )


def test_sin_duplicados_exactos(df):
    """No debe haber filas duplicadas (excluyendo id_registro y archivo_origen)."""
    cols = [c for c in df.columns if c not in ("id_registro", "archivo_origen")]
    n_dup = df[cols].duplicated().sum()
    assert n_dup == 0, f"Se encontraron {n_dup} duplicados exactos inesperados."


def test_sin_espacios_al_inicio_fin(df):
    """Ninguna columna de texto debe tener espacios al inicio o fin."""
    cols_texto = [c for c in df.columns if c not in ("id_registro",)]
    problemas = {}
    for col in cols_texto:
        n = (df[col] != df[col].str.strip()).sum()
        if n > 0:
            problemas[col] = n
    assert not problemas, f"Columnas con espacios al inicio/fin: {problemas}"


def test_departamentos_en_catalogo(df):
    """Todos los departamentos deben estar en el catálogo oficial (22) o marcados REVISAR:."""
    from limpieza.catalogos import DEPARTAMENTOS
    validos = set(DEPARTAMENTOS) | {d for d in df["departamento"].unique() if d.startswith("REVISAR:")}
    fuera = df[~df["departamento"].isin(validos)]["departamento"].unique()
    assert len(fuera) == 0, f"Departamentos no reconocidos: {fuera.tolist()}"


def test_municipios_sin_escritura_duplicada(df):
    """No debe haber municipios duplicados por diferencias de escritura (sin tildes)."""
    from limpieza.catalogos import normalizar_para_comparar
    pares_problema = []
    for depto, grupo in df.groupby("departamento"):
        muns = grupo["municipio"].unique()
        normalizados = [normalizar_para_comparar(m) for m in muns if not m.startswith("REVISAR:")]
        if len(normalizados) != len(set(normalizados)):
            pares_problema.append(depto)
    assert not pares_problema, (
        f"Municipios con variantes de escritura en: {pares_problema}"
    )


def test_codigo_patron(df):
    """Todos los códigos deben cumplir ##-##-####-## o estar marcados REVISAR:."""
    validos = df["codigo"].str.match(PATRON_CODIGO) | df["codigo"].str.startswith("REVISAR:")
    n_invalidos = (~validos).sum()
    assert n_invalidos == 0, (
        f"{n_invalidos} códigos no cumplen el patrón ##-##-####-##."
    )


def test_codigo_tipo_texto(df):
    """El código debe permanecer como texto (nunca se convirtió a int)."""
    assert pd.api.types.is_string_dtype(df["codigo"]), "codigo no es tipo texto."
    # Verificar que los ceros a la izquierda se conservan
    con_cero = df["codigo"].str.startswith("0")
    assert con_cero.any(), "No se encontró ningún código con cero a la izquierda."


def test_nivel_solo_diversificado(df):
    """El campo nivel debe contener únicamente 'DIVERSIFICADO'."""
    valores = df["nivel"].unique().tolist()
    assert valores == ["DIVERSIFICADO"], (
        f"nivel contiene valores inesperados: {valores}"
    )


def test_tipos_esperados_son_texto(df):
    """Todas las columnas deben ser tipo texto (str/object/StringDtype)."""
    no_texto = [c for c in df.columns if not pd.api.types.is_string_dtype(df[c])]
    assert not no_texto, f"Columnas con tipo no-texto: {no_texto}"


def test_sin_categorias_duplicadas_por_casing(df):
    """No deben coexistir variantes del mismo valor con distinto casing en categóricas."""
    CATEGORICAS = ["departamento", "nivel", "sector", "area", "status", "modalidad", "jornada", "plan"]
    problemas = {}
    for col in CATEGORICAS:
        if col not in df.columns:
            continue
        vals = df[col].unique()
        normalizados = [v.upper() for v in vals]
        if len(normalizados) != len(set(normalizados)):
            problemas[col] = [v for v in vals if normalizados.count(v.upper()) > 1]
    assert not problemas, f"Categorías duplicadas por casing: {problemas}"


def test_telefono_formato(df):
    """Cada telefono debe cumplir ####-#### o ser 'NA'."""
    validos = df["telefono"].str.match(PATRON_TELEFONO) | (df["telefono"] == "NA")
    n_invalidos = int((~validos).sum())
    assert n_invalidos == 0, f"{n_invalidos} teléfonos con formato distinto de ####-#### o NA."


def test_telefono_adicionales_formato(df):
    """telefono_adicionales debe ser 'NA' o números ####-#### separados por '; '."""
    def _ok(v: str) -> bool:
        if v == "NA":
            return True
        return all(PATRON_TELEFONO.match(p) for p in v.split("; "))

    invalidos = df.loc[~df["telefono_adicionales"].map(_ok), "telefono_adicionales"].unique()
    assert len(invalidos) == 0, f"telefono_adicionales con formato inesperado: {invalidos.tolist()}"


def test_categoricas_en_dominio(df):
    """Cada categórica debe estar en su set canónico o marcada REVISAR:."""
    from limpieza.limpiar_categoricas import CATEGORIAS_CANONICAS

    fuera = {}
    for col, canonicos in CATEGORIAS_CANONICAS.items():
        validos = canonicos | {v for v in df[col].unique() if v.startswith("REVISAR:")}
        no_reconocidos = [v for v in df[col].unique() if v not in validos]
        if no_reconocidos:
            fuera[col] = no_reconocidos
    assert not fuera, f"Categorías fuera de dominio: {fuera}"


def test_personas_normalizadas(df):
    """director/supervisor: sin espacios dobles, en MAYÚSCULAS, no-informativos = NA."""
    problemas = {}
    for col in ("director", "supervisor"):
        dobles = int(df[col].str.contains("  ", regex=False).sum())
        no_mayus = int((df[col] != df[col].str.upper()).sum())
        placeholders = int(df[col].isin(["-", ".", "--", "SIN DATO", "XXX", ""]).sum())
        if dobles or no_mayus or placeholders:
            problemas[col] = {"espacios_dobles": dobles, "no_mayusculas": no_mayus, "placeholders": placeholders}
    assert not problemas, f"Problemas de normalización en personas: {problemas}"
