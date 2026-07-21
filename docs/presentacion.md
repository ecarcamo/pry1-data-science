# Presentación: Obtención y Limpieza de los Datos
### Guion de diapositivas (qué incluir en cada slide)

**CC3084 – Data Science, UVG, Semestre II-2026. Equipo:** Esteban, Ernesto, Hugo

> Esta es la guía para armar la presentación. Cada bloque corresponde a 1 diapositiva. La línea "Incluir"
> dice explícitamente qué poner; "Decir" es el guion oral. El detalle completo está en `docs/informe_final.md`.
> Duración objetivo: ~10-12 min (13 slides).

---

### Slide 1: Portada

**Incluir:**
- Título: "Obtención y Limpieza de Datos, Establecimientos DIVERSIFICADO, MINEDUC".
- Curso, semestre, integrantes (Esteban, Ernesto, Hugo).
- Fuente + fecha de extracción: MINEDUC, 2026-07-12, v1.0.
- Link al repositorio.

**Decir:** de qué trata el proyecto en una frase y qué fuente se usó.

---

### Slide 2: Resumen ejecutivo (el antes y después de un vistazo)

Para esta diapositiva conviene incluir 3 bullets: 11,867 establecimientos de 23 departamentos; ninguna fila eliminada (lo dudoso se marca); resultado 19→31 variables y 39,330 correcciones. Además va la tabla antes/después completa (10 métricas), que es el corazón de la nota de "mejora objetiva".

**Decir:** "Todo lo que sigue explica cómo llegamos de esta columna a esta otra sin borrar datos."

---

### Slide 3: Obtención de los datos (Actividad 1-2, 5 pts)

**Incluir:**
- Diagrama simple: MINEDUC → `descarga.py` (Selenium) → 23 CSV crudos → `unir_datos.py` → CSV unido (11,867×19).
- Nota del bug de "Exportar a Excel" y por qué se extrae de la tabla renderizada.
- Que la unión es fiel (no limpia) y solo agrega `archivo_origen` + `id_registro`.

**Decir:** un scraper por departamento, unión validada (columnas + suma de filas).

---

### Slide 4: Diagnóstico del estado inicial (Actividad 3, 15 pts)

Va la cifra 11,867 × 19; todas cargadas como texto; hay que aclarar que `codigo` no debe volverse int (perdería los ceros a la izquierda). También la tabla de faltantes top: director 15.09%, telefono 7.97%, supervisor 4.51%, distrito 4.48%. Duplicados exactos son 0. Vale mostrar valores únicos clave (municipio 352 > ~340, señal de que hay problemas) y una captura de una tabla o gráfico del notebook `01_diagnostico.ipynb`.

**Decir:** qué problemas encontramos antes de tocar nada, esto justifica el plan.

---

### Slide 5: Problemas de calidad detectados (Actividad 3.f-3.h)

**Incluir:**
- `departamento`: CIUDAD CAPITAL (00) vs GUATEMALA (01) + 2,025 sin tildes.
- `municipio`: typos / fuera de catálogo. `telefono`: 23 sospechosos.
- Placeholders no informativos (`-`, `.`, `S/N`, `SIN DATO`, `XXX`) disfrazados de dato.
- Duplicados parciales (mismo centro con varios códigos).

**Decir:** estos son los 4-5 problemas reales que la limpieza va a resolver.

---

### Slide 6: Plan de limpieza (Actividad 4, 10 pts)

**Incluir:**
- Explicar el patrón: por cada variable, (a) problema, (b) regla + por qué, (c) riesgo.
- Tabla de reparto: Esteban / Ernesto / Hugo con sus variables.
- Un ejemplo completo (departamento): fusión 00+01 + tildes, riesgo mitigado con `_raw`.

**Decir:** no improvisamos, cada transformación se decidió y justificó antes de ejecutarla.

---

### Slide 7: Limpieza de texto, tipos y faltantes (Actividad 5.a-5.c)

