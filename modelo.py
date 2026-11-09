"""Dominio y logica de negocio de AutoRent."""
import sqlite3
from datetime import date, datetime, timedelta

FORMATO_FECHA = "%d/%m/%Y"


# ---------------------------------------------------------------- fechas
def parsear_fecha(texto):
    """'dd/mm/aaaa' -> date. Lanza ValueError con mensaje legible."""
    try:
        return datetime.strptime((texto or "").strip(), FORMATO_FECHA).date()
    except ValueError:
        raise ValueError("Fecha invalida (use dd/mm/aaaa).")


def formatear_fecha(d):
    return d.strftime(FORMATO_FECHA) if d else ""


def hoy_str():
    return formatear_fecha(date.today())


# ---------------------------------------------------------------- entidades
class Vehiculo:
    def __init__(self, patente, modelo, tarifa_diaria, activo=True, alquilado=False):
        if not patente or not patente.strip():
            raise ValueError("La patente no puede estar vacia.")
        if not modelo or not modelo.strip():
            raise ValueError("El modelo no puede estar vacio.")
        if tarifa_diaria is None or tarifa_diaria <= 0:
            raise ValueError("La tarifa diaria debe ser un valor positivo.")
        self.patente = patente.strip().upper()
        self.modelo = modelo.strip()
        self.tarifa_diaria = float(tarifa_diaria)
        self.activo = bool(activo)
        self.alquilado = bool(alquilado)

    def esta_disponible(self):
        return self.activo and not self.alquilado

    @property
    def estado(self):
        if not self.activo:
            return "inactivo"
        return "alquilado" if self.alquilado else "disponible"


class Cliente:
    def __init__(self, dni, nombre, activo=True):
        if not dni or not dni.strip():
            raise ValueError("El DNI no puede estar vacio.")
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacio.")
        self.dni = dni.strip()
        self.nombre = nombre.strip()
        self.activo = bool(activo)


class Alquiler:
    """Un alquiler, activo (sin devolver) o cerrado (con costo final)."""

    def __init__(self, vehiculo, cliente, fecha_inicio, dias_previstos,
                 tarifa_diaria, id=None, fecha_devolucion=None,
                 dias_reales=None, costo_final=None):
        if not isinstance(dias_previstos, int) or dias_previstos <= 0:
            raise ValueError("Los dias deben ser un entero positivo.")
        self.id = id
        self.vehiculo = vehiculo
        self.cliente = cliente
        self.fecha_inicio = fecha_inicio
        self.dias_previstos = dias_previstos
        self.tarifa_diaria = float(tarifa_diaria)   # tarifa vigente al alquilar
        self.fecha_devolucion = fecha_devolucion
        self.dias_reales = dias_reales
        self.costo_final = costo_final

    @property
    def activo(self):
        return self.fecha_devolucion is None

    @property
    def fecha_prevista_devolucion(self):
        return self.fecha_inicio + timedelta(days=self.dias_previstos)

    @property
    def costo_estimado(self):
        return self.dias_previstos * self.tarifa_diaria

    def dias_usados(self, fecha_devolucion):
        """Dias reales de uso: diferencia de fechas, con un minimo de 1."""
        if fecha_devolucion < self.fecha_inicio:
            raise ValueError("La devolucion no puede ser anterior al inicio del alquiler.")
        return max(1, (fecha_devolucion - self.fecha_inicio).days)

    def calcular_costo(self, fecha_devolucion):
        return self.dias_usados(fecha_devolucion) * self.tarifa_diaria


