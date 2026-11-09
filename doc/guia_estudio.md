# Guía de estudio — `modelo.py` y `repositorio.py`

Para poder explicar el código con tus propias palabras en la muestra en vivo. Los números de línea
corresponden a la versión actual de cada archivo.

## Idea general
`ui.py` → `Agencia` ([modelo.py](../modelo.py)) → `Repositorio` ([repositorio.py](../repositorio.py)) → SQLite.
Cada capa solo conoce a la de abajo. **Solo `Repositorio` escribe SQL**; `Agencia` decide qué está permitido;
la UI solo muestra y captura datos. Los errores de negocio son `ValueError` con un mensaje legible, y la
UI los muestra en pantalla.

## modelo.py
### Fechas (líneas 9–22)
- En pantalla se usa `dd/mm/aaaa`; en la base, ISO (`AAAA-MM-DD`). Se convierte en el borde:
  `parsear_fecha` / `formatear_fecha`. El formato ISO permite comparar fechas como texto en SQL (`BETWEEN`).

### Entidades (líneas 26–98)
- **`Vehiculo`** y **`Cliente`** validan en el constructor: no se puede crear un objeto inválido.
  La patente se normaliza (`strip().upper()`).
- `Vehiculo.estado` se **deduce**: inactivo / alquilado / disponible. `alquilado` no es una columna.
- **`Alquiler`** guarda la `tarifa_diaria` vigente al alquilar (congelada).
  - `activo` ⇔ `fecha_devolucion is None`.
  - `fecha_prevista_devolucion` = inicio + días previstos; `costo_estimado` = días previstos × tarifa.
  - `dias_usados` = `max(1, (devolución − inicio).days)`; lanza error si la devolución es anterior al inicio.
  - `calcular_costo` = días usados × tarifa congelada.

### Agencia (líneas 102–263)
- `_vehiculo`, `_cliente`, `_alquiler`: convierten filas de la base en objetos.
- **Registrar**: valida con la entidad; si ya existe y está activo → error de duplicado; si existe dado de
  baja → lo **reactiva** (`activo=1`); si no existe → inserta.
- **Modificar**: solo cambia modelo/tarifa (o nombre); la patente y el DNI son la clave y no se tocan.
- **Dar de baja**: baja lógica (`activo = 0`), bloqueada si tiene alquiler activo. Así el historial
  conserva los datos.
- **`alquilar_vehiculo`** (línea 204): comprueba que vehículo y cliente existan y estén activos, que el
  vehículo esté disponible y que los días sean un entero positivo (rechaza `bool`, que en Python es `int`).
  Inserta con la tarifa actual. Si el índice único de la base rechaza la inserción
  (`sqlite3.IntegrityError`), lo traduce al mismo error de "no disponible".
- **`devolver_vehiculo`** (línea 223): busca el alquiler activo, calcula días y costo con la tarifa
  **congelada** y cierra el alquiler. Devuelve `(alquiler, costo)`.
- **Reportes**: ingresos por período (según fecha de devolución, límites inclusivos; rechaza `desde > hasta`),
  detalle y ranking de vehículos.

## repositorio.py
- `_SELECT_VEHICULO` calcula `alquilado` con un `EXISTS` sobre alquileres sin devolución.
- `_SELECT_ALQUILER` une alquiler + vehículo + cliente y trae tanto la tarifa congelada (`a.tarifa_diaria`)
  como la actual (`tarifa_actual`).
- Todas las consultas usan **parámetros `?`** (nunca texto concatenado) → no hay inyección SQL.
- Las escrituras usan `with self.conn:` → transacción: se confirma al terminar o se revierte si falla.
- `ingresos_entre`: `COUNT(*)` y `SUM(costo_final)` de alquileres devueltos con `fecha_devolucion BETWEEN`.
- `ranking_vehiculos`: `GROUP BY patente`, ordenado por cantidad descendente y luego por patente.

## db.py (esquema)
- Claves primarias: `patente` y `dni`. `CHECK (tarifa_diaria > 0)` y `CHECK (dias_previstos > 0)`.
- `PRAGMA foreign_keys = ON` activa las claves foráneas (SQLite las ignora por defecto).
- **Índice único parcial** `ux_alquiler_activo ON alquileres(patente) WHERE fecha_devolucion IS NULL`:
  la propia base impide dos alquileres activos del mismo vehículo, aunque falle la lógica o haya dos
  accesos a la vez.

## Preguntas típicas y cómo responderlas (con tus palabras)
| Pregunta | Idea de respuesta |
|---|---|
| ¿Por qué SQLite? | Sin servidor ni instalación, un solo archivo, viene con Python; alcanza para una agencia en un puesto. Migrar a la nube solo cambia `repositorio.py` y `db.py`. |
| ¿Cómo evitás dos alquileres del mismo vehículo? | Dos defensas: `Agencia` verifica disponibilidad y el índice único parcial lo garantiza en la base. |
| ¿Cómo calculás el costo? | Días reales (devolución − inicio, mínimo 1) × tarifa congelada al alquilar. |
| ¿Por qué se congela la tarifa? | Para que cambiar la tarifa después no altere alquileres en curso ni el historial. |
| ¿Qué pasa al dar de baja un cliente o vehículo? | Baja lógica: se oculta pero se conserva el historial; se bloquea con alquiler activo; si se registra de nuevo, se reactiva. |
| ¿Por qué el estado "alquilado" no se guarda? | Se deduce de si existe un alquiler sin devolución; así no puede quedar desincronizado. |
| ¿Por qué tres capas? | Separar responsabilidades: cambiar la interfaz o la base no obliga a tocar las reglas de negocio. |
| ¿Cómo probaste el sistema? | 45 pruebas automáticas (40 de lógica y 5 de interfaz) más las manuales M1–M5; ver `doc/plan_pruebas.md`. |
| ¿Qué paradigmas usaste? | Orientación a objetos (entidades y `Agencia`), con acceso a datos separado en una capa propia. *(Ajustar a lo visto en la carrera.)* |

## Para practicar
1. Seguí a mano un alquiler: `PageAlquilar` → `Agencia.alquilar_vehiculo` → `Repositorio.insertar_alquiler`.
2. Seguí una devolución tardía (por ejemplo 5 días previstos, devuelto a los 8) y calculá el costo.
3. Explicá qué pasa si dos personas intentan alquilar la misma patente a la vez.
4. Abrí `tests/test_agencia.py` y elegí tres pruebas: qué regla comprueba cada una.
