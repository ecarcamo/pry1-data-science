"""
Une todos los CSV crudos descargados por departamento (main.py) en un único
archivo. Esto es solo unión fiel de los datos: NO limpia, NO normaliza y NO
elimina duplicados. Esas transformaciones se aplican en una fase posterior,
sobre este archivo unido.

Uso como script independiente:
    python unir_datos.py     # une datos/crudos/ -> datos/unido/

También puede importarse y usarse como función:
    from unir_datos import unir_crudos
    unir_crudos(crudos_dir, salida_dir)
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CRUDOS_DIR = PROJECT_ROOT / "datos" / "crudos"
UNIDO_DIR = PROJECT_ROOT / "datos" / "unido"

PATRON_ARCHIVOS = "establecimientos_diversificado_*.csv"
NOMBRE_SALIDA = "establecimientos_diversificado_unido.csv"

log = logging.getLogger("mineduc_scraper")


def _listar_archivos_crudos(crudos_dir: Path) -> list[Path]:
    archivos = sorted(
        p for p in crudos_dir.glob(PATRON_ARCHIVOS) if p.name != NOMBRE_SALIDA
    )
    if not archivos:
        raise FileNotFoundError(
            f"No se encontró ningún archivo '{PATRON_ARCHIVOS}' dentro de {crudos_dir}. "
            "Corré primero main.py para descargar los datos crudos."
        )
    return archivos


def _leer_crudo(archivo: Path) -> pd.DataFrame:
    # Lectura fiel: sin encoding, dtype, ni NA que alteren el crudo. La limpieza
    # semántica (mayúsculas, tildes, valores tipo "NA"/"NULL"/"-", etc.) es de
    # una fase posterior, no de esta unión.
    return pd.read_csv(
        archivo,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
        na_values=[],
    )


def _validar_columnas(dataframes: dict[Path, pd.DataFrame]) -> list[str]:
    archivos = list(dataframes.keys())
    referencia_archivo = archivos[0]
    referencia = list(dataframes[referencia_archivo].columns)

    for archivo in archivos[1:]:
        columnas = list(dataframes[archivo].columns)
        if columnas != referencia:
            set_ref, set_cur = set(referencia), set(columnas)
            faltan = set_ref - set_cur
            sobran = set_cur - set_ref
            detalle = [f"Columnas esperadas (según {referencia_archivo.name}): {referencia}",
                       f"Columnas encontradas en {archivo.name}: {columnas}"]
            if faltan:
                detalle.append(f"Faltan en {archivo.name}: {sorted(faltan)}")
            if sobran:
                detalle.append(f"Sobran en {archivo.name}: {sorted(sobran)}")
            if not faltan and not sobran:
                detalle.append("Mismas columnas pero en distinto orden.")
            raise ValueError(
                f"'{archivo.name}' tiene columnas distintas a las de los demás archivos crudos.\n"
                + "\n".join(detalle)
            )

    return referencia


def unir_crudos(crudos_dir: Path, salida_dir: Path) -> Path:
    crudos_dir = Path(crudos_dir)
    salida_dir = Path(salida_dir)

    archivos = _listar_archivos_crudos(crudos_dir)
    log.info("Uniendo %d archivos crudos desde %s", len(archivos), crudos_dir)

    dataframes = {archivo: _leer_crudo(archivo) for archivo in archivos}

    columnas_referencia = _validar_columnas(dataframes)

    filas_por_archivo = {}
    partes = []
    for archivo in archivos:  # orden ya determinista (sorted en _listar_archivos_crudos)
        df = dataframes[archivo].copy()
        # Columna derivada: de qué CSV crudo vino cada fila, para poder rastrear
        # cualquier registro hasta su archivo/departamento de origen.
        df["archivo_origen"] = archivo.name
        partes.append(df)
        filas_por_archivo[archivo.name] = len(df)
        log.info("  %s -> %d filas", archivo.name, len(df))

    total_esperado = sum(filas_por_archivo.values())

    unido = pd.concat(partes, ignore_index=True)

    if len(unido) != total_esperado:
        raise RuntimeError(
            f"Fallo de integridad al unir: se esperaban {total_esperado} filas "
            f"(suma de archivos individuales) pero el resultado unido tiene {len(unido)}."
        )

    # Columna derivada: id incremental estable (1..N), asignado después de
    # ordenar y concatenar, para poder referenciar cada fila en fases
    # posteriores (limpieza, deduplicación, validación) sin depender del
    # índice de pandas.
    unido["id_registro"] = range(1, len(unido) + 1)

    columnas_finales = columnas_referencia + ["archivo_origen", "id_registro"]
    unido = unido[columnas_finales]

    salida_dir.mkdir(parents=True, exist_ok=True)
    destino = salida_dir / NOMBRE_SALIDA
    unido.to_csv(destino, index=False, encoding="utf-8-sig")

    log.info("Total filas unidas: %d (== suma de archivos: %d)", len(unido), total_esperado)
    log.info("Unido guardado -> %s", destino)

    return destino


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(Path(__file__).resolve().parent / "scraper.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    unir_crudos(CRUDOS_DIR, UNIDO_DIR)
