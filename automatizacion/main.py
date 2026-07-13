"""
Menú interactivo para orquestar el pipeline de datos del MINEDUC.

Combina los dos módulos de este paquete:
    - descarga.py    -> web scraping con Selenium, guarda un CSV crudo por departamento.
    - unir_datos.py   -> une todos los CSV crudos en uno solo (sin limpiar ni deduplicar).

Uso:
    python main.py
"""

from __future__ import annotations

from descarga import DEPARTAMENTOS, CRUDOS_DIR, ejecutar_descarga
from unir_datos import unir_crudos, UNIDO_DIR, PATRON_ARCHIVOS


def _preguntar_si_no(mensaje: str, por_defecto: bool = True) -> bool:
    sufijo = "[S/n]" if por_defecto else "[s/N]"
    respuesta = input(f"{mensaje} {sufijo}: ").strip().lower()
    if not respuesta:
        return por_defecto
    return respuesta in ("s", "si", "sí", "y", "yes")


def _preguntar_departamentos() -> list[str] | None:
    print("\nDepartamentos disponibles:")
    for codigo, nombre in DEPARTAMENTOS.items():
        print(f"  {codigo} - {nombre}")
    respuesta = input(
        "\nCódigos separados por coma (ej: 16,00) o Enter para TODOS: "
    ).strip()
    if not respuesta:
        return None

    pedidos = {c.strip() for c in respuesta.split(",") if c.strip()}
    codigos = [c for c in DEPARTAMENTOS if c in pedidos]
    invalidos = pedidos - set(codigos)
    if invalidos:
        print(f"  (se ignoran códigos no reconocidos: {', '.join(sorted(invalidos))})")
    return codigos or None


def _preguntar_reintentos(por_defecto: int = 2) -> int:
    respuesta = input(f"Reintentos por departamento en caso de error [{por_defecto}]: ").strip()
    if not respuesta:
        return por_defecto
    try:
        return max(0, int(respuesta))
    except ValueError:
        print(f"  Valor inválido, se usa {por_defecto}.")
        return por_defecto


def _reportar_descarga(exitosos: list[str], fallidos: list[str]) -> None:
    print(f"\nDescarga finalizada. Exitosos: {len(exitosos)}, fallidos: {len(fallidos)}")
    if fallidos:
        print("Departamentos con problemas:", ", ".join(fallidos))


def _unir(avisar_si_falta: bool = True) -> None:
    if not CRUDOS_DIR.exists() or not any(CRUDOS_DIR.glob(PATRON_ARCHIVOS)):
        if avisar_si_falta:
            print(
                f"\nNo hay datos descargados en {CRUDOS_DIR}. "
                "Corré primero la opción 1 (descargar) o la opción 3 (pipeline completo)."
            )
        return
    try:
        destino = unir_crudos(CRUDOS_DIR, UNIDO_DIR)
        print(f"\nUnión completada -> {destino}")
    except Exception as exc:  # noqa: BLE001
        print(f"\nNo se pudo unir los datos: {exc}")


def opcion_descargar() -> None:
    print("\n--- Configuración de la descarga ---")
    headless = _preguntar_si_no("¿Correr Chrome en modo headless (sin ventana)?", por_defecto=True)
    codigos = _preguntar_departamentos()
    reintentos = _preguntar_reintentos()

    exitosos, fallidos = ejecutar_descarga(codigos=codigos, headless=headless, reintentos=reintentos)
    _reportar_descarga(exitosos, fallidos)


def opcion_unir() -> None:
    print("\n--- Unión de los datos crudos ---")
    _unir(avisar_si_falta=True)


def opcion_pipeline_completo() -> None:
    print("\n--- Pipeline completo: descarga (todos los departamentos) + unión ---")
    headless = _preguntar_si_no("¿Correr Chrome en modo headless (sin ventana)?", por_defecto=True)
    reintentos = _preguntar_reintentos()

    exitosos, fallidos = ejecutar_descarga(codigos=None, headless=headless, reintentos=reintentos)
    _reportar_descarga(exitosos, fallidos)

    if not exitosos:
        print("No se descargó ningún departamento; se omite la unión.")
        return
    _unir(avisar_si_falta=False)


def main() -> None:
    opciones = {
        "1": ("Solo descargar la data", opcion_descargar),
        "2": ("Unir la data descargada", opcion_unir),
        "3": ("Ejecutar pipeline completo (descargar todos + unir)", opcion_pipeline_completo),
        "4": ("Salir", None),
    }

    while True:
        print("\n===== MINEDUC - Pipeline de datos =====")
        for clave, (etiqueta, _) in opciones.items():
            print(f"  {clave}) {etiqueta}")

        eleccion = input("\nElegí una opción: ").strip()

        if eleccion == "4":
            print("Saliendo.")
            break

        accion = opciones.get(eleccion)
        if accion is None:
            print("Opción inválida, intentá de nuevo.")
            continue

        _, funcion = accion
        funcion()


if __name__ == "__main__":
    main()
