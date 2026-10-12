# Dibujos de MO nuevas MAFESA (regla 22:00, paso 3c)

Pedido de Moisés (8-oct-2026): cada noche, un PDF reducido (1 hoja; 7 MO por hoja) con las MO de MAFESA
que se abrieron y que todavía no se le han enviado. Por MO: la pieza recortada del plano + el proceso de Katana
en orden (seg/pz, verde = terminada) + lo que muestra el plano. No lleva medidas a detalle: el objetivo es ver la
pieza y revisar si el proceso cargado en Katana es correcto. Se guarda en Dropbox `Dimaco/Mafesa/MO en proceso/`
y se le manda por correo.

- `catalogo.json` — SKU → `desc` (nombre y medida), `plano` (qué muestra: barrenos, ranuras, dobleces),
  `ref` (archivo y vista del plano), `nota` (aviso fijo del plano, opcional) e `imgs` (recortes).
- `recortes/` — PNG en gris, uno o dos por SKU (`<SKU>-1.png`, `<SKU>-2.png` = vista de doblez si aplica).
- `enviadas.json` — MO que ya salieron (no se repiten aunque sigan abiertas). Arranque: las 27 abiertas el 8-oct-2026.
- `dibujos_mo.py armar` / `registrar` — ver el encabezado del script.

## SKU nuevo sin recorte (solo con la iMac encendida)
REGLA (Moisés, 11-oct-2026): los planos de MAFESA se toman SIEMPRE de la carpeta central, sin copiarlos a ningún otro lado
("lo que no quiero es que haya planos por aquí y por allá"):
`/Moises Peña/Carpeta del equipo DIMACO METALMECANICA/MAFESA/Dibujos MAFESA` (en la iMac:
`/Users/moisespena/Library/CloudStorage/Dropbox-Dimaco2022/Moises Peña/Carpeta del equipo DIMACO METALMECANICA/MAFESA/Dibujos MAFESA`).
Un PDF por número de plano (la parte antes del guion del SKU; a veces `AutoVue - _<plano>.dwg.pdf` o `<plano>-REVn.pdf`;
si hay varios, el de revisión más alta).
1. `device_stage_files` del plano DIRECTO de esa carpeta (la tarea debe tenerla entre sus carpetas). NO usar Dropbox `copy`
   ni la carpeta vieja "Dibujos MAFESA (copia)".
2. `pdftoppm -r 300`, mirar la hoja (Read de un PNG a 80 dpi) y ubicar la vista de la parte (número después del guion:
   -0005 = P.5; en planos de tabla, la FIG. que dice su renglón). Si la parte trae vista de doblez aparte, recortarla también como `-2`.
3. Guardar en `recortes/` (gris, máx. 1800 px de ancho), agregar la entrada a `catalogo.json` y revisar el recorte a ojo.
4. Si el SKU está en alguna estación y no tiene dibujo, agregar también a `piezas-extra.js` (vista + renglón de la tabla en
   amarillo) y subir el `?v=` en la plantilla y las 5 estaciones.
Sin iMac: la MO sale con "Sin recorte de plano" y no se registra; vuelve a salir la noche siguiente.
