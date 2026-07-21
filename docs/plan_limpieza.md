# Plan de limpieza - Nombre y dirección del establecimiento (Actividad 4)

**Autor:** Esteban
**Variables:** `establecimiento`, `direccion`
**Fuente:** `datos/unido/establecimientos_diversificado_unido.csv` (11,867 × 19)

---

## 1. `establecimiento`

### (a) Problema detectado

Encontré 1,396 registros con espacios múltiples internos y 5 valores vacíos (cadena vacía), con IDs afectados `114`, `1814`, `3644`, `7592` y `9627`. También revisé caracteres de control o texto no normalizado en Unicode (NFC): 0 detectados en esta corrida, aunque se verifica de forma defensiva por si aparecen en el futuro. Hay 2,228 registros con comillas dobles (ej. `COLEGIO "SANTA ANA"`), pero esto no es un error: son parte del nombre propio. El casing ya viene 100% en MAYÚSCULAS (0 registros en minúscula detectados). Por último, aparecen nombres parecidos pero distintos (ej. `AMERICA` vs `AMÉRICA`), que son candidatos a duplicado parcial y no un problema de formato.

### (b) Regla de corrección y justificación

1. Preservar el original en `establecimiento_raw`.
2. Normalizar a NFC, colapsar espacios múltiples a uno solo, `strip()`. Justificación: no cambia el contenido, solo el separador.
3. Quitar caracteres de control invisibles (categoría Unicode `Cc`) de forma defensiva, sin tocar tildes/ñ.
4. Valores vacíos pasan a `"NA"`. Justificación: no hay forma de inferir el nombre real de un establecimiento a partir de otras columnas; inventarlo sería peor que dejarlo faltante.
5. `.upper()` defensivo (el dataset ya viene en MAYÚSCULAS). Descarté Title Case por acrónimos con puntos (`C.E.T.A.CH.`) y numerales (`NO. 1`); es la opción conservadora, cero riesgo.
6. Comillas dobles y variantes con/sin tilde no se autocorrigen: son parte del nombre propio o candidatos a duplicado parcial que requieren revisión manual (ver `detectar_duplicados` más abajo), no una corrección de formato segura.

### (c) Riesgos

Marcar como `"NA"` un establecimiento sin nombre en la fuente pierde esa fila para búsquedas por nombre; se mitiga documentando los IDs afectados y preservando `establecimiento_raw`. Corregir automáticamente nombres "parecidos" (fuzzy) arriesga fusionar centros educativos realmente distintos, por eso se deja para revisión manual vía `datos/interim/duplicados_parciales_revisar.csv` en lugar de fusionar aquí.

---

## 2. `direccion`

### (a) Problema detectado

Hay 485 registros con espacios múltiples internos y 89 valores vacíos o placeholders no informativos (cadena vacía, `.`, `---`, `S/N`, etc.). El vocabulario de direcciones tiene abreviaturas inconsistentes: `AV`/`AV.` (405), `No`/`No.` (253), `COL`/`COL.` (25), `#` (23), `Z.` (11), `BO`/`BO.` (3).

### (b) Regla de corrección y justificación

1. Preservar el original en `direccion_raw`.
2. Normalizar a NFC, colapsar espacios múltiples, `strip()`, quitar caracteres de control invisibles.
3. Valores vacíos o placeholders no informativos pasan a `"NA"`. Justificación: no aportan información real de ubicación; inventar una dirección sería peor que dejarla faltante.
4. Estandarizar abreviaturas a su forma completa (`AV`→`AVENIDA`, `COL`→`COLONIA`, `Z.`→`ZONA`, `BO`→`BARRIO`, `#`/`No`→`NO.`) con regex de límites de palabra (`\b`), para no romper palabras que las contengan. Justificación: uniformar el vocabulario para que sea comparable/buscable.
5. `.upper()`, la misma decisión que en `establecimiento`, por consistencia entre columnas de texto del dataset.

### (c) Riesgos

El diccionario de abreviaturas es explícito y usa límites de palabra para evitar falsos positivos (p. ej. no reemplaza dentro de una palabra que solo contenga "AV" como substring); una abreviatura ambigua no listada simplemente no se corrige. Marcar placeholders como `"NA"` es conservador: el set de placeholders (`PLACEHOLDERS_EXACTOS`) es explícito para evitar borrar direcciones reales que casualmente sean cortas.

---

## Orden de aplicación (Esteban)

