# Informe final: Obtención y Limpieza de los Datos
### Establecimientos educativos de nivel DIVERSIFICADO, MINEDUC Guatemala
**CC3084 – Data Science, UVG, Semestre II-2026**

**Equipo:** Esteban, Ernesto, Hugo
**Fuente:** Buscador de establecimientos del MINEDUC, http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/
**Fecha de extracción:** 2026-07-12. **Versión del conjunto limpio:** v1.0
**Dataset:** 11,867 establecimientos, 23 archivos crudos (23 departamentos), nivel DIVERSIFICADO

> Este es el informe final del proceso. Cada sección mapea a una actividad de la rúbrica. Todas las cifras
> se generan por código y son reproducibles (ver §11). Para la exposición ver `docs/presentacion.md`.

---

## Resumen ejecutivo

Obtuvimos por scraping los 11,867 establecimientos de nivel DIVERSIFICADO de los 23 departamentos, los unimos fielmente y los limpiamos de forma transparente y reproducible. Ninguna fila se eliminó (regla de la rúbrica): lo dudoso se marca (`NA` / `REVISAR:`), no se borra. El resultado son 19 → 31 variables (12 nuevas de trazabilidad/derivadas), 39,330 correcciones puntuales, formato/tipo/categorías inconsistentes llevados a 0, y 13 pruebas automáticas en verde.

| Métrica | Antes | Después |
|---|---|---|
| Registros | 11,867 | 11,867 |
| Variables | 19 | 31 |
| Valores faltantes | 3,890 (1.93%) | 4,377 (2.17%) |
| Variables con NA | 6 | 6 |
| Duplicados exactos | 0 | 0 |
| Posibles duplicados | — | 4,301 pares (0 fusionados, revisión manual) |
| Variables con formato inconsistente | 5 | 0 |
| Variables con tipo incorrecto | 1 | 0 |
| Categorías inconsistentes | 1 | 0 |
| Errores corregidos | 0 | 39,330 |

---

## 1-2. Obtención y guardado de datos crudos (5 pts)

El scraping se hace con Selenium (`automatizacion/descarga.py`): por cada departamento se fija Municipio/Sector/Plan/Modalidad = TODOS y Nivel = DIVERSIFICADO, se ejecuta la búsqueda y se guarda un `.csv` crudo en `datos/crudos/`. El botón "Exportar a Excel" del sitio tiene un bug del servidor (siempre devuelve error de ASP.NET), así que en su lugar se extraen los datos directamente de la tabla renderizada, algo igual de fiel.

La unión (`automatizacion/unir_datos.py`) es fiel: concatena los 23 CSV crudos (17 columnas c/u), valida columnas idénticas y que las filas sumen exactamente, y no limpia nada. Agrega solo 2 columnas de trazabilidad: `archivo_origen` e `id_registro` (1..11867). La salida queda en `datos/unido/establecimientos_diversificado_unido.csv`, con 11,867 × 19.

**Archivos:** `automatizacion/{descarga.py, unir_datos.py, main.py}`, `datos/crudos/`, `datos/unido/`

---

## 3. Diagnóstico del estado inicial (15 pts)

Todo se genera por código sobre el conjunto unido; las tablas quedan en `datos/interim/` y en `notebooks/01_diagnostico.ipynb`.

**a. Registros y variables:** 11,867 registros × 19 variables (17 originales + `archivo_origen` + `id_registro`).

**b. Tipo de dato** (`diagnostico_tipos.csv`): todas cargadas como `str`. El riesgo real detectado está en `codigo` (perdería ceros a la izquierda si se convirtiera a `int`). Las categóricas son `departamento, municipio, nivel, sector, area, status, modalidad, jornada, plan`.

**c. Faltantes por variable** (`diagnostico_faltantes.csv`), top:

