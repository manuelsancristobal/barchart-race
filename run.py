"""
Punto de entrada unico del proyecto Barchart Race.

Uso:
    python run.py          # Muestra ayuda
    python run.py etl      # Ejecuta ETL (datos locales)
    python run.py charts   # Genera graficos de analisis
    python run.py ver      # Abre la visualizacion en el navegador
    python run.py test     # Ejecuta tests + linting
    python run.py deploy   # Copia archivos al repo Jekyll
    python run.py all      # Pipeline completo: etl -> charts -> deploy
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import webbrowser

# Directorio raiz del proyecto (donde vive run.py)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- Colores ANSI (se desactivan si la terminal no soporta) -----------

def _supports_color() -> bool:
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True

_COLOR = _supports_color()

def _green(text: str) -> str:
    return f"\033[92m{text}\033[0m" if _COLOR else text

def _cyan(text: str) -> str:
    return f"\033[96m{text}\033[0m" if _COLOR else text

def _red(text: str) -> str:
    return f"\033[91m{text}\033[0m" if _COLOR else text

def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if _COLOR else text

def _yellow(text: str) -> str:
    return f"\033[93m{text}\033[0m" if _COLOR else text


# --- Helpers ----------------------------------------------------------

def _run(cmd: list[str], label: str) -> bool:
    """Ejecuta un comando y retorna True si fue exitoso."""
    print(f"\n{_cyan('>')} {_bold(label)}")
    print(f"  {' '.join(cmd)}\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = _PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(cmd, cwd=_PROJECT_ROOT, env=env)
    if result.returncode != 0:
        print(f"\n{_red('X')} {label} fallo (exit code {result.returncode})")
        return False
    print(f"\n{_green('OK')} {label}")
    return True


# --- Comandos ---------------------------------------------------------

def cmd_etl(args: list[str]) -> bool:
    cmd = [sys.executable, "-m", "src.main"]
    if "--remote" in args:
        cmd.append("--remote")
    return _run(cmd, "ETL - Generando JSONs")


def cmd_charts() -> bool:
    return _run(
        [sys.executable, "scripts/analyze_traffic.py"],
        "Charts - Generando graficos de analisis",
    )


def _sync_viz_data() -> None:
    """Copia JSONs y annotations a viz/assets/ para que el servidor local funcione."""
    src_data = os.path.join(_PROJECT_ROOT, "data", "processed")
    dst_data = os.path.join(_PROJECT_ROOT, "viz", "assets", "data")
    src_ann = os.path.join(_PROJECT_ROOT, "data", "annotations")
    dst_ann = os.path.join(_PROJECT_ROOT, "viz", "assets", "annotations")

    for src_dir, dst_dir, pattern in [
        (src_data, dst_data, "*.json"),
        (src_ann, dst_ann, "*.json"),
    ]:
        if not os.path.isdir(src_dir):
            continue
        files = glob.glob(os.path.join(src_dir, pattern))
        if not files:
            continue
        os.makedirs(dst_dir, exist_ok=True)
        for f in files:
            shutil.copy2(f, dst_dir)

    count = len(glob.glob(os.path.join(dst_data, "*.json"))) if os.path.isdir(dst_data) else 0
    print(f"  Sincronizados {count} JSONs en viz/assets/data/")


def cmd_ver() -> bool:
    url = "http://127.0.0.1:8000/viz/index.html"
    print(f"\n{_cyan('>')} {_bold('Servidor local')}")
    _sync_viz_data()
    print(f"  Abriendo {url} en el navegador...")
    print(f"  Presiona Ctrl+C para detener el servidor.\n")
    webbrowser.open(url)
    try:
        subprocess.run(
            [sys.executable, "-m", "http.server", "8000", "--bind", "127.0.0.1"],
            cwd=_PROJECT_ROOT,
        )
    except KeyboardInterrupt:
        print(f"\n{_green('OK')} Servidor detenido.")
    return True


def cmd_test() -> bool:
    ok = _run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        "Tests - pytest",
    )
    ok2 = _run(
        [sys.executable, "-m", "ruff", "check", "src/", "scripts/", "tests/"],
        "Linting - ruff",
    )
    return ok and ok2


def cmd_deploy() -> bool:
    return _run(
        [sys.executable, "-m", "src.deploy"],
        "Deploy - Copiando al repo Jekyll",
    )


def cmd_all(args: list[str]) -> bool:
    steps = [
        ("etl", lambda: cmd_etl(args)),
        ("charts", cmd_charts),
        ("deploy", cmd_deploy),
    ]
    for name, fn in steps:
        if not fn():
            print(f"\n{_red('X')} Pipeline detenido en '{name}'.")
            return False
    print(f"\n{_green('OK')} Pipeline completo.")
    return True


def cmd_help() -> None:
    print(f"""
{_bold('Barchart Race - Comandos disponibles')}

  python run.py {_green('etl')}            Ejecuta el ETL (genera 8 JSONs)
  python run.py {_green('etl --remote')}    Descarga datos frescos y ejecuta ETL
  python run.py {_green('charts')}          Genera graficos de analisis (PNGs)
  python run.py {_green('ver')}             Abre la visualizacion en el navegador
  python run.py {_green('test')}            Ejecuta tests (pytest) + linting (ruff)
  python run.py {_green('deploy')}          Copia archivos al repo Jekyll
  python run.py {_green('all')}             Pipeline completo: etl -> charts -> deploy

{_yellow('Ejemplo:')} python run.py etl --remote
""")


# --- Main -------------------------------------------------------------

COMMANDS = {
    "etl": lambda args: cmd_etl(args),
    "charts": lambda _: cmd_charts(),
    "ver": lambda _: cmd_ver(),
    "test": lambda _: cmd_test(),
    "deploy": lambda _: cmd_deploy(),
    "all": lambda args: cmd_all(args),
}


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        cmd_help()
        sys.exit(0)

    command = args[0]
    if command not in COMMANDS:
        print(f"{_red('Error:')} Comando desconocido '{command}'")
        cmd_help()
        sys.exit(1)

    extra_args = args[1:]
    ok = COMMANDS[command](extra_args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
