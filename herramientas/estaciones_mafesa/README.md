# Estaciones MAFESA — las 5 iguales (6-oct-2026)

Pedido de Moisés: Corte, Taladro, TM-2P, Doblez y Limpieza & SQA funcionan igual y en formato teléfono.

- **Base:** la plantilla de teléfono (la más completa: avisos de Moisés, alarma de estación parada con WhatsApp, "lista para…/espera", sonido, pantalla siempre encendida, Faltan X de total con barra).
- **Lo que se tomó de la TM-2P anterior:** cola EN VIVO desde Katana cuando el teléfono está conectado (cada 3 min y al conectar), y elegir operador con PIN (solo TM-2P, donde hay varios operadores; los demás tienen un operador fijo).
- **Avance por proceso** (recuadro de arriba): se lee en vivo del `datos.json` de la TV.

## Archivos
- `plantilla.html` — el código de las 5 (con marcadores `@@...@@`). **Cambios de diseño se hacen aquí** y luego `python3 gen.py`.
- `gen.py` — genera `app-corte`, `app-taladro`, `app-tm2p`, `app-doblez`, `app-limpieza` con su configuración (nombre, operador, textos, alarma, PIN). Conserva los DATOS que tenga cada app y las claves de cada teléfono (no se pierden los lapsos guardados).
- `mk_plantilla.py` + `base_limpieza_6oct.html` — cómo se hizo la plantilla (historia; no hace falta volver a correrlo).

## Datos
Las 5 usan el mismo arreglo `var DATA=[...]` (formato Doblez): `mo, sec, nombre, sku, piezas (planeadas), entregadas (completed_quantity), ent, deadline, prio, paso, recurso, planeado, fuenteT, recursoMal, ruta [[estación, done|prog|none, esActual]], ingSku, ingNombre, ingTot, ingUom, notas, hechas, rowId` (+ `so`, `espera` en Limpieza). TM-2P ya NO usa `mos:[...]`.
La corrida de las 22:00 reemplaza solo `var DATA=[...]` y el texto "MOs de Katana al d-mmm HH:MM" del pie.