| Variable | Faltantes | % |
|---|---|---|
| director | 1,791 | 15.09% |
| telefono | 946 | 7.97% |
| supervisor | 535 | 4.51% |
| distrito | 532 | 4.48% |
| direccion | 81 | 0.68% |
| establecimiento | 5 | 0.04% |

El resto de variables no presenta faltantes en el crudo.

**d. Valores únicos** (`diagnostico_unicos.csv`): `nivel` 1, `modalidad` 2, `area` 3, `sector` 4, `status` 5, `jornada` 6, `plan` 13, `departamento` 23, `departamental` 26, `municipio` 352, `codigo`/`id_registro` 11,867 (únicos).

**e. Duplicados exactos:** 0 (el `codigo` es único por diseño del MINEDUC).

**f. Valores fuera de dominio / inconsistentes:**

La fuente separa CIUDAD CAPITAL (00) y GUATEMALA (01) dentro de `departamento`, y 2,025 registros vienen sin tildes. En `municipio` hay 352 únicos frente a los ~340 del catálogo INE, señal de typos o valores fuera de catálogo. `telefono` tiene 23 casos sospechosos (letras o pocos dígitos). Para `nivel` falta verificar que solo exista DIVERSIFICADO.

**g. Formatos inconsistentes:** aparecen espacios internos dobles y bordes en columnas de texto (`establecimiento` 1,396, `direccion` 485, `director` 868, `supervisor` 98); abreviaturas mixtas en `direccion` (`AV/AV.`, `No/No.`, `COL`, `Z.`, `BO`, `#`); y `distrito` con formato variable.

**h. Problemas potenciales de calidad:** placeholders no informativos (`-`, `.`, `S/N`, `SIN DATO`, `XXX`) que se ven como datos reales, ceros a la izquierda en `codigo`, y posibles duplicados parciales (mismo centro con varios códigos).

**Archivos:** `datos/interim/diagnostico_*.csv`, `notebooks/01_diagnostico.ipynb`

---

## 4. Plan de limpieza (10 pts)

Para cada variable documentamos: (a) problema, (b) regla y por qué funciona, (c) riesgos. El documento completo está en `docs/plan_limpieza.md`. Resumen por responsable:

| Autor | Variables |
|---|---|
| Esteban | `establecimiento`, `direccion` (+ duplicados) |
| Ernesto | `departamento`, `municipio`, `codigo`, `distrito`, `departamental`, `nivel` |
| Hugo | `telefono`, `director`, `supervisor`, categóricas (`sector, area, status, modalidad, jornada, plan`) |

Un ejemplo de regla + riesgo, patrón usado en todas: para `departamento`, el problema era 00/01 separados más tildes faltantes. La regla: fusionar CIUDAD CAPITAL+GUATEMALA en `GUATEMALA` y normalizar tildes al catálogo INE, preservando el original en `departamento_raw`. El riesgo era perder el matiz "capital vs interior", mitigado con `_raw`.

---

## 5. Limpieza del conjunto de datos (30 pts)

Cada variable se limpia con una función pura (`limpieza/limpiar_*.py`) que preserva el original en `<var>_raw` y solo toca su columna. El orquestador es `limpieza/generar_limpio.py`.

**a. Faltantes / cadenas vacías / espacios / placeholders** (`N/A`,`NULL`,`-`,`.`,`SIN DATO`…): se normalizan a `"NA"` explícito, con sets de placeholders explícitos y conservadores por columna.

**b. Tipo de dato:** `codigo` y `id_registro` siempre texto (conservan ceros a la izquierda); las categóricas quedan documentadas con su tipo analítico `category` en el Libro de Códigos.

**c. Normalización de texto:** NFC + `strip()` + colapsar espacios múltiples + quitar caracteres de control/invisibles (`Cc`/`Cf`) + MAYÚSCULAS defensivas + tildes correctas al catálogo. No se altera la ortografía de nombres propios.

