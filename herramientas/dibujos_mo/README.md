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

## SKU nuevo sin recorte — SIN iMac (Moisés, 12-oct-2026: "sin dibujos no hay procesos")
REGLA (11-oct-2026): los planos se toman SIEMPRE de la carpeta central y nunca se copian a otro lado:
`/Moises Peña/Carpeta del equipo DIMACO METALMECANICA/MAFESA/Dibujos MAFESA` (conector de Dropbox).
Un PDF por número de plano (la parte antes del guion del SKU; a veces `AutoVue - _<plano>.dwg.pdf`, `<plano>-REVn.pdf`
o `<plano>.DWG (1).pdf`; si hay varios, el de revisión más alta).

La regla corre en la nube y no puede bajar archivos de Dropbox, así que el plano llega por el robot de GitHub
`.github/workflows/planos.yml`, CIFRADO (el repo es público; solo la regla tiene la llave privada):
1. Dropbox `list_folder` (recursive=false, paginar hasta has_more=false) de la carpeta central; ubica el PDF de cada plano.
2. Dropbox `download_link` (expiration_in_sec 900) de esos PDF. El link es de un solo uso: NO lo abras ni lo pruebes.
3. Escribe `pedido/<FS>.json` = `{"files":[{"name":"<archivo.pdf>","url":"<download_url>"}, ...]}`, commit + push.
4. Espera (git fetch cada 15 s, hasta 6 min) a que aparezcan `entrega/<FS>.enc` y `entrega/<FS>.key`.
5. Descifra (llave privada en /tmp/planos_priv.pem, nunca al repo):
   `openssl pkeyutl -decrypt -inkey /tmp/planos_priv.pem -pkeyopt rsa_padding_mode:oaep -in entrega/<FS>.key -out k`
   `openssl enc -d -aes-256-cbc -pbkdf2 -in entrega/<FS>.enc -out p.tgz -pass file:k` y `tar -xzf p.tgz` (trae `_estado.json`).
6. `pdftoppm -r 300`, mirar la hoja (Read de un PNG a 80 dpi) y ubicar la vista de la parte (-0005 = P.5; en planos de tabla,
   la FIG. de su renglón). Si trae vista de doblez aparte, recortarla también como `-2`.
7. Guardar en `recortes/` (gris, máx. 1800 px de ancho), agregar la entrada a `catalogo.json` y revisar el recorte a ojo.
8. Si el SKU está en alguna estación y no tiene dibujo, agregar también a `piezas-extra.js` (vista + renglón en amarillo)
   y subir el `?v=` en la plantilla y las 5 estaciones.
9. `git rm` de `entrega/<FS>.*` y borra los PDF y PNG locales (no quedan planos en ningún lado). Commit + push.
Si el robot no entrega a tiempo o un link falla (`_estado.json`), repite UNA vez con links nuevos. Si aun así no hay plano,
la MO sale con "Sin recorte de plano", NO se registra y se dice en el cierre y en el correo.
