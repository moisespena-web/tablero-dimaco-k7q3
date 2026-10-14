"""Arma calidad.json para la TV MAFESA a partir de las incidencias del Tablero de Calidad MAFESA.
Uso: python3 exportar.py <carpeta_con_json_de_incidencias> <salida calidad.json>
Solo copia lo que se ve en planta: SIN montos ($) y SIN nombre de quien capturo."""
import json, sys, os, datetime
src, out = sys.argv[1], sys.argv[2]
CAMPOS = ["fecha","tipo","origen","deteccion","causa","mo","so","sku","producto","material","piezas","estado","accion","accionDetalle"]
inc = []
for f in sorted(os.listdir(src)):
    if f.endswith(".json"):
        d = json.load(open(os.path.join(src, f)))
        inc.append({k: d.get(k) for k in CAMPOS})
inc.sort(key=lambda r: r.get("fecha") or "", reverse=True)
mx = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
json.dump({"stamp": mx.strftime("%Y-%m-%dT%H:%M"), "incidencias": inc}, open(out, "w"), ensure_ascii=False, indent=1)
print(len(inc), "incidencias ->", out)
