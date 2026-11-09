import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colores personalizados
ACCENT   = "#E8890C"
ACCENT_H = "#F0A030"
DANGER   = "#C0392B"
DANGER_H = "#E74c3C"
SUCCESS  = "#27AE60"
BG       = "#1A1C1E"
PANEL    = "#242628"
CARD     = "#2D2F32"
FG       = "#E8E6E3"
FG2      = "#9A9890"
FG3      = "#6A6865"
ENTRY_BG = "#1E2022"

FONT_TITLE  = ("Georgia",   20, "bold")
FONT_BOLD   = ("Helvetica", 13, "bold")
FONT_LABEL  = ("Helvetica", 12)
FONT_SMALL  = ("Helvetica", 11)
FONT_MONO   = ("Courier",   12, "bold")
FONT_NAV    = ("Helvetica", 13, "bold")
FONT_MICRO  = ("Helvetica",  9, "bold")

def mk_field(parent, label, var, mono=False, w=200):
    """Label + CTkEntry apilados."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(f, text=label, font=FONT_SMALL,
                 text_color=FG2).pack(anchor="w", pady=(0, 2))
    font = FONT_MONO if mono else FONT_LABEL
    ctk.CTkEntry(
        f, textvariable=var,
        font=font, width=w,
        fg_color=ENTRY_BG,
        border_color="#3A3D41",
        text_color=FG,
    ).pack(anchor="w")
    return f


def mk_btn(parent, text, cmd, color=ACCENT, hover=ACCENT_H, w=220,
           text_color="#111111"):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        font=FONT_BOLD,
        fg_color=color, hover_color=hover,
        text_color=text_color,
        width=w, height=36,
        corner_radius=6,
    )


def section_title(parent, text):
    ctk.CTkLabel(parent, text=text, font=FONT_BOLD,
                 text_color=ACCENT).pack(anchor="w", pady=(0, 12))


def msg_label(parent):
    lbl = ctk.CTkLabel(parent, text="", font=FONT_SMALL,
                       text_color=SUCCESS, wraplength=680)
    lbl.pack(anchor="w", pady=(6, 0))
    return lbl


def set_msg(lbl, text, ok=True):
    lbl.configure(text=text, text_color=SUCCESS if ok else DANGER)


class Table(ctk.CTkScrollableFrame):
    """
    Tabla ligera con cabecera fija y filas dibujadas en CTkLabels.
    cols = [(header, weight), ...]   weight = ancho relativo en px
    """

    ROW_H    = 32
    HDR_BG   = PANEL
    ROW_BG   = CARD
    ROW_ALT  = "#272A2D"
    SEL_BG   = "#2D4A6A"

    def __init__(self, parent, cols, **kw):
        super().__init__(parent, fg_color=CARD,
                         scrollbar_button_color=PANEL,
                         scrollbar_button_hover_color=ACCENT, **kw)
        self.cols     = cols
        self._rows    = []      # lista de dicts con los valores
        self._widgets = []      # lista de listas de CTkLabel
        self._sel_idx = None
        self._on_select_cb = None

        self._build_header()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=self.HDR_BG, height=self.ROW_H)
        hdr.pack(fill="x", pady=(0, 2))
        hdr.pack_propagate(False)
        for text, w in self.cols:
            ctk.CTkLabel(hdr, text=text, font=FONT_MICRO,
                         text_color=ACCENT, width=w,
                         anchor="w").pack(side="left", padx=(8, 0))

    def bind_select(self, cb):
        self._on_select_cb = cb

    def load(self, rows):
        """rows = lista de listas/tuplas con valores por columna."""
        # Limpiar filas anteriores
        for widget_row in self._widgets:
            for w in widget_row: w.master.destroy()
        self._widgets.clear()
        self._rows = list(rows)
        self._sel_idx = None

        for i, row in enumerate(self._rows):
            bg = self.ROW_BG if i % 2 == 0 else self.ROW_ALT
            frame = ctk.CTkFrame(self, fg_color=bg, height=self.ROW_H)
            frame.pack(fill="x", pady=1)
            frame.pack_propagate(False)

            lbls = []
            for j, (val, (_, w)) in enumerate(zip(row, self.cols)):
                lbl = ctk.CTkLabel(
                    frame, text=str(val),
                    font=FONT_SMALL, text_color=FG,
                    width=w, anchor="w",
                )
                lbl.pack(side="left", padx=(8, 0))
                lbl.bind("<Button-1>", lambda e, idx=i: self._select(idx))
                frame.bind("<Button-1>", lambda e, idx=i: self._select(idx))
                lbls.append(lbl)

            self._widgets.append(lbls)

    def _select(self, idx):
        # Restaurar color anterior
        if self._sel_idx is not None and self._sel_idx < len(self._widgets):
            bg = self.ROW_BG if self._sel_idx % 2 == 0 else self.ROW_ALT
            self._widgets[self._sel_idx][0].master.configure(fg_color=bg)

        self._sel_idx = idx
        if idx < len(self._widgets):
            self._widgets[idx][0].master.configure(fg_color=self.SEL_BG)

        if self._on_select_cb:
            self._on_select_cb(list(self._rows[idx]))

    def selected_row(self):
        if self._sel_idx is not None:
            return list(self._rows[self._sel_idx])
        return None
