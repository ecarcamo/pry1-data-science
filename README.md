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
├── automatizacion/       # script de web scraping (Selenium) para descargar los datos crudos
│   └── main.py
├── datos/
│   └── crudos/           # CSV crudos por departamento (generados por el scraper, no se versionan)
├── requirements.txt      # dependencias del proyecto
└── venv/                 # entorno virtual de Python (no se versiona)
```

## Obtención de los datos (web scraping)

Los datos se descargan automáticamente con Selenium desde el buscador del MINEDUC. Por cada uno de los 23 departamentos, el script deja Municipio/Sector/Plan/Modalidad en "TODOS" y el Nivel Escolar en "DIVERSIFICADO", ejecuta la búsqueda y guarda el resultado como un `.csv` en `datos/crudos/`.

> **Nota:** el botón "Exportar a Excel" del sitio tiene un bug del lado del servidor (siempre devuelve una página de error de ASP.NET en vez del archivo, sin importar el departamento o filtro elegido). Por eso el script no depende de ese botón: extrae los datos directamente de la tabla de resultados que renderiza la página, lo cual es igual de confiable y entrega el `.csv` que pide el proyecto.

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

### 3. Ejecutar el scraper

```bash
cd automatizacion
python main.py
```

Esto abre Chrome, recorre los 23 departamentos y deja los archivos en `datos/crudos/`, con el formato de nombre:

```
establecimientos_diversificado_<codigo_departamento>_<nombre_departamento>.csv
```

Por ejemplo: `establecimientos_diversificado_16_alta_verapaz.csv`.

### Opciones útiles

| Opción | Descripción |
|---|---|
| `--headless` | Corre Chrome sin abrir ventana (recomendado para correr el proceso completo). |
| `--departamentos 16,00` | Corre solo los departamentos indicados (útil para pruebas). |
| `--reintentos N` | Cantidad de reintentos por departamento si falla (por defecto 2). |

Ejemplo para correr todo sin interfaz gráfica:

```bash
python main.py --headless
```

El progreso se registra en `automatizacion/scraper.log` y también se imprime en consola.
