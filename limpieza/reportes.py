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
    seccion_nueva = "\n".join(cuerpo) + "\n"

    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        contenido = (
            "# Registro de transformaciones\n\n"
            "Registro compartido de las operaciones de limpieza aplicadas sobre "
            "`datos/unido/establecimientos_diversificado_unido.csv`. Cada sección la "
            "genera el script correspondiente; no editar a mano el contenido entre "
            "`<!-- inicio:... -->` / `<!-- fin:... -->`.\n\n"
        )
        ruta.write_text(contenido + seccion_nueva, encoding="utf-8")
        return

    contenido = ruta.read_text(encoding="utf-8")
    if inicio in contenido and fin in contenido:
        antes = contenido.split(inicio)[0]
        despues = contenido.split(fin)[1]
        contenido = antes + seccion_nueva + despues
    else:
        if not contenido.endswith("\n\n"):
            contenido = contenido.rstrip("\n") + "\n\n"
        contenido += seccion_nueva

    ruta.write_text(contenido, encoding="utf-8")
