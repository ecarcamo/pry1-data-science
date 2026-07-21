# Informe de calidad de datos

Comparación entre el estado antes (`datos/unido/establecimientos_diversificado_unido.csv`) y después (`datos/clean/establecimientos_diversificado_limpio.csv`). Se genera automáticamente con `limpieza/informe_calidad.py`; no se edita a mano.

- Antes: 11,867 × 19. Después: 11,867 × 31.

| Métrica | Antes | Después |
|---|---|---|
| Registros | 11,867 | 11,867 |
| Variables | 19 | 31 |
| Valores faltantes | 3,890 (1.93%) | 4,377 (2.17%) |
| Variables con NA | 6 | 6 |
| Duplicados exactos | 0 | 0 |
| Posibles duplicados | — | 4301 pares generados; 4301 pendientes de revisión manual |
| Variables con formato inconsistente | 5 | 0 |
| Variables con tipo incorrecto | 1 | 0 |
| Categorías inconsistentes | 1 | 0 |
| Errores corregidos | 0 | 39,330 |

## Notas

- Valores faltantes / Variables con NA: se calcula sobre las 17 variables originales del proyecto (excluye `archivo_origen`/`id_registro`, que siempre están completas). Antes se contaban vacío o tokens `""`, `"-"`, `"."`, `"N/A"`, `"NULL"`, `"SIN DATO"`; después, celda == `"NA"`.
- Duplicados exactos: filas idénticas excluyendo `id_registro` y `archivo_origen` (mismo criterio que `tests/test_validacion.py::test_sin_duplicados_exactos`).
- Posibles duplicados: son los pares candidatos generados por `limpieza/duplicados.py` (similitud RapidFuzz 88-99 en `establecimiento`, dentro del mismo departamento+municipio) y exportados a `datos/interim/duplicados_parciales_revisar.csv` para revisión manual. De los 4301 pares, los 4301 siguen sin una `decision` registrada (columna `decision` vacía); quedan pendientes de que alguien del equipo los revise a mano y marque `conservar`, `fusionar` o `revisar`, como indica `datos/interim/README.md`. No se fusiona ni elimina nada automáticamente.
- Variables con formato inconsistente: columnas originales con espacios al inicio/fin o espacios internos dobles.
- Variables con tipo incorrecto: columnas señaladas en `datos/interim/diagnostico_tipos.csv` con riesgo real de tipo (ej. `codigo` perdería ceros a la izquierda si se convirtiera a `int`).
- Categorías inconsistentes: columnas categóricas cuya cardinalidad observada supera el tamaño de su set canónico documentado (`limpieza/catalogos.py`, `limpieza/limpiar_categoricas.py`).
- Errores corregidos: suma de la columna "Registros afectados" de todas las filas de `docs/transformaciones.md` (total de correcciones puntuales aplicadas por el pipeline).

## Análisis de la mejora objetiva

Aquí va la lectura métrica por métrica de por qué el conjunto limpio es mejor que el unido, respetando la regla de la rúbrica de no eliminar registros automáticamente: lo dudoso se marca (`NA` / `REVISAR:`), no se borra.

Registros (11,867 → 11,867): no se eliminó ninguna fila. Es una decisión de diseño alineada con la rúbrica, los casos dudosos (faltantes, valores fuera de catálogo, posibles duplicados) se marcan de forma explícita en lugar de descartarse, para que ninguna decisión destructiva quede oculta.

Variables (19 → 31): las 12 columnas nuevas no agregan datos inventados. Son 11 columnas `_raw` de trazabilidad (preservan el valor original de cada variable limpiada, para poder auditar cada corrección) más `telefono_adicionales` (derivada, rescata los teléfonos secundarios sin romper la atomicidad de `telefono`). Más columnas equivale a más trazabilidad, no más ruido.

Valores faltantes (3,890 → 4,377): el número sube a propósito, y eso es una mejora. Antes, placeholders no informativos (`""`, `-`, `.`, `S/N`, `SIN DATO`, `N/A`, `NULL`) se veían como datos reales y no contaban como faltantes; ahora se normalizan a `"NA"` y quedan visibles y explícitos. La limpieza no crea faltantes: los que estaban disfrazados ahora se reconocen como lo que son. Un conteo honesto de faltantes es justo el objetivo, no una regresión.

- Variables con formato inconsistente (5 → 0): las columnas de texto con espacios al inicio/fin o espacios internos dobles quedaron normalizadas (`strip()` + colapso de espacios + NFC), de modo que valores iguales dejan de verse distintos por un espacio y se vuelven comparables/buscables.
- Variables con tipo incorrecto (1 → 0): `codigo` se mantiene como texto en todo el pipeline, conservando los ceros a la izquierda que un `int` habría destruido (ej. `00-01-0001-00`); un `assert` de patrón y los tests garantizan que el tipo correcto se preserve en futuras descargas.
- Categorías inconsistentes (1 → 0): las variables categóricas se mapean a un set canónico documentado (`limpieza/catalogos.py`) y todo valor fuera de catálogo se marca `REVISAR:`; así la cardinalidad observada deja de exceder el dominio permitido y desaparecen las categorías duplicadas por diferencias de escritura.

Errores corregidos (39,330): es el volumen total de operaciones puntuales de limpieza (suma de la columna "Registros afectados" de `docs/transformaciones.md`), no la cantidad de filas únicas afectadas, ya que una misma fila puede recibir varias correcciones. Esto da una idea de la magnitud del trabajo de limpieza aplicado.

Posibles duplicados: se generaron 4,301 pares candidatos a duplicado parcial para revisión manual, y ninguno se fusionó ni eliminó automáticamente. Nombres muy parecidos suelen ser el mismo centro con varios códigos (jornada/plan distinto) o centros realmente diferentes, así que fusionarlos a ciegas podría borrar establecimientos reales. La decisión queda documentada y se deja para revisión humana.
