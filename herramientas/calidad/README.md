# Calidad MAFESA → TV y catálogo de MOs (automático, 14-oct-2026)

Tarea programada "Calidad MAFESA → TV y catálogo" (L-V cada 2 h, 8:52 a 18:52 hora de México). Hace dos cosas:

1. **TV:** lee el Tablero de Calidad MAFESA (artifact https://claude.ai/artifact/6GjgdTJkEkdWDe7xJxXT4H) con ArtifactData:
   `list incidencias` y `list privado` con `out_dir` → `python3 -I herramientas/calidad/exportar.py <dir>/incidencias <dir>/privado calidad.json`.
   Si `calidad.json` cambió (sin contar el `stamp`): copia el MISMO contenido a `window.__CAL__` de `index.html`, commit
   "Calidad: N incidencias · scrap $X" + push, y `ArtifactData set` del doc `tv/calidad` en el artifact de la TV
   https://claude.ai/artifact/G3zuCpVd4oPBgxv3xLyH7r (con if_version leído antes). Si no cambió, no se toca nada.
2. **Catálogo de MOs del Tablero de Calidad** (doc `catalogo/katana` del artifact de Calidad): lo que se usa al capturar una
   incidencia (MO → SO, SKU, material). Katana: `GET /manufacturing_orders?created_at_min=<hace 21 días>&limit=250` (todas las
   páginas) + `/variants?ids[]=…&extend[]=product_or_material` de las que no estén en el catálogo →
   `python3 -I herramientas/calidad/catalogo.py <catalogo actual> <mos> <variantes> datos.json <salida> <AAAA-MM-DD>` →
   `ArtifactData set catalogo/katana` (con if_version). Solo MAFESA (SKU 36…/37…); racks no.

Nunca se escribe en Katana. Nunca se borran incidencias. Los importes `$` salen de `privado` (solo dueño) y solo van como total de scrap.
