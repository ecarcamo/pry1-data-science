# Libro de códigos — Establecimientos DIVERSIFICADO (MINEDUC)

Metadatos y diccionario de variables del conjunto de datos limpio
`datos/clean/establecimientos_diversificado_limpio.csv`.

## Metadatos globales

| Campo | Valor |
|---|---|
| Fuente | Buscador de establecimientos del MINEDUC |
| URL | http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/ |
| Fecha de extracción | 2026-07-12 (corrida registrada en `automatizacion/scraper.log`, confirmada por el `mtime` de los CSV en `datos/crudos/`) |
| Versión | v1.0 |
| Registros | 11,867 |
| Variables | 31 |
| Autores | Esteban, Ernesto, Hugo |

## Plantilla por columna

Cada variable se documenta con los siguientes campos:

- **Descripción:** qué representa la columna.
- **Tipo de dato:** tipo de dato con el que se almacena en el CSV limpio.
- **Dominio permitido:** qué valores son válidos.
- **Valores posibles:** cardinalidad / catálogo observado.
- **Tratamiento aplicado:** transformación de limpieza aplicada (ver `docs/transformaciones.md` para el detalle con conteos).
- **Variable derivada:** Sí/No — de dónde y cómo se calculó, si aplica.
- **Fecha de extracción:** fecha en que se obtuvo el dato de la fuente.
- **Fuente:** de dónde proviene el dato.
- **Versión:** versión de este libro de códigos bajo la cual se documentó la columna.

---

## Columnas de Esteban

### `establecimiento`

- **Descripción:** Nombre oficial del establecimiento educativo, tal como lo registra el MINEDUC.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena no vacía en MAYÚSCULAS; `"NA"` si no hay dato.
- **Valores posibles:** 6,668 valores únicos observados sobre 11,867 registros; es texto libre (nombre propio), no una categórica cerrada.
- **Tratamiento aplicado:** NFC + colapsar espacios múltiples + `strip()` + quitar caracteres de control + `.upper()` defensivo; 5 valores vacíos (IDs `114`, `1814`, `3644`, `7592`, `9627`) → `"NA"`; comillas dobles y variantes con/sin tilde se conservan tal cual (no se autocorrigen, ver `docs/transformaciones.md#establecimiento`).
- **Variable derivada:** No — proviene directamente de la columna cruda `establecimiento`, solo normalizada en formato.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `establecimiento_raw`

- **Descripción:** Valor original de `establecimiento` tal como llegó de la fuente, sin ninguna normalización.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena, incluidos vacíos, espacios múltiples y caracteres de control.
- **Valores posibles:** Misma cardinalidad que la columna cruda en el CSV unido (ver `datos/interim/diagnostico_unicos.csv`).
- **Tratamiento aplicado:** Ninguno — se preserva sin modificar como respaldo/trazabilidad de `establecimiento`.
- **Variable derivada:** Sí — copia literal de la columna `establecimiento` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_establecimiento.py`).
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `direccion`

- **Descripción:** Dirección física del establecimiento (calle, avenida, zona, colonia, etc.).
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena no vacía en MAYÚSCULAS con abreviaturas estandarizadas; `"NA"` si no hay dato.
- **Valores posibles:** 7,528 valores únicos observados; texto libre, no una categórica cerrada.
- **Tratamiento aplicado:** NFC + colapsar espacios múltiples + `strip()` + quitar caracteres de control + `.upper()`; 89 vacíos/placeholders no informativos (`.`, `---`, `S/N`, etc.) → `"NA"`; abreviaturas estandarizadas (`AV`→`AVENIDA`, `COL`→`COLONIA`, `Z.`→`ZONA`, `BO`→`BARRIO`, `#`/`No`→`NO.`). Ver `docs/transformaciones.md#direccion`.
- **Variable derivada:** No — proviene directamente de la columna cruda `direccion`, normalizada en formato y vocabulario.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `direccion_raw`

- **Descripción:** Valor original de `direccion` tal como llegó de la fuente.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena, incluidos vacíos y placeholders no informativos.
- **Valores posibles:** Misma cardinalidad que la columna cruda en el CSV unido.
- **Tratamiento aplicado:** Ninguno — se preserva sin modificar.
- **Variable derivada:** Sí — copia literal de la columna `direccion` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_direccion.py`).
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `archivo_origen`

- **Descripción:** Nombre del archivo CSV crudo (uno por departamento) del que proviene cada fila.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Uno de los nombres de archivo `establecimientos_diversificado_<codigo>_<departamento>.csv` generados por `automatizacion/descarga.py`.
- **Valores posibles:** 23 valores únicos (uno por archivo/departamento descargado; Guatemala se descarga en 2 archivos — `00_ciudad_capital` y `01_guatemala` — antes de la fusión que hace Ernesto en `departamento`).
- **Tratamiento aplicado:** Ninguno adicional a la asignación hecha en la unión; ya es un nombre de archivo consistente, no requiere normalización.
- **Variable derivada:** Sí — asignada en `automatizacion/unir_datos.py` (`df["archivo_origen"] = archivo.name`) al concatenar los 23 CSV crudos de `datos/crudos/`.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC (nombre de archivo generado por el propio pipeline de descarga).
- **Versión:** v1.0.

### `id_registro`

- **Descripción:** Identificador único y estable de cada fila del conjunto de datos, para referenciarla en cualquier fase (limpieza, deduplicación, validación) sin depender del índice de pandas.
- **Tipo de dato:** Texto (string) — almacenado como texto por consistencia con el `dtype=str` de todo el pipeline, aunque semánticamente es un entero.
- **Dominio permitido:** Enteros positivos consecutivos.
- **Valores posibles:** 11,867 valores únicos, rango `1..11867`.
- **Tratamiento aplicado:** Ninguno posterior a su asignación; se excluye explícitamente (junto con `archivo_origen`) del chequeo de filas idénticas al buscar duplicados exactos.
- **Variable derivada:** Sí — entero incremental estable (1..N), asignado en `automatizacion/unir_datos.py` (`unido["id_registro"] = range(1, len(unido) + 1)`) después de ordenar y concatenar los 23 CSV crudos.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC (id generado por el propio pipeline de unión).
- **Versión:** v1.0.

---

<!-- TODO Ernesto: codigo, codigo_raw, distrito, distrito_raw, departamento, departamento_raw,
     municipio, municipio_raw, nivel, nivel_raw, departamental, departamental_raw
     (reusar docs/transformaciones.md y docs/plan_limpieza.md) -->

<!-- TODO Hugo: telefono, telefono_adicionales, telefono_raw, supervisor, supervisor_raw,
     director, director_raw, sector, area, status, modalidad, jornada, plan
     (reusar docs/transformaciones.md y docs/plan_limpieza.md) -->