```
clean_establecimiento(df)   # normaliza formato + NA para vacíos
clean_direccion(df)         # normaliza formato + NA para no informativos + abreviaturas estandarizadas
...
detectar_duplicados(df)     # al final del pipeline completo (generar_limpio.py): genera
                             # datos/interim/duplicados_parciales_revisar.csv; no elimina filas
```

Cada función de limpieza es pura: recibe el DataFrame, devuelve una copia con `<var>_raw` + `<var>` limpiada; solo toca sus columnas. `detectar_duplicados` corre después de todas las limpiezas (incluidas las de Ernesto), porque agrupa candidatos por `departamento` + `municipio` ya limpios. Ver `docs/transformaciones.md`.

---
---

# Plan de limpieza para las variables geográficas y de códigos (Actividad 4)

**Autor:** Ernesto
**Variables:** `departamento`, `municipio`, `distrito`, `codigo`, `departamental`, `nivel`
**Fuente:** `datos/unido/establecimientos_diversificado_unido.csv` (11,867 × 19)

---

## 1. `departamento`

### (a) Problema detectado

- La fuente descarga por separado **CIUDAD CAPITAL** (código 00) y **GUATEMALA** (código 01), tratándolos como departamentos distintos, aunque oficialmente Guatemala es un solo departamento de los 22 reconocidos.
- 2,025 registros (17% del total) usan variantes sin tildes: `SACATEPEQUEZ`, `PETEN`, `SOLOLA`, `TOTONICAPAN`, `QUICHE`, `SUCHITEPEQUEZ`, en lugar de `SACATEPÉQUEZ`, `PETÉN`, `SOLOLÁ`, `TOTONICAPÁN`, `QUICHÉ`, `SUCHITEPÉQUEZ`.

### (b) Regla de corrección y justificación

1. **Normalización de tildes:** se normaliza a la forma canónica oficial con tildes correctas (MAYÚSCULAS). La comparación es sin tildes para el matching, pero el valor guardado siempre lleva tilde.
2. **Decisión 00+01 → GUATEMALA:** unificar `CIUDAD CAPITAL` y `GUATEMALA` bajo el valor canónico `GUATEMALA`, preservando el original en `departamento_raw`. El catálogo oficial del INE reconoce 22 departamentos; la distinción 00/01 es un artefacto del selector del MINEDUC, no una entidad administrativa real. La fusión queda documentada en `docs/transformaciones.md`.
3. **Validar contra catálogo de 22 departamentos:** cualquier valor que no matchee se marca con prefijo `REVISAR:` (no se borra).

### (c) Riesgos

Unificar 00+01 pierde la información del sector "Ciudad Capital" vs "Guatemala interior", pero se mitiga con `departamento_raw`. Si en una futura descarga aparece un nuevo valor de departamento, se marcará automáticamente como `REVISAR:` en lugar de fallar silenciosamente.

---

## 2. `municipio`

### (a) Problema detectado

El catálogo esperado tiene ~340 municipios distribuidos en 22 departamentos (INE). Pueden aparecer typos (nombres casi correctos), municipios en departamento equivocado o valores completamente fuera de catálogo. La cardinalidad observada es de 352 valores únicos (esperado ≤340), es decir hay al menos 12 valores no estándar.

### (b) Regla de corrección y justificación

1. Normalizar a MAYÚSCULAS con tildes correctas (igual que departamento).
2. Para cada registro, buscar el municipio en el catálogo filtrado por su `departamento` ya limpio.
3. Correcciones de typo con RapidFuzz (`token_sort_ratio ≥ 90`), comparando sin tildes. Cada corrección se documenta en `docs/transformaciones.md` con el valor original → canónico.
4. Municipios fuera de catálogo sin match suficiente se marcan `REVISAR:` y se exportan a `datos/interim/municipios_fuera_catalogo.csv` para revisión manual.

### (c) Riesgos

Un umbral de RapidFuzz muy bajo puede corregir incorrectamente; se fija en ≥ 90 para reducir falsos positivos. También existe el riesgo de municipios nuevos creados desde la última actualización del catálogo, aunque en Guatemala los municipios son relativamente estables, así que el riesgo es bajo.

---

## 3. `distrito`

### (a) Problema detectado

Hay 532 registros con valor vacío (4.48% de faltantes). El formato es inconsistente: algunos valores usan `01-` sin sufijo, otros `01-403`, otros cadena vacía (muestra: `01-`, `01-403`, `05-033`, etc., patrón esperado `##-###`).

