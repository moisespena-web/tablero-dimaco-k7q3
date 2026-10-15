"""Actualiza el catálogo de MOs del Tablero de Calidad MAFESA (doc catalogo/katana del artifact de Calidad).
Uso: python3 -I catalogo.py <catalogo_actual.json> <mos_katana.json> <variantes.json> <datos.json de la TV> <salida.json> <AAAA-MM-DD>
- mos_katana.json: lista (o {"data": [...]}) de MOs de Katana (GET /manufacturing_orders?created_at_min=...  y/o por estatus).
- variantes.json: lista (o {"data": [...]}) de /variants?ids[]=...&extend[]=product_or_material de esas MOs.
- Solo entran MOs de MAFESA: SKU que empieza con 36 o 37 (terminales). Las de racks se ignoran.
- Las que ya están en el catálogo solo actualizan su estado; las nuevas se agregan arriba con SO/material del tablero de la TV si la traen.
14-oct-2026 (Moisés)."""
import json, sys
cat_p, mos_p, var_p, tv_p, out_p, fecha = sys.argv[1:7]
L = lambda p: (lambda d: d.get("data", d) if isinstance(d, dict) else d)(json.load(open(p)))
cat = json.load(open(cat_p)); mos = L(mos_p); var = {v["id"]: v for v in L(var_p)}
rows = {r["mo"]: r for r in json.load(open(tv_p)).get("datos", {}).get("rows", [])}
have = {m["mo"]: m for m in cat["mos"]}; nuevos = 0; cambios = 0
for m in sorted(mos, key=lambda x: x.get("created_at") or ""):
    if m.get("deleted_at"): continue
    mo = m["order_no"]
    if mo in have:
        if have[mo].get("estado") != m["status"]: have[mo]["estado"] = m["status"]; cambios += 1
        continue
    v = var.get(m["variant_id"]) or {}; sku = v.get("sku") or ""
    if not sku.startswith(("36", "37")): continue
    pm = v.get("product_or_material") or {}; nombre = pm.get("name") or ""
    r = rows.get(mo, {})
    cu = r.get("cu") if r else ("CU" in nombre.upper().replace(".", " ").split() or "COBRE" in (pm.get("category_name") or "").upper())
    sos = r.get("sos") or ([r["so"].split(" · ")[0]] if r.get("so") else [])
    item = {"cant": int(float(m.get("planned_quantity") or 0)), "estado": m["status"], "material": "Cobre" if cu else "Aluminio",
            "mo": mo, "producto": r.get("nombre") or nombre, "sku": sku, "sos": sos}
    cat["mos"].insert(0, item); have[mo] = item; nuevos += 1
cat["actualizado"] = fecha
json.dump(cat, open(out_p, "w"), ensure_ascii=False)
print("nuevas", nuevos, "| estados cambiados", cambios, "| total", len(cat["mos"]))