**d. Consistencia de categorías:** mapeo explícito `{variante → canónico}` por columna (ej. `DIARIO (REGULAR)`→`DIARIO(REGULAR)`, `MONOLINGÜE`→`MONOLINGUE`, `S/J`→`SIN JORNADA`); lo fuera de catálogo pasa a `REVISAR:`. Cada unificación queda justificada y se evita fusionar categorías realmente distintas.

**e. Formatos:** `telefono` → `####-####` (8 dígitos GT); `codigo` → assert `##-##-####-##`; `direccion` → abreviaturas estandarizadas; `distrito` → formato `##-###`.

**f. Valores inválidos:** `departamento`/`municipio` se validan contra catálogo INE (fuera → `REVISAR:`); `telefono` con letras o largo distinto de 8 → `"NA"`; `codigo` fuera de patrón → `REVISAR:` (0 casos).

**g. Duplicados (exactos + parciales):** los exactos dieron 0 (excluyendo `id_registro`/`archivo_origen`). Para los parciales usamos RapidFuzz `token_sort_ratio` 88-99 dentro de mismo departamento+municipio, lo que arrojó 4,301 pares en `datos/interim/duplicados_parciales_revisar.csv` (columna `decision`). No se elimina ni fusiona nada automáticamente; queda documentado para revisión manual.

**h. Consistencia entre variables:** `municipio` se valida por su `departamento` ya limpio; `departamental` se verifica consistente con `departamento` (Guatemala subdividida en 4 zonas, algo intencional).

**i. Variables derivadas** (todas documentadas en el Libro de Códigos): las 11 columnas `_raw` (trazabilidad del valor original) y `telefono_adicionales` (rescata teléfonos secundarios sin romper la atomicidad de `telefono`). También `archivo_origen` e `id_registro` (trazabilidad de la unión).

Entre las correcciones destacadas: fusión 00+01 (2,161 filas), tildes en `departamento` (2,025), 1 municipio corregido con fuzzy (`SAN MIGUEL PANAM`→`SAN MIGUEL PANÁN`), 8 marcados `REVISAR:` (zonas 24/25 de capital), 946+127 teléfonos → `NA`, 2,143 directores → `NA`.

**Archivos:** `limpieza/limpiar_*.py`, `limpieza/{generar_limpio.py, duplicados.py, catalogos.py}`

---

## 6. Registro de transformaciones (reproducible)

Se documenta una tabla `Variable | Problema | Transformación | Registros afectados | Justificación` por bloque de limpieza, autogenerada por cada script entre marcadores idempotentes. La suma de "Registros afectados" da 39,330 (la métrica "Errores corregidos" del informe).

**Archivo:** `docs/transformaciones.md`

---

## 7. Validación del conjunto limpio (10 pts)

Son 13 pruebas automáticas (`tests/test_validacion.py`, `pytest`), todas en verde:

| # | Prueba | Verifica |
|---|---|---|
| 1 | `test_sin_duplicados_exactos` | 0 filas idénticas |
| 2 | `test_sin_espacios_al_inicio_fin` | sin espacios de borde |
| 3 | `test_departamentos_en_catalogo` | catálogo INE |
| 4 | `test_municipios_sin_escritura_duplicada` | catálogo por depto |
| 5 | `test_codigo_patron` | `##-##-####-##` |
| 6 | `test_codigo_tipo_texto` | tipo texto / ceros preservados |
| 7 | `test_nivel_solo_diversificado` | dominio único |
| 8 | `test_tipos_esperados_son_texto` | tipos esperados |
| 9 | `test_sin_categorias_duplicadas_por_casing` | sin dup. por escritura |
| 10 | `test_telefono_formato` | `####-####` o `NA` |
| 11 | `test_telefono_adicionales_formato` | formato derivada |
| 12 | `test_categoricas_en_dominio` | sets canónicos |
| 13 | `test_personas_normalizadas` | director/supervisor |

Se ejecuta con: `PYTHONPATH="$PWD" python -m pytest tests/test_validacion.py -q`, y el resultado es 13 passed.

---

## 8. Informe de calidad, mejora objetiva (10 pts)

