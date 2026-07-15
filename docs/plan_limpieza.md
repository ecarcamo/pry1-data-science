# Plan de limpieza — Variables geográficas y códigos (Actividad 4)

**Autor:** Ernesto  
**Variables:** `departamento`, `municipio`, `distrito`, `codigo`, `departamental`, `nivel`  
**Fuente:** `datos/unido/establecimientos_diversificado_unido.csv` (11,867 × 19)

---

## 1. `departamento`

### (a) Problema detectado
- La fuente descarga por separado **CIUDAD CAPITAL** (código 00) y **GUATEMALA** (código 01), tratándolos como departamentos distintos, aunque oficialmente Guatemala es **un solo departamento** de los 22 reconocidos.
- Además, **2,025 registros** (17% del total) usan variantes sin tildes: `SACATEPEQUEZ`, `PETEN`, `SOLOLA`, `TOTONICAPAN`, `QUICHE`, `SUCHITEPEQUEZ` en lugar de `SACATEPÉQUEZ`, `PETÉN`, `SOLOLÁ`, `TOTONICAPÁN`, `QUICHÉ`, `SUCHITEPÉQUEZ`.

### (b) Regla de corrección y justificación
1. **Normalización de tildes:** normalizar a la forma canónica oficial con tildes correctas (MAYÚSCULAS). Comparación sin tildes para matching; valor guardado siempre con tilde.
2. **Decisión 00+01 → GUATEMALA:** unificar `CIUDAD CAPITAL` y `GUATEMALA` bajo el valor canónico `GUATEMALA`, preservando el original en `departamento_raw`. Justificación: el catálogo oficial del INE reconoce 22 departamentos; la distinción 00/01 es un artefacto del selector del MINEDUC, no una entidad administrativa real. Documentar la fusión en `docs/transformaciones.md`.
3. **Validar contra catálogo de 22 departamentos:** cualquier valor que no matchee → marcar con prefijo `REVISAR:` (no borrar).

### (c) Riesgos
- Unificar 00+01 pierde la información del sector "Ciudad Capital" vs "Guatemala interior". Se mitiga con `departamento_raw`.
- Si en una futura descarga aparece un nuevo valor de departamento, se marcará automáticamente como `REVISAR:` en lugar de fallar silenciosamente.

---

## 2. `municipio`

### (a) Problema detectado
- Catálogo esperado: ~340 municipios distribuidos en 22 departamentos (INE).
- Posibles typos (nombres casi correctos), municipios en departamento equivocado, o valores completamente fuera de catálogo.
- Cardinalidad observada: **352 valores únicos** (esperado ≤340) → hay al menos 12 valores no estándar.

### (b) Regla de corrección y justificación
1. Normalizar a MAYÚSCULAS con tildes correctas (igual que departamento).
2. Para cada registro, buscar el municipio en el catálogo filtrado por su `departamento` ya limpio.
3. Correcciones de typo con **RapidFuzz** (`token_sort_ratio ≥ 90`), comparando sin tildes. Cada corrección se documenta en `docs/transformaciones.md` con el valor original → canónico.
4. Municipios fuera de catálogo sin match suficiente: marcar `REVISAR:` + exportar a `datos/interim/municipios_fuera_catalogo.csv` para revisión manual.

### (c) Riesgos
- Un umbral de RapidFuzz muy bajo puede corregir incorrectamente; se fija en ≥ 90 para reducir falsos positivos.
- Municipios nuevos creados desde la última actualización del catálogo (Guatemala tiene municipios relativamente estables, riesgo bajo).

---

## 3. `distrito`

### (a) Problema detectado
- **532 registros con valor vacío** (4.48% de faltantes).
- Formato inconsistente: algunos valores usan `01-` sin sufijo, otros `01-403`, otros cadena vacía.
- Muestra: `01-`, `01-403`, `05-033`, etc. (patrón esperado: `##-###`).

### (b) Regla de corrección y justificación
1. Preservar en `distrito_raw`.
2. Normalizar espacios y strip.
3. Valores vacíos → marcar `"NA"` (sin datos; no se puede inferir el distrito desde otras columnas).
4. No se corrige el contenido (no hay catálogo público oficial de distritos escolares MINEDUC disponible).

### (c) Riesgos
- Sin catálogo de referencia, no se puede validar más allá del formato. Documentar la limitación.

---

## 4. `codigo`

### (a) Problema detectado
- El diagnóstico confirmó **0 códigos fuera del patrón** `##-##-####-##`.
- Los 11,867 códigos son únicos (ya verificado por la unión).
- Riesgo latente: conversión a int perdería ceros a la izquierda (ej. `00-01-0001-00`).

### (b) Regla de corrección y justificación
1. Preservar en `codigo_raw`.
2. Verificar (assert) que todos cumplan `^\d{2}-\d{2}-\d{4}-\d{2}$`.
3. Mantener tipo `str` en todo momento — nunca convertir a int/float.
4. Generar reporte: si algún código no cumple el patrón, exportarlo a `datos/interim/codigos_invalidos.csv`.

### (c) Riesgos
- Bajo (0 inválidos en el dataset actual). El assert sirve de guardia para futuras descargas.

---

## 5. `departamental`

### (a) Problema detectado
- 26 valores únicos observados (más que los 22 departamentos: Guatemala aparece subdividida en zonas: `GUATEMALA NORTE`, `GUATEMALA SUR`, `GUATEMALA ORIENTE`, `GUATEMALA OCCIDENTE`).
- Sin faltantes. Posibles inconsistencias de escritura.

### (b) Regla de corrección y justificación
1. Preservar en `departamental_raw`.
2. Strip + normalizar a MAYÚSCULAS con tildes (igual patrón del proyecto).
3. Validar que cada valor de `departamental` sea consistente con `departamento` limpio (mismo depto o subdivisión conocida).
4. Documentar los valores observados y su mapping a departamento oficial.

### (c) Riesgos
- La subdivisión de Guatemala en zonas es intencional (estructura administrativa MINEDUC), no un error. Documentar explícitamente en transformaciones.

---

## 6. `nivel`

### (a) Problema detectado
- El diagnóstico confirmó que los **11,867 registros tienen exactamente un valor:** `DIVERSIFICADO`.
- Sin faltantes, sin variantes de escritura.

### (b) Regla de corrección y justificación
1. Preservar en `nivel_raw` (defensivo).
2. Assert de que `df["nivel"].nunique() == 1 and df["nivel"].iloc[0] == "DIVERSIFICADO"`.
3. No se modifica el valor — ya está en el formato correcto.

### (c) Riesgos
- Casi nulo. Si una futura descarga incluyera otro nivel, el assert lo detecta.

---

## Orden de aplicación (Actividad 5)

```
clean_departamento(df)          # normaliza tildes + fusión 00/01 + valida catálogo
clean_municipio(df)             # valida por depto ya limpio + RapidFuzz + marcado
clean_codigo(df)                # assert patrón + mantener str
clean_distrito_departamental_nivel(df)  # normaliza + assert nivel
```

Cada función es pura: recibe el DataFrame, devuelve una copia con `<var>_raw` + `<var>` limpiada. Solo toca sus columnas.
