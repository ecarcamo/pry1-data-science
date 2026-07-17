"""Limpieza de `telefono`: valida 8 dígitos (Guatemala), formato `####-####`, separa múltiples números."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIDO_CSV = PROJECT_ROOT / "datos" / "unido" / "establecimientos_diversificado_unido.csv"
TRANSFORMACIONES_MD = PROJECT_ROOT / "docs" / "transformaciones.md"

MARCADOR_VALOR_FALTANTE = "NA"
_SEPARADORES = re.compile(r"[/,;]|\bY\b|\bE\b", re.IGNORECASE)
_NO_DIGITO = re.compile(r"\D")


def _numeros_validos(valor: str) -> list[str]:
    """Devuelve la lista ordenada de números de 8 dígitos hallados en el valor crudo.

    Separa por `/ , ; Y/E` y además des-concatena secuencias de dígitos cuyo largo
    es múltiplo de 8 (ej. 16 dígitos = dos números pegados sin separador).
    """
    numeros: list[str] = []
    for parte in _SEPARADORES.split(valor):
        digitos = _NO_DIGITO.sub("", parte)
        if len(digitos) == 8:
            numeros.append(digitos)
        elif len(digitos) > 8 and len(digitos) % 8 == 0:
            numeros.extend(digitos[i : i + 8] for i in range(0, len(digitos), 8))
        # cualquier otro largo (letras, <8, no múltiplo de 8) se descarta como inválido

    vistos: list[str] = []
    for n in numeros:
        if n not in vistos:
            vistos.append(n)
    return vistos


def _formatear(digitos: str) -> str:
    return f"{digitos[:4]}-{digitos[4:]}"


def _normalizar_telefono(valor: str) -> tuple[str, str]:
    if valor is None:
        return MARCADOR_VALOR_FALTANTE, MARCADOR_VALOR_FALTANTE

    texto = unicodedata.normalize("NFC", valor)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Cc")
    texto = texto.strip()

    if texto == "":
        return MARCADOR_VALOR_FALTANTE, MARCADOR_VALOR_FALTANTE

    numeros = _numeros_validos(texto)
    if not numeros:
        return MARCADOR_VALOR_FALTANTE, MARCADOR_VALOR_FALTANTE

    principal = _formatear(numeros[0])
    adicionales = "; ".join(_formatear(n) for n in numeros[1:]) or MARCADOR_VALOR_FALTANTE
    return principal, adicionales


def clean_telefono(df: pd.DataFrame) -> pd.DataFrame:
    """Función pura: normaliza `telefono` a `####-####`, preserva `telefono_raw`,
    y guarda números extra en la columna derivada `telefono_adicionales`."""
    df = df.copy()

    if "telefono_raw" not in df.columns:
        df.insert(df.columns.get_loc("telefono") + 1, "telefono_raw", df["telefono"])

    resultado = df["telefono_raw"].map(_normalizar_telefono)
    df["telefono"] = resultado.map(lambda t: t[0])

    if "telefono_adicionales" not in df.columns:
        df.insert(df.columns.get_loc("telefono") + 1, "telefono_adicionales", "")
    df["telefono_adicionales"] = resultado.map(lambda t: t[1])

    return df


def _leer_unido(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[])


def _generar_reporte(antes: pd.DataFrame, despues: pd.DataFrame) -> list[str]:
    total = len(antes)
    vacios = (antes["telefono"].str.strip() == "").sum()

    con_letras = antes["telefono"].str.contains(r"[A-Za-z]", regex=True).sum()
    con_separador = antes["telefono"].str.contains(_SEPARADORES).sum()

    resultado_na = despues["telefono"] == MARCADOR_VALOR_FALTANTE
    invalidos_no_vacios = int((resultado_na & (antes["telefono"].str.strip() != "")).sum())

    con_adicionales = int((despues["telefono_adicionales"] != MARCADOR_VALOR_FALTANTE).sum())

    filas = [
        f"| `telefono` | {vacios} valores vacíos | Se marcan como `\"{MARCADOR_VALOR_FALTANTE}\"` | "
        f"{vacios} | No se puede inferir un teléfono desde otras columnas. |",
        f"| `telefono` | Formato heterogéneo (dígitos pelados, con guiones/espacios) | "
        f"Se dejan solo dígitos y se aplica formato consistente `####-####` (convención "
        f"de 8 dígitos de Guatemala) | {total - vacios - invalidos_no_vacios} números "
        f"válidos formateados | Formato uniforme y comparable para todos los registros. |",
        f"| `telefono` | Celdas con varios números (separados por `/ , ; Y/E` o dígitos "
        f"concatenados en múltiplos de 8) | Se conserva el primero en `telefono` y el resto "
        f"en la columna derivada `telefono_adicionales` | {con_adicionales} registros con "
        f"números adicionales | No se pierde información; se mantiene un valor principal "
        "atómico por registro. |",
        f"| `telefono` | {con_letras} con letras y otros con menos/otros largos de dígitos "
        f"(no 8) | Se consideran inválidos y se marcan `\"{MARCADOR_VALOR_FALTANTE}\"` "
        f"(no se borra la fila; el original queda en `telefono_raw`) | {invalidos_no_vacios} "
        "inválidos no vacíos | Un teléfono guatemalteco válido tiene exactamente 8 dígitos. |",
        f"| `telefono_adicionales` | Variable derivada | Números de 8 dígitos extra de "
        f"celdas con múltiples teléfonos, formateados `####-####` y unidos por `; ` "
        f"(`{MARCADOR_VALOR_FALTANTE}` si no hay) | {con_adicionales} | Preserva los "
        "teléfonos secundarios sin romper la atomicidad de `telefono`. |",
    ]
    return filas


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from limpieza.reportes import actualizar_seccion_markdown

    df_unido = _leer_unido(UNIDO_CSV)
    df_limpio = clean_telefono(df_unido)
    filas_reporte = _generar_reporte(df_unido, df_limpio)

    actualizar_seccion_markdown(
        TRANSFORMACIONES_MD,
        marcador="telefono",
        titulo="`telefono` (limpiar_telefono.py)",
        filas_tabla=filas_reporte,
    )

    print(f"clean_telefono() aplicado sobre {len(df_limpio)} filas.")
    print(f"Registro actualizado -> {TRANSFORMACIONES_MD.relative_to(PROJECT_ROOT)}")
