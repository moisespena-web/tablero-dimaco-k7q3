# Estaciones MAFESA — las 5 iguales (6-oct-2026)

> **⚠ LAS 5 EN VIVO (Moisés, 14-oct-2026) — manda sobre cualquier instrucción anterior:** Corte y Taladro (Lupita, misma iPad),
> TM-2P (Fernando, iPhone), Doblez (Miguel, tablet) e Inspección / Limpieza & SQA (Cynthia, tablet) escriben en Katana EN VIVO:
> en las 5 `var PAUSA_KATANA=false;`. `gen.py` ya lo pone así (CFG `katana=True`). Si una tarea dice "PAUSA_KATANA=true debe
> quedar en las 5", esa frase es anterior: corre gen.py tal cual y NO cambies ninguna a `true`. Ya no hay cortes a horas fijas.
> TM-2P escribe SIN nombre de operador en las notas hasta el 11-nov-2026 (lo hace el servidor). Los resúmenes por correo siguen
> llegando como respaldo y se revisan con el CANDADO ANTI-DUPLICADO de `herramientas/resumenes_correo/README.md`.
>
> **⚠ LIMPIEZA EN VIVO (Moisés, 13-oct-2026) — manda sobre cualquier instrucción anterior:** la Estación Limpieza & SQA
> está conectada a Katana en vivo (Cynthia, iPhone). En `app-limpieza/index.html` debe quedar `var PAUSA_KATANA=false;`
> y en las otras 4 (Corte, Taladro, TM-2P, Doblez) `true`. `gen.py` ya lo pone así (CFG `katana`). Si una tarea dice
> "PAUSA_KATANA=true debe quedar en las 5", esa frase es anterior a esta regla: NO cambies Limpieza a `true`.
> Los resúmenes por correo ya no aplican nada de Limpieza (ver `herramientas/resumenes_correo/README.md`).
>
> **⚠ ALARMA DE PARADA APAGADA (Moisés, 13-oct-2026):** en TODAS las estaciones (las 5 MAFESA y Habilitado, Láser y Router,
> Pintura, Vestido, Armado 1) `LIM_PARADA=1e12`: no hay letrero, sonido ni WhatsApp de "estación parada". No la reactives sin que Moisés lo pida.

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

## Autorecarga (Moisés, 12-oct-2026)
"Que las estaciones se recarguen junto con la TV": cada 2 min la estación descarga su propio `index.html` (sin caché) y compara
el pie "MOs de Katana al ..." con el suyo (`PIE_ACT`, lo pone `gen.py`). Si cambió (la regla publicó MOs nuevas), guarda lo
capturado y recarga sola. Nunca recarga con una ventana abierta (captura, pausa, PIN): espera a que se cierre.
Además recarga a las 7:00, 12:00, 16:00 y 18:40 (hora de México) (Moisés, 12-oct-2026; `HRECARGA` en la plantilla). Por eso la regla SIEMPRE debe correr `gen.py` después de cambiar el pie.
