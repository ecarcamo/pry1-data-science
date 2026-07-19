# Informe de calidad de datos

Comparación **antes** (`datos/unido/establecimientos_diversificado_unido.csv`) vs. **después** (`datos/clean/establecimientos_diversificado_limpio.csv`). Generado automáticamente por `limpieza/informe_calidad.py`; no editar a mano.

- Antes: 11,867 × 19 — Después: 11,867 × 31

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

- **Valores faltantes / Variables con NA**: calculado sobre las 17 variables originales del proyecto (excluye `archivo_origen`/`id_registro`, que siempre están completas). Antes: vacío o tokens `""`, `"-"`, `"."`, `"N/A"`, `"NULL"`, `"SIN DATO"`. Después: celda == `"NA"`.
- **Duplicados exactos**: filas idénticas excluyendo `id_registro` y `archivo_origen` (mismo criterio que `tests/test_validacion.py::test_sin_duplicados_exactos`).
- **Posibles duplicados**: pares candidatos generados por `limpieza/duplicados.py` (similitud RapidFuzz 88–99 en `establecimiento`, dentro del mismo departamento+municipio) y exportados a `datos/interim/duplicados_parciales_revisar.csv` para revisión manual. De los 4301 pares, 4301 siguen sin una `decision` registrada (columna `decision` vacía) — quedan pendientes de que alguien del equipo los revise a mano y marque `conservar`, `fusionar` o `revisar`, como indica `datos/interim/README.md`. No se fusiona ni elimina nada automáticamente.
- **Variables con formato inconsistente**: columnas originales con espacios al inicio/fin o espacios internos dobles. <!-- TODO Ernesto: narrativa de mejora objetiva -->
- **Variables con tipo incorrecto**: columnas señaladas en `datos/interim/diagnostico_tipos.csv` con riesgo real de tipo (ej. `codigo` perdería ceros a la izquierda si se convirtiera a `int`). <!-- TODO Ernesto: narrativa de mejora objetiva -->
- **Categorías inconsistentes**: columnas categóricas cuya cardinalidad observada supera el tamaño de su set canónico documentado (`limpieza/catalogos.py`, `limpieza/limpiar_categoricas.py`). <!-- TODO Ernesto: narrativa de mejora objetiva -->
- **Errores corregidos**: suma de la columna "Registros afectados" de todas las filas de `docs/transformaciones.md` (total de correcciones puntuales aplicadas por el pipeline). <!-- TODO Ernesto: narrativa de mejora objetiva -->

