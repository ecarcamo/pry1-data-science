# Libro de códigos - Establecimientos DIVERSIFICADO (MINEDUC)

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

- **Descripción**: qué representa la columna.
- Tipo de dato: con el que se almacena en el CSV limpio.
- Dominio permitido: qué valores son válidos.
- Valores posibles: cardinalidad o catálogo observado.
- Tratamiento aplicado: transformación de limpieza aplicada (ver `docs/transformaciones.md` para el detalle con conteos).
- Variable derivada: sí o no, y de dónde y cómo se calculó si aplica.
- Fecha de extracción: cuándo se obtuvo el dato de la fuente.
- Fuente: de dónde proviene el dato.
- Versión: la de este libro de códigos bajo la cual se documentó la columna.

---

## Columnas de Esteban

### `establecimiento`

Nombre oficial del establecimiento educativo, tal como lo registra el MINEDUC. Es texto (string) y su dominio permitido es cualquier cadena no vacía en MAYÚSCULAS, con `"NA"` si no hay dato. Se observan 6,668 valores únicos sobre 11,867 registros: es texto libre (nombre propio), no una categórica cerrada.

- **Tratamiento aplicado:** NFC + colapsar espacios múltiples + `strip()` + quitar caracteres de control + `.upper()` defensivo; 5 valores vacíos (IDs `114`, `1814`, `3644`, `7592`, `9627`) pasan a `"NA"`; comillas dobles y variantes con/sin tilde se conservan tal cual, no se autocorrigen (ver `docs/transformaciones.md#establecimiento`).
- Variable derivada: no, proviene directamente de la columna cruda `establecimiento`, solo normalizada en formato.
- Fecha de extracción: 2026-07-12.
- Fuente: Buscador de establecimientos del MINEDUC.
- Versión: v1.0.

### `establecimiento_raw`

Guarda el valor original de `establecimiento` tal como llegó de la fuente, sin ninguna normalización. Es texto (string) y su dominio admite cualquier cadena, incluidos vacíos, espacios múltiples y caracteres de control. Tiene la misma cardinalidad que la columna cruda en el CSV unido (ver `datos/interim/diagnostico_unicos.csv`).

No se le aplicó ningún tratamiento: se preserva sin modificar como respaldo y trazabilidad de `establecimiento`. Es una variable derivada, copia literal de la columna `establecimiento` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_establecimiento.py`). Fecha de extracción: 2026-07-12. Fuente: Buscador de establecimientos del MINEDUC. Versión: v1.0.

### `direccion`

- **Descripción:** dirección física del establecimiento (calle, avenida, zona, colonia, etc.).
- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena no vacía en MAYÚSCULAS con abreviaturas estandarizadas; `"NA"` si no hay dato.
- Valores posibles: 7,528 valores únicos observados; texto libre, no una categórica cerrada.
- Tratamiento aplicado: NFC + colapsar espacios múltiples + `strip()` + quitar caracteres de control + `.upper()`; 89 vacíos/placeholders no informativos (`.`, `---`, `S/N`, etc.) pasan a `"NA"`; abreviaturas estandarizadas (`AV`→`AVENIDA`, `COL`→`COLONIA`, `Z.`→`ZONA`, `BO`→`BARRIO`, `#`/`No`→`NO.`). Ver `docs/transformaciones.md#direccion`.
- Variable derivada: no, proviene directamente de la columna cruda `direccion`, normalizada en formato y vocabulario.
- Fecha de extracción: 2026-07-12.
- Fuente: Buscador de establecimientos del MINEDUC.
- Versión: v1.0.

### `direccion_raw`

