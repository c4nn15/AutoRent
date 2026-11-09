"""Paginas de la interfaz grafica de AutoRent."""
from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from componentes import (ACCENT, ACCENT_H, BG, CARD, DANGER, DANGER_H, FG, FG2,
                         FG3, FONT_BOLD, FONT_NAV, FONT_SMALL, PANEL, Table,
                         mk_btn, mk_field, msg_label, section_title, set_msg)
from modelo import formatear_fecha, hoy_str, parsear_fecha

NEUTRO, NEUTRO_H = "#3A3D41", "#4A4D52"


def money(valor):
    return f"${valor:,.2f}"


def card(parent, titulo):
    """Tarjeta con titulo. Devuelve el frame interior donde van los campos."""
    frm = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=10)
    frm.pack(fill="x", padx=20, pady=(20, 10))
    inner = ctk.CTkFrame(frm, fg_color="transparent")
    inner.pack(fill="x", padx=20, pady=16)
    section_title(inner, titulo)
    return inner


def fila(parent):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", pady=4)
    return f


def barra_botones(parent, pady=(14, 0)):
    b = ctk.CTkFrame(parent, fg_color="transparent")
    b.pack(anchor="w", pady=pady)
    return b


def zona_tabla(parent, titulo, columnas):
    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    wrap.pack(fill="both", expand=True, padx=20, pady=4)
    ctk.CTkLabel(wrap, text=titulo, font=FONT_SMALL,
                 text_color=FG2).pack(anchor="w", pady=(0, 4))
    tabla = Table(wrap, columnas)
    tabla.pack(fill="both", expand=True)
    return tabla


def tip(parent, texto):
    ctk.CTkLabel(parent, text=texto, font=FONT_SMALL,
                 text_color=FG3).pack(anchor="w", pady=(8, 0))


class BasePage(ctk.CTkFrame):
    def __init__(self, master, agencia):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.agencia = agencia

    def on_show(self):
        pass


