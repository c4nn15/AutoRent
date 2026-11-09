# Herramientas utilizadas — AutoRent

Los lineamientos de la materia permiten usar IA ("uso, no abuso") declarando las herramientas.
**Borrador:** revisar cada fila y corregir con lo que realmente se usó.

## Herramientas de desarrollo
| Herramienta | Para qué se usó | Partes del proyecto |
|---|---|---|
| Python 3.10+ (probado con 3.12 y 3.13) | Lenguaje | Todo el producto |
| CustomTkinter | Interfaz gráfica de escritorio | `ui.py`, `componentes.py`, `main.py` |
| SQLite (módulo `sqlite3`) | Base de datos local | `db.py`, `repositorio.py` |
| `unittest` | Pruebas automatizadas | `tests/` |
| Git y GitHub | Control de versiones y repositorio | Todo el proyecto |
| Mermaid | Diagramas UML en Markdown | `doc/uml_*.md`, `doc/modelo_datos.md` |
| Visual Studio Code | Entorno de desarrollo | Todo el código |

## Inteligencia artificial
| Herramienta | Para qué se usó | Partes del proyecto | Cómo se verificó |
|---|---|---|---|
| Claude (Anthropic) | Interpretar los lineamientos; redactar la ficha de propuesta | Ficha de propuesta | Revisión y ajustes propios |
| Claude Code (extensión de VS Code) | Desarrollar la capa de datos, la lógica y la interfaz; escribir pruebas y documentación; preparar el repositorio | `db.py`, `repositorio.py`, `modelo.py`, `ui.py`, `tests/`, `doc/`, `scripts/` | Ejecución de las 45 pruebas (`doc/resultados_pruebas.txt`), prueba de la interfaz y revisión del código |

## Qué decidió el autor y qué hizo la IA
*(Completar con tus palabras; es lo que más pesa en la declaración.)*

- **Decisiones del autor:** el tema y el alcance del proyecto; las reglas de negocio (costo por días reales
  con mínimo de 1, tarifa congelada al alquilar, fechas editables, bajas lógicas bloqueadas con alquiler
  activo, reactivación al volver a registrar, los tres reportes).
- **Trabajo asistido por IA:** escritura de código, pruebas y documentación a partir de esas decisiones.
- **Verificación del autor:** *completar* (pruebas manuales M1–M5, lectura y comprensión del código, etc.).

> Debe poder explicarse todo el código en la muestra en vivo; ver `doc/guia_estudio.md`.
