# Registro de transformaciones

Registro compartido de las operaciones de limpieza aplicadas sobre `datos/unido/establecimientos_diversificado_unido.csv`. Cada sección la genera el script correspondiente; no editar a mano el contenido entre `<!-- inicio:... -->` / `<!-- fin:... -->`.

<!-- inicio:establecimiento -->
### `establecimiento` (limpiar_establecimiento.py)

| Variable | Problema detectado | Transformación | Registros afectados | Justificación |
|---|---|---|---|---|
| `establecimiento` | 1396 registros con espacios múltiples internos | `strip()` + colapsar espacios múltiples a uno solo | 1396 | Formato: no cambia el contenido, solo normaliza separadores. |
| `establecimiento` | 5 valores vacíos (cadena vacía) | Se marcan como `"NA"` en vez de inventar un nombre; IDs afectados: ['114', '1814', '3644', '7592', '9627'] | 5 | No hay forma de inferir el nombre real de un establecimiento a partir de otras columnas. |
| `establecimiento` | Caracteres de control / no normalizados Unicode (NFC) | Se eliminan caracteres de control invisibles y se normaliza a NFC | 0 detectados en esta corrida | Defensivo: si una futura descarga trae caracteres invisibles, quedan removidos sin alterar tildes/ñ. |
| `establecimiento` | Casing: decisión documentada | Se deja el dataset en MAYÚSCULAS (100% de los 11867 registros ya venía así); se aplica .upper() de forma defensiva sin tocar letras/tildes | 0 registros cambiaron de caja en esta corrida | Opción conservadora: cero riesgo. La alternativa (Title Case) es riesgosa por acrónimos con puntos (`C.E.T.A.CH.`) y numerales (`NO. 1`); se descarta. |
| `establecimiento` | 2228 registros con comillas dobles (ej. `COLEGIO "SANTA ANA"`) | Ninguna: se conservan tal cual, son parte del nombre propio | 0 (no se modifican) | Las comillas son parte del nombre oficial del establecimiento, no un problema de formato. |
| `establecimiento` | 0 registros en minúscula encontrados (verificado sobre el dataset actual) | Ninguna (no se detectó el caso) | 0 | Se deja documentado por transparencia; la normalización de casing sigue aplicándose de forma defensiva por si aparece en una futura descarga. |
| `establecimiento` | Nombres parecidos pero distintos (ej. `AMERICA` vs `AMÉRICA`) | No se autocorrigen — son establecimientos distintos o candidatos a revisar a mano | Ver reporte de duplicados parciales | Corregir automáticamente arriesga fusionar registros que en realidad son centros educativos diferentes. |
<!-- fin:establecimiento -->