# ----------------------------------------------------------------------
class PageVehiculos(BasePage):
    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._por_patente = {}
        self._build()

    def _build(self):
        inner = card(self, "Vehiculos")
        self.v_pat = ctk.StringVar()
        self.v_mod = ctk.StringVar()
        self.v_tar = ctk.StringVar()

        row = fila(inner)
        mk_field(row, "PATENTE", self.v_pat, mono=True, w=140).pack(side="left", padx=(0, 16))
        mk_field(row, "MODELO", self.v_mod, w=240).pack(side="left", padx=(0, 16))
        mk_field(row, "TARIFA / DIA ($)", self.v_tar, w=140).pack(side="left")

        bot = barra_botones(inner)
        mk_btn(bot, "+ Registrar", self._registrar, w=130).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Guardar cambios", self._guardar, color=NEUTRO, hover=NEUTRO_H,
               text_color=FG, w=150).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Dar de baja", self._baja, color=DANGER, hover=DANGER_H,
               text_color=FG, w=120).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Limpiar", self._limpiar, color=NEUTRO, hover=NEUTRO_H,
               text_color=FG, w=90).pack(side="left")
        tip(inner, "Hace clic en un vehiculo de la tabla para editarlo o darlo de baja.")
        self.lbl = msg_label(inner)

        self.table = zona_tabla(self, "Flota registrada", [
            ("PATENTE", 120), ("MODELO", 240), ("TARIFA/DIA", 140), ("ESTADO", 130)])
        self.table.bind_select(self._seleccionar)
        self._reload()

    def _seleccionar(self, row):
        v = self._por_patente.get(row[0])
        if v:
            self.v_pat.set(v.patente)
            self.v_mod.set(v.modelo)
            self.v_tar.set(f"{v.tarifa_diaria:g}")

    def _limpiar(self):
        for var in (self.v_pat, self.v_mod, self.v_tar):
            var.set("")

    def _tarifa(self):
        try:
            return float(self.v_tar.get().strip().replace(",", "."))
        except ValueError:
            raise ValueError("Tarifa invalida.")

    def _registrar(self):
        try:
            v = self.agencia.registrar_vehiculo(self.v_pat.get(), self.v_mod.get(), self._tarifa())
            self._limpiar()
            set_msg(self.lbl, f"Vehiculo '{v.patente}' registrado correctamente.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _guardar(self):
        try:
            v = self.agencia.modificar_vehiculo(self.v_pat.get(), self.v_mod.get(), self._tarifa())
            set_msg(self.lbl, f"Vehiculo '{v.patente}' actualizado.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _baja(self):
        pat = self.v_pat.get().strip().upper()
        if not pat:
            set_msg(self.lbl, "Selecciona un vehiculo o ingresa la patente.", ok=False)
            return
        if not messagebox.askyesno("Dar de baja", f"Dar de baja el vehiculo {pat}?"):
            return
        try:
            self.agencia.dar_baja_vehiculo(pat)
            self._limpiar()
            set_msg(self.lbl, f"Vehiculo '{pat}' dado de baja.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _reload(self):
        vehiculos = self.agencia.listar_vehiculos()
        self._por_patente = {v.patente: v for v in vehiculos}
        self.table.load([(v.patente, v.modelo, money(v.tarifa_diaria), v.estado)
                         for v in vehiculos])

    def on_show(self):
        self._reload()


# ----------------------------------------------------------------------
class PageClientes(BasePage):
    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._build()

    def _build(self):
        inner = card(self, "Clientes")
        self.v_dni = ctk.StringVar()
        self.v_nom = ctk.StringVar()

        row = fila(inner)
        mk_field(row, "DNI", self.v_dni, mono=True, w=160).pack(side="left", padx=(0, 16))
        mk_field(row, "NOMBRE COMPLETO", self.v_nom, w=300).pack(side="left")

        bot = barra_botones(inner)
        mk_btn(bot, "+ Registrar", self._registrar, w=130).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Guardar cambios", self._guardar, color=NEUTRO, hover=NEUTRO_H,
               text_color=FG, w=150).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Dar de baja", self._baja, color=DANGER, hover=DANGER_H,
               text_color=FG, w=120).pack(side="left", padx=(0, 8))
        mk_btn(bot, "Limpiar", self._limpiar, color=NEUTRO, hover=NEUTRO_H,
               text_color=FG, w=90).pack(side="left")
        tip(inner, "Hace clic en un cliente de la tabla para editarlo o darlo de baja.")
        self.lbl = msg_label(inner)

        self.table = zona_tabla(self, "Clientes registrados", [("DNI", 160), ("NOMBRE", 400)])
        self.table.bind_select(lambda row: (self.v_dni.set(row[0]), self.v_nom.set(row[1])))
        self._reload()

    def _limpiar(self):
        self.v_dni.set("")
        self.v_nom.set("")

    def _registrar(self):
        try:
            c = self.agencia.registrar_cliente(self.v_dni.get(), self.v_nom.get())
            self._limpiar()
            set_msg(self.lbl, f"Cliente '{c.nombre}' registrado correctamente.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _guardar(self):
        try:
            c = self.agencia.modificar_cliente(self.v_dni.get(), self.v_nom.get())
            set_msg(self.lbl, f"Cliente '{c.nombre}' actualizado.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _baja(self):
        dni = self.v_dni.get().strip()
        if not dni:
            set_msg(self.lbl, "Selecciona un cliente o ingresa el DNI.", ok=False)
            return
        if not messagebox.askyesno("Dar de baja", f"Dar de baja al cliente con DNI {dni}?"):
            return
        try:
            c = self.agencia.dar_baja_cliente(dni)
            self._limpiar()
            set_msg(self.lbl, f"Cliente '{c.nombre}' dado de baja.")
            self._reload()
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)

    def _reload(self):
        self.table.load([(c.dni, c.nombre) for c in self.agencia.listar_clientes()])

    def on_show(self):
        self._reload()


# ----------------------------------------------------------------------
class PageAlquilar(BasePage):
    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._build()

    def _build(self):
        inner = card(self, "Registrar alquiler")
        self.v_pat = ctk.StringVar()
        self.v_dni = ctk.StringVar()
        self.v_dias = ctk.StringVar()
        self.v_ini = ctk.StringVar(value=hoy_str())

        row = fila(inner)
        mk_field(row, "PATENTE", self.v_pat, mono=True, w=140).pack(side="left", padx=(0, 16))
        mk_field(row, "DNI CLIENTE", self.v_dni, mono=True, w=160).pack(side="left", padx=(0, 16))
        mk_field(row, "DIAS", self.v_dias, w=80).pack(side="left", padx=(0, 16))
        mk_field(row, "FECHA INICIO (dd/mm/aaaa)", self.v_ini, w=170).pack(side="left")

        tip(inner, "Hace clic en un vehiculo o cliente de las tablas para autocompletar.")
        bot = barra_botones(inner, pady=(12, 0))
        mk_btn(bot, "Confirmar alquiler", self._alquilar).pack(side="left")
        self.lbl = msg_label(inner)

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True)
        izq = ctk.CTkFrame(cuerpo, fg_color="transparent")
        izq.pack(side="left", fill="both", expand=True)
        der = ctk.CTkFrame(cuerpo, fg_color="transparent")
        der.pack(side="left", fill="both", expand=True)

        self.t_veh = zona_tabla(izq, "Vehiculos disponibles",
                                [("PATENTE", 80), ("MODELO", 130), ("TARIFA/DIA", 90)])
        self.t_veh.bind_select(lambda row: self.v_pat.set(row[0]))
        self.t_cli = zona_tabla(der, "Clientes", [("DNI", 90), ("NOMBRE", 190)])
        self.t_cli.bind_select(lambda row: self.v_dni.set(row[0]))
        self._reload()

    def _alquilar(self):
        try:
            dias = int(self.v_dias.get().strip())
        except ValueError:
            set_msg(self.lbl, "Dias invalidos (entero positivo).", ok=False)
            return
        try:
            inicio = parsear_fecha(self.v_ini.get())
            a = self.agencia.alquilar_vehiculo(self.v_pat.get(), self.v_dni.get(), dias, inicio)
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)
            return
        self.v_pat.set("")
        self.v_dni.set("")
        self.v_dias.set("")
        self.v_ini.set(hoy_str())
        set_msg(self.lbl,
                f"Alquiler OK  |  {a.vehiculo.patente}  |  {a.cliente.nombre}  |  {a.dias_previstos} dias  |  "
                f"devolucion prevista {formatear_fecha(a.fecha_prevista_devolucion)}  |  "
                f"{money(a.costo_estimado)} estimado")
        self._reload()

    def _reload(self):
        self.t_veh.load([(v.patente, v.modelo, money(v.tarifa_diaria))
                         for v in self.agencia.listar_vehiculos() if v.esta_disponible()])
        self.t_cli.load([(c.dni, c.nombre) for c in self.agencia.listar_clientes()])

    def on_show(self):
        self._reload()


