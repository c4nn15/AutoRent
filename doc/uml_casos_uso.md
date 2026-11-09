# Diagrama de Casos de Uso — AutoRent

```mermaid
flowchart TD
    Actor["👤 Empleado de Agencia"]

    Actor --> CU1["Registrar / modificar / dar de baja Vehículo"]
    Actor --> CU2["Registrar / modificar / dar de baja Cliente"]
    Actor --> CU3["Alquilar Vehículo"]
    Actor --> CU4["Devolver Vehículo"]
    Actor --> CU5["Listar Vehículos y Clientes"]
    Actor --> CU6["Consultar Historial de Alquileres"]
    Actor --> CU7["Consultar Reportes"]

    CU3 --> CU3a["Validar disponibilidad"]
    CU3 --> CU3b["Calcular costo estimado"]
    CU4 --> CU4a["Calcular días reales y costo final"]
    CU4 --> CU4b["Liberar vehículo"]
    CU1 --> CU1a["Validar que no tenga alquiler activo (baja)"]
    CU2 --> CU2a["Validar que no tenga alquiler activo (baja)"]
    CU7 --> CU7a["Alquileres activos"]
    CU7 --> CU7b["Ingresos por período"]
    CU7 --> CU7c["Vehículos más alquilados"]
```