La tabla antes/después se autogenera (`limpieza/informe_calidad.py`) junto con una narrativa métrica por métrica. El documento completo está en `docs/informe_calidad.md`. Algunos puntos clave:

Los registros se mantuvieron en 11,867→11,867: no se borró ninguna fila (decisión de rúbrica), lo dudoso se marca. Las variables pasaron de 19→31, +12 entre 11 `_raw` de trazabilidad y `telefono_adicionales` (derivada). Los faltantes subieron de 3,890→4,377, y eso es bueno: antes los placeholders se contaban como datos, ahora son `NA` explícito, así que los faltantes reales quedan visibles. La limpieza no crea faltantes, los revela.

En formato, tipo y categorías la mejora es directa: 5→0, 1→0 y 1→0 respectivamente (normalización + tipos + catálogos). Los errores corregidos llegan a 39,330, que es el volumen de operaciones puntuales, no de filas únicas. Sobre los posibles duplicados: 4,301 pares candidatos, 0 fusionados o eliminados, con revisión manual documentada.

---

## 9. Generación del conjunto limpio (10 pts)

Se generó un único CSV con los 23 departamentos que cumple con estructura consistente, tipos correctos, nombres descriptivos, formato uniforme y sin errores de validación.

La salida es `datos/clean/establecimientos_diversificado_limpio.csv`, con 11,867 × 31 registros. No se versiona porque es reproducible: se regenera con `python limpieza/generar_limpio.py`.

---

## 10. Libro de códigos (10 pts), PDF entregable

Para cada una de las 31 variables se documenta: descripción, tipo, dominio permitido, valores posibles, tratamiento aplicado, variable derivada, fecha de extracción (2026-07-12), fuente y versión (v1.0). Los autores por bloque de columnas son Esteban (6 col.), Ernesto (12 col.), Hugo (13 col.).

**Archivo:** `docs/libro_de_codigos.md` → exportar a PDF (pandoc / VS Code).

---

## 11. Reproducibilidad

```bash
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd automatizacion && python main.py        # opción 3: descargar 23 deptos + unir
cd .. && python limpieza/generar_limpio.py # aplica toda la limpieza → datos/clean/
python limpieza/informe_calidad.py         # regenera informe antes/después
PYTHONPATH="$PWD" python -m pytest tests/test_validacion.py -q
```

Todo el pipeline es determinista: las mismas entradas producen las mismas salidas. Los docs autogenerados (`transformaciones.md`, `informe_calidad.md`) quedan siempre en sync con el CSV limpio.

---

## Mapa rúbrica → evidencia

| Actividad (pts) | Evidencia |
|---|---|
| Obtención + unión (5) | `automatizacion/`, `datos/crudos/`, `datos/unido/` |
| Diagnóstico (15) | `notebooks/01_diagnostico.ipynb`, `datos/interim/diagnostico_*.csv` |
| Plan de limpieza (10) | `docs/plan_limpieza.md` |
| Limpieza de calidad (30) | `limpieza/limpiar_*.py`, `generar_limpio.py`, `duplicados.py` |
| Pruebas (10) | `tests/test_validacion.py` — 13 passed |
| Mejora objetiva (10) | `docs/informe_calidad.md` (tabla + narrativa) |
| Libro de códigos (10) | `docs/libro_de_codigos.md` → PDF |
| Conjunto limpio (10) | `datos/clean/…_limpio.csv` (11,867 × 31) |

## Material a entregar

- [x] Código del proceso completo (`automatizacion/`, `limpieza/`, `tests/`, `notebooks/`).
- [x] Link del repositorio (código + datos + libro de códigos).
- [x] Libro de códigos en markdown (`docs/libro_de_codigos.md`).
- [ ] Libro de códigos en PDF (exportar `docs/libro_de_codigos.md`).
- [x] CSV con los datos limpios (`datos/clean/establecimientos_diversificado_limpio.csv`).
