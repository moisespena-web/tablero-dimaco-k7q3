# Regla "todo igual" (Moisés, 11-oct-2026)

> "Lo que se hace en los tableros, se hace en tabletas y archivos, es decir en todo."

Cualquier cambio de contenido, orden, color o leyenda en la TV se aplica en el mismo cambio a:
las 5 tabletas (herramientas/estaciones_mafesa/plantilla.html + gen.py), el PDF, el widget y el Excel de
MO en proceso (vía herramientas/pz6oct/parche_*.py), las hojas de avance (herramientas/hojas_avance.py)
y la copia de la TV en el artifact de Claude.

## Colores por estación (11-oct-2026)
| Estación | Pantalla (fondo oscuro) | Papel (fondo blanco) |
|---|---|---|
| Corte | #5AB0FF | #1F6FD1 |
| Taladro | #B79CFF | #6E4BD8 |
| TM-2P | #FF7EB6 | #D6337F |
| Doblez | #C9E24F | #6F8C00 |
| Limpieza & SQA | #3FD9D9 | #0E9C9C |

- El nombre de cada estación va siempre en su color; la rayita de cada MO = color de la estación donde está (verde si ya terminó todo).
- Ya no hay TIPOS (Corte → estaciones → Limpieza & SQA lo sabe todo mundo). Solo queda la nota de COBRE.
- La TV lleva la franja de flujo: por estación MOs, piezas en espera, % de avance, alertas (vencidas, CU) y "MÁS ATRASADA".
- La TV tiene ◀ ⏸ ▶ (pausa se quita sola a los 5 min).
