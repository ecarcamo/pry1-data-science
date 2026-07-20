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

## Columnas de Hugo

### `telefono`

- **Descripción:** Número de teléfono principal de contacto del establecimiento educativo.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cadena con formato `####-####` (8 dígitos, convención de Guatemala) o `"NA"` si no hay dato válido.
- **Valores posibles:** 10,794 números válidos formateados; texto libre bajo el patrón `####-####`, no una categórica cerrada.
- **Tratamiento aplicado:** NFC + quitar caracteres de control + `strip()`; se dejan solo dígitos y se aplica formato `####-####`; 946 vacíos → `"NA"`; 127 inválidos (con letras o con un número de dígitos distinto de 8) → `"NA"`; en celdas con varios números se conserva el primero aquí y el resto en `telefono_adicionales`. Ver `docs/transformaciones.md#telefono`.
- **Variable derivada:** No — proviene directamente de la columna cruda `telefono`, solo normalizada y validada; el original queda en `telefono_raw`.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `telefono_adicionales`

- **Descripción:** Teléfonos secundarios del establecimiento, cuando la celda original contenía varios números.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Uno o más números con formato `####-####` unidos por `; `, o `"NA"` si no hay números adicionales.
- **Valores posibles:** 119 registros con al menos un número adicional; el resto es `"NA"`.
- **Tratamiento aplicado:** Números de 8 dígitos extra de celdas con múltiples teléfonos (separados por `/ , ; Y/E` o dígitos concatenados en múltiplos de 8), formateados `####-####` y unidos por `; ` (`"NA"` si no hay). Ver `docs/transformaciones.md#telefono`.
- **Variable derivada:** Sí — extraída en `limpieza/limpiar_telefono.py` a partir de los números secundarios de `telefono_raw`, para preservar los teléfonos extra sin romper la atomicidad de `telefono`.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `telefono_raw`

- **Descripción:** Valor original de `telefono` tal como llegó de la fuente, sin ninguna normalización.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena, incluidos vacíos, letras, separadores y varios números en una misma celda.
- **Valores posibles:** Misma cardinalidad que la columna cruda `telefono` en el CSV unido.
- **Tratamiento aplicado:** Ninguno — se preserva sin modificar como respaldo/trazabilidad de `telefono` y `telefono_adicionales`.
- **Variable derivada:** Sí — copia literal de la columna `telefono` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_telefono.py`).
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `supervisor`

- **Descripción:** Nombre del supervisor educativo asignado al establecimiento.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Nombre propio en MAYÚSCULAS; `"NA"` si no hay dato.
- **Valores posibles:** Texto libre (nombre propio de persona), no una categórica cerrada.
- **Tratamiento aplicado:** Quitar caracteres invisibles/de control (`Cc`/`Cf`) + NFC + `strip()` + colapsar espacios múltiples + `.upper()`; 535 vacíos → `"NA"`; se normaliza formato, no ortografía. Ver `docs/transformaciones.md#personas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `supervisor`, solo normalizada en formato; el original queda en `supervisor_raw`.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `supervisor_raw`

- **Descripción:** Valor original de `supervisor` tal como llegó de la fuente.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena, incluidos vacíos, placeholders y caracteres invisibles.
- **Valores posibles:** Misma cardinalidad que la columna cruda `supervisor` en el CSV unido.
- **Tratamiento aplicado:** Ninguno — se preserva sin modificar como respaldo/trazabilidad de `supervisor`.
- **Variable derivada:** Sí — copia literal de la columna `supervisor` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_personas.py`).
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `director`

- **Descripción:** Nombre del director del establecimiento educativo.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Nombre propio en MAYÚSCULAS; `"NA"` si no hay dato.
- **Valores posibles:** Texto libre (nombre propio de persona), no una categórica cerrada.
- **Tratamiento aplicado:** Quitar caracteres invisibles/de control (`Cc`/`Cf`) + NFC + `strip()` + colapsar espacios múltiples + `.upper()`; 2,143 → `"NA"` (1,733 vacíos + 410 placeholders no informativos como `-`, `.`, `SIN DATO`, `XXX`); se normaliza formato, no ortografía. Ver `docs/transformaciones.md#personas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `director`, solo normalizada en formato; el original queda en `director_raw`.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `director_raw`

- **Descripción:** Valor original de `director` tal como llegó de la fuente.
- **Tipo de dato:** Texto (string).
- **Dominio permitido:** Cualquier cadena, incluidos vacíos, placeholders y caracteres invisibles.
- **Valores posibles:** Misma cardinalidad que la columna cruda `director` en el CSV unido.
- **Tratamiento aplicado:** Ninguno — se preserva sin modificar como respaldo/trazabilidad de `director`.
- **Variable derivada:** Sí — copia literal de la columna `director` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_personas.py`).
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `sector`

- **Descripción:** Sector administrativo bajo el cual opera el establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 4 valores canónicos: `COOPERATIVA`, `MUNICIPAL`, `OFICIAL`, `PRIVADO`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 4 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico; fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `sector`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `area`

- **Descripción:** Área geográfica en la que se ubica el establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 3 valores canónicos: `RURAL`, `URBANA`, `SIN ESPECIFICAR`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 3 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico; fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `area`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `status`

- **Descripción:** Estado operativo del establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 5 valores canónicos: `ABIERTA`, `CERRADA DEFINITIVAMENTE`, `CERRADA TEMPORALMENTE`, `TEMPORAL NOMBRAMIENTO`, `TEMPORAL TITULOS`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 5 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico; fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `status`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `modalidad`

- **Descripción:** Modalidad lingüística de enseñanza del establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 2 valores canónicos: `BILINGUE`, `MONOLINGUE` (sin diéresis, tal como la fuente); cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 2 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico (incluye `MONOLINGÜE`→`MONOLINGUE`, `BILINGÜE`→`BILINGUE`); fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `modalidad`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `jornada`

- **Descripción:** Jornada horaria en la que funciona el establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 6 valores canónicos: `DOBLE`, `INTERMEDIA`, `MATUTINA`, `NOCTURNA`, `SIN JORNADA`, `VESPERTINA`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 6 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico (incluye `S/J`→`SIN JORNADA`); fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `jornada`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.

### `plan`

- **Descripción:** Plan o régimen de estudios del establecimiento educativo.
- **Tipo de dato:** Texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- **Dominio permitido:** Uno de 13 valores canónicos: `A DISTANCIA`, `DIARIO(REGULAR)`, `DOMINICAL`, `FIN DE SEMANA`, `INTERCALADO`, `IRREGULAR`, `MIXTO`, `SABATINO`, `SEMIPRESENCIAL`, `SEMIPRESENCIAL (DOS DÍAS A LA SEMANA)`, `SEMIPRESENCIAL (FIN DE SEMANA)`, `SEMIPRESENCIAL (UN DÍA A LA SEMANA)`, `VIRTUAL A DISTANCIA`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- **Valores posibles:** 13 categorías.
- **Tratamiento aplicado:** Normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico (incluye `DIARIO (REGULAR)`→`DIARIO(REGULAR)`, `REGULAR`→`DIARIO(REGULAR)`); fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- **Variable derivada:** No — proviene directamente de la columna cruda `plan`, solo normalizada y validada contra el catálogo.
- **Fecha de extracción:** 2026-07-12.
- **Fuente:** Buscador de establecimientos del MINEDUC.
- **Versión:** v1.0.