### (b) Regla de corrección y justificación

1. Preservar en `distrito_raw`.
2. Normalizar espacios y strip.
3. Valores vacíos pasan a `"NA"` (sin datos; no se puede inferir el distrito desde otras columnas).
4. No se corrige el contenido, no hay catálogo público oficial de distritos escolares MINEDUC disponible.

### (c) Riesgos

Sin catálogo de referencia no se puede validar más allá del formato; queda documentada esta limitación.

---

## 4. `codigo`

### (a) Problema detectado

El diagnóstico confirmó 0 códigos fuera del patrón `##-##-####-##`. Los 11,867 códigos son únicos (ya verificado por la unión). Queda un riesgo latente: convertir a int perdería ceros a la izquierda (ej. `00-01-0001-00`).

### (b) Regla de corrección y justificación

1. Preservar en `codigo_raw`.
2. Verificar (assert) que todos cumplan `^\d{2}-\d{2}-\d{4}-\d{2}$`.
3. Mantener tipo `str` en todo momento, nunca convertir a int/float.
4. Generar reporte: si algún código no cumple el patrón, exportarlo a `datos/interim/codigos_invalidos.csv`.

### (c) Riesgos

Bajo (0 inválidos en el dataset actual). El assert sirve de guardia para futuras descargas.

---

## 5. `departamental`

### (a) Problema detectado

Se observan 26 valores únicos, más que los 22 departamentos, porque Guatemala aparece subdividida en zonas: `GUATEMALA NORTE`, `GUATEMALA SUR`, `GUATEMALA ORIENTE`, `GUATEMALA OCCIDENTE`. No hay faltantes, aunque sí posibles inconsistencias de escritura.

### (b) Regla de corrección y justificación

1. Preservar en `departamental_raw`.
2. Strip + normalizar a MAYÚSCULAS con tildes (igual patrón del proyecto).
3. Validar que cada valor de `departamental` sea consistente con `departamento` limpio (mismo depto o subdivisión conocida).
4. Documentar los valores observados y su mapping a departamento oficial.

### (c) Riesgos

La subdivisión de Guatemala en zonas es intencional (estructura administrativa MINEDUC), no un error; se documenta explícitamente en transformaciones.

---

## 6. `nivel`

### (a) Problema detectado

El diagnóstico confirmó que los 11,867 registros tienen exactamente un valor: `DIVERSIFICADO`. Sin faltantes, sin variantes de escritura.

### (b) Regla de corrección y justificación

1. Preservar en `nivel_raw` (defensivo).
2. Assert de que `df["nivel"].nunique() == 1 and df["nivel"].iloc[0] == "DIVERSIFICADO"`.
3. No se modifica el valor, ya está en el formato correcto.

### (c) Riesgos

Casi nulo. Si una futura descarga incluyera otro nivel, el assert lo detecta.

---

## Orden de aplicación (Actividad 5)

```
clean_departamento(df)          # normaliza tildes + fusión 00/01 + valida catálogo
clean_municipio(df)             # valida por depto ya limpio + RapidFuzz + marcado
clean_codigo(df)                # assert patrón + mantener str
clean_distrito_departamental_nivel(df)  # normaliza + assert nivel
```

Cada función es pura: recibe el DataFrame, devuelve una copia con `<var>_raw` + `<var>` limpiada. Solo toca sus columnas.

---
---

# Plan de limpieza: contacto, personas y categóricas (Hugo)

**Autor:** Hugo
**Variables:** `telefono`, `director`, `supervisor`, `sector`, `area`, `status`, `modalidad`, `jornada`, `plan`
**Fuente:** `datos/unido/establecimientos_diversificado_unido.csv` (11,867 × 19)

---

## 7. `telefono`

### (a) Problema detectado

946 registros vienen vacíos (7.97%). El formato es heterogéneo: en su mayoría son 8 dígitos pelados, pero hay valores con más dígitos (14, 15, 16, 21, 24) que corresponden a varios números pegados o con separadores (`,`, `/`, ` Y `). También hay 9 registros con letras y unos ~50 con menos de 8 dígitos (2 a 7), teléfonos incompletos o inválidos.

### (b) Regla de corrección y justificación

