"""Prueba de humo de la interfaz grafica: recorre las paginas y simula acciones.

Necesita un entorno grafico (en Linux sin pantalla: `xvfb-run -a python -m unittest ...`).
Si no hay pantalla disponible, la prueba se omite.
Usa una base temporal: no toca autorent.db.
"""
import os
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock

try:
    import customtkinter  # noqa: F401
    import tkinter
except ImportError:                                   # pragma: no cover
    raise unittest.SkipTest("customtkinter/tkinter no disponible")

from modelo import formatear_fecha


class TestInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.patch = mock.patch("tkinter.messagebox.askyesno", return_value=True)
        cls.patch.start()
        import main
        try:
            cls.app = main.App(ruta_db=os.path.join(cls.tmp.name, "gui.db"))
        except tkinter.TclError as e:                  # sin pantalla
            cls.patch.stop()
            cls.tmp.cleanup()
            raise unittest.SkipTest(f"sin entorno grafico: {e}")
        cls.app.update()
        cls.P = cls.app._pages

    @classmethod
    def tearDownClass(cls):
        cls.app._cerrar()
        cls.patch.stop()
        cls.tmp.cleanup()

    # utilidades
    @staticmethod
    def filas(page):
        return [list(r) for r in page.table._rows]

    @staticmethod
    def msg(page):
        return page.lbl.cget("text")

    def test_01_vehiculos(self):
        self.app._show("vehiculos")
        pv = self.P["vehiculos"]
        self.assertEqual(len(self.filas(pv)), 3)                      # demo
        pv.v_pat.set("qwe123"); pv.v_mod.set("Fiat Cronos"); pv.v_tar.set("4500.5")
        pv._registrar()
        self.assertIn("registrado", self.msg(pv))
        self.assertEqual(len(self.filas(pv)), 4)
        pv.v_pat.set("QWE123"); pv.v_mod.set("Fiat Cronos"); pv.v_tar.set("abc"); pv._registrar()
        self.assertIn("Tarifa invalida", self.msg(pv))
        pv.v_tar.set("4500"); pv._registrar()
        self.assertIn("Ya existe", self.msg(pv))
        pv._seleccionar(["QWE123", "", "", ""])
        self.assertEqual(pv.v_tar.get(), "4500.5")
        pv.v_tar.set("5000"); pv._guardar()
        self.assertIn("actualizado", self.msg(pv))
        self.assertTrue(any(r[0] == "QWE123" and r[2] == "$5,000.00" for r in self.filas(pv)))

    def test_02_clientes(self):
        self.app._show("clientes")
        pc = self.P["clientes"]
        pc.v_dni.set("11222333"); pc.v_nom.set("Lucia Perez"); pc._registrar()
        self.assertIn("registrado", self.msg(pc))
        pc.v_dni.set("11222333"); pc.v_nom.set("Lucia P. Diaz"); pc._guardar()
        self.assertIn("actualizado", self.msg(pc))

    def test_03_alquilar_y_devolver(self):
        self.app._show("alquilar")
        pa = self.P["alquilar"]
        self.assertEqual(pa.v_ini.get(), formatear_fecha(date.today()))
        pa.v_pat.set("ABC123"); pa.v_dni.set("11222333"); pa.v_dias.set("3")
        pa.v_ini.set(formatear_fecha(date.today() - timedelta(days=4)))
        pa._alquilar()
        self.assertIn("Alquiler OK", self.msg(pa))
        pa.v_pat.set("ABC123"); pa.v_dni.set("11222333"); pa.v_dias.set("3"); pa._alquilar()
        self.assertIn("no esta disponible", self.msg(pa))
        pa.v_pat.set("MNP456"); pa.v_dias.set("x"); pa._alquilar()
        self.assertIn("Dias invalidos", self.msg(pa))
        pa.v_dias.set("2"); pa.v_ini.set("31/02/2026"); pa._alquilar()
        self.assertIn("Fecha invalida", self.msg(pa))

        self.app._show("devolver")
        pd = self.P["devolver"]
        self.assertEqual(len(self.filas(pd)), 2)
        pd.v_pat.set("ABC123"); pd.v_fin.set("01/01/2020"); pd._devolver()
        self.assertIn("anterior", self.msg(pd))
        pd.v_fin.set(formatear_fecha(date.today())); pd._devolver()
        self.assertIn("4 dias reales", self.msg(pd))
        self.assertIn("$20,000.00", self.msg(pd))

    def test_04_historial_y_reportes(self):
        self.app._show("historial")
        self.assertEqual(len(self.filas(self.P["historial"])), 2)
        self.app._show("reportes")
        pr = self.P["reportes"]
        self.assertIn("activos", pr.lbl.cget("text"))
        pr._mostrar("ingresos")
        self.assertIn("$20,000.00", pr.lbl.cget("text"))
        pr.v_desde.set("10/10/2026"); pr.v_hasta.set("01/10/2026"); pr._consultar_ingresos()
        self.assertIn("posterior", pr.lbl.cget("text"))
        pr._mostrar("ranking")
        self.assertGreaterEqual(len(pr.tablas["ranking"]._rows), 1)

    def test_05_bajas(self):
        self.app._show("vehiculos")
        pv = self.P["vehiculos"]
        pv.v_pat.set("XYZ789"); pv._baja()
        self.assertIn("alquiler activo", self.msg(pv))
        pv.v_pat.set("MNP456"); pv._baja()
        self.assertIn("dado de baja", self.msg(pv))
        self.assertFalse(any(r[0] == "MNP456" for r in self.filas(pv)))
        self.app._show("clientes")
        pc = self.P["clientes"]
        pc.v_dni.set("30123456"); pc._baja()
        self.assertIn("alquiler activo", self.msg(pc))


if __name__ == "__main__":
    unittest.main()