Valor original de `direccion` tal como llegó de la fuente. Texto (string); admite cualquier cadena, incluidos vacíos y placeholders no informativos. Tiene la misma cardinalidad que la columna cruda en el CSV unido. Sin tratamiento aplicado, se preserva sin modificar. Es variable derivada: copia literal de la columna `direccion` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_direccion.py`). Extraída el 2026-07-12 del buscador de establecimientos del MINEDUC. Versión v1.0.

### `archivo_origen`

Contiene el nombre del archivo CSV crudo (uno por departamento) del que proviene cada fila. Es texto (string), y su dominio permitido es alguno de los nombres de archivo `establecimientos_diversificado_<codigo>_<departamento>.csv` que genera `automatizacion/descarga.py`.

Tiene 23 valores únicos (uno por archivo o departamento descargado; Guatemala se descarga en 2 archivos, `00_ciudad_capital` y `01_guatemala`, antes de la fusión que hace Ernesto en `departamento`). No recibe tratamiento adicional al de la asignación hecha en la unión, ya es un nombre de archivo consistente que no requiere normalización. Es variable derivada: se asigna en `automatizacion/unir_datos.py` (`df["archivo_origen"] = archivo.name`) al concatenar los 23 CSV crudos de `datos/crudos/`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC (el nombre de archivo lo genera el propio pipeline de descarga). Versión: v1.0.

### `id_registro`

- **Descripción:** identificador único y estable de cada fila del conjunto de datos, para referenciarla en cualquier fase (limpieza, deduplicación, validación) sin depender del índice de pandas.
- Tipo de dato: texto (string), almacenado como texto por consistencia con el `dtype=str` de todo el pipeline, aunque semánticamente es un entero.
- Dominio permitido: enteros positivos consecutivos.
- Valores posibles: 11,867 valores únicos, rango `1..11867`.
- Tratamiento aplicado: ninguno posterior a su asignación; se excluye explícitamente (junto con `archivo_origen`) del chequeo de filas idénticas al buscar duplicados exactos.
- Variable derivada: sí, entero incremental estable (1..N), asignado en `automatizacion/unir_datos.py` (`unido["id_registro"] = range(1, len(unido) + 1)`) después de ordenar y concatenar los 23 CSV crudos.
- Fecha de extracción: 2026-07-12.
- Fuente: buscador de establecimientos del MINEDUC (id generado por el propio pipeline de unión).
- Versión: v1.0.

---

## Columnas de Ernesto

### `departamento`

Departamento de Guatemala en el que se ubica el establecimiento educativo. Texto (string). El dominio permitido es uno de los 22 departamentos oficiales del INE, en MAYÚSCULAS con tildes correctas; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`. Hay 22 categorías posibles (catálogo oficial INE, ver `limpieza/catalogos.py`).

Tratamiento aplicado: fusión de `CIUDAD CAPITAL` (código 00) + `GUATEMALA` (código 01) en el valor canónico `GUATEMALA` (2,161 registros fusionados), por ser un artefacto del selector de descarga y no una entidad administrativa distinta; normalización de tildes a la forma canónica del INE (2,025 registros, comparación sin tildes y valor guardado con tildes); `.upper()` defensivo; 0 valores fuera de catálogo. Ver `docs/transformaciones.md#departamento`.

No es variable derivada: proviene directamente de la columna cruda `departamento`, normalizada y fusionada; el original queda en `departamento_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `departamento_raw`

- **Descripción:** valor original de `departamento` tal como llegó de la fuente, sin fusión ni normalización.
- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena; conserva `CIUDAD CAPITAL` y las variantes sin tildes (`PETEN`, `SOLOLA`, etc.).
- Valores posibles: misma cardinalidad que la columna cruda en el CSV unido (incluye `CIUDAD CAPITAL` como valor separado de `GUATEMALA`).
- Tratamiento aplicado: ninguno, se preserva sin modificar como respaldo y trazabilidad de `departamento` (permite auditar la fusión 00+01 y la normalización de tildes).
- Variable derivada: sí, copia literal de la columna `departamento` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_departamento.py`).
- Fecha de extracción: 2026-07-12.
- Fuente: buscador de establecimientos del MINEDUC.
- Versión: v1.0.

### `municipio`

Municipio en el que se ubica el establecimiento educativo. Es texto (string) cuyo dominio permitido es uno de los ~340 municipios oficiales del INE, válido para su departamento, en MAYÚSCULAS con tildes correctas; sin match suficiente se marca con prefijo `REVISAR:`. Se manejan ~340 municipios posibles (catálogo oficial INE validado por departamento, ver `limpieza/catalogos.py`).

