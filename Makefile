.PHONY: help install install-dev lint test coverage assets deploy ver clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install      Instalar dependencias del proyecto"
	@echo "  make install-dev  Instalar proyecto + dependencias de desarrollo"
	@echo "  make lint         Ejecutar linting con ruff"
	@echo "  make test         Ejecutar tests con pytest"
	@echo "  make coverage     Ejecutar tests con reporte de cobertura"
	@echo "  make assets       Generar gráficos de análisis (PNGs)"
	@echo "  make deploy       Copiar archivos al repo Jekyll"
	@echo "  make ver          Abrir visualización en el navegador"
	@echo "  make clean        Eliminar archivos generados y caché"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src/ scripts/ tests/
	ruff format --check src/ scripts/ tests/

test:
	pytest tests/ -v

coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "\nReporte de cobertura generado en htmlcov/index.html"

assets:
	python run.py charts

deploy:
	python run.py deploy

ver:
	python run.py ver

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.DEFAULT_GOAL := help
