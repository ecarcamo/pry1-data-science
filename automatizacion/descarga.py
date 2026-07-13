"""
Módulo de descarga (web scraping) de establecimientos educativos
(Nivel Escolar: DIVERSIFICADO) del buscador del MINEDUC:
https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/

Por cada departamento del catalogo se deja Municipio/Sector/Plan/Modalidad en "TODOS"
y se presiona "Buscar Establecimiento". Los resultados se extraen directamente de la
tabla HTML (id dgResultado) que renderiza el sitio y se guardan como .csv en datos/crudos/,
con un nombre que identifica el departamento.

Nota: el botón "Exportar a Excel" del sitio (btnExportar) tiene un bug del lado del
servidor: siempre devuelve una página de error de ASP.NET ("Control 'grvHistorial' of
type 'GridView' must be placed inside a form tag with runat=server") en lugar del
archivo, sin importar el departamento o el Nivel Escolar elegido (se verificó de forma
reproducible). Por eso este script no usa ese botón: en su lugar parsea la tabla de
resultados ya renderizada en la página, que contiene exactamente los mismos datos.

Este módulo solo descarga; no une los CSV crudos (eso lo hace unir_datos.py, y
el menú de main.py orquesta ambos pasos).

Uso como script independiente:
    python descarga.py                        # corre los 23 departamentos
    python descarga.py --headless             # sin ventana de navegador
    python descarga.py --departamentos 16,00  # solo esos codigos (pruebas)

También puede importarse y usarse como función:
    from descarga import ejecutar_descarga
    exitosos, fallidos = ejecutar_descarga(codigos=None, headless=True, reintentos=2)
"""

from __future__ import annotations

import argparse
import logging
import time
import unicodedata
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROME_BINARY = "/usr/bin/chromium"

NIVEL_DIVERSIFICADO = "46"

RESULTADOS_TABLE_ID = "_ctl0_ContentPlaceHolder1_dgResultado"
# La primera columna de la tabla es solo el ícono para "seleccionar" (sin encabezado).
COLUMNAS = [
    "codigo", "distrito", "departamento", "municipio", "establecimiento",
    "direccion", "telefono", "supervisor", "director", "nivel", "sector",
    "area", "status", "modalidad", "jornada", "plan", "departamental",
]

DEPARTAMENTOS = {
    "16": "ALTA VERAPAZ",
    "15": "BAJA VERAPAZ",
    "04": "CHIMALTENANGO",
    "20": "CHIQUIMULA",
    "00": "CIUDAD CAPITAL",
    "02": "EL PROGRESO",
    "05": "ESCUINTLA",
    "01": "GUATEMALA",
    "13": "HUEHUETENANGO",
    "18": "IZABAL",
    "21": "JALAPA",
    "22": "JUTIAPA",
    "17": "PETEN",
    "09": "QUETZALTENANGO",
    "14": "QUICHE",
    "11": "RETALHULEU",
    "03": "SACATEPEQUEZ",
    "12": "SAN MARCOS",
    "06": "SANTA ROSA",
    "07": "SOLOLA",
    "10": "SUCHITEPEQUEZ",
    "08": "TOTONICAPAN",
    "19": "ZACAPA",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CRUDOS_DIR = PROJECT_ROOT / "datos" / "crudos"

ELEMENT_TIMEOUT = 20
SEARCH_RESULTS_TIMEOUT = 90

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).resolve().parent / "scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("mineduc_scraper")


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return "_".join(normalized.lower().split())


def build_driver(headless: bool) -> webdriver.Chrome:
    options = Options()
    options.binary_location = CHROME_BINARY
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def select_departamento(driver: webdriver.Chrome, wait: WebDriverWait, codigo: str) -> None:
    dep_select_el = wait.until(
        EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_cmbDepartamento"))
    )
    muni_select_el = driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_cmbMunicipio")
    municipio_options_before = len(Select(muni_select_el).options)

    Select(dep_select_el).select_by_value(codigo)

    # El cambio de departamento dispara un postback (AJAX UpdatePanel) que
    # repuebla el combo de Municipio. Esperamos a que cambie su cantidad de opciones.
    wait.until(
        lambda d: len(
            Select(d.find_element(By.ID, "_ctl0_ContentPlaceHolder1_cmbMunicipio")).options
        )
        != municipio_options_before
    )
    # Pequeño colchón adicional: el sitio a veces sigue reordenando el DOM
    # brevemente después de que cambian las opciones del combo.
    time.sleep(0.8)


