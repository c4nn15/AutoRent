"""Prepara la base de datos para grabar la demo o para la muestra en vivo.

Uso (con la aplicacion CERRADA):
    python scripts/preparar_demo.py respaldar [nombre]   # copia autorent.db a respaldos/<nombre>.db
    python scripts/preparar_demo.py limpiar              # respalda y borra autorent.db (la app carga los datos de demo)
    python scripts/preparar_demo.py restaurar [nombre]   # vuelve a una copia (por defecto, la mas reciente)
    python scripts/preparar_demo.py listar               # muestra las copias disponibles
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "autorent.db"
RESPALDOS = RAIZ / "respaldos"


def _copias():
    return sorted(RESPALDOS.glob("*.db"), key=lambda p: p.stat().st_mtime)


def respaldar(nombre=None):
    if not DB.exists():
        sys.exit("No existe autorent.db: no hay nada que respaldar.")
    RESPALDOS.mkdir(exist_ok=True)
    nombre = nombre or datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = RESPALDOS / f"{nombre}.db"
    shutil.copy2(DB, destino)
    print(f"Copia guardada en {destino.relative_to(RAIZ)}")


def limpiar():
    if DB.exists():
        respaldar("antes_de_limpiar_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        DB.unlink()
    print("Base borrada. Al abrir la app se cargan los datos de demo.")


def restaurar(nombre=None):
    if nombre:
        origen = RESPALDOS / f"{nombre}.db"
    else:
        copias = _copias()
        if not copias:
            sys.exit("No hay copias en respaldos/.")
        origen = copias[-1]
    if not origen.exists():
        sys.exit(f"No existe la copia {origen.name}.")
    shutil.copy2(origen, DB)
    print(f"Base restaurada desde {origen.name}")


def listar():
    copias = _copias()
    if not copias:
        print("No hay copias en respaldos/.")
    for p in copias:
        print(p.name)


def main(argv):
    if not argv or argv[0] not in ("respaldar", "limpiar", "restaurar", "listar"):
        print(__doc__)
        return 1
    accion, args = argv[0], argv[1:2]
    if accion in ("limpiar", "listar"):
        args = []
    {"respaldar": respaldar, "limpiar": limpiar,
     "restaurar": restaurar, "listar": listar}[accion](*args)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
