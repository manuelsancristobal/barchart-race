"""Constantes, rutas y configuración del proyecto."""

import os
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_ANNOTATIONS = PROJECT_ROOT / "data" / "annotations"
DATA_REFERENCE = PROJECT_ROOT / "data" / "reference"
DATA_WORK = PROJECT_ROOT / "data" / "work"

CSV_LOCAL = DATA_RAW / "jac_data.csv"
CONTINENT_MAPPING_CSV = DATA_REFERENCE / "continent_mapping.csv"

# Ruta al repo Jekyll local (opcional; solo necesario para deploy)
_jekyll_env = os.getenv("JEKYLL_REPO")
JEKYLL_REPO: Path | None = Path(_jekyll_env) if _jekyll_env else None
JEKYLL_BASE = (JEKYLL_REPO / "proyectos" / "barchart-race") if JEKYLL_REPO else None
JEKYLL_DATA_DIR = (JEKYLL_BASE / "assets" / "data") if JEKYLL_BASE else None
JEKYLL_ANNOTATIONS_DIR = (JEKYLL_BASE / "assets" / "annotations") if JEKYLL_BASE else None
JEKYLL_CHARTS_DIR = (JEKYLL_BASE / "assets" / "charts") if JEKYLL_BASE else None
JEKYLL_CSS_DIR = (JEKYLL_BASE / "assets" / "css") if JEKYLL_BASE else None
JEKYLL_JS_DIR = (JEKYLL_BASE / "assets" / "js") if JEKYLL_BASE else None
JEKYLL_PAGE = (JEKYLL_BASE / "viz.html") if JEKYLL_BASE else None
JEKYLL_PROJECTS_DIR = (JEKYLL_REPO / "_projects") if JEKYLL_REPO else None

# Markdown del proyecto (fuente local)
JEKYLL_PROJECT_MD = PROJECT_ROOT / "jekyll" / "barchart-race.md"

# Directorio de visualización
VIZ_DIR = PROJECT_ROOT / "viz"

# ── Google Sheets ──────────────────────────────────────
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1U3JiVuxjDcvaIoLw9XkW3JKfuh-8_3Pc/export?format=csv&gid=499690993"

# ── Columnas esperadas en la fuente ────────────────────
EXPECTED_COLUMNS = [
    "Año",
    "Mes",
    "Cod_Operador",
    "Operador",
    "Grupo",
    "ORIG_1",
    "DEST_1",
    "ORIG_1_N",
    "DEST_1_N",
    "ORIG_1_PAIS",
    "DEST_1_PAIS",
    "ORIG_2",
    "DEST_2",
    "ORIG_2_N",
    "DEST_2_N",
    "ORIG_2_PAIS",
    "DEST_2_PAIS",
    "OPER_2",
    "NAC",
    "PAX_LIB",
    "PASAJEROS",
    "CAR_LIB",
    "CARGA (Ton)",
    "CORREO",
    "Distancia",
]

# ── Nombres de meses en español (índice 0 vacío) ─────
MONTH_NAMES_ES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# ── Paleta de colores por continente ───────────────────
CONTINENT_COLORS = {
    "América": "#e48381",
    "Europa": "#90d595",
    "Asia": "#ffb3ff",
    "Medio Oriente": "#eafb50",
    "Oceanía": "#aafbff",
    "África": "#f7bb5f",
    "Antártica": "#adb0ff",  # reservado, sin uso actual
    "Otro": "#cccccc",
}

# ── Combinaciones de pipeline ──────────────────────────
PERSPECTIVAS = ["emisivo", "receptivo"]
DIMENSIONES = ["destinos", "aerolinea"]
METRICAS = ["pasajeros", "tonelaje"]

# ── Mapeo de continentes (país → continente) ──────────
# Se carga desde CSV si existe; este dict es el fallback/seed.
CONTINENT_MAP = {
    "ALEMANIA": "Europa",
    "ANGOLA": "África",
    "ANTIGUA": "América",
    "ANTILLAS HOLANDESA": "América",
    "ARGENTINA": "América",
    "ARUBA": "América",
    "AUSTRALIA": "Oceanía",
    "BAHAMAS": "América",
    "BARBADOS": "América",
    "BELGICA": "Europa",
    "BELICE": "América",
    "BOLIVIA": "América",
    "BRASIL": "América",
    "CABO VERDE": "África",
    "CANADA": "América",
    "CHECOESLOVAQUIA": "Europa",
    "COLOMBIA": "América",
    "COSTA DE MARFIL": "África",
    "COSTA RICA": "América",
    "CUBA": "América",
    "DINAMARCA": "Europa",
    "ECUADOR": "América",
    "EL SALVADOR": "América",
    "EMI. ARABES UNIDOS": "Medio Oriente",
    "EMI.ARABES UNIDOS": "Medio Oriente",
    "ESPAÑA": "Europa",
    "ESTADOS UNIDOS": "América",
    "ETIOPIA": "África",
    "FILIPINAS": "Asia",
    "FRANCIA": "Europa",
    "GHANA": "África",
    "GUATEMALA": "América",
    "GUAYANA FRANCESA": "América",
    "GUYANA FRANCESA": "América",
    "HAITI": "América",
    "HOLANDA": "Europa",
    "HONDURAS": "América",
    "INDIA": "Asia",
    "IRLANDA DEL NORTE": "Europa",
    "ISLA DE HAWAI": "Oceanía",
    "ISLA DE TAHITI": "Oceanía",
    "ISLA MARTINICA": "América",
    "ISRAEL": "Medio Oriente",
    "ITALIA": "Europa",
    "JAMAICA": "América",
    "JAPON": "Asia",
    "LUXEMBURGO": "Europa",
    "MALASIA": "Asia",
    "MALI": "África",
    "MARRUECOS": "África",
    "MEXICO": "América",
    "NAMIBIA": "África",
    "NICARAGUA": "América",
    "NIGERIA": "África",
    "NORUEGA": "Europa",
    "NUEVA ZELANDIA": "Oceanía",
    "PANAMA": "América",
    "PARAGUAY": "América",
    "PERU": "América",
    "PORTUGAL": "Europa",
    "PUERTO RICO": "América",
    "QATAR": "Medio Oriente",
    "REINO UNIDO": "Europa",
    "REP. COREA DEL SUR": "Asia",
    "REP. DOMINICANA": "América",
    "REP. POPULAR CHINA": "Asia",
    "REP.COREA DEL SUR": "Asia",
    "RUSIA": "Europa",
    "SENEGAL": "África",
    "SINGAPUR": "Asia",
    "SUDAFRICA": "África",
    "SUECIA": "Europa",
    "SUIZA": "Europa",
    "SURINAM": "América",
    "TAILANDIA": "Asia",
    "TAIWAN": "Asia",
    "TOGO": "África",
    "TRINIDAD Y TOBAGO": "América",
    "TURQUIA": "Europa",
    "URUGUAY": "América",
    "VENEZUELA": "América",
}
