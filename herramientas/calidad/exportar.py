"""Arma calidad.json para la TV MAFESA a partir del Tablero de Calidad MAFESA.
Uso: python3 exportar.py <carpeta incidencias/*.json> <carpeta privado/ (costos.json, montos.json)> <salida calidad.json>
14-oct-2026 (Moisés): la TV muestra el nombre de quien originó cada incidencia y el importe de scrap
(solo material, mismo cálculo que el Tablero de Calidad: precio congelado en privado/montos, si no, costo vigente del SKU)."""
import json, sys, os, datetime
src, priv, out = sys.argv[1], sys.argv[2], sys.argv[3]
def cargar(n):
    p = os.path.join(priv, n)
    return json.load(open(p)) if os.path.exists(p) else {}
costos = cargar("costos.json").get("costos", {})
montos = cargar("montos.json").get("m", {})
CAMPOS = ["fecha","tipo","origen","operador","deteccion","causa","mo","so","sku","producto","material","piezas","estado","accion","accionDetalle"]
inc = []
for f in sorted(os.listdir(src)):
    if not f.endswith(".json"): continue
    d = json.load(open(os.path.join(src, f))); iid = f[:-5]
    r = {k: d.get(k) for k in CAMPOS}
    if r["tipo"] == "scrap":
        u = montos[iid]["unit"] if iid in montos else costos.get(r["sku"])
        r["monto"] = round(u * (r["piezas"] or 0), 2) if u is not None else None
    inc.append(r)
inc.sort(key=lambda r: r.get("fecha") or "", reverse=True)
mx = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)
json.dump({"stamp": mx.strftime("%Y-%m-%dT%H:%M"), "incidencias": inc}, open(out, "w"), ensure_ascii=False, indent=1)
print(len(inc), "incidencias ->", out, "| scrap $", sum(r.get("monto") or 0 for r in inc))
