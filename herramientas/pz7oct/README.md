# PZ7OCT — TV, estaciones y Katana dicen lo mismo (Moisés, 6-oct-2026 23:06)

Sustituye la regla PZ6OCT ("Faltan X en la estación actual").

- **Número grande en todos lados = los 3 de Katana:** Total = `planned_quantity`, Entregadas = `completed_quantity`,
  **FALTAN = `remaining_quantity` = planeadas − entregadas**. Ej. MO-365: FALTAN 2,300 de 3,500 (igual que Katana).
- **La barra explica dónde están las que faltan** (siempre suma el total):
  verde = entregadas · azul = ya hechas en la estación actual (pasan a la siguiente) · gris = por hacer en la estación.
  Leyenda: "1,200 entregadas · 724 ya dobladas → Limpieza · 1,576 por doblar".
  Verbos: Corte cortadas/por cortar · Taladro taladradas/por taladrar · TM-2P maquinadas/por maquinar ·
  Doblez dobladas/por doblar · Limpieza limpias/por limpiar · (Racks: Láser, Router, Armado, Pintura, Vestido).
- Las notas de la MO ("Doblez: Miguel … = 1,924/3,500") cuentan sobre la MO completa e INCLUYEN lo entregado
  (así las escribe la estación conectada): ya hechas = x − entregadas.
- **EN PAUSA:** si Katana tiene la operación en PAUSED, la TV la pinta roja con ❚❚ y la estación dice "EN PAUSA"
  (en los datos de las estaciones, `ruta` usa "pausa" además de "done" | "prog" | "none").

| Archivo | Qué hace |
|---|---|
| `patch_tv.py REPO [BUILD]` | TV MAFESA y Racks (index.html, racks/index.html): número grande, leyenda, celdas "N dobladas", EN PAUSA, sello. También sirve para la copia artifact de la TV. |
| `patch_est_racks.py REPO` | Las 5 estaciones de Racks (plantilla vieja). |
| `../estaciones_mafesa/plantilla.html` + `gen.py` | Las 5 estaciones MAFESA ya traen PZ7OCT (marcadores @@HECHO@@, @@PORH@@…). |
| `../pz6oct/pz6.py`, `parche_reportes.py` | PDF, widget y Excel ya usan PZ7OCT (calc() trae `pend`, `hecho`, `por`). |
| `../hojas_avance.py` | Hojas de pluma con Faltan = Remaining de Katana y la hora del corte. |