# ----------------------------------------------------------------------
class PageDevolver(BasePage):
    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._build()

    def _build(self):
        inner = card(self, "Procesar devolucion")
        self.v_pat = ctk.StringVar()
        self.v_fin = ctk.StringVar(value=hoy_str())

        row = fila(inner)
        mk_field(row, "PATENTE A DEVOLVER", self.v_pat, mono=True, w=160).pack(side="left", padx=(0, 16))
        mk_field(row, "FECHA DEVOLUCION (dd/mm/aaaa)", self.v_fin, w=200).pack(side="left")

        tip(inner, "Hace clic en la tabla para seleccionar. El costo se calcula con los dias reales usados (minimo 1).")
        bot = barra_botones(inner, pady=(12, 0))
        mk_btn(bot, "Procesar devolucion", self._devolver,
               color=DANGER, hover=DANGER_H, text_color=FG).pack(side="left")
        self.lbl = msg_label(inner)

        self.table = zona_tabla(self, "Alquileres activos  (clic para seleccionar)", [
            ("PATENTE", 85), ("MODELO", 130), ("CLIENTE", 140), ("INICIO", 90),
            ("DIAS PREV.", 80), ("DEV. PREVISTA", 105), ("COSTO EST.", 100)])
        self.table.bind_select(lambda row: self.v_pat.set(row[0]))
        self._reload()

    def _devolver(self):
        try:
            fin = parsear_fecha(self.v_fin.get())
            alq, costo = self.agencia.devolver_vehiculo(self.v_pat.get(), fin)
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)
            return
        self.v_pat.set("")
        self.v_fin.set(hoy_str())
        set_msg(self.lbl,
                f"Devolucion OK  |  {alq.vehiculo.patente}  |  {alq.cliente.nombre}  |  "
                f"{alq.dias_reales} dias reales  |  TOTAL: {money(costo)}")
        self._reload()

    def _reload(self):
        self.table.load([
            (a.vehiculo.patente, a.vehiculo.modelo, a.cliente.nombre,
             formatear_fecha(a.fecha_inicio), a.dias_previstos,
             formatear_fecha(a.fecha_prevista_devolucion), money(a.costo_estimado))
            for a in self.agencia.listar_alquileres()])

    def on_show(self):
        self._reload()


