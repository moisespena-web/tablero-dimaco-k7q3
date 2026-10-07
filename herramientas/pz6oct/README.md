# Regla de piezas del 6-oct-2026 (Moisés)

En piso, TV, PDF, widget y Excel las piezas de una MO se muestran como:

**FALTAN X** (en la estación actual) · **de TOTAL** (planeadas de la MO), con una barra que siempre suma el total:

- verde = entregadas (`completed_quantity` de Katana)
- azul = listas → siguiente estación (hechas en la estación actual; notas "x/y" − entregadas)
- gris = faltan en la estación

Ejemplo MO-366 (182 pz): 30 entregadas + 85 listas → Limpieza + 67 faltan en TM-2P.
Si ya hay piezas hechas, el estado dice EN PROCESO aunque la tablet diga NO INICIADA.

| Pieza | Qué hace |
|---|---|
| `pz6.py` | La lógica en Python (igual a `pzMO()` de la TV y `barraPz()` de las estaciones). |
| `parche_reportes.py DIR` | Parcha en DIR los scripts escritos desde los skills: `build_entregas.py` (agrega `plan` y `entr` a cada row), `build_pdf_entregas.py`, `build_widget_entregas.py`, `build_xlsx_mo.py`, `build_pdf_racks.py`, `build_widget_racks.py`. Correrlo SIEMPRE justo después de escribirlos y antes de usarlos. Idempotente. Si falla, no publicar reportes a medias y avisar. |
| `enriquecer_tv.py` | Respaldo: agrega `plan`/`entr` a un `tv_datos.json` ya armado, desde los JSON de MOs de Katana. |
| `patch_tv.py`, `patch_est.py` | Los cambios ya aplicados al `index.html` de la TV y a las 10 estaciones (idempotentes; sirven para la copia artifact de la TV). |

Estaciones: cada entrada de datos debe traer `entregadas` (= `completed_quantity`) y su `ruta`; sin `entregadas` la app lo deduce del `datos.json` de la TV.

## 2a parte (6-oct-2026 21:08): barra y leyenda también en PDF y Excel
`parche_reportes.py` ahora también agrega:
- **PDF**: en las MOs con avance, un renglón extra con la leyenda ("1,200 entregadas · 724 listas → Limpieza · 1,576 faltan en Doblez") y la barra (verde oscuro / azul / gris claro: se distingue en B/N).
- **Excel**: columnas O "Avance" (barra de 20 bloques de color, como en las estaciones) y P "Desglose" (la leyenda en texto); el filtro llega hasta P.
- **Widget**: se sigue generando y guardando en Dropbox, pero ya no se le envía a Moisés (pedido del 6-oct-2026).
