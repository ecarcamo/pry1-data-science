# pry1-data-science

Proyecto 1 del curso **CC3084 – Data Science** (Universidad del Valle de Guatemala, Semestre II-2026): *Obtención y Limpieza de los Datos*.

## Contexto del proyecto

El objetivo es tomar una fuente de datos real, obtenerla, diagnosticar su calidad y limpiarla de forma transparente y reproducible. La fuente utilizada es el buscador público del Ministerio de Educación de Guatemala (MINEDUC), que expone los centros educativos autorizados en todo el país:

http://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/

Se descargan los establecimientos que llegan hasta el **Nivel Escolar: DIVERSIFICADO**, para los 23 departamentos del país. Con esos datos crudos se hará luego:

- un diagnóstico del estado inicial de los datos (tipos, faltantes, duplicados, inconsistencias, etc.),
- un plan y proceso de limpieza documentado y reproducible,
- pruebas automáticas de calidad sobre el conjunto limpio,
- un Libro de Códigos (Code Book) con los metadatos de cada variable,
- un conjunto de datos único, limpio y consolidado de todos los departamentos.

## Estructura del repositorio

```
.
├── automatizacion/
│   ├── main.py           # menú interactivo: orquesta descarga.py y unir_datos.py
│   ├── descarga.py       # módulo de descarga (Selenium): un CSV crudo por departamento
│   └── unir_datos.py     # une todos los CSV crudos en uno solo (sin limpiar ni deduplicar)
├── datos/
│   ├── crudos/           # CSV crudos por departamento (se versiona)
│   └── unido/            # CSV unido de todos los departamentos (no se versiona, es reproducible)
├── requirements.txt      # dependencias del proyecto
└── venv/                 # entorno virtual de Python (no se versiona)
```

## Obtención de los datos (web scraping)

Los datos se descargan automáticamente con Selenium desde el buscador del MINEDUC. Por cada uno de los 23 departamentos, se deja Municipio/Sector/Plan/Modalidad en "TODOS" y el Nivel Escolar en "DIVERSIFICADO", se ejecuta la búsqueda y se guarda el resultado como un `.csv` en `datos/crudos/`.

> **Nota:** el botón "Exportar a Excel" del sitio tiene un bug del lado del servidor (siempre devuelve una página de error de ASP.NET en vez del archivo, sin importar el departamento o filtro elegido). Por eso `descarga.py` no depende de ese botón: extrae los datos directamente de la tabla de resultados que renderiza la página, lo cual es igual de confiable y entrega el `.csv` que pide el proyecto.

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

- **Opción 1 — Solo descargar:** pregunta si correr Chrome en modo headless, qué departamentos correr (Enter = todos los 23) y cuántos reintentos por departamento, y luego descarga solo eso a `datos/crudos/`.
- **Opción 2 — Unir la data descargada:** llama a `unir_datos.py` sobre lo que ya haya en `datos/crudos/`. Si la carpeta no existe o está vacía, avisa que hace falta descargar primero (opción 1 o 3) y no hace nada más.
- **Opción 3 — Pipeline completo:** descarga los 23 departamentos y, si al menos uno tuvo éxito, une automáticamente el resultado.
- **Opción 4 — Salir.**

### Uso directo de los módulos (sin menú)

`descarga.py` y `unir_datos.py` también se pueden correr por separado, útil para pruebas o para automatizar sin el menú:

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

`unir_datos.py` (invocado desde el menú o directamente):

- toma **todos** los archivos `establecimientos_diversificado_*.csv` que haya en `datos/crudos/` (no solo los de la última corrida),
- valida que todos tengan exactamente las mismas 17 columnas (mismo nombre y orden); si alguno difiere, aborta con un error indicando cuál archivo y qué columnas cambian,
- los concatena en un único CSV en `datos/unido/establecimientos_diversificado_unido.csv`,
- verifica que el total de filas del unido sea exactamente la suma de filas de los archivos individuales (si no cuadra, aborta).

Esta unión es **fiel**: no limpia, no normaliza mayúsculas/tildes/teléfonos ni elimina duplicados — eso corresponde a una fase posterior de limpieza sobre este archivo unido. Se agregan únicamente dos columnas derivadas para trazabilidad:

| Columna | Descripción |
|---|---|
| `archivo_origen` | Nombre del CSV crudo del que vino cada fila (para rastrear su departamento de origen). |
| `id_registro` | Entero incremental estable (1..N), asignado después de ordenar y concatenar, para poder referenciar cada fila en fases posteriores sin depender del índice de pandas. |
