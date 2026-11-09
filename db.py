"""Conexion y esquema de la base de datos SQLite de AutoRent."""
import sqlite3
import sys
from pathlib import Path

# El archivo de la base queda junto al codigo (o junto al ejecutable si se empaqueta).
_BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
DB_PATH = _BASE / "autorent.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS vehiculos (
    patente        TEXT PRIMARY KEY,
    modelo         TEXT NOT NULL,
    tarifa_diaria  REAL NOT NULL CHECK (tarifa_diaria > 0),
    activo         INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clientes (
    dni      TEXT PRIMARY KEY,
    nombre   TEXT NOT NULL,
    activo   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS alquileres (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    patente           TEXT NOT NULL REFERENCES vehiculos(patente),
    dni               TEXT NOT NULL REFERENCES clientes(dni),
    fecha_inicio      TEXT NOT NULL,                -- ISO: AAAA-MM-DD
    dias_previstos    INTEGER NOT NULL CHECK (dias_previstos > 0),
    tarifa_diaria     REAL NOT NULL,                -- tarifa vigente al alquilar
    fecha_devolucion  TEXT,                         -- NULL mientras esta activo
    dias_reales       INTEGER,
    costo_final       REAL
);

-- Un vehiculo no puede tener dos alquileres activos a la vez.
CREATE UNIQUE INDEX IF NOT EXISTS ux_alquiler_activo
    ON alquileres(patente) WHERE fecha_devolucion IS NULL;
"""


def conectar(ruta=DB_PATH):
    """Abre la base (la crea si no existe) y garantiza el esquema.

    Usar ":memory:" como ruta sirve para pruebas automatizadas.
    """
    conn = sqlite3.connect(str(ruta))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ESQUEMA)
    conn.commit()
    return conn