# ----------------------------------------------------------------------
class PageHistorial(BasePage):
    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Historial de alquileres", font=FONT_BOLD,
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(20, 4))
        self.resumen = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=FG2)
        self.resumen.pack(anchor="w", padx=20, pady=(0, 6))
        self.table = zona_tabla(self, "Del mas reciente al mas antiguo", [
            ("PATENTE", 85), ("MODELO", 125), ("CLIENTE", 125), ("INICIO", 85),
            ("DEVOLUCION", 90), ("DIAS", 50), ("COSTO", 95), ("ESTADO", 80)])
        self._reload()

    def _reload(self):
        alquileres = self.agencia.listar_historial()
        filas = []
        for a in alquileres:
            if a.activo:
                filas.append((a.vehiculo.patente, a.vehiculo.modelo, a.cliente.nombre,
                              formatear_fecha(a.fecha_inicio), "-", f"{a.dias_previstos} (prev.)",
                              money(a.costo_estimado) + " est.", "activo"))
            else:
                filas.append((a.vehiculo.patente, a.vehiculo.modelo, a.cliente.nombre,
                              formatear_fecha(a.fecha_inicio), formatear_fecha(a.fecha_devolucion),
                              a.dias_reales, money(a.costo_final), "devuelto"))
        self.table.load(filas)
        activos = sum(1 for a in alquileres if a.activo)
        self.resumen.configure(
            text=f"{len(alquileres)} alquileres en total  |  {activos} activos  |  "
                 f"{len(alquileres) - activos} devueltos")

    def on_show(self):
        self._reload()