1. Preservar el original en `telefono_raw`.
2. Separar múltiples números por `/ , ; Y/E` y des-concatenar secuencias de dígitos cuyo largo sea múltiplo de 8 (ej. 16 dígitos = dos números).
3. Validar 8 dígitos (longitud oficial de teléfonos en Guatemala). Un teléfono es válido solo si al quitar lo no-numérico quedan exactamente 8 dígitos.
4. Formato consistente `####-####` (convención guatemalteca de 4-4) para todos los válidos.
5. El primer número válido va en `telefono`; los demás en la variable derivada `telefono_adicionales` (`; ` como separador, `NA` si no hay).
6. Vacíos, con letras o con largo distinto de 8 pasan a `"NA"` (no se borra la fila).

### (c) Riesgos

Al quedarnos con el primer número como principal podríamos relegar el "principal real" a `telefono_adicionales`, algo que se mitiga conservando todos los números y el `telefono_raw`. Números de 8 dígitos que en realidad sean erróneos no se detectan, porque no hay catálogo de teléfonos: solo se valida forma, no existencia.

---

## 8. `director` y `supervisor`

### (a) Problema detectado

Hay muchos faltantes: `director` con 1,733 vacíos más placeholders (`-`, `--`, `.`, `SIN DATO`, `XXX`, etc., ~410); `supervisor` con 535 vacíos. `director` tiene 868 registros con espacios múltiples internos y `supervisor` tiene 98. Existe riesgo de caracteres invisibles (` `, zero-width), aunque no se detectaron en esta descarga. El casing ya está 100% en MAYÚSCULAS.

### (b) Regla de corrección y justificación

1. Preservar el original en `director_raw` / `supervisor_raw`.
2. Quitar invisibles + caracteres de control (categorías Unicode `Cc`/`Cf`), NFC, `strip`, colapsar espacios múltiples.
3. MAYÚSCULAS (decisión del proyecto), sin cambiar las letras del nombre: se normaliza formato, no ortografía, porque son nombres propios de personas reales.
4. Valores no informativos (vacío, solo puntuación, `SIN DATO`, `XXX`, `N/A`, `NULL`, etc.) pasan a `"NA"`.

### (c) Riesgos

Marcar como `NA` un placeholder que fuera un nombre real es improbable, la lista de placeholders es explícita y conservadora. Tampoco se corrigen typos de nombres propios a propósito: conservar la ortografía real evita inventar identidades.

---

## 9. Categóricas: `sector`, `area`, `status`, `modalidad`, `jornada`, `plan`

### (a) Problema detectado

Un `value_counts()` sobre las 6 columnas muestra sets ya consistentes y en MAYÚSCULAS: `sector` (4), `area` (3, incluye `SIN ESPECIFICAR`), `status` (5), `modalidad` (2, `MONOLINGUE`/`BILINGUE` sin diéresis, tal como la fuente), `jornada` (6), `plan` (13). No se observan variantes de casing ni espacios sobrantes en esta descarga, pero es el punto donde suelen aparecer (caso `Guatemala`/`GUATEMALA` de la rúbrica, aplicado a categóricas).

### (b) Regla de corrección y justificación

1. Normalizar formato: NFC, quitar control chars, colapsar espacios, `strip`, MAYÚSCULAS.
2. Aplicar un diccionario de mapeo explícito `{"variante": "CANONICO"}` por columna (ej. `DIARIO (REGULAR)` → `DIARIO(REGULAR)`, `MONOLINGÜE` → `MONOLINGUE`). Sirve para unificar diferencias de escritura y como guardia documentada para futuras descargas.
3. Validar contra el set canónico de cada columna; cualquier valor fuera lleva prefijo `REVISAR:` (no se borra).
4. El tipo analítico natural es `category`; se documenta en el Libro de Códigos (el CSV limpio se mantiene como texto para no perder el tipo al serializar y para que el pipeline de validación opere sobre str).

### (c) Riesgos

Un mapeo demasiado agresivo podría fusionar categorías realmente distintas; por eso el diccionario es explícito y auditable, y las categorías de `plan` (que parecen similares, ej. las variantes de `SEMIPRESENCIAL`) se conservan como valores distintos.

---

## Orden de aplicación (Hugo, dentro de `generar_limpio.py`)

```
clean_telefono(df)      # separa múltiples + valida 8 dígitos + formato ####-#### + telefono_adicionales
clean_director(df)      # normaliza formato, MAYÚSCULAS, NA para no informativos
clean_supervisor(df)    # idem director
clean_categoricas(df)   # normaliza + mapeo canónico + REVISAR: para fuera de dominio
```
