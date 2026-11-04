"""Actualiza la lista de MOs incrustada (var DATA=[...]) de las 5 estaciones piloto de racks:
app-habilitado (Corte Sierra), app-laser (Corte Laser + Router), app-pintura, app-vestido (Vestido + Colocación Dunnage),
app-armado1 (Armado y Soldadura). 4-nov-2026 (Moisés: "actualiza las estaciones piloto del área de racks").

Con código de equipo la estación ya baja la lista en vivo del servidor (/cola) cada 2 min y el orden sale de racks/datos.json;
esta lista incrustada es la que se ve sin código o sin conexión. Mismo criterio que el servidor: MOs de racks (las del Tablero TV
de Racks) con una operación de los recursos de la estación que no esté COMPLETED. Orden = orden de ataque del Tablero TV.
Uso (desde la raíz del repo): python3 herramientas/racks/estaciones_racks.py CARPETA_K racks/datos.json "4-nov 16:25"
"""
import json, glob, os, re, sys
K, DATOS, CORTE = sys.argv[1], sys.argv[2], sys.argv[3]
def L(p):
    out = []
    for f in sorted(glob.glob(os.path.join(K, p))):
        d = json.load(open(f)); out += d['data'] if isinstance(d, dict) else d
    return out
EST = {'habilitado': ['Corte Sierra'], 'laser': ['Corte Laser', 'Router'], 'pintura': ['Pintura'],
       'vestido': ['Vestido', 'Colocación Dunnage'], 'armado1': ['Armado y Soldadura']}
ETQ = {'habilitado': lambda r: 'Corte', 'laser': lambda r: (r.get('operation_name') or '').strip() or 'Láser',
       'pintura': lambda r: 'Pintura', 'vestido': lambda r: 'Vestido', 'armado1': lambda r: 'Armado y Soldadura'}
rows = json.load(open(DATOS))['datos']['rows']
pos = {r['mo']: i for i, r in enumerate(rows)}; byMo = {r['mo']: r for r in rows}
mos = {m['id']: m for m in L('mo_*.json')}
ops = {}
for o in L('ops_*.json'):
    ops.setdefault(o['manufacturing_order_id'], []).append(o)
for v in ops.values(): v.sort(key=lambda o: o.get('rank') or 0)
var = {v['id']: v for v in L('var_*.json')}
rec = {}
for r in L('rec_*.json'): rec.setdefault(r['manufacturing_order_id'], []).append(r)
def colR(nombre, recurso):
    u = (str(nombre or '') + ' ' + str(recurso or '')).upper()
    if re.search('L[AÁ]SER', u): return 'Láser'
    if 'ROUTER' in u: return 'Router'
    if re.match('^CORTE', u) or 'SIERRA' in u: return 'Corte'
    if re.match('^ARMADO', u) or 'SOLDADURA' in u: return 'Armado'
    if re.search('VESTIDO|ROTULADO|DUNNAGE', u): return 'Vestido'
    if 'PINTURA' in u: return 'Pintura'
    if 'DOBLEZ' in u: return 'Doblez'
    return (nombre or recurso or '').strip()
def avance(notas, etq):
    for l in str(notas or '').split('\n'):
        m = re.match(r'^' + re.escape(etq) + r':\s*(.*?)\s+(\d+)/(\d+)\s*\(([^)]*)\)', l.strip())
        if m: return int(m.group(2))
    return 0
def num(x):
    try: return float(x or 0)
    except: return 0.0
for a, recursos in EST.items():
    p = f'app-{a}/index.html'; s = open(p).read()
    m0 = re.search(r'var DATA=(\[.*?\]);\n', s); viejo = json.loads(m0.group(1))
    base = viejo[0] if viejo else {}
    nuevo = []
    for mid, mo in mos.items():
        if mo['order_no'] not in pos: continue                       # solo MOs del Tablero TV de Racks
        oo = ops.get(mid, [])
        mias = [o for o in oo if (o.get('resource_name') or '') in recursos and o['status'] != 'COMPLETED']
        if not mias: continue
        f = mias[0]; r = byMo[mo['order_no']]
        mia = colR(f.get('operation_name'), f.get('resource_name'))
        cols = []
        for o in oo:
            c = colR(o.get('operation_name'), o.get('resource_name'))
            if c not in cols: cols.append(c)
        ruta = []
        for c in cols:
            st = [o['status'] for o in oo if colR(o.get('operation_name'), o.get('resource_name')) == c]
            ruta.append([c, 'done' if all(x == 'COMPLETED' for x in st) else ('prog' if any(x in ('IN_PROGRESS', 'PAUSED', 'BLOCKED') for x in st) else 'none'), c == mia])
        rr = (rec.get(mid) or [None])[0]; ing = {}
        if rr:
            v = var.get(rr['variant_id'], {}); pm = v.get('product_or_material') or {}
            ing = dict(sku=v.get('sku') or '', nombre=pm.get('name') or '', uom=pm.get('uom') or '',
                       total=round(num(rr.get('planned_quantity_per_unit')) * num(mo.get('planned_quantity')), 3))
        va = var.get(mo['variant_id'], {}); pm = va.get('product_or_material') or {}
        paso = ('Router' if mia == 'Router' else 'Láser') if a == 'laser' else base.get('paso', f.get('operation_name'))
        nuevo.append(dict(mo=mo['order_no'], sec=pos[mo['order_no']] + 1, nombre=pm.get('name') or r['nombre'], sku=va.get('sku') or '—',
            piezas=int(num(mo.get('planned_quantity'))), ent=r['entrega'], deadline=(mo.get('production_deadline_date') or r['entrega'])[:10],
            prio=bool(r.get('prio')), grupo=base.get('grupo'), tipo=base.get('tipo', 'RACK'), color=base.get('color'), paso=paso,
            opName=f.get('operation_name'), recurso=f.get('resource_name'), planeado=num(f.get('planned_time_parameter')), recursoMal=False,
            rowId=f['id'], ruta=ruta, ingSku=ing.get('sku', ''), ingNombre=ing.get('nombre') or 'Sin receta en Katana',
            ingTot=ing.get('total', 0), ingUom=ing.get('uom', ''), notas=mo.get('additional_info') or 'Sin notas.',
            hechas=avance(mo.get('additional_info'), ETQ[a](f)), cliente=r.get('cliente', '')))
    nuevo.sort(key=lambda x: (x['sec'], x['ent']))
    s = s[:m0.start(1)] + json.dumps(nuevo, ensure_ascii=False) + s[m0.end(1):]
    s, n = re.subn(r'PILOTO · MOs de Katana en vivo \([^)]*\)', 'PILOTO · MOs de Katana en vivo (' + CORTE + ')', s)
    open(p, 'w').write(s)
    print(a, len(viejo), '->', len(nuevo), [(x['mo'], x['opName'], x['piezas']) for x in nuevo], 'pie', n)
