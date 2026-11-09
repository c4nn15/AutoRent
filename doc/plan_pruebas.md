# Plan de pruebas — AutoRent

## Estrategia
- **Pruebas unitarias y de integración** (`tests/test_agencia.py`): ejercitan las entidades, las reglas
  de negocio y la persistencia sobre una base SQLite en memoria o temporal.
- **Prueba de humo de la interfaz** (`tests/test_gui_smoke.py`): abre la aplicación con una base temporal,
  recorre las seis páginas y simula las acciones del usuario (registrar, editar, alquilar, devolver,
  dar de baja, consultar reportes). Se omite sola si no hay entorno gráfico.
- **Pruebas manuales** de interfaz: ver el listado al final.

## Cómo ejecutarlas
```bash
python -m unittest discover -s tests -t . -v
```

## Casos cubiertos
| Área | Casos (RF) | Pruebas |
|---|---|---|
| Entidades | Validación de patente, modelo, tarifa, DNI, nombre y días; normalización de patente; fechas dd/mm/aaaa | RF01, RF03 |
| Vehículos y clientes | Alta, duplicados, modificación, modificación con datos inválidos, inexistentes | RF01, RF02, RF03, RF04 |
| Bajas | Baja lógica oculta pero conserva; bloqueada con alquiler activo; reactivación al registrar de nuevo | RF02, RF04 |
| Alquilar | Alquiler correcto, fecha por defecto, vehículo o cliente inexistente o de baja, vehículo no disponible, días inválidos, índice único | RF05 |
| Devolver | Costo por días reales, devolución anticipada y tardía, mínimo 1 día, fecha anterior al inicio, sin alquiler activo, tarifa congelada, vehículo liberado | RF06 |
| Historial | Incluye activos y devueltos, orden, conserva datos tras una baja | RF08 |
| Reportes | Ingresos por rango (límites inclusivos, sin datos, rango inválido), detalle, ranking | RF09, RF10, RF11 |
| Persistencia | Los datos sobreviven al cerrar y reabrir la base; el esquema se crea de forma idempotente | RNF06 |
| Interfaz | Mensajes de éxito y error en cada formulario, selección en tablas, confirmación de bajas, reportes | RNF02, RNF03, RNF05 |

## Resultados

| Fecha | Entorno | Pruebas | Resultado |
|---|---|---|---|
| 09/11/2026 | Linux, Python 3.12, CustomTkinter 6.0.0, pantalla virtual (xvfb) | 45 (40 de lógica y 5 de interfaz) | 45 correctas, 0 fallas |
| 09/11/2026 | Linux, Python 3.11, sin pantalla | 41 (la prueba de interfaz se omite) | 40 correctas, 1 omitida |

## Pruebas manuales pendientes en el equipo de desarrollo
Completar al ejecutar la aplicación en macOS o Windows.

| # | Verificación | Resultado |
|---|---|---|
| M1 | La aplicación abre y muestra los datos de demo | |
| M2 | Cerrar y volver a abrir conserva lo cargado | |
| M3 | Aspecto y legibilidad de las seis pantallas | |
| M4 | Cuadro de confirmación al dar de baja | |
| M5 | Redimensionar la ventana al tamaño mínimo | |
