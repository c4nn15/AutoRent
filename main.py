"""AutoRent - punto de entrada de la aplicacion."""
from datetime import date, timedelta

import customtkinter as ctk

from componentes import (ACCENT, ACCENT_H, BG, FG, FG2, FG3, FONT_MICRO,
                         FONT_NAV, FONT_SMALL, FONT_TITLE, PANEL)
from db import conectar
from modelo import Agencia
from repositorio import Repositorio
from ui import (PageAlquilar, PageClientes, PageDevolver, PageHistorial,
                PageReportes, PageVehiculos)


def cargar_datos_demo(agencia):
    """Datos de ejemplo, solo en la primera ejecucion (base vacia)."""
    if agencia.listar_vehiculos(solo_activos=False) or agencia.listar_clientes(solo_activos=False):
        return
    agencia.registrar_vehiculo("ABC123", "Toyota Corolla", 5000)
    agencia.registrar_vehiculo("XYZ789", "Ford Ranger", 8500)
    agencia.registrar_vehiculo("MNP456", "Volkswagen Vento", 6200)
    agencia.registrar_cliente("30123456", "Ana Garcia")
    agencia.registrar_cliente("25987654", "Martin Lopez")
    agencia.alquilar_vehiculo("XYZ789", "30123456", 5, date.today() - timedelta(days=2))


class App(ctk.CTk):
    def __init__(self, ruta_db=None):
        super().__init__()
        self.title("AutoRent - Sistema de Alquiler de Vehiculos")
        self.geometry("1040x700")
        self.minsize(920, 620)
        self.configure(fg_color=BG)

        self.conn = conectar(ruta_db) if ruta_db else conectar()
        self.agencia = Agencia(Repositorio(self.conn))
        cargar_datos_demo(self.agencia)
        self._current = None
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _cerrar(self):
        self.conn.close()
        self.destroy()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=PANEL, height=58, corner_radius=0)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="AutoRent", font=FONT_TITLE,
                     text_color=FG).pack(side="left", padx=(24, 10), pady=10)
        ctk.CTkLabel(header, text="Sistema de Alquiler de Vehiculos",
                     font=FONT_SMALL, text_color=FG3).pack(side="left", pady=20)

        # Separador naranja
        ctk.CTkFrame(self, fg_color=ACCENT, height=2, corner_radius=0).pack(side="top", fill="x")

        # Cuerpo
        body = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(body, fg_color=PANEL, width=175, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="MENU", font=FONT_MICRO,
                     text_color=FG3).pack(anchor="w", padx=16, pady=(20, 6))

        # Contenedor de paginas
        self._content = ctk.CTkFrame(body, fg_color=BG, corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)

        self._pages = {
            "vehiculos": PageVehiculos(self._content, self.agencia),
            "clientes":  PageClientes(self._content, self.agencia),
            "alquilar":  PageAlquilar(self._content, self.agencia),
            "devolver":  PageDevolver(self._content, self.agencia),
            "historial": PageHistorial(self._content, self.agencia),
            "reportes":  PageReportes(self._content, self.agencia),
        }

        nav_items = [
            ("vehiculos", "  Vehiculos"),
            ("clientes",  "  Clientes"),
            ("alquilar",  "  Alquilar"),
            ("devolver",  "  Devolver"),
            ("historial", "  Historial"),
            ("reportes",  "  Reportes"),
        ]
        self._nav_btns = {}
        for key, label in nav_items:
            b = ctk.CTkButton(
                sidebar, text=label, font=FONT_NAV,
                fg_color="transparent", text_color=FG2, hover_color="#2A2C2E",
                anchor="w", height=44, corner_radius=0,
                command=lambda k=key: self._show(k),
            )
            b.pack(fill="x")
            self._nav_btns[key] = b

        self._show("vehiculos")

    def _show(self, key):
        if self._current and self._current in self._pages:
            self._pages[self._current].pack_forget()
        self._current = key

        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(fg_color=ACCENT, text_color="#111111", hover_color=ACCENT_H)
            else:
                b.configure(fg_color="transparent", text_color=FG2, hover_color="#2A2C2E")

        page = self._pages[key]
        page.pack(fill="both", expand=True)
        page.on_show()


if __name__ == "__main__":
    App().mainloop()
