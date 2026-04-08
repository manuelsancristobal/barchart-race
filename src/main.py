"""Orquestador: ejecuta el ETL completo para las 8 combinaciones."""

from __future__ import annotations

import logging
import sys

from src.config import DIMENSIONES, METRICAS, PERSPECTIVAS
from src.etl.extract import extract
from src.etl.load import load
from src.etl.transform import build_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run(*, use_remote: bool = False) -> list[str]:
    """Ejecuta extract → transform → load para las 8 combinaciones."""
    logger.info("Iniciando ETL...")
    df = extract(use_remote=use_remote)

    generated: list[str] = []
    errors: list[str] = []
    for perspectiva in PERSPECTIVAS:
        for dimension in DIMENSIONES:
            for metrica in METRICAS:
                combo = f"{perspectiva}_{dimension}_{metrica}"
                try:
                    logger.info("Procesando: %s", combo)
                    transformed = build_pipeline(df, perspectiva, dimension, metrica)
                    path = load(transformed, perspectiva, dimension, metrica)
                    generated.append(path)
                except Exception:
                    logger.exception("Error procesando %s", combo)
                    errors.append(combo)

    logger.info("ETL completado. %d JSONs generados.", len(generated))
    for p in generated:
        logger.info("  → %s", p)

    if errors:
        logger.error("Combinaciones con error: %s", errors)

    return generated


if __name__ == "__main__":
    use_remote = "--remote" in sys.argv
    result = run(use_remote=use_remote)
    if len(result) < len(PERSPECTIVAS) * len(DIMENSIONES) * len(METRICAS):
        sys.exit(1)