Conviene mostrar cómo se tratan faltantes/vacíos/espacios/placeholders: todos van a `"NA"` explícito. También la normalización de texto (NFC, strip, espacios múltiples, MAYÚSCULAS, tildes, caracteres invisibles) y los tipos correctos (`codigo`/`id_registro` siempre texto). Un ejemplo antes→después de una celda ayuda mucho (ej. `"  colegio  x "` → `"COLEGIO X"`).

**Decir:** cada función es pura y preserva el original en `<var>_raw`.

---

### Slide 8: Limpieza de categorías, formatos y valores inválidos (Actividad 5.d-5.f)

**Incluir:**
- Categorías: mapeo `{variante → canónico}` + `REVISAR:` para lo fuera de catálogo (ej. `MONOLINGÜE`→`MONOLINGUE`).
- Formatos: `telefono` `####-####`, `codigo` `##-##-####-##`, `direccion` abreviaturas, `distrito` `##-###`.
- Valores inválidos: departamento/municipio contra catálogo INE; teléfono ≠ 8 dígitos → `NA`.
- Ejemplo real: `SAN MIGUEL PANAM`→`SAN MIGUEL PANÁN` (fuzzy); zonas 24/25 → `REVISAR:`.

**Decir:** unificamos categorías sin fusionar las que de verdad son distintas.

---

### Slide 9: Duplicados y consistencia (Actividad 5.g-5.i)

Los exactos dieron 0. Para los parciales usamos RapidFuzz 88-99 por departamento+municipio, lo que dio 4,301 pares a revisión manual; vale la pena recalcar que no se elimina ni fusiona nada automáticamente (columna `decision`). También entra la consistencia entre variables (`municipio` validado por `departamento`) y las variables derivadas: 11 `_raw` + `telefono_adicionales` (por qué, cómo, utilidad).

**Decir:** cumplimos "buscar duplicados parciales por similitud" sin destruir registros.

---

### Slide 10: Validación automática (Actividad 7, 10 pts)

**Incluir:**
- Que hay 13 pruebas (`pytest`) y una captura de `13 passed`.
- Listar 4-5 de las más representativas: sin duplicados, sin espacios de borde, catálogos, teléfono `####-####`, categóricas en dominio.

**Decir:** la calidad no es afirmación, es una suite que corre y pasa.

---

### Slide 11: Mejora objetiva (Actividad 8, 10 pts) — slide clave

Aquí se repite la tabla antes/después y se resaltan 3 filas: faltantes 3,890→4,377 sube y es bueno (placeholders ahora visibles como `NA`); formato 5→0, tipo 1→0, categorías 1→0; errores corregidos = 39,330 (volumen de operaciones, no filas). La frase que resume todo: no borramos nada, hicimos los problemas visibles y medibles.

**Decir:** el argumento de por qué el dataset está objetivamente mejor. Conviene anticipar la pregunta de por qué suben los faltantes.

---

### Slide 12: Conjunto limpio + Libro de códigos (Actividades 9-10, 20 pts)

**Incluir:**
- CSV final único: 11,867 × 31, estructura consistente, tipos correctos, reproducible.
- Libro de códigos: 9 campos por variable (descripción, tipo, dominio, valores, tratamiento, derivada,
  fecha, fuente, versión); autores por bloque de columnas.
- Recordatorio: exportar el libro de códigos a PDF (entregable).

**Decir:** este es el producto que un analista puede usar directamente.

---

### Slide 13: Reproducibilidad y cierre (Actividad 11)

Van los 5 comandos del pipeline (venv → install → main.py → generar_limpio.py → informe → pytest), la mención de que los docs (`transformaciones.md`, `informe_calidad.md`) se autogeneran y quedan en sync, un mapa rúbrica→evidencia (mini tabla) con la contribución de cada integrante, y el cierre: una frase de conclusión más preguntas.

**Decir:** cualquiera puede clonar y regenerar todo con las mismas cifras.

---

## Checklist antes de exponer

- [ ] Tabla antes/después visible en slides 2 y 11.
- [ ] Captura real de `13 passed` (slide 10) y de una tabla del notebook (slide 4).
- [ ] Ejemplo antes→después de al menos una celda (slide 7 u 8).
- [ ] PDF del libro de códigos exportado.
- [ ] Repo actualizado y link correcto en portada.