# ---------------------------------------------------------------- logica
class Agencia:
    """Reglas de negocio. Persiste a traves de un Repositorio."""

    def __init__(self, repo):
        self.repo = repo

    # -- conversion de filas a objetos --
    @staticmethod
    def _vehiculo(fila):
        return Vehiculo(fila["patente"], fila["modelo"], fila["tarifa_diaria"],
                        activo=fila["activo"], alquilado=fila["alquilado"])

    @staticmethod
    def _cliente(fila):
        return Cliente(fila["dni"], fila["nombre"], activo=fila["activo"])

    @staticmethod
    def _alquiler(f):
        veh = Vehiculo(f["patente"], f["modelo"], f["tarifa_actual"],
                       activo=f["vehiculo_activo"],
                       alquilado=f["fecha_devolucion"] is None)
        cli = Cliente(f["dni"], f["nombre"], activo=f["cliente_activo"])
        dev = date.fromisoformat(f["fecha_devolucion"]) if f["fecha_devolucion"] else None
        return Alquiler(veh, cli, date.fromisoformat(f["fecha_inicio"]),
                        f["dias_previstos"], f["tarifa_diaria"], id=f["id"],
                        fecha_devolucion=dev, dias_reales=f["dias_reales"],
                        costo_final=f["costo_final"])

    # -- vehiculos --
    def registrar_vehiculo(self, patente, modelo, tarifa):
        nuevo = Vehiculo(patente, modelo, tarifa)          # valida
        existente = self.repo.obtener_vehiculo(nuevo.patente)
        if existente and existente["activo"]:
            raise ValueError(f"Ya existe un vehiculo con patente '{nuevo.patente}'.")
        if existente:                                       # estaba dado de baja
            self.repo.actualizar_vehiculo(nuevo.patente, nuevo.modelo,
                                          nuevo.tarifa_diaria, activo=1)
        else:
            self.repo.insertar_vehiculo(nuevo.patente, nuevo.modelo, nuevo.tarifa_diaria)
        return self.buscar_vehiculo(nuevo.patente)

    def buscar_vehiculo(self, patente):
        fila = self.repo.obtener_vehiculo((patente or "").strip().upper())
        return self._vehiculo(fila) if fila else None

    def listar_vehiculos(self, solo_activos=True):
        return [self._vehiculo(f) for f in self.repo.listar_vehiculos(solo_activos)]

    def modificar_vehiculo(self, patente, modelo, tarifa):
        actual = self.buscar_vehiculo(patente)
        if not actual or not actual.activo:
            raise ValueError(f"Vehiculo '{(patente or '').strip().upper()}' no encontrado.")
        nuevo = Vehiculo(actual.patente, modelo, tarifa)    # valida
        self.repo.actualizar_vehiculo(nuevo.patente, nuevo.modelo, nuevo.tarifa_diaria)
        return self.buscar_vehiculo(nuevo.patente)

    def dar_baja_vehiculo(self, patente):
        v = self.buscar_vehiculo(patente)
        if not v or not v.activo:
            raise ValueError(f"Vehiculo '{(patente or '').strip().upper()}' no encontrado.")
        if v.alquilado:
            raise ValueError(f"'{v.patente}' tiene un alquiler activo: devuelvalo antes de darlo de baja.")
        self.repo.desactivar_vehiculo(v.patente)
        return v

    # -- clientes --
    def registrar_cliente(self, dni, nombre):
        nuevo = Cliente(dni, nombre)                        # valida
        existente = self.repo.obtener_cliente(nuevo.dni)
        if existente and existente["activo"]:
            raise ValueError(f"Ya existe un cliente con DNI '{nuevo.dni}'.")
        if existente:
            self.repo.actualizar_cliente(nuevo.dni, nuevo.nombre, activo=1)
        else:
            self.repo.insertar_cliente(nuevo.dni, nuevo.nombre)
        return self.buscar_cliente(nuevo.dni)

    def buscar_cliente(self, dni):
        fila = self.repo.obtener_cliente((dni or "").strip())
        return self._cliente(fila) if fila else None

    def listar_clientes(self, solo_activos=True):
        return [self._cliente(f) for f in self.repo.listar_clientes(solo_activos)]

    def modificar_cliente(self, dni, nombre):
        actual = self.buscar_cliente(dni)
        if not actual or not actual.activo:
            raise ValueError(f"Cliente con DNI '{(dni or '').strip()}' no encontrado.")
        nuevo = Cliente(actual.dni, nombre)                 # valida
        self.repo.actualizar_cliente(nuevo.dni, nuevo.nombre)
        return self.buscar_cliente(nuevo.dni)

    def dar_baja_cliente(self, dni):
        c = self.buscar_cliente(dni)
        if not c or not c.activo:
            raise ValueError(f"Cliente con DNI '{(dni or '').strip()}' no encontrado.")
        if self.repo.tiene_alquiler_activo_cliente(c.dni):
            raise ValueError(f"'{c.nombre}' tiene un alquiler activo: debe devolverse antes de la baja.")
        self.repo.desactivar_cliente(c.dni)
        return c

    # -- alquileres --
    def alquilar_vehiculo(self, patente, dni, dias, fecha_inicio=None):
        v = self.buscar_vehiculo(patente)
        if not v or not v.activo:
            raise ValueError(f"Vehiculo '{(patente or '').strip().upper()}' no encontrado.")
        c = self.buscar_cliente(dni)
        if not c or not c.activo:
            raise ValueError(f"Cliente con DNI '{(dni or '').strip()}' no encontrado.")
        if not v.esta_disponible():
            raise ValueError(f"El vehiculo '{v.patente}' no esta disponible.")
        if not isinstance(dias, int) or isinstance(dias, bool) or dias <= 0:
            raise ValueError("Los dias deben ser un entero positivo.")
        inicio = fecha_inicio or date.today()
        try:
            nuevo_id = self.repo.insertar_alquiler(
                v.patente, c.dni, inicio.isoformat(), dias, v.tarifa_diaria)
        except sqlite3.IntegrityError:
            raise ValueError(f"El vehiculo '{v.patente}' no esta disponible.")
        return self._alquiler(self.repo.obtener_alquiler(nuevo_id))

    def devolver_vehiculo(self, patente, fecha_devolucion=None):
        """Cierra el alquiler activo. Devuelve (alquiler, costo_final)."""
        v = self.buscar_vehiculo(patente)
        if not v:
            raise ValueError(f"Vehiculo '{(patente or '').strip().upper()}' no encontrado.")
        fila = self.repo.obtener_alquiler_activo(v.patente)
        if not fila:
            raise ValueError(f"'{v.patente}' no tiene alquiler activo.")
        alq = self._alquiler(fila)
        fin = fecha_devolucion or date.today()
        dias = alq.dias_usados(fin)                         # valida fechas
        costo = dias * alq.tarifa_diaria
        self.repo.cerrar_alquiler(alq.id, fin.isoformat(), dias, costo)
        return self._alquiler(self.repo.obtener_alquiler(alq.id)), costo

    def listar_alquileres(self):
        """Alquileres activos."""
        return [self._alquiler(f) for f in self.repo.listar_alquileres_activos()]

    def listar_historial(self):
        """Todos los alquileres (activos y devueltos), del mas reciente al mas antiguo."""
        return [self._alquiler(f) for f in self.repo.listar_historial()]

    # -- reportes --
    def reporte_ingresos(self, desde, hasta):
        """(cantidad de alquileres devueltos, total facturado) con devolucion en [desde, hasta]."""
        if desde > hasta:
            raise ValueError("La fecha 'desde' no puede ser posterior a 'hasta'.")
        return self.repo.ingresos_entre(desde.isoformat(), hasta.isoformat())

    def detalle_ingresos(self, desde, hasta):
        """Alquileres devueltos con devolucion en [desde, hasta] (detalle del reporte)."""
        if desde > hasta:
            raise ValueError("La fecha 'desde' no puede ser posterior a 'hasta'.")
        return [self._alquiler(f) for f in
                self.repo.listar_devueltos_entre(desde.isoformat(), hasta.isoformat())]

    def reporte_mas_alquilados(self, limite=10):
        """[(patente, modelo, cantidad de alquileres, facturado)] de mayor a menor."""
        return [(f["patente"], f["modelo"], f["cantidad"], f["facturado"])
                for f in self.repo.ranking_vehiculos(limite)]