Se validó contra el catálogo filtrado por el `departamento` ya limpio: 11,858 registros con match exacto (sin tildes), 1 typo corregido con RapidFuzz (`token_sort_ratio ≥ 90`), 8 sin match marcados `REVISAR:` y exportados a `datos/interim/municipios_fuera_catalogo.csv`; el valor canónico se guarda con tildes y en MAYÚSCULAS (ver `docs/transformaciones.md#municipio`). No es variable derivada, viene directo de la columna cruda `municipio`, normalizada y validada; el original queda en `municipio_raw`. Extraída el 2026-07-12 del buscador de establecimientos del MINEDUC, versión v1.0.

### `municipio_raw`

Valor original de `municipio` tal como llegó de la fuente, sin normalizar ni corregir.

- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena, incluidos typos y variantes sin tildes.
- Valores posibles: misma cardinalidad que la columna cruda en el CSV unido (352 valores únicos observados).
- Tratamiento aplicado: ninguno, se preserva sin modificar; hace auditable cada corrección de typo (RapidFuzz) y cada valor marcado `REVISAR:`.
- Variable derivada: sí, copia literal de la columna `municipio` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_municipio.py`).
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `codigo`

Código único del establecimiento educativo asignado por el MINEDUC. Se guarda como texto (string) siempre, para conservar los ceros a la izquierda (convertirlo a `int`/`float` los perdería). El dominio permitido es una cadena que cumple el patrón `##-##-####-##` (`^\d{2}-\d{2}-\d{4}-\d{2}$`); cualquier valor fuera de patrón se marca con prefijo `REVISAR:`.

Hay 11,867 valores únicos (uno por registro) y 0 inválidos en el dataset actual. El tratamiento aplicado fue `strip()` defensivo, verificación (assert) del patrón `##-##-####-##` sobre los 11,867 registros y de la unicidad (`nunique() == len(df)`); resultó en 0 inválidos y 0 duplicados detectados (ver `docs/transformaciones.md#codigo`). No es variable derivada: proviene directamente de la columna cruda `codigo`; el original queda en `codigo_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `codigo_raw`

- **Descripción:** valor original de `codigo` tal como llegó de la fuente.
- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena, incluidos posibles espacios al inicio/fin.
- Valores posibles: misma cardinalidad que la columna cruda en el CSV unido (11,867 únicos).
- Tratamiento aplicado: ninguno, se preserva sin modificar como respaldo y trazabilidad de `codigo`.
- Variable derivada: sí, copia literal de la columna `codigo` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_codigo.py`).
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `distrito`

Distrito escolar del establecimiento educativo, según la organización interna del MINEDUC. Texto (string), cuyo dominio permitido es una cadena con formato `##-###`, o `"NA"` si no hay dato. No existe catálogo público oficial de distritos escolares, por lo que solo se valida el formato, no el contenido. Es texto libre bajo el patrón `##-###`, no una categórica cerrada verificable.

Se le aplicó `strip()` defensivo y normalización de formato; 532 valores vacíos pasaron a `"NA"`. No se corrige el contenido por falta de catálogo de referencia (ver `docs/transformaciones.md#distrito_departamental_nivel`). No es variable derivada: proviene directamente de la columna cruda `distrito`; el original queda en `distrito_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `distrito_raw`

Valor original de `distrito` tal como llegó de la fuente. Texto (string) que admite cualquier cadena, incluidos vacíos y variantes de formato (`01-`, `01-403`, etc.), con la misma cardinalidad que la columna cruda en el CSV unido. Ningún tratamiento se le aplicó: se preserva sin modificar como respaldo y trazabilidad de `distrito`. Variable derivada: sí, copia literal de la columna `distrito` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_distrito_departamental_nivel.py`). Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `departamental`

