# Reporte de duplicados parciales

`duplicados_parciales_revisar.csv` contiene pares de registros cuyo `establecimiento`
(ya limpio) tiene una similitud (RapidFuzz `token_sort_ratio`) entre 88 y 100 (sin
incluir 100), dentro del mismo `departamento` + `municipio`. Las tildes NO se quitan
para la comparación (a propósito: diferencias de tildes, como "AMERICA" vs "AMÉRICA",
son justo el tipo de caso casi-idéntico que este reporte debe capturar). No incluye
pares con nombre idéntico (score 100): esos son mayoritariamente el mismo centro con
varios códigos (jornada/plan/modalidad distintos) y no ameritan revisión caso por caso.

Este script **no decide ni borra nada**. Ordena los pares por `score` descendente
para que alguien los revise a mano y llene la columna `decision` con uno de:
`conservar` (son establecimientos distintos), `fusionar` o `revisar`.

Guía orientativa:
- Nombre casi igual + códigos distintos + jornada/plan distintos → probablemente
  **legítimo** (mismo centro, varios códigos) → `conservar`.
- Nombre casi igual + mismo municipio + misma jornada y mismo plan → **sospechoso** →
  `revisar`.
