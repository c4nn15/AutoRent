"""Pruebas unitarias de AutoRent (modelo, logica de negocio y persistencia).

Ejecutar desde la carpeta del proyecto:
    python -m unittest discover -s tests -t . -v
"""
import os
import sqlite3
import tempfile
import unittest
from datetime import date

from db import conectar
from modelo import (Agencia, Alquiler, Cliente, Vehiculo, formatear_fecha,
                    parsear_fecha)
from repositorio import Repositorio


def nueva_agencia():
    return Agencia(Repositorio(conectar(":memory:")))


class AgenciaBase(unittest.TestCase):
    def setUp(self):
        self.ag = nueva_agencia()
        self.ag.registrar_vehiculo("abc123", "Toyota Corolla", 5000)
        self.ag.registrar_cliente("30123456", "Ana Garcia")


class TestEntidades(unittest.TestCase):
    def test_vehiculo_normaliza_patente(self):
        v = Vehiculo("  abc123 ", " Corolla ", 100)
        self.assertEqual(v.patente, "ABC123")
        self.assertEqual(v.modelo, "Corolla")

    def test_vehiculo_valida_campos(self):
        for args in [("", "X", 1), ("  ", "X", 1), ("A", "", 1), ("A", "X", 0), ("A", "X", -5)]:
            with self.assertRaises(ValueError, msg=str(args)):
                Vehiculo(*args)

    def test_cliente_valida_campos(self):
        with self.assertRaises(ValueError):
            Cliente("", "Ana")
        with self.assertRaises(ValueError):
            Cliente("1", "  ")

    def test_alquiler_valida_dias(self):
        v, c = Vehiculo("A", "X", 10), Cliente("1", "Ana")
        for dias in (0, -1, "3", 2.5):
            with self.assertRaises(ValueError, msg=str(dias)):
                Alquiler(v, c, date(2026, 1, 1), dias, 10)

    def test_fechas(self):
        self.assertEqual(parsear_fecha("05/11/2026"), date(2026, 11, 5))
        self.assertEqual(formatear_fecha(date(2026, 11, 5)), "05/11/2026")
        for malo in ("", "2026-11-05", "31/02/2026", "abc", None):
            with self.assertRaises(ValueError, msg=str(malo)):
                parsear_fecha(malo)


class TestVehiculosClientes(AgenciaBase):
    def test_registrar_y_listar(self):
        self.assertEqual([v.patente for v in self.ag.listar_vehiculos()], ["ABC123"])
        self.assertEqual([c.dni for c in self.ag.listar_clientes()], ["30123456"])

    def test_duplicados(self):
        with self.assertRaises(ValueError):
            self.ag.registrar_vehiculo(" ABC123 ", "Otro", 1)
        with self.assertRaises(ValueError):
            self.ag.registrar_cliente("30123456", "Otra")

    def test_modificar_vehiculo_y_cliente(self):
        v = self.ag.modificar_vehiculo("abc123", "Corolla XEi", 5500)
        self.assertEqual((v.modelo, v.tarifa_diaria), ("Corolla XEi", 5500.0))
        c = self.ag.modificar_cliente("30123456", "Ana G. Perez")
        self.assertEqual(c.nombre, "Ana G. Perez")

    def test_modificar_inexistente(self):
        with self.assertRaises(ValueError):
            self.ag.modificar_vehiculo("ZZZ999", "X", 1)
        with self.assertRaises(ValueError):
            self.ag.modificar_cliente("999", "X")

    def test_modificar_con_datos_invalidos_no_cambia(self):
        with self.assertRaises(ValueError):
            self.ag.modificar_vehiculo("ABC123", "", 100)
        self.assertEqual(self.ag.buscar_vehiculo("ABC123").modelo, "Toyota Corolla")

    def test_baja_logica_oculta_pero_conserva(self):
        self.ag.dar_baja_vehiculo("ABC123")
        self.assertEqual(self.ag.listar_vehiculos(), [])
        todos = self.ag.listar_vehiculos(solo_activos=False)
        self.assertEqual(todos[0].estado, "inactivo")
        self.ag.dar_baja_cliente("30123456")
        self.assertEqual(self.ag.listar_clientes(), [])
        self.assertEqual(len(self.ag.listar_clientes(solo_activos=False)), 1)

    def test_baja_inexistente_o_repetida(self):
        with self.assertRaises(ValueError):
            self.ag.dar_baja_vehiculo("ZZZ999")
        self.ag.dar_baja_vehiculo("ABC123")
        with self.assertRaises(ValueError):
            self.ag.dar_baja_vehiculo("ABC123")

    def test_registrar_reactiva_dado_de_baja(self):
        self.ag.dar_baja_vehiculo("ABC123")
        v = self.ag.registrar_vehiculo("ABC123", "Corolla nuevo", 6000)
        self.assertTrue(v.activo)
        self.assertEqual((v.modelo, v.tarifa_diaria), ("Corolla nuevo", 6000.0))
        self.ag.dar_baja_cliente("30123456")
        c = self.ag.registrar_cliente("30123456", "Ana Garcia")
        self.assertTrue(c.activo)

    def test_baja_bloqueada_con_alquiler_activo(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 3)
        with self.assertRaises(ValueError):
            self.ag.dar_baja_vehiculo("ABC123")
        with self.assertRaises(ValueError):
            self.ag.dar_baja_cliente("30123456")
        self.ag.devolver_vehiculo("ABC123")
        self.ag.dar_baja_vehiculo("ABC123")        # ahora si