- **Descripción:** Dirección Departamental de Educación (DIDEDUC) del MINEDUC a la que pertenece el establecimiento.
- Tipo de dato: texto (string).
- Dominio permitido: nombre de dirección departamental en MAYÚSCULAS con tildes correctas, consistente con el `departamento` limpio (o una de sus subdivisiones administrativas conocidas).
- Valores posibles: 26 valores únicos, 22 departamentos más Guatemala subdividida en 4 zonas administrativas del MINEDUC (`GUATEMALA NORTE`, `GUATEMALA SUR`, `GUATEMALA ORIENTE`, `GUATEMALA OCCIDENTE`). La subdivisión es intencional, no un error.
- Tratamiento aplicado: `strip()` + NFC + `.upper()` con tildes correctas; 0 cambios de caja detectados. Se documentan los 26 valores observados y su mapeo al departamento oficial (ver `docs/transformaciones.md#distrito_departamental_nivel`).
- Variable derivada: no, proviene directamente de la columna cruda `departamental`; el original queda en `departamental_raw`.
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `departamental_raw`

Valor original de `departamental` tal como llegó de la fuente. Texto (string), admite cualquier cadena, incluidas posibles variantes de escritura, con la misma cardinalidad que la columna cruda en el CSV unido (26 valores únicos observados). No recibió tratamiento, se preserva sin modificar como respaldo y trazabilidad de `departamental`. Es variable derivada: copia literal de la columna `departamental` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_distrito_departamental_nivel.py`). Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `nivel`

Nivel escolar del establecimiento educativo. Texto (string) cuyo dominio permitido es un único valor, `DIVERSIFICADO` (el dataset se filtró por este nivel en la descarga). Solo existe 1 categoría: `DIVERSIFICADO`.

Se verificó (assert) que `nivel.nunique() == 1` y `nivel == "DIVERSIFICADO"` en los 11,867 registros, con 0 anomalías; no se modifica el valor (ver `docs/transformaciones.md#distrito_departamental_nivel`). No es variable derivada, proviene directamente de la columna cruda `nivel`; el original queda en `nivel_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `nivel_raw`

- **Descripción:** valor original de `nivel` tal como llegó de la fuente.
- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena (defensivo; en la práctica siempre `DIVERSIFICADO`).
- Valores posibles: misma cardinalidad que la columna cruda en el CSV unido (1 valor único observado).
- Tratamiento aplicado: ninguno, se preserva sin modificar como respaldo/trazabilidad de `nivel` (defensivo por si una futura descarga incluyera otro nivel).
- Variable derivada: sí, copia literal de la columna `nivel` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_distrito_departamental_nivel.py`).
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

---

## Columnas de Hugo

### `telefono`

Número de teléfono principal de contacto del establecimiento educativo. Texto (string), cuyo dominio permitido es una cadena con formato `####-####` (8 dígitos, convención de Guatemala) o `"NA"` si no hay dato válido. Se cuentan 10,794 números válidos formateados; es texto libre bajo el patrón `####-####`, no una categórica cerrada.

Tratamiento aplicado: NFC + quitar caracteres de control + `strip()`; se dejan solo dígitos y se aplica formato `####-####`; 946 vacíos pasan a `"NA"`; 127 inválidos (con letras o con un número de dígitos distinto de 8) también van a `"NA"`; en celdas con varios números se conserva el primero aquí y el resto en `telefono_adicionales` (ver `docs/transformaciones.md#telefono`). No es variable derivada: proviene directamente de la columna cruda `telefono`, solo normalizada y validada; el original queda en `telefono_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `telefono_adicionales`

- **Descripción:** teléfonos secundarios del establecimiento, cuando la celda original contenía varios números.
- Tipo de dato: texto (string).
- Dominio permitido: uno o más números con formato `####-####` unidos por `; `, o `"NA"` si no hay números adicionales.
- Valores posibles: 119 registros con al menos un número adicional; el resto es `"NA"`.
- Tratamiento aplicado: números de 8 dígitos extra de celdas con múltiples teléfonos (separados por `/ , ; Y/E` o dígitos concatenados en múltiplos de 8), formateados `####-####` y unidos por `; ` (`"NA"` si no hay). Ver `docs/transformaciones.md#telefono`.
- Variable derivada: sí, extraída en `limpieza/limpiar_telefono.py` a partir de los números secundarios de `telefono_raw`, para preservar los teléfonos extra sin romper la atomicidad de `telefono`.
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `telefono_raw`

