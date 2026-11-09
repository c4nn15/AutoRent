# AutoRent — contexto para Claude Code

Aplicación de escritorio (Python + CustomTkinter + SQLite) para gestionar el alquiler de vehículos de una
agencia. Es el trabajo de **Prácticas de Laboratorio** de la Tecnicatura en Programación de Computadoras
(Universidad de Belgrano). Docente: Mg. Ing. Guillermo Ramiro Maquieira. Autor: Santiago Cannistra Rovati
(trabaja solo).

## Cómo trabajar con Santiago
- Comunicación concisa y directa, en español.
- Si una decisión depende de supuestos del negocio (reglas de alquiler, costos, bajas, etc.), **consultarle antes de implementar**.
- El prototipo original en memoria es el proyecto de **Testing** y vive aparte (`Testing/TP Final/AutoRent-Testing`). No modificarlo desde acá.

## Comandos
```bash
pip install customtkinter
python main.py                                        # ejecutar la app
python -m unittest discover -s tests -t . -v          # todas las pruebas
xvfb-run -a python -m unittest discover -s tests -t . # Linux sin pantalla (incluye la prueba de interfaz)
```
Compatibilidad objetivo: **Python 3.10+**. Las pruebas de interfaz se omiten solas si no hay pantalla.

## Arquitectura (tres capas)
| Archivo | Rol |
|---|---|
| `main.py` | Punto de entrada, ventana y navegación. Carga datos de demo si la base está vacía. |
| `ui.py` | Páginas: Vehículos, Clientes, Alquilar, Devolver, Historial, Reportes. |
| `componentes.py` | Colores, fuentes y widgets reutilizables (`Table`, `mk_field`, `mk_btn`…). Las constantes de estilo viven **solo acá**. |
| `modelo.py` | Entidades (`Vehiculo`, `Cliente`, `Alquiler`) y reglas de negocio (`Agencia`). |
| `repositorio.py` | **Única** capa que escribe SQL. |
| `db.py` | Conexión y esquema SQLite (`autorent.db`, junto al código). |
| `tests/` | `test_agencia.py` (lógica y persistencia) y `test_gui_smoke.py` (interfaz). |
| `doc/` | Guía de uso, UML en Mermaid, modelo de datos, plan de pruebas, bitácora, herramientas y guía de estudio. |
| `scripts/` | `preparar_demo.py`: respaldar, limpiar y restaurar `autorent.db` para la demo. |

La UI llama a `Agencia`; `Agencia` llama a `Repositorio`; solo `Repositorio` ve SQL. Los errores de
negocio se lanzan como `ValueError` con mensaje legible, y la UI los muestra con `set_msg(..., ok=False)`.

## Reglas de negocio ya decididas
- **Costo final** = días reales × tarifa vigente al alquilar. Días reales = devolución − inicio, **mínimo 1**.
- La **tarifa se congela** en `alquileres.tarifa_diaria` al alquilar; cambiarla después no afecta alquileres en curso.
- **Fecha de inicio** editable (por defecto hoy); la de devolución también. Formato en pantalla `dd/mm/aaaa`, en la base ISO.
- **Bajas lógicas** (`activo = 0`); bloqueadas si hay alquiler activo. Registrar de nuevo una patente o DNI dado de baja lo **reactiva**.
- **Alquiler activo** = `fecha_devolucion IS NULL`. El estado "alquilado" se deduce, no se guarda.
- Un índice único parcial impide dos alquileres activos del mismo vehículo.
- Reportes: alquileres activos (marca vencidos), ingresos por período (según fecha de devolución, límites inclusivos) y ranking de vehículos.

## Convenciones
- Los textos de la interfaz están **sin tildes** (estilo del prototipo); la documentación sí lleva tildes.
- Al agregar una regla: primero en `modelo.py` con su prueba en `tests/test_agencia.py`, después en la UI.
- Actualizar `README.md` (requerimientos) y `doc/` (UML, modelo de datos, plan de pruebas) cuando cambie el comportamiento.
- No commitear `autorent.db`, `respaldos/` ni `presentaciones/` (están en `.gitignore`).

## Estado actual
- App completa y funcional con persistencia SQLite; 45 pruebas pasando (40 de lógica y 5 de interfaz).
- La interfaz se verificó en pantalla virtual de Linux; **falta correrla en el equipo de Santiago** y completar M1–M5 en `doc/plan_pruebas.md`.
- Repositorio publicado en GitHub (`c4nn15/AutoRent`, rama `main`) desde el 09/11/2026.
- Pruebas ejecutadas también en macOS (Python 3.13, CustomTkinter 5.2.2): 45 correctas (`doc/resultados_pruebas.txt`).
- Documentos de entrega: `doc/bitacora.md`, `doc/herramientas.md`, `doc/guia_estudio.md`. Utilidad: `scripts/preparar_demo.py` (respaldar / limpiar / restaurar la base).

## Qué pide la materia
**Ficha de propuesta** (Word): ya completada y enviada al docente para su aprobación. Plan de trabajo: octubre a diciembre.
Requisitos de la propuesta: UML, paradigmas vistos en la carrera, interfaz gráfica, base de datos, desarrollo incremental,
pruebas documentadas, guía de instalación y uso, sin hardware especializado.

**Entregables finales:**
1. Ficha técnica (Word).
2. Presentación comercial y técnica (PPT/PDF), con bitácora de avance, herramientas utilizadas y diagramas UML.
3. Repositorio con `README.md` técnico.
4. Demo pre-grabada y muestra en vivo del software funcionando.

**Reglas:** Full Stack es lo esperado por defecto; la nube es opcional pero recomendada; se puede usar IA ("uso, no abuso")
**declarando las herramientas utilizadas**. Final previsto: **17/12/2026** (alternativas: 26/11/2026 y 11/02/2027).
Rúbrica: No cumple (<4), Cumple (4–7), Destacado (8–10).

## Pendientes
- [ ] Probar en el equipo de Santiago y completar las pruebas manuales M1–M5.
- [x] Primer commit del repositorio.
- [ ] Respuesta del docente sobre: reutilizar el prototipo previo y si una app de escritorio con base local cuenta como Full Stack.
- [ ] Presentación comercial y técnica.
- [ ] Bitácora de avance (borrador en `doc/bitacora.md`; completar y mantener).
- [ ] Lista de herramientas utilizadas, incluida la IA (borrador en `doc/herramientas.md`; revisar).
- [ ] Demo pre-grabada.
- [ ] Opcionales: empaquetar con PyInstaller (genera ejecutable para el sistema donde se compila), migrar la base a la nube (solo cambia `repositorio.py` y `db.py`).
