# Estación Caja chica (Paty) — app-caja/

Liga: https://moisespena-web.github.io/tablero-dimaco-k7q3/app-caja/ (Paty no usa cuenta de Claude).

- **Capturar**: Paty registra salidas y entradas en su teléfono (se guardan en el teléfono, localStorage).
  Cada movimiento lleva un **folio** (Paammdd-XXXX). Botón "📤 Enviar a Ing. Moisés" abre Mail con el correo
  `CAJA CHICA PATY · DD/MM/AAAA HH:MM` a moises.pena@dimaco-mx.com. Lo enviado ya no se corrige: se cancela con motivo (renglón CANCELA).
- **Consultar**: libro de caja del año, solo lectura (libro.json). Sin notas internas, alertas ni historial.
- **Saldo**: saldo.json (saldo del tablero en la última corrida) + lo que Paty capturó y aún no está en el tablero (folios fuera de saldo.json).

## Corrida nocturna (tarea "Respaldo Caja chica")
1. Gmail `"CAJA CHICA PATY" newer_than:10d` → correos.json [{id, from, date, body}].
2. Export del tablero (ArtifactData list fondos/entradas/salidas con out_dir).
3. `python3 -I herramientas/caja/importar.py correos.json <export> herramientas/caja/aplicado.json <out>` →
   nuevos.json (batch set sin if_version, máx 50 por batch), cancelar.json (get + update estado "cancelada", motivoCancel, con if_version).
   Si todo salió bien: copia <out>/aplicado.json sobre herramientas/caja/aplicado.json.
   Entradas DIRECCIÓN: si ya existe la entrega (mismo monto, ±3 días) solo se liga; si no, se crea en fondos con "revisar" para que Moisés la confirme.
4. Vuelve a exportar y corre `python3 -I herramientas/caja/publicar.py <export> app-caja herramientas/caja/aplicado.json <ahora ISO>`.
5. commit "Caja chica <stamp> (auto)" de app-caja/saldo.json, app-caja/libro.json y herramientas/caja/aplicado.json; push.
El folio es la llave: repetir correos no duplica. Nunca se borra nada.

## Respaldo en Excel (a pedido: "respaldo de caja chica")
Ya no va en la tarea nocturna (corre en la nube, sin Mac). Se genera cuando Moisés lo pide, con alguna Mac encendida:
1. Export del tablero (fondos, entradas, salidas, cuadre_nomina) con ArtifactData list + out_dir.
2. Scripts en la Mac: Dimaco/Caja chica/scripts/ (respaldo_xlsx.py, subs.py, maximizar.py, logos). `python3 respaldo_xlsx.py <export> logo_dimaco.png logo_marca_gto.png "Caja chica 2026.xlsx"` → recalc.py del skill xlsx (0 errores) → `python3 maximizar.py "Caja chica 2026.xlsx"` (abre maximizado; recalc lo quita, por eso va después).
3. El Libro de caja abre filtrado a la semana corriente (lunes–domingo); lo demás queda oculto por el filtro de Fecha.
4. Subirlo con SendUserFile y device_commit_files usando el **fileUuid** (no stagedPath: con stagedPath se ha subido una copia vieja del mismo nombre). Verificar en la Mac que diga "generado <hoy>".