Valor original de `telefono` tal como llegó de la fuente, sin ninguna normalización. Texto (string) que admite cualquier cadena, incluidos vacíos, letras, separadores y varios números en una misma celda, con la misma cardinalidad que la columna cruda `telefono` en el CSV unido. No tiene tratamiento aplicado: se preserva sin modificar como respaldo y trazabilidad de `telefono` y `telefono_adicionales`. Es variable derivada: copia literal de la columna `telefono` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_telefono.py`). Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `supervisor`

Nombre del supervisor educativo asignado al establecimiento. Texto (string) cuyo dominio permitido es un nombre propio en MAYÚSCULAS, con `"NA"` si no hay dato. Es texto libre (nombre propio de persona), no una categórica cerrada.

Se le quitaron caracteres invisibles/de control (`Cc`/`Cf`) + NFC + `strip()` + colapso de espacios múltiples + `.upper()`; 535 vacíos pasaron a `"NA"`; se normaliza formato, no ortografía (ver `docs/transformaciones.md#personas`). No es variable derivada: proviene directamente de la columna cruda `supervisor`, solo normalizada en formato; el original queda en `supervisor_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `supervisor_raw`

- **Descripción:** valor original de `supervisor` tal como llegó de la fuente.
- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena, incluidos vacíos, placeholders y caracteres invisibles.
- Valores posibles: misma cardinalidad que la columna cruda `supervisor` en el CSV unido.
- Tratamiento aplicado: ninguno, se preserva sin modificar como respaldo/trazabilidad de `supervisor`.
- Variable derivada: sí, copia literal de la columna `supervisor` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_personas.py`).
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `director`

Nombre del director del establecimiento educativo. Texto (string), con dominio permitido igual a un nombre propio en MAYÚSCULAS, o `"NA"` si no hay dato. Es texto libre (nombre propio de persona), no una categórica cerrada.

Tratamiento aplicado: se quitaron caracteres invisibles/de control (`Cc`/`Cf`) + NFC + `strip()` + colapso de espacios múltiples + `.upper()`; 2,143 registros pasaron a `"NA"` (1,733 vacíos + 410 placeholders no informativos como `-`, `.`, `SIN DATO`, `XXX`); se normaliza formato, no ortografía (ver `docs/transformaciones.md#personas`). No es variable derivada: viene directo de la columna cruda `director`, solo normalizada en formato; el original queda en `director_raw`. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `director_raw`

Valor original de `director` tal como llegó de la fuente.

- Tipo de dato: texto (string).
- Dominio permitido: cualquier cadena, incluidos vacíos, placeholders y caracteres invisibles.
- Valores posibles: misma cardinalidad que la columna cruda `director` en el CSV unido.
- Tratamiento aplicado: ninguno, se preserva sin modificar como respaldo/trazabilidad de `director`.
- Variable derivada: sí, copia literal de la columna `director` del CSV unido, insertada antes de aplicar la limpieza (`limpieza/limpiar_personas.py`).
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `sector`

Sector administrativo bajo el cual opera el establecimiento educativo. Es texto (string) en el CSV limpio, aunque su tipo analítico natural es `category`. El dominio permitido es uno de 4 valores canónicos: `COOPERATIVA`, `MUNICIPAL`, `OFICIAL`, `PRIVADO`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`. Hay 4 categorías posibles.

Se normalizó (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) y se aplicó un mapeo explícito a set canónico; lo que quedó fuera de catálogo se marcó `REVISAR:` (ver `docs/transformaciones.md#categoricas`). No es variable derivada: proviene directamente de la columna cruda `sector`, solo normalizada y validada contra el catálogo. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `area`