class TestAlquilar(AgenciaBase):
    def test_alquiler_ok(self):
        a = self.ag.alquilar_vehiculo("abc123", "30123456", 4, date(2026, 11, 1))
        self.assertTrue(a.activo)
        self.assertEqual(a.vehiculo.estado, "alquilado")
        self.assertEqual(a.fecha_prevista_devolucion, date(2026, 11, 5))
        self.assertEqual(a.costo_estimado, 20000.0)
        self.assertEqual(len(self.ag.listar_alquileres()), 1)

    def test_fecha_por_defecto_es_hoy(self):
        a = self.ag.alquilar_vehiculo("ABC123", "30123456", 1)
        self.assertEqual(a.fecha_inicio, date.today())

    def test_inexistentes(self):
        with self.assertRaises(ValueError):
            self.ag.alquilar_vehiculo("ZZZ999", "30123456", 1)
        with self.assertRaises(ValueError):
            self.ag.alquilar_vehiculo("ABC123", "999", 1)

    def test_dado_de_baja_no_se_alquila(self):
        self.ag.dar_baja_vehiculo("ABC123")
        with self.assertRaises(ValueError):
            self.ag.alquilar_vehiculo("ABC123", "30123456", 1)

    def test_cliente_dado_de_baja_no_alquila(self):
        self.ag.dar_baja_cliente("30123456")
        with self.assertRaises(ValueError):
            self.ag.alquilar_vehiculo("ABC123", "30123456", 1)

    def test_no_disponible(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 2)
        self.ag.registrar_cliente("111", "Otro")
        with self.assertRaises(ValueError):
            self.ag.alquilar_vehiculo("ABC123", "111", 2)

    def test_dias_invalidos(self):
        for dias in (0, -3, "2", 1.5, True):
            with self.assertRaises(ValueError, msg=str(dias)):
                self.ag.alquilar_vehiculo("ABC123", "30123456", dias)
        self.assertEqual(self.ag.listar_alquileres(), [])

    def test_indice_unico_impide_dos_activos(self):
        repo = self.ag.repo
        repo.insertar_alquiler("ABC123", "30123456", "2026-11-01", 2, 5000)
        with self.assertRaises(sqlite3.IntegrityError):
            repo.insertar_alquiler("ABC123", "30123456", "2026-11-02", 2, 5000)


class TestDevolver(AgenciaBase):
    def test_costo_por_dias_reales(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 3, date(2026, 11, 1))
        alq, costo = self.ag.devolver_vehiculo("ABC123", date(2026, 11, 6))
        self.assertEqual(alq.dias_reales, 5)
        self.assertEqual(costo, 25000.0)
        self.assertEqual(alq.costo_final, 25000.0)
        self.assertFalse(alq.activo)

    def test_devolucion_anticipada(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 7, date(2026, 11, 1))
        _, costo = self.ag.devolver_vehiculo("ABC123", date(2026, 11, 3))
        self.assertEqual(costo, 10000.0)

    def test_minimo_un_dia(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 3, date(2026, 11, 1))
        alq, costo = self.ag.devolver_vehiculo("ABC123", date(2026, 11, 1))
        self.assertEqual((alq.dias_reales, costo), (1, 5000.0))

    def test_devolucion_anterior_al_inicio(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 3, date(2026, 11, 10))
        with self.assertRaises(ValueError):
            self.ag.devolver_vehiculo("ABC123", date(2026, 11, 9))
        self.assertEqual(len(self.ag.listar_alquileres()), 1)      # sigue activo

    def test_sin_alquiler_activo(self):
        with self.assertRaises(ValueError):
            self.ag.devolver_vehiculo("ABC123")
        with self.assertRaises(ValueError):
            self.ag.devolver_vehiculo("ZZZ999")

    def test_vehiculo_vuelve_a_estar_disponible(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 2, date(2026, 11, 1))
        self.ag.devolver_vehiculo("ABC123", date(2026, 11, 2))
        self.assertTrue(self.ag.buscar_vehiculo("ABC123").esta_disponible())
        self.ag.alquilar_vehiculo("ABC123", "30123456", 1, date(2026, 11, 3))   # se puede volver a alquilar

    def test_tarifa_se_congela_al_alquilar(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 2, date(2026, 11, 1))
        self.ag.modificar_vehiculo("ABC123", "Toyota Corolla", 9000)
        _, costo = self.ag.devolver_vehiculo("ABC123", date(2026, 11, 3))
        self.assertEqual(costo, 10000.0)                           # 2 dias a $5000, no $9000

    def test_devolver_no_pisa_dos_veces(self):
        self.ag.alquilar_vehiculo("ABC123", "30123456", 1, date(2026, 11, 1))
        self.ag.devolver_vehiculo("ABC123", date(2026, 11, 2))
        with self.assertRaises(ValueError):
            self.ag.devolver_vehiculo("ABC123", date(2026, 11, 3))


