"""Actualiza secciones de docs/transformaciones.md de forma idempotente (por marcador)."""

from __future__ import annotations

from pathlib import Path

ENCABEZADO_TABLA = (
    "| Variable | Problema detectado | Transformación | Registros afectados | Justificación |\n"
    "|---|---|---|---|---|\n"
)


def actualizar_seccion_markdown(ruta: Path, marcador: str, titulo: str, filas_tabla: list[str]) -> None:
    inicio = f"<!-- inicio:{marcador} -->"
    fin = f"<!-- fin:{marcador} -->"

    cuerpo = [
        inicio,
        f"### {titulo}",
        "",
        ENCABEZADO_TABLA.rstrip("\n"),
        *filas_tabla,
        fin,
    ]
    seccion_nueva = "\n".join(cuerpo)

    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        encabezado = (
            "# Registro de transformaciones\n\n"
            "Registro compartido de las operaciones de limpieza aplicadas sobre "
            "`datos/unido/establecimientos_diversificado_unido.csv`. Cada sección la "
            "genera el script correspondiente; no editar a mano el contenido entre "
            "`<!-- inicio:... -->` / `<!-- fin:... -->`."
        )
        ruta.write_text(encabezado + "\n\n" + seccion_nueva + "\n", encoding="utf-8")
        return

    contenido = ruta.read_text(encoding="utf-8")
    if inicio in contenido and fin in contenido:
        antes = contenido.split(inicio)[0].rstrip("\n")
        despues = contenido.split(fin)[1].strip("\n")
        partes = [p for p in (antes, seccion_nueva, despues) if p]
        contenido = "\n\n".join(partes) + "\n"
    else:
        contenido = contenido.rstrip("\n") + "\n\n" + seccion_nueva + "\n"

    ruta.write_text(contenido, encoding="utf-8")
