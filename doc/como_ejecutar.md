# Guía de instalación y uso — AutoRent

## Requisitos
- Python 3.10 o superior (en Linux puede hacer falta instalar `python3-tk`)
- pip

## Instalación
```bash
pip install customtkinter
```

## Ejecución
Desde la carpeta del proyecto:
```bash
python main.py
```

## Datos y base de datos
- Los datos se guardan en el archivo `autorent.db`, que se crea automáticamente junto al código.
- En la primera ejecución (base vacía) se cargan datos de ejemplo: vehículos ABC123, XYZ789 y MNP456;
  clientes 30123456 (Ana Garcia) y 25987654 (Martin Lopez); y un alquiler activo de XYZ789.
- Para volver al estado inicial, cerrar la aplicación y borrar `autorent.db`.
- Para hacer una copia de seguridad, copiar ese archivo.

## Uso por pantalla
**Vehículos / Clientes**
1. Completar los campos y presionar *Registrar*.
2. Para editar: hacer clic en una fila de la tabla, cambiar los datos y presionar *Guardar cambios*
   (la patente y el DNI no se modifican).
3. *Dar de baja* oculta el registro, pero conserva el historial. No se puede con un alquiler activo.

**Alquilar**
1. Indicar patente, DNI, días y fecha de inicio (por defecto hoy, formato dd/mm/aaaa). Se puede
   autocompletar haciendo clic en las tablas.
2. *Confirmar alquiler*: muestra la devolución prevista y el costo estimado.

**Devolver**
1. Seleccionar el alquiler activo e indicar la fecha de devolución (por defecto hoy).
2. *Procesar devolución*: calcula el costo con los días reales usados (mínimo 1 día).

**Historial**: todos los alquileres, activos y devueltos, del más reciente al más antiguo.

**Reportes**: alquileres activos (con aviso de vencidos), ingresos por período (elegir desde/hasta y
*Consultar*) y ranking de vehículos más alquilados.

## Ejecutar las pruebas
```bash
python -m unittest discover -s tests -t . -v
```
Las pruebas de interfaz necesitan entorno gráfico; sin pantalla se omiten solas. En Linux sin
escritorio: `xvfb-run -a python -m unittest discover -s tests -t . -v`.
