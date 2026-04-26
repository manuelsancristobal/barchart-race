"""Copia archivos al repo Jekyll local: datos, anotaciones, charts, HTML, CSS y JS."""

from __future__ import annotations

import logging
import shutil

from src.config import (
    DATA_ANNOTATIONS,
    DATA_PROCESSED,
    JEKYLL_ANNOTATIONS_DIR,
    JEKYLL_CHARTS_DIR,
    JEKYLL_CSS_DIR,
    JEKYLL_DATA_DIR,
    JEKYLL_JS_DIR,
    JEKYLL_PAGE,
    JEKYLL_PROJECT_MD,
    JEKYLL_PROJECTS_DIR,
    JEKYLL_REPO,
    VIZ_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def deploy() -> None:
    """Copia archivos al repo Jekyll. El push es manual."""
    if JEKYLL_REPO is None:
        logger.error("Variable de entorno 'JEKYLL_REPO' no definida.")
        return
    # ── JSONs de datos y anotaciones ──
    for src_dir, dst_dir, label, pattern in [
        (DATA_PROCESSED, JEKYLL_DATA_DIR, "datos", "*.json"),
        (DATA_ANNOTATIONS, JEKYLL_ANNOTATIONS_DIR, "anotaciones", "*.json"),
    ]:
        if not src_dir.exists():
            logger.warning("Directorio fuente no existe: %s", src_dir)
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in src_dir.glob(pattern):
            shutil.copy2(f, dst_dir / f.name)
            count += 1
        logger.info("Copiados %d archivos de %s → %s", count, label, dst_dir)

    # ── Charts (PNGs + captions.json) ──
    charts_src = VIZ_DIR / "assets" / "charts"
    if charts_src.exists():
        JEKYLL_CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in charts_src.glob("*.png"):
            shutil.copy2(f, JEKYLL_CHARTS_DIR / f.name)
            count += 1
        captions = charts_src / "captions.json"
        if captions.exists():
            shutil.copy2(captions, JEKYLL_CHARTS_DIR / captions.name)
            count += 1
        logger.info("Copiados %d archivos de charts → %s", count, JEKYLL_CHARTS_DIR)

    # ── CSS ──
    css_src = VIZ_DIR / "assets" / "css" / "barchart.css"
    if css_src.exists():
        JEKYLL_CSS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(css_src, JEKYLL_CSS_DIR / css_src.name)
        logger.info("Copiado CSS → %s", JEKYLL_CSS_DIR)

    # ── JS ──
    js_src = VIZ_DIR / "assets" / "js" / "barchart-race.js"
    if js_src.exists():
        JEKYLL_JS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(js_src, JEKYLL_JS_DIR / js_src.name)
        logger.info("Copiado JS → %s", JEKYLL_JS_DIR)

    # ── HTML (index.html) ──
    html_src = VIZ_DIR / "index.html"
    if html_src.exists():
        JEKYLL_PAGE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(html_src, JEKYLL_PAGE)
        logger.info("Copiado viz.html → %s", JEKYLL_PAGE)

    # ── Markdown del proyecto ──
    if JEKYLL_PROJECT_MD.exists():
        JEKYLL_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(JEKYLL_PROJECT_MD, JEKYLL_PROJECTS_DIR / JEKYLL_PROJECT_MD.name)
        logger.info("Copiado proyecto .md → %s", JEKYLL_PROJECTS_DIR)

    logger.info("Deploy completado. Recuerda hacer git push en el repo Jekyll.")


if __name__ == "__main__":
    deploy()
