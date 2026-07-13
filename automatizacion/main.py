"""
Descarga automatizada de establecimientos educativos (Nivel Escolar: DIVERSIFICADO)
del buscador del MINEDUC: https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/

Por cada departamento del catalogo se deja Municipio/Sector/Plan/Modalidad en "TODOS",
se presiona "Buscar Establecimiento" y luego "Exportar a Excel". El archivo descargado
(siempre nombrado "establecimiento.xls" por el sitio) se renombra y se mueve a
datos/raw/ en la raiz del proyecto, con un nombre que identifica el departamento.

Uso:
    python main.py                      # corre los 23 departamentos
    python main.py --headless           # sin ventana de navegador
    python main.py --departamentos 16,00  # solo esos codigos (pruebas)
"""

from __future__ import annotations

import argparse
import logging
import time
import unicodedata
from pathlib import Path

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
DOWNLOAD_DIR = Path(__file__).resolve().parent / "_descargas_tmp"
RAW_DIR = PROJECT_ROOT / "datos" / "raw"

ELEMENT_TIMEOUT = 20
SEARCH_RESULTS_TIMEOUT = 90
DOWNLOAD_TIMEOUT = 60

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
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.binary_location = CHROME_BINARY
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--safebrowsing-disable-download-protection")
    options.add_argument("--disable-features=InsecureDownloadWarnings,DownloadBubble,DownloadBubblePartialViewController")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(DOWNLOAD_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
        },
    )

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

    Devuelve True si aparece el botón de exportar (hay resultados),
    False si la búsqueda no arrojó resultados dentro del tiempo de espera.
    """
    boton = driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_IbtnConsultar")
    boton.click()

    wait = WebDriverWait(driver, SEARCH_RESULTS_TIMEOUT)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_btnExportar")))
        return True
    except TimeoutException:
        return False


def click_exportar(driver: webdriver.Chrome) -> Path:
    before = {p.name for p in DOWNLOAD_DIR.glob("*")}

    boton = driver.find_element(By.ID, "_ctl0_ContentPlaceHolder1_btnExportar")
    boton.click()

    deadline = time.time() + DOWNLOAD_TIMEOUT
    while time.time() < deadline:
        current = {p.name for p in DOWNLOAD_DIR.glob("*")}
        nuevos = current - before
        nuevos_completos = [
            n for n in nuevos if not n.endswith(".crdownload") and not n.endswith(".tmp")
        ]
        if nuevos_completos:
            return DOWNLOAD_DIR / nuevos_completos[0]
        time.sleep(0.5)

    raise TimeoutException("La descarga del Excel no finalizó dentro del tiempo esperado.")


def mover_archivo(descargado: Path, codigo: str, nombre_departamento: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    extension = descargado.suffix or ".xls"
    destino = RAW_DIR / f"establecimientos_diversificado_{codigo}_{slugify(nombre_departamento)}{extension}"
    descargado.replace(destino)
    return destino


def procesar_departamento(driver: webdriver.Chrome, codigo: str, nombre: str) -> bool:
    wait = WebDriverWait(driver, ELEMENT_TIMEOUT)

    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_cmbDepartamento")))

    select_departamento(driver, wait, codigo)
    set_filtros_todos(driver)

    hay_resultados = click_buscar(driver)
    if not hay_resultados:
        log.warning("Departamento %s (%s): sin resultados / botón exportar no apareció.", codigo, nombre)
        return False

    descargado = click_exportar(driver)
    destino = mover_archivo(descargado, codigo, nombre)
    log.info("Departamento %s (%s): OK -> %s", codigo, nombre, destino.relative_to(PROJECT_ROOT))
    return True


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

    driver = build_driver(headless=args.headless)
    exitosos, fallidos = [], []

    try:
        for codigo in codigos:
            nombre = DEPARTAMENTOS[codigo]
            log.info("=== Procesando %s - %s ===", codigo, nombre)

            intento = 0
            ok = False
            while intento <= args.reintentos and not ok:
                intento += 1
                try:
                    ok = procesar_departamento(driver, codigo, nombre)
                except Exception as exc:  # noqa: BLE001
                    log.error(
                        "Departamento %s (%s): error en intento %d/%d -> %s",
                        codigo, nombre, intento, args.reintentos + 1, exc,
                    )
                    time.sleep(2)

            (exitosos if ok else fallidos).append(f"{codigo} - {nombre}")
    finally:
        driver.quit()
        if DOWNLOAD_DIR.exists() and not any(DOWNLOAD_DIR.iterdir()):
            DOWNLOAD_DIR.rmdir()

    log.info("Finalizado. Exitosos: %d, Fallidos/sin resultados: %d", len(exitosos), len(fallidos))
    if fallidos:
        log.warning("Departamentos con problemas: %s", ", ".join(fallidos))


if __name__ == "__main__":
    main()