# ----------------------------------------------------------------------
class PageReportes(BasePage):
    NOMBRES = [("activos", "Alquileres activos"),
               ("ingresos", "Ingresos por periodo"),
               ("ranking", "Vehiculos mas alquilados")]

    def __init__(self, master, agencia):
        super().__init__(master, agencia)
        self._actual = None
        self._build()

    def _build(self):
        inner = card(self, "Reportes")

        tabs = ctk.CTkFrame(inner, fg_color="transparent")
        tabs.pack(anchor="w")
        self._tabs = {}
        for key, texto in self.NOMBRES:
            b = ctk.CTkButton(tabs, text=texto, font=FONT_NAV, width=190, height=34,
                              corner_radius=6, command=lambda k=key: self._mostrar(k))
            b.pack(side="left", padx=(0, 8))
            self._tabs[key] = b

        # Filtro de fechas (solo para "ingresos")
        hoy = date.today()
        self.v_desde = ctk.StringVar(value=formatear_fecha(hoy.replace(day=1)))
        self.v_hasta = ctk.StringVar(value=formatear_fecha(hoy))
        self.filtro = ctk.CTkFrame(inner, fg_color="transparent")
        mk_field(self.filtro, "DESDE (dd/mm/aaaa)", self.v_desde, w=160).pack(side="left", padx=(0, 16))
        mk_field(self.filtro, "HASTA (dd/mm/aaaa)", self.v_hasta, w=160).pack(side="left", padx=(0, 16))
        mk_btn(self.filtro, "Consultar", self._consultar_ingresos, w=120).pack(side="left", anchor="s")

        self.lbl = msg_label(inner)

        self.tablas = {}
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=4)
        self.tablas["activos"] = Table(wrap, [
            ("PATENTE", 85), ("MODELO", 130), ("CLIENTE", 140), ("INICIO", 90),
            ("DEV. PREVISTA", 105), ("COSTO EST.", 100), ("PLAZO", 80)])
        self.tablas["ingresos"] = Table(wrap, [
            ("PATENTE", 85), ("MODELO", 140), ("CLIENTE", 150), ("INICIO", 90),
            ("DEVOLUCION", 100), ("DIAS", 50), ("COSTO", 100)])
        self.tablas["ranking"] = Table(wrap, [
            ("#", 40), ("PATENTE", 110), ("MODELO", 200), ("ALQUILERES", 110), ("FACTURADO", 130)])
        self._mostrar("activos")

    def _mostrar(self, key):
        self._actual = key
        for k, b in self._tabs.items():
            if k == key:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_H, text_color="#111111")
            else:
                b.configure(fg_color=PANEL, hover_color="#2A2C2E", text_color=FG2)
        for k, t in self.tablas.items():
            t.pack_forget()
        self.tablas[key].pack(fill="both", expand=True)
        if key == "ingresos":
            self.filtro.pack(anchor="w", pady=(12, 0))
        else:
            self.filtro.pack_forget()
        self._refrescar()

    def _refrescar(self):
        self.lbl.configure(text="")
        if self._actual == "activos":
            hoy = date.today()
            activos = self.agencia.listar_alquileres()
            self.tablas["activos"].load([
                (a.vehiculo.patente, a.vehiculo.modelo, a.cliente.nombre,
                 formatear_fecha(a.fecha_inicio), formatear_fecha(a.fecha_prevista_devolucion),
                 money(a.costo_estimado),
                 "vencido" if a.fecha_prevista_devolucion < hoy else "en plazo")
                for a in activos])
            vencidos = sum(1 for a in activos if a.fecha_prevista_devolucion < hoy)
            set_msg(self.lbl, f"{len(activos)} alquileres activos  |  {vencidos} con devolucion vencida")
        elif self._actual == "ingresos":
            self._consultar_ingresos()
        else:
            ranking = self.agencia.reporte_mas_alquilados()
            self.tablas["ranking"].load([(i + 1, p, m, n, money(f))
                                         for i, (p, m, n, f) in enumerate(ranking)])
            set_msg(self.lbl, f"Top {len(ranking)} de vehiculos por cantidad de alquileres")

    def _consultar_ingresos(self):
        try:
            desde = parsear_fecha(self.v_desde.get())
            hasta = parsear_fecha(self.v_hasta.get())
            cantidad, total = self.agencia.reporte_ingresos(desde, hasta)
            detalle = self.agencia.detalle_ingresos(desde, hasta)
        except ValueError as e:
            set_msg(self.lbl, str(e), ok=False)
            return
        self.tablas["ingresos"].load([
            (a.vehiculo.patente, a.vehiculo.modelo, a.cliente.nombre,
             formatear_fecha(a.fecha_inicio), formatear_fecha(a.fecha_devolucion),
             a.dias_reales, money(a.costo_final))
            for a in detalle])
        set_msg(self.lbl, f"{cantidad} alquileres devueltos en el periodo  |  Total facturado: {money(total)}")

    def on_show(self):
        self._refrescar()
