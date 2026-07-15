"""Catálogos oficiales de departamentos y municipios de Guatemala (INE/MINEDUC).

Fuente: Instituto Nacional de Estadística (INE) — División político-administrativa.
22 departamentos, ~340 municipios.

Uso interno: normalizar y validar las columnas departamento y municipio.
"""

from __future__ import annotations

import unicodedata


# ---------------------------------------------------------------------------
# Helper de normalización (solo para comparar, NUNCA para guardar)
# ---------------------------------------------------------------------------

def _quitar_tildes(texto: str) -> str:
    """Elimina diacríticos para comparación case-insensitive sin tildes."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_para_comparar(texto: str) -> str:
    """MAYÚSCULAS sin tildes, sin espacios extra — solo para matching, no para guardar."""
    return _quitar_tildes(texto.strip().upper())


# ---------------------------------------------------------------------------
# Catálogo de departamentos — 22 valores canónicos (MAYÚSCULAS con tildes)
# ---------------------------------------------------------------------------

DEPARTAMENTOS: list[str] = [
    "GUATEMALA",
    "EL PROGRESO",
    "SACATEPÉQUEZ",
    "CHIMALTENANGO",
    "ESCUINTLA",
    "SANTA ROSA",
    "SOLOLÁ",
    "TOTONICAPÁN",
    "QUETZALTENANGO",
    "SUCHITEPÉQUEZ",
    "RETALHULEU",
    "SAN MARCOS",
    "HUEHUETENANGO",
    "QUICHÉ",
    "BAJA VERAPAZ",
    "ALTA VERAPAZ",
    "PETÉN",
    "IZABAL",
    "ZACAPA",
    "CHIQUIMULA",
    "JALAPA",
    "JUTIAPA",
]

# Lookup sin tildes → canónico con tildes
_DEPTO_SIN_TILDE: dict[str, str] = {
    normalizar_para_comparar(d): d for d in DEPARTAMENTOS
}

# Alias extra de la fuente MINEDUC (selector descarga por separado 00 y 01)
# "CIUDAD CAPITAL" se fusiona en GUATEMALA (decisión documentada en plan_limpieza.md)
_ALIAS_DEPTO: dict[str, str] = {
    "CIUDAD CAPITAL": "GUATEMALA",
}


def lookup_departamento(valor: str) -> str | None:
    """Devuelve el nombre canónico del departamento o None si no hay match.

    Primero prueba alias exactos (ej. CIUDAD CAPITAL → GUATEMALA),
    luego búsqueda por normalización sin tildes.
    """
    v = valor.strip().upper()
    if v in _ALIAS_DEPTO:
        return _ALIAS_DEPTO[v]
    clave = normalizar_para_comparar(v)
    return _DEPTO_SIN_TILDE.get(clave)


# ---------------------------------------------------------------------------
# Catálogo de municipios — por departamento canónico
# ---------------------------------------------------------------------------
# Fuente: INE, División político-administrativa de Guatemala (340 municipios).

MUNICIPIOS_POR_DEPTO: dict[str, list[str]] = {
    "GUATEMALA": [
        "GUATEMALA", "SANTA CATARINA PINULA", "SAN JOSÉ PINULA", "SAN JOSÉ DEL GOLFO",
        "PALENCIA", "CHINAUTLA", "SAN PEDRO AYAMPUC", "MIXCO", "SAN PEDRO SACATEPÉQUEZ",
        "SAN JUAN SACATEPÉQUEZ", "SAN RAYMUNDO", "CHUARRANCHO", "FRAIJANES", "AMATITLÁN",
        "VILLA NUEVA", "VILLA CANALES", "SAN MIGUEL PETAPA",
        # Zonas de la ciudad capital — MINEDUC las usa como "municipio" para establecimientos
        # dentro del municipio de Guatemala. No son municipios del INE, pero son válidos en
        # este dataset (documentado en docs/transformaciones.md).
        "ZONA 1", "ZONA 2", "ZONA 3", "ZONA 4", "ZONA 5", "ZONA 6", "ZONA 7",
        "ZONA 8", "ZONA 9", "ZONA 10", "ZONA 11", "ZONA 12", "ZONA 13", "ZONA 14",
        "ZONA 15", "ZONA 16", "ZONA 17", "ZONA 18", "ZONA 19", "ZONA 21",
    ],
    "EL PROGRESO": [
        "GUASTATOYA", "MORAZÁN", "SAN AGUSTÍN ACASAGUASTLÁN", "SAN CRISTÓBAL ACASAGUASTLÁN",
        "EL JÍCARO", "SANSARE", "SANARATE", "SAN ANTONIO LA PAZ",
    ],
    "SACATEPÉQUEZ": [
        "ANTIGUA GUATEMALA", "JOCOTENANGO", "PASTORES", "SUMPANGO", "SANTO DOMINGO XENACOJ",
        "SANTIAGO SACATEPÉQUEZ", "SAN BARTOLOMÉ MILPAS ALTAS", "SAN LUCAS SACATEPÉQUEZ",
        "SANTA LUCÍA MILPAS ALTAS", "MAGDALENA MILPAS ALTAS", "SANTA MARÍA DE JESÚS",
        "CIUDAD VIEJA", "SAN MIGUEL DUEÑAS", "SAN JUAN ALOTENANGO", "SAN ANTONIO AGUAS CALIENTES",
        "SANTA CATARINA BARAHONA",
    ],
    "CHIMALTENANGO": [
        "CHIMALTENANGO", "SAN JOSÉ POAQUIL", "SAN MARTÍN JILOTEPEQUE", "SAN JUAN COMALAPA",
        "SANTA APOLONIA", "TECPÁN GUATEMALA", "PATZÚN", "POCHUTA", "PATZICÍA",
        "SANTA CRUZ BALANYÁ", "ACATENANGO", "YEPOCAPA", "SAN ANDRÉS ITZAPA",
        "PARRAMOS", "ZARAGOZA", "EL TEJAR",
    ],
    "ESCUINTLA": [
        "ESCUINTLA", "SANTA LUCÍA COTZUMALGUAPA", "LA DEMOCRACIA", "SIQUINALÁ",
        "MASAGUA", "TIQUISATE", "LA GOMERA", "GUANAGAZAPA", "SAN JOSÉ",
        "IZTAPA", "PALÍN", "SAN VICENTE PACAYA", "NUEVA CONCEPCIÓN",
        "SIPACATE",  # comunidad/aldea de La Gomera; MINEDUC la registra como municipio
    ],
    "SANTA ROSA": [
        "CUILAPA", "BARBERENA", "SANTA ROSA DE LIMA", "CASILLAS", "SAN RAFAEL LAS FLORES",
        "ORATORIO", "SAN JUAN TECUACO", "CHIQUIMULILLA", "TAXISCO", "SANTA MARÍA IXHUATÁN",
        "GUAZACAPÁN", "SANTA CRUZ NARANJO", "PUEBLO NUEVO VIÑAS", "NUEVA SANTA ROSA",
    ],
    "SOLOLÁ": [
        "SOLOLÁ", "SAN JOSÉ CHACAYÁ", "SANTA MARÍA VISITACIÓN", "SANTA LUCÍA UTATLÁN",
        "NAHUALÁ", "SANTA CATARINA IXTAHUACÁN", "SANTA CLARA LA LAGUNA", "CONCEPCIÓN",
        "SAN ANDRÉS SEMETABAJ", "PANAJACHEL", "SANTA CATARINA PALOPÓ", "SAN ANTONIO PALOPÓ",
        "SAN LUCAS TOLIMÁN", "SANTA CRUZ LA LAGUNA", "SAN PABLO LA LAGUNA",
        "SAN MARCOS LA LAGUNA", "SAN JUAN LA LAGUNA", "SAN PEDRO LA LAGUNA",
        "SANTIAGO ATITLÁN",
    ],
    "TOTONICAPÁN": [
        "TOTONICAPÁN", "SAN CRISTÓBAL TOTONICAPÁN", "SAN FRANCISCO EL ALTO",
        "SAN ANDRÉS XECUL", "MOMOSTENANGO", "SANTA MARÍA CHIQUIMULA",
        "SANTA LUCÍA LA REFORMA", "SAN BARTOLO",
    ],
    "QUETZALTENANGO": [
        "QUETZALTENANGO", "SALCAJÁ", "OLINTEPEQUE", "SAN CARLOS SIJA", "SIBILIA",
        "CABRICÁN", "CAJOLÁ", "SAN MIGUEL SIGÜILÁ", "SAN JUAN OSTUNCALCO",
        "SAN MATEO", "CONCEPCIÓN CHIQUIRICHAPA", "SAN MARTÍN SACATEPÉQUEZ",
        "ALMOLONGA", "CANTEL", "HUITÁN", "ZUNIL", "COLOMBA COSTA CUCA",
        "SAN FRANCISCO LA UNIÓN", "EL PALMAR", "COATEPEQUE", "GÉNOVA",
        "FLORES COSTA CUCA", "LA ESPERANZA", "PALESTINA DE LOS ALTOS",
    ],
    "SUCHITEPÉQUEZ": [
        "MAZATENANGO", "CUYOTENANGO", "SAN FRANCISCO ZAPOTITLÁN", "SANTO DOMINGO SUCHITEPÉQUEZ",
        "SAN LORENZO", "SAMAYAC", "SAN PABLO JOCOPILAS", "SAN ANTONIO SUCHITEPÉQUEZ",
        "SAN MIGUEL PANÁN", "SAN GABRIEL", "CHICACAO", "PATULUL",
        "SANTA BÁRBARA", "SAN JUAN BAUTISTA", "SANTO TOMÁS LA UNIÓN",
        "ZUNILITO", "PUEBLO NUEVO", "RÍO BRAVO",
        "SAN JOSÉ LA MÁQUINA",  # municipio creado en 2006
        "SAN BERNARDINO",       # municipio de Suchitepéquez
        "SAN JOSÉ EL ÍDOLO",    # municipio de Suchitepéquez
    ],
    "RETALHULEU": [
        "RETALHULEU", "SAN SEBASTIÁN", "SANTA CRUZ MULUÁ", "SAN MARTÍN ZAPOTITLÁN",
        "SAN FELIPE RETALHULEU", "SAN ANDRÉS VILLA SECA", "CHAMPERICO",
        "NUEVO SAN CARLOS", "EL ASINTAL",
    ],
    "SAN MARCOS": [
        "SAN MARCOS", "SAN PEDRO SACATEPÉQUEZ", "SAN ANTONIO SACATEPÉQUEZ",
        "COMITANCILLO", "SAN MIGUEL IXTAHUACÁN", "CONCEPCIÓN TUTUAPA",
        "TACANÁ", "SIBINAL", "TAJUMULCO", "TEJUTLA", "SAN RAFAEL PIE DE LA CUESTA",
        "NUEVO PROGRESO", "EL TUMBADOR", "SAN JOSÉ EL RODEO", "MALACATÁN",
        "CATARINA", "AYUTLA", "OCÓS", "SAN PABLO", "EL QUETZAL",
        "LA REFORMA", "PAJAPITA", "IXCHIGUÁN", "SAN JOSÉ OJETENAM",
        "SAN CRISTÓBAL CUCHO", "SIPACAPA", "ESQUIPULAS PALO GORDO",
        "RÍO BLANCO", "SAN LORENZO",
        "LA BLANCA",  # municipio creado en 2006, no siempre en catálogos antiguos
    ],
    "HUEHUETENANGO": [
        "HUEHUETENANGO", "CHIANTLA", "MALACATANCITO", "CUILCO", "NENTÓN",
        "SAN PEDRO NECTA", "JACALTENANGO", "SOLOMA", "IXTAHUACÁN",
        "SANTA BÁRBARA", "LA LIBERTAD", "LA DEMOCRACIA", "SAN MIGUEL ACATÁN",
        "SAN RAFAEL LA INDEPENDENCIA", "TODOS SANTOS CUCHUMATÁN",
        "SAN JUAN ATITÁN", "SANTA EULALIA", "SAN MATEO IXTATÁN",
        "COLOTENANGO", "SAN SEBASTIÁN HUEHUETENANGO", "TECTITÁN",
        "CONCEPCIÓN HUISTA", "SAN JUAN IXCOY", "SAN ANTONIO HUISTA",
        "SAN SEBASTIÁN COATÁN", "BARILLAS", "AGUACATÁN", "SAN RAFAEL PETZAL",
        "SAN GASPAR IXCHIL", "SANTIAGO CHIMALTENANGO", "SANTA ANA HUISTA",
        "UNIÓN CANTINIL", "PETATÁN",
    ],
    "QUICHÉ": [
        "SANTA CRUZ DEL QUICHÉ", "CHICHÉ", "CHINIQUE", "ZACUALPA",
        "CHAJUL", "CHICHICASTENANGO", "PATZITÉ", "SAN ANTONIO ILOTENANGO",
        "SAN PEDRO JOCOPILAS", "CUNÉN", "SAN JUAN COTZAL", "JOYABAJ",
        "NEBAJ", "SAN ANDRÉS SAJCABAJÁ", "USPANTÁN", "SACAPULAS",
        "SAN BARTOLOMÉ JOCOTENANGO", "CANILLÁ", "CHICAMÁN",
        "IXCÁN", "PACHALUM",
    ],
    "BAJA VERAPAZ": [
        "SALAMÁ", "SAN MIGUEL CHICAJ", "RABINAL", "CUBULCO", "GRANADOS",
        "SANTA CRUZ EL CHOL", "SAN JERÓNIMO", "PURULHÁ",
    ],
    "ALTA VERAPAZ": [
        "COBÁN", "SANTA CRUZ VERAPAZ", "SAN CRISTÓBAL VERAPAZ", "TACTIC",
        "TAMAHÚ", "TUCURÚ", "PANZÓS", "SENAHÚ", "SAN PEDRO CARCHÁ",
        "SAN JUAN CHAMELCO", "LANQUÍN", "SANTA MARÍA CAHABÓN", "CHISEC",
        "CHAHAL", "FRAY BARTOLOMÉ DE LAS CASAS", "LA TINTA",
        "RAXRUHÁ",
    ],
    "PETÉN": [
        "FLORES", "SAN JOSÉ", "SAN BENITO", "SAN ANDRÉS", "LA LIBERTAD",
        "SAN FRANCISCO", "SANTA ANA", "DOLORES", "SAN LUIS",
        "SAYAXCHÉ", "MELCHOR DE MENCOS", "POPTÚN", "LAS CRUCES",
        "EL CHAL",
    ],
    "IZABAL": [
        "PUERTO BARRIOS", "LIVINGSTON", "EL ESTOR", "MORALES", "LOS AMATES",
    ],
    "ZACAPA": [
        "ZACAPA", "ESTANZUELA", "RÍO HONDO", "GUALÁN", "TECULUTÁN",
        "USUMATLÁN", "CABAÑAS", "SAN DIEGO", "LA UNIÓN", "HUITÉ",
        "SAN JORGE",
    ],
    "CHIQUIMULA": [
        "CHIQUIMULA", "SAN JOSÉ LA ARADA", "SAN JUAN ERMITA", "JOCOTÁN",
        "CAMOTÁN", "OLOPA", "ESQUIPULAS", "CONCEPCIÓN LAS MINAS",
        "QUEZALTEPEQUE", "SAN JACINTO", "IPALA",
    ],
    "JALAPA": [
        "JALAPA", "SAN PEDRO PINULA", "SAN LUIS JILOTEPEQUE",
        "SAN MANUEL CHAPARRÓN", "SAN CARLOS ALZATATE",
        "MONJAS", "MATAQUESCUINTLA",
    ],
    "JUTIAPA": [
        "JUTIAPA", "EL PROGRESO", "SANTA CATARINA MITA", "AGUA BLANCA",
        "ASUNCIÓN MITA", "YUPILTEPEQUE", "ATESCATEMPA", "JEREZ",
        "EL ADELANTO", "ZAPOTITLÁN", "COMAPA", "JALPATAGUA",
        "CONGUACO", "MOYUTA", "PASACO", "SAN JOSÉ ACATEMPA", "QUESADA",
    ],
}

# Aliases de municipios: nombre largo en fuente MINEDUC → canónico INE.
# Solo para nombres que la normalización sin tildes + fuzzy no resuelve bien.
# Formato: (depto_canónico, alias_sin_tilde) → municipio_canónico
_ALIAS_MUNICIPIO: dict[tuple[str, str], str] = {
    ("GUATEMALA",       "SANTA CATARINA PINULA")         : "SANTA CATARINA PINULA",
    ("HUEHUETENANGO",   "SANTA CRUZ BARILLAS")           : "BARILLAS",
    ("HUEHUETENANGO",   "SAN ILDEFONSO IXTAHUACAN")      : "IXTAHUACÁN",
    ("HUEHUETENANGO",   "SAN PEDRO SOLOMA")              : "SOLOMA",
    ("QUICHE",          "SAN MIGUEL USPANTAN")           : "USPANTÁN",
    ("QUICHE",          "SANTO TOMAS CHICHICASTENANGO")  : "CHICHICASTENANGO",
    ("QUICHE",          "PACHALUN")                      : "PACHALUM",
    ("CHIMALTENANGO",   "SAN PEDRO YEPOCAPA")            : "YEPOCAPA",
    ("QUETZALTENANGO",  "GENOVA COSTA CUCA")             : "GÉNOVA",
    ("RETALHULEU",      "SAN FELIPE")                    : "SAN FELIPE RETALHULEU",
    ("SUCHITEPEQUEZ",   "SAN JOSE LA MAQUINA")           : "SAN JOSÉ LA MÁQUINA",
    # Nombres largos con prefijo "SAN MIGUEL" / "SAN PEDRO" que usan en la fuente
    ("ALTA VERAPAZ",    "SAN MIGUEL TUCURU")             : "TUCURÚ",
    ("CHIMALTENANGO",   "SAN MIGUEL POCHUTA")            : "POCHUTA",
    ("SACATEPEQUEZ",    "ALOTENANGO")                    : "SAN JUAN ALOTENANGO",
    ("TOTONICAPAN",     "SAN BARTOLO AGUAS CALIENTES")   : "SAN BARTOLO",
    ("SUCHITEPEQUEZ",   "SAN JOSE EL IDOLO")             : "SAN JOSÉ EL ÍDOLO",
}

# Lookup: (depto_sin_tilde, mun_sin_tilde) → municipio canónico
_MUN_LOOKUP: dict[tuple[str, str], str] = {
    (normalizar_para_comparar(d), normalizar_para_comparar(m)): m
    for d, muns in MUNICIPIOS_POR_DEPTO.items()
    for m in muns
}
# Agregar aliases normalizados al lookup
_MUN_LOOKUP.update({
    (normalizar_para_comparar(d), normalizar_para_comparar(alias)): canon
    for (d, alias), canon in _ALIAS_MUNICIPIO.items()
})

# Lista plana de todos los municipios (para RapidFuzz sin filtrar por depto)
TODOS_MUNICIPIOS: list[str] = [
    m for muns in MUNICIPIOS_POR_DEPTO.values() for m in muns
]


def lookup_municipio(municipio: str, departamento: str | None = None) -> str | None:
    """Devuelve el municipio canónico o None si no hay match exacto (sin tildes).

    Si se provee departamento (canónico), filtra por él primero.
    """
    m_key = normalizar_para_comparar(municipio)
    if departamento:
        d_key = normalizar_para_comparar(departamento)
        resultado = _MUN_LOOKUP.get((d_key, m_key))
        if resultado:
            return resultado
    # Fallback: buscar en todos los departamentos
    for (d_key, mk), canon in _MUN_LOOKUP.items():
        if mk == m_key:
            return canon
    return None
