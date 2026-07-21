# pry1-data-science

Proyecto 1 del curso **CC3084 – Data Science** (Universidad del Valle de Guatemala, Semestre II-2026): *Obtención y Limpieza de los Datos*.

## Contexto del proyecto

El objetivo del proyecto es tomar una fuente de datos real, obtenerla, diagnosticar su calidad y limpiarla de forma transparente y reproducible. La fuente que usamos es el buscador público del Ministerio de Educación de Guatemala (MINEDUC), que expone los centros educativos autorizados en todo el país:

http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/

Descargamos los establecimientos que llegan hasta el **Nivel Escolar: DIVERSIFICADO**, para los 23 departamentos del país. Con esos datos crudos se hace luego un diagnóstico del estado inicial de los datos (tipos, faltantes, duplicados, inconsistencias, etc.), un plan y proceso de limpieza documentado y reproducible, pruebas automáticas de calidad sobre el conjunto limpio, un Libro de Códigos (Code Book) con los metadatos de cada variable, y finalmente un conjunto de datos único, limpio y consolidado de todos los departamentos.

## Estructura del repositorio

```
.
├── automatizacion/
│   ├── main.py           # menú interactivo: orquesta descarga.py y unir_datos.py
│   ├── descarga.py       # módulo de descarga (Selenium): un CSV crudo por departamento
│   └── unir_datos.py     # une todos los CSV crudos en uno solo (sin limpiar ni deduplicar)
├── datos/
│   ├── crudos/           # CSV crudos por departamento (se versiona)
│   ├── unido/            # CSV unido de todos los departamentos (no se versiona, es reproducible)
│   ├── interim/          # diagnósticos y reportes intermedios (duplicados, faltantes, tipos, etc.)
│   └── clean/            # CSV limpio y consolidado final (se versiona para la entrega)
├── limpieza/              # funciones de limpieza por variable + orquestador del conjunto limpio
│   ├── generar_limpio.py      # aplica todas las limpiezas y escribe datos/clean/*.csv
│   ├── informe_calidad.py     # compara datos/unido/ (antes) vs. datos/clean/ (después)
│   ├── limpiar_*.py           # una función pura de limpieza por variable o grupo de variables
│   ├── duplicados.py          # detección de duplicados exactos y candidatos a duplicado parcial
│   ├── catalogos.py           # catálogos oficiales (departamentos, municipios)
│   └── reportes.py            # helper para actualizar docs/transformaciones.md
├── docs/
│   ├── plan_limpieza.md       # plan de limpieza por variable (problema, regla, riesgos)
│   ├── transformaciones.md    # registro de transformaciones aplicadas, con conteos
│   ├── libro_de_codigos.md    # Code Book: metadatos y dominio de cada variable
│   ├── libro_de_codigos.pdf   # Code Book exportado a PDF
│   └── informe_calidad.md     # informe de calidad antes/después (generado por informe_calidad.py)
├── tests/
│   └── test_validacion.py     # pruebas automáticas de calidad sobre el conjunto limpio
├── notebooks/
│   └── 01_diagnostico.ipynb   # diagnóstico exploratorio del estado inicial de los datos
├── requirements.txt      # dependencias del proyecto
└── venv/                 # entorno virtual de Python (no se versiona)
```

## Obtención de los datos (web scraping)

Los datos se descargan automáticamente con Selenium desde el buscador del MINEDUC. Por cada uno de los 23 departamentos se deja Municipio/Sector/Plan/Modalidad en "TODOS" y el Nivel Escolar en "DIVERSIFICADO", se ejecuta la búsqueda y se guarda el resultado como un `.csv` en `datos/crudos/`.

> **Nota:** el botón "Exportar a Excel" del sitio tiene un bug del lado del servidor: siempre devuelve una página de error de ASP.NET en vez del archivo, sin importar el departamento o filtro elegido. Por eso `descarga.py` no depende de ese botón. Extrae los datos directamente de la tabla de resultados que renderiza la página, algo igual de confiable, y entrega el `.csv` que pide el proyecto.

### Requisitos previos

- Python 3.11
- Google Chrome / Chromium instalado
- `chromedriver` compatible con la versión de Chrome/Chromium instalada

### 1. Crear y activar el entorno virtual

```bash
python3.11 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Correr el pipeline con el menú interactivo (recomendado)

```bash
cd automatizacion
python main.py
```

Esto muestra un menú con 4 opciones:

```
1) Solo descargar la data
2) Unir la data descargada
3) Ejecutar pipeline completo (descargar todos + unir)
4) Salir
```

La opción 1, solo descargar, pregunta si correr Chrome en modo headless, qué departamentos correr (Enter equivale a todos los 23) y cuántos reintentos por departamento, y luego descarga solo eso a `datos/crudos/`. La opción 2, unir la data descargada, llama a `unir_datos.py` sobre lo que ya haya en `datos/crudos/`; si la carpeta no existe o está vacía, avisa que hace falta descargar primero (opción 1 o 3) y no hace nada más. La opción 3, pipeline completo, descarga los 23 departamentos y, si al menos uno tuvo éxito, une automáticamente el resultado. La opción 4 simplemente sale.

### Uso directo de los módulos (sin menú)

`descarga.py` y `unir_datos.py` también se pueden correr por separado, algo útil para pruebas o para automatizar sin el menú:

```bash
cd automatizacion

# Descarga
python descarga.py                        # corre los 23 departamentos
python descarga.py --headless             # sin ventana de navegador
python descarga.py --departamentos 16,00  # solo esos departamentos (pruebas)
python descarga.py --reintentos 3         # reintentos por departamento (por defecto 2)