class TestHistorialYReportes(AgenciaBase):
    def setUp(self):
        super().setUp()
        self.ag.registrar_vehiculo("XYZ789", "Ford Ranger", 8000)
        self.ag.registrar_cliente("25987654", "Martin Lopez")
        # ABC123: 2 alquileres devueltos; XYZ789: 1 devuelto + 1 activo
        self.ag.alquilar_vehiculo("ABC123", "30123456", 2, date(2026, 10, 1))
        self.ag.devolver_vehiculo("ABC123", date(2026, 10, 3))      # 2 d x 5000 = 10000
        self.ag.alquilar_vehiculo("ABC123", "25987654", 1, date(2026, 10, 10))
        self.ag.devolver_vehiculo("ABC123", date(2026, 10, 11))     # 1 d x 5000 = 5000
        self.ag.alquilar_vehiculo("XYZ789", "30123456", 3, date(2026, 10, 15))
        self.ag.devolver_vehiculo("XYZ789", date(2026, 10, 18))     # 3 d x 8000 = 24000
        self.ag.alquilar_vehiculo("XYZ789", "25987654", 2, date(2026, 11, 2))   # activo

    def test_historial_incluye_todo_y_ordena_reciente_primero(self):
        h = self.ag.listar_historial()
        self.assertEqual(len(h), 4)
        self.assertEqual([a.fecha_inicio for a in h], sorted((a.fecha_inicio for a in h), reverse=True))
        self.assertTrue(h[0].activo)

    def test_activos(self):
        self.assertEqual([a.vehiculo.patente for a in self.ag.listar_alquileres()], ["XYZ789"])

    def test_historial_conserva_datos_tras_baja_de_cliente(self):
        self.ag.devolver_vehiculo("XYZ789", date(2026, 11, 4))
        self.ag.dar_baja_cliente("25987654")
        nombres = {a.cliente.nombre for a in self.ag.listar_historial()}
        self.assertIn("Martin Lopez", nombres)

    def test_ingresos_en_rango(self):
        n, total = self.ag.reporte_ingresos(date(2026, 10, 1), date(2026, 10, 31))
        self.assertEqual((n, total), (3, 39000.0))
        n, total = self.ag.reporte_ingresos(date(2026, 10, 1), date(2026, 10, 11))
        self.assertEqual((n, total), (2, 15000.0))

    def test_ingresos_limites_inclusivos(self):
        n, total = self.ag.reporte_ingresos(date(2026, 10, 3), date(2026, 10, 3))
        self.assertEqual((n, total), (1, 10000.0))

    def test_detalle_ingresos_coincide_con_totales(self):
        det = self.ag.detalle_ingresos(date(2026, 10, 1), date(2026, 10, 31))
        self.assertEqual(len(det), 3)
        self.assertEqual(sum(a.costo_final for a in det), 39000.0)
        self.assertTrue(all(not a.activo for a in det))
        with self.assertRaises(ValueError):
            self.ag.detalle_ingresos(date(2026, 11, 1), date(2026, 10, 1))

    def test_ingresos_sin_datos_o_rango_invalido(self):
        self.assertEqual(self.ag.reporte_ingresos(date(2025, 1, 1), date(2025, 12, 31)), (0, 0))
        with self.assertRaises(ValueError):
            self.ag.reporte_ingresos(date(2026, 11, 1), date(2026, 10, 1))

    def test_ranking(self):
        r = self.ag.reporte_mas_alquilados()
        self.assertEqual([(p, c) for p, _, c, _ in r], [("ABC123", 2), ("XYZ789", 2)])
        r1 = self.ag.reporte_mas_alquilados(limite=1)
        self.assertEqual(len(r1), 1)
        facturado = {p: f for p, _, _, f in r}
        self.assertEqual(facturado, {"ABC123": 15000.0, "XYZ789": 24000.0})


class TestPersistencia(unittest.TestCase):
    def test_los_datos_sobreviven_al_reabrir_la_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "autorent_test.db")
            conn = conectar(ruta)
            ag = Agencia(Repositorio(conn))
            ag.registrar_vehiculo("ABC123", "Corolla", 5000)
            ag.registrar_cliente("1", "Ana")
            ag.alquilar_vehiculo("ABC123", "1", 2, date(2026, 11, 1))
            conn.close()

            conn2 = conectar(ruta)
            ag2 = Agencia(Repositorio(conn2))
            self.assertEqual(len(ag2.listar_vehiculos()), 1)
            self.assertEqual(len(ag2.listar_alquileres()), 1)
            self.assertFalse(ag2.buscar_vehiculo("ABC123").esta_disponible())
            ag2.devolver_vehiculo("ABC123", date(2026, 11, 3))
            conn2.close()

    def test_conectar_es_idempotente(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "x.db")
            conectar(ruta).close()
            conectar(ruta).close()          # no falla si el esquema ya existe


if __name__ == "__main__":
    unittest.main()
