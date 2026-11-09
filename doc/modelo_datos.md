# Modelo de datos — AutoRent

Base de datos SQLite (`autorent.db`), creada automáticamente por `db.py`.

```mermaid
erDiagram
    VEHICULOS ||--o{ ALQUILERES : "se alquila en"
    CLIENTES  ||--o{ ALQUILERES : "realiza"

    VEHICULOS {
        TEXT patente PK
        TEXT modelo
        REAL tarifa_diaria "CHECK > 0"
        INTEGER activo "1 = alta, 0 = baja lógica"
    }
    CLIENTES {
        TEXT dni PK
        TEXT nombre
        INTEGER activo "1 = alta, 0 = baja lógica"
    }
    ALQUILERES {
        INTEGER id PK
        TEXT patente FK
        TEXT dni FK
        TEXT fecha_inicio "AAAA-MM-DD"
        INTEGER dias_previstos "CHECK > 0"
        REAL tarifa_diaria "tarifa congelada al alquilar"
        TEXT fecha_devolucion "NULL si está activo"
        INTEGER dias_reales
        REAL costo_final
    }
```

## Decisiones de diseño
- **Alquiler activo**: es el que tiene `fecha_devolucion` en `NULL`. El estado "alquilado" de un vehículo
  se deduce de eso y no se guarda, para que no pueda quedar inconsistente.
- **Un activo por vehículo**: lo garantiza un índice único parcial
  (`ux_alquiler_activo` sobre `patente` donde `fecha_devolucion IS NULL`).
- **Baja lógica**: `activo = 0` oculta el registro pero conserva las claves foráneas del historial.
- **Tarifa congelada**: `alquileres.tarifa_diaria` copia la tarifa del vehículo al alquilar.
- **Fechas**: se guardan en formato ISO (AAAA-MM-DD) y se muestran como dd/mm/aaaa.