# Unión (requiere que ya existan CSV en datos/crudos/)
python unir_datos.py
```

Los archivos crudos quedan en `datos/crudos/` con el formato de nombre:

```
establecimientos_diversificado_<codigo_departamento>_<nombre_departamento>.csv
```

Por ejemplo: `establecimientos_diversificado_16_alta_verapaz.csv`.

El progreso se registra en `automatizacion/scraper.log` y también se imprime en consola.

### Unión de los datos crudos

`unir_datos.py` (invocado desde el menú o directamente) toma todos los archivos `establecimientos_diversificado_*.csv` que haya en `datos/crudos/`, no solo los de la última corrida. Valida que todos tengan exactamente las mismas 17 columnas (mismo nombre y orden); si alguno difiere, aborta con un error indicando cuál archivo y qué columnas cambian. Luego los concatena en un único CSV en `datos/unido/establecimientos_diversificado_unido.csv` y verifica que el total de filas del unido sea exactamente la suma de filas de los archivos individuales (si no cuadra, aborta).

Esta unión es fiel: no limpia, no normaliza mayúsculas/tildes/teléfonos ni elimina duplicados, eso corresponde a una fase posterior de limpieza sobre este archivo unido. Se agregan únicamente dos columnas derivadas para trazabilidad:

| Columna | Descripción |
|---|---|
| `archivo_origen` | Nombre del CSV crudo del que vino cada fila (para rastrear su departamento de origen). |
| `id_registro` | Entero incremental estable (1..N), asignado después de ordenar y concatenar, para poder referenciar cada fila en fases posteriores sin depender del índice de pandas. |

## Diagnóstico del estado inicial

Antes de limpiar, el estado crudo del conjunto unido se analiza en `notebooks/01_diagnostico.ipynb` (shape, tipos de dato, faltantes, valores únicos, duplicados exactos, valores fuera de dominio y formatos inconsistentes). Para reproducirlo:

```bash
jupyter notebook notebooks/01_diagnostico.ipynb
```

El notebook lee `datos/unido/establecimientos_diversificado_unido.csv` y escribe las tablas de respaldo en `datos/interim/` (`diagnostico_resumen.csv`, `diagnostico_faltantes.csv`, `diagnostico_tipos.csv`, `diagnostico_unicos.csv`, `diagnostico_fuera_dominio.csv`), que son la base del plan de limpieza en `docs/plan_limpieza.md`.

## Limpieza y generación del conjunto final

Con el conjunto unido ya generado en `datos/unido/`, se corre el orquestador de limpieza:

```bash
python limpieza/generar_limpio.py
```

Esto aplica en orden todas las funciones `clean_<variable>` del paquete `limpieza/` (una por variable o grupo de variables: establecimiento, dirección, geográficas/códigos, teléfono, personas, categóricas), preservando siempre el valor original en una columna con sufijo `_raw` y sin eliminar ninguna fila. También corre la detección de duplicados (`limpieza/duplicados.py`), que documenta los duplicados exactos encontrados y genera el reporte de candidatos a duplicado parcial en `datos/interim/duplicados_parciales_revisar.csv` (similitud RapidFuzz, sin fusionar ni eliminar nada automáticamente).

El resultado queda en:

```
datos/clean/establecimientos_diversificado_limpio.csv
```

Cada transformación aplicada (variable, problema detectado, transformación, registros afectados, justificación) queda documentada en `docs/transformaciones.md`.

### Validación automática

```bash
pytest tests/test_validacion.py -v
```

Son 13 pruebas que verifican, entre otras cosas: ausencia de duplicados exactos, ausencia de espacios al inicio/fin de textos, formato consistente de teléfonos (`telefono` y `telefono_adicionales`), que `departamento` y `municipio` pertenezcan al catálogo oficial del INE, que `codigo` cumpla su patrón y se mantenga como texto, que `nivel` sea únicamente `"DIVERSIFICADO"`, ausencia de categorías duplicadas por diferencias de escritura, que las variables categóricas estén dentro de su dominio permitido, y que los nombres de personas (`director`/`supervisor`) estén normalizados.

### Informe de calidad (antes/después)

```bash
python limpieza/informe_calidad.py
```

Compara `datos/unido/establecimientos_diversificado_unido.csv` (ANTES) contra `datos/clean/establecimientos_diversificado_limpio.csv` (DESPUÉS) y escribe `docs/informe_calidad.md` con las métricas de calidad de la rúbrica (registros, variables, valores faltantes, duplicados exactos y posibles, variables con formato/tipo inconsistente, categorías inconsistentes y errores corregidos). Es reproducible, se puede correr las veces que haga falta y siempre sobrescribe el mismo archivo con datos frescos.

## Libro de códigos

El Code Book completo, con la descripción, tipo de dato, dominio, tratamiento aplicado y metadatos de cada una de las 31 columnas del conjunto limpio, está en:

- `docs/libro_de_codigos.md` (fuente, editable)
- `docs/libro_de_codigos.pdf` (versión de entrega)

## Pipeline completo, de punta a punta

Para replicar todo el proceso desde cero, en orden:

```bash
# 1. Entorno
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Obtención (requiere Chrome/chromedriver)
cd automatizacion
python descarga.py --headless
python unir_datos.py
cd ..

# 3. Diagnóstico (opcional, exploratorio)
jupyter notebook notebooks/01_diagnostico.ipynb

# 4. Limpieza y conjunto final
python limpieza/generar_limpio.py

# 5. Validación
pytest tests/test_validacion.py -v

# 6. Informe de calidad
python limpieza/informe_calidad.py
```

Al finalizar, el conjunto de datos limpio queda en `datos/clean/establecimientos_diversificado_limpio.csv`, la validación en verde confirma que cumple las reglas de calidad, y `docs/informe_calidad.md` documenta objetivamente la mejora obtenida frente al estado crudo.
