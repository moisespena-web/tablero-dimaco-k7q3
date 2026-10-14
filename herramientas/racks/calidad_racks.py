"""Arma racks/calidad.json para la TV RACKS a partir del Tablero de Calidad de racks
(artifact https://claude.ai/artifact/1fJMcymce3whquAWFuEYZj, colecciones `incidencias` y `privado`).
Uso: python3 calidad_racks.py <carpeta incidencias/*.json> <carpeta privado/ (costos.json, montos.json)> <salida racks/calidad.json>
14-oct-2026 (Moisés): la TV de Racks lleva su página CALIDAD RACKS, copia de la de MAFESA.
- "Quién originó" = líder del departamento donde se originó (en racks no se captura operador).
- Scrap en $ = solo material, mismo cálculo que el Tablero de Calidad de racks:
  monto congelado en privado/montos si existe; si no, Σ cantidad × precio de compra (privado/costos.precios),
  o "rack completo" = costo del BOM del producto (privado/costos.rack[vid])."""
import json, sys, os, datetime
src, priv, out = sys.argv[1], sys.argv[2], sys.argv[3]
def cargar(n):
    p = os.path.join(priv, n)
    return json.load(open(p)) if os.path.exists(p) else {}
C = cargar("costos.json"); precios = C.get("precios", {}); rack = C.get("rack", {})
montos = cargar("montos.json").get("m", {})
LIDER = {"dis": "Uriel", "hab": "Mario", "las": "Luis", "arm": "Arturo", "pin": "Daniel", "ves": "Ricardo", "cal": "Bety", "ext": "Compras"}
CAMPOS = ["fecha","tipo","origen","deteccion","causa","mo","so","producto","cliente","piezas","estado","accion","accionDetalle","diasRetraso"]
def monto(iid, d):
    if d.get("tipo") != "scrap": return None
    if iid in montos:
        m = montos[iid]; return m.get("monto") if isinstance(m, dict) else m
    t, ok = 0.0, False
    for it in d.get("scrapMat") or []:
        q = float(it.get("cant") or 0)
        if not q: continue
        u = rack.get(str(d.get("vid") or "")) if it.get("id") == "rack" else precios.get(str(it.get("id")))
        if u is not None: t += u * q; ok = True
    return round(t, 2) if ok else None
inc = []
for f in sorted(os.listdir(src)):
    if not f.endswith(".json"): continue
    d = json.load(open(os.path.join(src, f))); iid = f[:-5]
    r = {k: d.get(k) for k in CAMPOS}
    r["operador"] = LIDER.get(r["origen"] or "", "")
    r["monto"] = monto(iid, d)
    inc.append(r)
inc.sort(key=lambda r: r.get("fecha") or "", reverse=True)
mx = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)
json.dump({"stamp": mx.strftime("%Y-%m-%dT%H:%M"), "proyecto": "racks", "incidencias": inc}, open(out, "w"), ensure_ascii=False, indent=1)
print(len(inc), "incidencias ->", out, "| scrap $", sum(r.get("monto") or 0 for r in inc))
