"""Acceso a datos: unica capa que conoce SQL."""

_SELECT_VEHICULO = """
    SELECT v.patente, v.modelo, v.tarifa_diaria, v.activo,
           EXISTS (SELECT 1 FROM alquileres a
                   WHERE a.patente = v.patente
                     AND a.fecha_devolucion IS NULL) AS alquilado
    FROM vehiculos v
"""

_SELECT_ALQUILER = """
    SELECT a.id, a.patente, v.modelo, v.tarifa_diaria AS tarifa_actual,
           v.activo AS vehiculo_activo,
           a.dni, c.nombre, c.activo AS cliente_activo,
           a.fecha_inicio, a.dias_previstos, a.tarifa_diaria,
           a.fecha_devolucion, a.dias_reales, a.costo_final
    FROM alquileres a
    JOIN vehiculos v ON v.patente = a.patente
    JOIN clientes  c ON c.dni     = a.dni
"""


class Repositorio:
    def __init__(self, conn):
        self.conn = conn

    # ---------------- vehiculos ----------------
    def obtener_vehiculo(self, patente):
        return self.conn.execute(
            _SELECT_VEHICULO + " WHERE v.patente = ?", (patente,)).fetchone()

    def listar_vehiculos(self, solo_activos=True):
        sql = _SELECT_VEHICULO
        if solo_activos:
            sql += " WHERE v.activo = 1"
        return self.conn.execute(sql + " ORDER BY v.patente").fetchall()

    def insertar_vehiculo(self, patente, modelo, tarifa):
        with self.conn:
            self.conn.execute(
                "INSERT INTO vehiculos (patente, modelo, tarifa_diaria) VALUES (?, ?, ?)",
                (patente, modelo, tarifa))

    def actualizar_vehiculo(self, patente, modelo, tarifa, activo=1):
        with self.conn:
            self.conn.execute(
                "UPDATE vehiculos SET modelo = ?, tarifa_diaria = ?, activo = ? "
                "WHERE patente = ?", (modelo, tarifa, activo, patente))

    def desactivar_vehiculo(self, patente):
        with self.conn:
            self.conn.execute(
                "UPDATE vehiculos SET activo = 0 WHERE patente = ?", (patente,))

    # ---------------- clientes ----------------
    def obtener_cliente(self, dni):
        return self.conn.execute(
            "SELECT dni, nombre, activo FROM clientes WHERE dni = ?", (dni,)).fetchone()

    def listar_clientes(self, solo_activos=True):
        sql = "SELECT dni, nombre, activo FROM clientes"
        if solo_activos:
            sql += " WHERE activo = 1"
        return self.conn.execute(sql + " ORDER BY nombre").fetchall()

    def insertar_cliente(self, dni, nombre):
        with self.conn:
            self.conn.execute(
                "INSERT INTO clientes (dni, nombre) VALUES (?, ?)", (dni, nombre))

    def actualizar_cliente(self, dni, nombre, activo=1):
        with self.conn:
            self.conn.execute(
                "UPDATE clientes SET nombre = ?, activo = ? WHERE dni = ?",
                (nombre, activo, dni))

    def desactivar_cliente(self, dni):
        with self.conn:
            self.conn.execute("UPDATE clientes SET activo = 0 WHERE dni = ?", (dni,))

    # ---------------- alquileres ----------------
    def insertar_alquiler(self, patente, dni, fecha_inicio, dias, tarifa):
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO alquileres "
                "(patente, dni, fecha_inicio, dias_previstos, tarifa_diaria) "
                "VALUES (?, ?, ?, ?, ?)",
                (patente, dni, fecha_inicio, dias, tarifa))
            return cur.lastrowid

    def obtener_alquiler(self, alquiler_id):
        return self.conn.execute(
            _SELECT_ALQUILER + " WHERE a.id = ?", (alquiler_id,)).fetchone()

    def obtener_alquiler_activo(self, patente):
        return self.conn.execute(
            _SELECT_ALQUILER +
            " WHERE a.patente = ? AND a.fecha_devolucion IS NULL", (patente,)).fetchone()

    def cerrar_alquiler(self, alquiler_id, fecha_devolucion, dias_reales, costo):
        with self.conn:
            self.conn.execute(
                "UPDATE alquileres SET fecha_devolucion = ?, dias_reales = ?, "
                "costo_final = ? WHERE id = ?",
                (fecha_devolucion, dias_reales, costo, alquiler_id))

    def listar_alquileres_activos(self):
        return self.conn.execute(
            _SELECT_ALQUILER +
            " WHERE a.fecha_devolucion IS NULL ORDER BY a.fecha_inicio, a.id").fetchall()

    def listar_historial(self):
        return self.conn.execute(
            _SELECT_ALQUILER + " ORDER BY a.fecha_inicio DESC, a.id DESC").fetchall()

    def tiene_alquiler_activo_cliente(self, dni):
        return self.conn.execute(
            "SELECT 1 FROM alquileres WHERE dni = ? AND fecha_devolucion IS NULL LIMIT 1",
            (dni,)).fetchone() is not None

    # ---------------- reportes ----------------
    def ingresos_entre(self, desde_iso, hasta_iso):
        """(cantidad de alquileres devueltos, total facturado) en [desde, hasta]."""
        fila = self.conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(costo_final), 0) AS total "
            "FROM alquileres "
            "WHERE fecha_devolucion IS NOT NULL "
            "AND fecha_devolucion BETWEEN ? AND ?", (desde_iso, hasta_iso)).fetchone()
        return fila["n"], fila["total"]

    def listar_devueltos_entre(self, desde_iso, hasta_iso):
        return self.conn.execute(
            _SELECT_ALQUILER +
            " WHERE a.fecha_devolucion IS NOT NULL "
            "AND a.fecha_devolucion BETWEEN ? AND ? "
            "ORDER BY a.fecha_devolucion, a.id", (desde_iso, hasta_iso)).fetchall()

    def ranking_vehiculos(self, limite=10):
        return self.conn.execute(
            "SELECT a.patente, v.modelo, COUNT(*) AS cantidad, "
            "COALESCE(SUM(a.costo_final), 0) AS facturado "
            "FROM alquileres a JOIN vehiculos v ON v.patente = a.patente "
            "GROUP BY a.patente, v.modelo "
            "ORDER BY cantidad DESC, a.patente LIMIT ?", (limite,)).fetchall()