def set_filtros_todos(driver: webdriver.Chrome) -> None:
    Select(driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_cmbNivel")).select_by_value(
        NIVEL_DIVERSIFICADO
    )

    muni_select = Select(driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_cmbMunicipio"))
    try:
        muni_select.select_by_value("TODOS")
    except Exception:
        try:
            muni_select.select_by_visible_text("TODOS")
        except Exception:
            log.warning("No se encontró opción 'TODOS' en Municipio; se deja el valor por defecto.")

    Select(driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_cmbSector")).select_by_value(
        "TODOS"
    )
    Select(driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_ddlplan")).select_by_value(
        "TODOS"
    )
    Select(driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_ddlModalidad")).select_by_value(
        "TODOS"
    )


def click_buscar(driver: webdriver.Chrome) -> bool:
    """Presiona 'Buscar Establecimiento' y espera resultados.

    Devuelve True si aparece la tabla de resultados, False si la búsqueda no
    arrojó resultados dentro del tiempo de espera.
    """
    boton = driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_IbtnConsultar")
    boton.click()

    wait = WebDriverWait(driver, SEARCH_RESULTS_TIMEOUT)
    try:
        wait.until(EC.presence_of_element_located((By.ID, RESULTADOS_TABLE_ID)))
        return True
    except TimeoutException:
        return False


def hay_paginacion(soup: BeautifulSoup) -> bool:
    return soup.find(string=lambda s: isinstance(s, str) and "Siguiente" in s) is not None


def extraer_tabla_resultados(driver: webdriver.Chrome) -> pd.DataFrame:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tabla = soup.find(id=RESULTADOS_TABLE_ID)
    if tabla is None:
        return pd.DataFrame(columns=COLUMNAS)

    if hay_paginacion(soup):
        log.warning(
            "La tabla de resultados parece tener paginación ('Siguiente'); "
            "es posible que falten registros de este departamento."
        )

    filas = tabla.find_all("tr")[1:]  # la primera fila es el encabezado
    registros = []
    for fila in filas:
        celdas = fila.find_all("td")[1:]  # se descarta la columna del ícono "seleccionar"
        valores = [c.get_text(strip=True).replace("\xa0", "") for c in celdas]
        if len(valores) != len(COLUMNAS):
            log.warning("Fila con %d columnas (se esperaban %d); se omite: %s", len(valores), len(COLUMNAS), valores)
            continue
        if not any(valores):  # fila espaciadora vacía que a veces agrega el grid
            continue
        registros.append(valores)

    return pd.DataFrame(registros, columns=COLUMNAS)


def guardar_csv(df: pd.DataFrame, codigo: str, nombre_departamento: str) -> Path:
    CRUDOS_DIR.mkdir(parents=True, exist_ok=True)
    destino = CRUDOS_DIR / f"establecimientos_diversificado_{codigo}_{slugify(nombre_departamento)}.csv"
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    return destino


def procesar_departamento(driver: webdriver.Chrome, codigo: str, nombre: str) -> bool:
    wait = WebDriverWait(driver, ELEMENT_TIMEOUT)

    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_cmbDepartamento")))

    select_departamento(driver, wait, codigo)
    set_filtros_todos(driver)

    hay_resultados = click_buscar(driver)
    if not hay_resultados:
        log.warning("Departamento %s (%s): sin resultados.", codigo, nombre)
        return False

    df = extraer_tabla_resultados(driver)
    if df.empty:
        log.warning("Departamento %s (%s): tabla de resultados vacía.", codigo, nombre)
        return False

    destino = guardar_csv(df, codigo, nombre)
    log.info(
        "Departamento %s (%s): OK -> %s (%d registros)",
        codigo, nombre, destino.relative_to(PROJECT_ROOT), len(df),
    )
    return True


def ejecutar_descarga(
    codigos: list[str] | None = None,
    headless: bool = False,
    reintentos: int = 2,
) -> tuple[list[str], list[str]]:
    """Descarga los CSV crudos de los departamentos indicados (o todos si es None).

    Devuelve (exitosos, fallidos), cada uno como lista de strings "codigo - nombre".
    """
    codigos = codigos if codigos else list(DEPARTAMENTOS.keys())

    driver = build_driver(headless=headless)
    exitosos: list[str] = []
    fallidos: list[str] = []

    try:
        for codigo in codigos:
            nombre = DEPARTAMENTOS[codigo]
            log.info("=== Procesando %s - %s ===", codigo, nombre)

            intento = 0
            ok = False
            while intento <= reintentos and not ok:
                intento += 1
                try:
                    ok = procesar_departamento(driver, codigo, nombre)
                except Exception as exc:  # noqa: BLE001
                    log.error(
                        "Departamento %s (%s): error en intento %d/%d -> %s",
                        codigo, nombre, intento, reintentos + 1, exc,
                    )
                    time.sleep(2)

            (exitosos if ok else fallidos).append(f"{codigo} - {nombre}")
    finally:
        driver.quit()

    log.info("Finalizado. Exitosos: %d, Fallidos/sin resultados: %d", len(exitosos), len(fallidos))
    if fallidos:
        log.warning("Departamentos con problemas: %s", ", ".join(fallidos))

    return exitosos, fallidos


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga establecimientos DIVERSIFICADO por departamento (MINEDUC).")
    parser.add_argument("--headless", action="store_true", help="Ejecuta Chrome sin interfaz gráfica.")
    parser.add_argument(
        "--departamentos",
        type=str,
        default=None,
        help="Lista de códigos separados por coma para correr un subconjunto (ej: 16,00,01). Por defecto corre todos.",
    )
    parser.add_argument("--reintentos", type=int, default=2, help="Reintentos por departamento en caso de error.")
    args = parser.parse_args()

    codigos = list(DEPARTAMENTOS.keys())
    if args.departamentos:
        pedidos = {c.strip() for c in args.departamentos.split(",")}
        codigos = [c for c in codigos if c in pedidos]

    ejecutar_descarga(codigos=codigos, headless=args.headless, reintentos=args.reintentos)


if __name__ == "__main__":
    main()