- **Descripción:** área geográfica en la que se ubica el establecimiento educativo.
- Tipo de dato: texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- Dominio permitido: uno de 3 valores canónicos: `RURAL`, `URBANA`, `SIN ESPECIFICAR`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- Valores posibles: 3 categorías.
- Tratamiento aplicado: normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico; fuera de catálogo pasa a `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- Variable derivada: no, proviene directamente de la columna cruda `area`, solo normalizada y validada contra el catálogo.
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `status`

Estado operativo del establecimiento educativo. Texto (string) en el CSV limpio, con tipo analítico natural `category`. El dominio permitido es uno de 5 valores canónicos: `ABIERTA`, `CERRADA DEFINITIVAMENTE`, `CERRADA TEMPORALMENTE`, `TEMPORAL NOMBRAMIENTO`, `TEMPORAL TITULOS`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`. Son 5 categorías posibles.

Se aplicó normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) más mapeo explícito a set canónico; lo fuera de catálogo va a `REVISAR:` (ver `docs/transformaciones.md#categoricas`). No es variable derivada, viene directo de la columna cruda `status`, solo normalizada y validada contra el catálogo. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `modalidad`

Modalidad lingüística de enseñanza del establecimiento educativo. Texto (string) en el CSV limpio, con tipo analítico natural `category`. Dominio permitido: uno de 2 valores canónicos, `BILINGUE` o `MONOLINGUE` (sin diéresis, tal como la fuente); cualquier valor fuera de catálogo se marca `REVISAR:`. Hay 2 categorías posibles.

- Tratamiento aplicado: normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico (incluye `MONOLINGÜE`→`MONOLINGUE`, `BILINGÜE`→`BILINGUE`); fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- Variable derivada: no, viene directo de la columna cruda `modalidad`, solo normalizada y validada contra el catálogo.
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `jornada`

Jornada horaria en la que funciona el establecimiento educativo. Texto (string) en el CSV limpio, tipo analítico natural `category`. Dominio permitido: uno de 6 valores canónicos: `DOBLE`, `INTERMEDIA`, `MATUTINA`, `NOCTURNA`, `SIN JORNADA`, `VESPERTINA`; fuera de catálogo se marca `REVISAR:`. 6 categorías posibles.

Tratamiento aplicado: normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) más mapeo explícito a set canónico (incluye `S/J`→`SIN JORNADA`); fuera de catálogo pasa a `REVISAR:` (ver `docs/transformaciones.md#categoricas`). No es variable derivada, proviene directamente de la columna cruda `jornada`, solo normalizada y validada contra el catálogo. Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.

### `plan`

- **Descripción:** plan o régimen de estudios del establecimiento educativo.
- Tipo de dato: texto (string) en el CSV limpio; su tipo analítico natural es `category`.
- Dominio permitido: uno de 13 valores canónicos: `A DISTANCIA`, `DIARIO(REGULAR)`, `DOMINICAL`, `FIN DE SEMANA`, `INTERCALADO`, `IRREGULAR`, `MIXTO`, `SABATINO`, `SEMIPRESENCIAL`, `SEMIPRESENCIAL (DOS DÍAS A LA SEMANA)`, `SEMIPRESENCIAL (FIN DE SEMANA)`, `SEMIPRESENCIAL (UN DÍA A LA SEMANA)`, `VIRTUAL A DISTANCIA`; cualquier valor fuera de catálogo se marca con prefijo `REVISAR:`.
- Valores posibles: 13 categorías.
- Tratamiento aplicado: normalización (NFC, quitar control chars, colapsar espacios, `strip()`, MAYÚSCULAS) + mapeo explícito a set canónico (incluye `DIARIO (REGULAR)`→`DIARIO(REGULAR)`, `REGULAR`→`DIARIO(REGULAR)`); fuera de catálogo → `REVISAR:`. Ver `docs/transformaciones.md#categoricas`.
- Variable derivada: no, proviene directamente de la columna cruda `plan`, solo normalizada y validada contra el catálogo.
- Fecha de extracción: 2026-07-12. Fuente: buscador de establecimientos del MINEDUC. Versión: v1.0.
