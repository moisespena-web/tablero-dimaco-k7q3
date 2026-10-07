#!/usr/bin/env python3
"""Arma los datos del Tablero de TV RACKS (todo lo que NO es MAFESA) desde respuestas crudas de Katana.
Uso: python3 build_racks.py --dir CARPETA_K --now 2026-10-06T17:40 --out racks/datos.json
CARPETA_K trae: so_*.json (NOT_SHIPPED, PARTIALLY_DELIVERED), mo_*.json (NOT_STARTED, IN_PROGRESS,
PARTIALLY_COMPLETED, BLOCKED), ops_*.json, ful_*.json, customers.json, var_*.json ({"data":[...]}).
Mismo orden de ataque que MAFESA: 1) prioridad (additional_info contiene "prioridad") -> 2) MOs ya iniciadas
-> 3) antigüedad de la orden de venta (la más vieja primero) -> MO más baja.
Sin Tipos, sin reposición de MOs, sin material, sin meta mensual."""
import json, glob, os, re, argparse, collections, datetime as dt
A=argparse.ArgumentParser(); A.add_argument('--dir',required=True); A.add_argument('--now',required=True); A.add_argument('--out',required=True)
a=A.parse_args()
def L(pat):
    out=[]
    for f in sorted(glob.glob(os.path.join(a.dir,pat))):
        d=json.load(open(f)); out+= d['data'] if isinstance(d,dict) else d
    return out
MAFESA=111818362
NOW=dt.datetime.fromisoformat(a.now); HOY=NOW.date()
cust={c['id']:c['name'] for c in L('customers.json')}
so=[o for o in L('so_*.json') if o['customer_id']!=MAFESA and o['status'] in ('NOT_SHIPPED','PARTIALLY_DELIVERED')]
mos=[m for m in L('mo_*.json') if m['status'] in ('NOT_STARTED','IN_PROGRESS','PARTIALLY_COMPLETED','BLOCKED')]
ops=L('ops_*.json'); ful=L('ful_*.json')
var={v['id']:v for v in L('var_*.json')}
# ---- columnas de racks (orden fijo de la planta) ----
COLS=[('Corte','CORTE'),('Laser','LÁSER'),('Router','ROUTER'),('Doblez','DOBLEZ'),('Armado','ARMADO'),('Pintura','PINTURA'),('Vestido','VESTIDO')]
def col(name):
    n=(name or '').strip().lower()
    if 'laser' in n or 'láser' in n: return 'Laser'
    if n.startswith('router'): return 'Router'
    if n.startswith('corte'): return 'Corte'
    if n.startswith('doblez'): return 'Doblez'
    if n.startswith('armado') or 'soldadura' in n or 'dunnage' in n: return 'Armado'
    if n.startswith('pintura'): return 'Pintura'
    if n.startswith('vestido') or n.startswith('rotulado'): return 'Vestido'
    return (name or '?').strip()
# ---- SO por variante (las MOs no vienen ligadas a su SO: se cruza por variant_id) ----
rows={}; v2so=collections.defaultdict(list)
for o in so:
    for r in o['sales_order_rows']:
        rows[r['id']]=(o,r); v2so[r['variant_id']].append(o)
dl=collections.Counter()
for f in ful:
    if f['status']!='DELIVERED': continue
    for fr in f['sales_order_fulfillment_rows']:
        rid=fr['fulfilled_row_id'] if fr.get('fulfilled_row_id') in rows else fr['sales_order_row_id']
        if rid in rows: dl[rid]+=fr['quantity']
pend_so=collections.Counter()
for rid,(o,r) in rows.items(): pend_so[o['id']]+=max(0,r['quantity']-dl[rid])
# ---- operaciones por MO ----
byop=collections.defaultdict(list)
for o in ops: byop[o['manufacturing_order_id']].append(o)
def opsof(m):
    out={}
    for o in sorted(byop.get(m['id'],[]),key=lambda o:(o.get('rank') or 0)):
        k=col(o.get('operation_name'))
        s=o['status']
        if k not in out: out[k]=s
        else:
            ss={out[k],s}
            out[k]='COMPLETED' if ss=={'COMPLETED'} else ('NOT_STARTED' if ss=={'NOT_STARTED'} else 'IN_PROGRESS')
    return [[k,s] for k,s in out.items()]
def avance(info):
    av={}
    for ln in (info or '').split('\n'):
        mh=re.match(r'\s*([^:\n]+):(.*)',ln)
        if not mh: continue
        fr=list(re.finditer(r'(?<![\d/])(\d+)\s*/\s*(\d+)(?![\d/])',mh.group(2)))
        if not fr: continue
        k=col(mh.group(1))
        if k in dict(COLS): av[k]='%s/%s'%(fr[-1].group(1),fr[-1].group(2))
    return av
# ---- colores por cliente (franja) ----
PAL=['#2F7FD8','#7A1F3D','#3F8F2F','#C2552B','#8E5BD0','#B8901A','#1C8C8C','#C23C7A']
clientes=sorted({cust.get(o['customer_id'],'?') for o in so})
CCOL={c:PAL[i%len(PAL)] for i,c in enumerate(clientes)}
# ---- renglones ----
tv=[]; extra=[]
for m in mos:
    sos=v2so.get(m['variant_id'])
    if not sos: continue                      # no es de una SO abierta de racks (MAFESA o catálogo)
    s=sorted(sos,key=lambda o:o['order_created_date'])[0]
    o=opsof(m); prio='prioridad' in (m.get('additional_info') or '').lower()
    v=var.get(m['variant_id'],{}); pm=v.get('product_or_material') or {}
    cli=cust.get(s['customer_id'],'?')
    ini=any(x[1]!='NOT_STARTED' for x in o)
    ddl=(m.get('production_deadline_date') or s.get('delivery_date') or '')
    ddl=(dt.datetime.fromisoformat(ddl.replace('Z','+00:00'))-dt.timedelta(hours=6)).date().isoformat() if ddl else ''
    so_dd=(s.get('delivery_date') or '')[:10]
    tv.append(dict(mo=m['order_no'],id=m['id'],sku=v.get('sku') or '',nombre=pm.get('name','?'),
        piezas=int(m['remaining_quantity'] or m['planned_quantity'] or 0),
        plan=int(m.get('planned_quantity') or 0),entr=int(m.get('completed_quantity') or 0),   # 6-oct: FALTAN X de total + barra
        deadline=ddl,entrega=ddl,prio=prio,ops=o,
        av=avance(m.get('additional_info')),cliente=cli,color=CCOL.get(cli,'#8A93A6'),
        so=s['order_no']+' · '+cli,grp='urge' if prio else 'sig',nota='',
        _g=0 if prio else (1 if ini else 2),_old=s['order_created_date'],
        _n=int(m['order_no'].split('-')[1]) if m['order_no'].split('-')[-1].isdigit() else 0))
tv.sort(key=lambda r:(r['_g'],r['_old'],r['_n']))
# agrupado por cliente (pedido de Moisés, 6-oct-2026): el cliente con la MO más urgente va primero;
# dentro de cada cliente se respeta el orden de ataque
pos={}
for i,r in enumerate(tv): pos.setdefault(r['cliente'],i)
tv.sort(key=lambda r:pos[r['cliente']])          # sort estable: conserva el orden de ataque dentro del cliente
for r in tv:
    for k in ('_g','_old','_n'): r.pop(k)
# ---- avance por proceso (piezas que ya pasaron / piezas que deben pasar) ----
T=collections.Counter(); H=collections.Counter()
for r in tv:
    for k,s in r['ops']:
        T[k]+=r['piezas']; av=r['av'].get(k)
        H[k]+= r['piezas'] if s=='COMPLETED' else (min(r['piezas'],int(av.split('/')[0])) if av else 0)
usadas=[c for c in COLS if T[c[0]]]+[(k,k.upper()) for k in T if k not in dict(COLS)]
datos=dict(stamp=NOW.strftime('%Y-%m-%dT%H:%M:00-06:00'),modo='entregas',proyecto='racks',
    ops=[list(c) for c in usadas],clientes=[[c,CCOL[c]] for c in clientes if any(r['cliente']==c for r in tv)],rows=tv,
    avProc=[dict(p=lbl,h=H[k],t=T[k],pct=round(100*H[k]/T[k])) for k,lbl in usadas if T[k]],
    faltaPz=int(sum(pend_so.values())),
    soSinMO=[o['order_no']+' · '+cust.get(o['customer_id'],'?') for o in so
             if pend_so[o['id']]>0 and not any(m['variant_id'] in {r['variant_id'] for r in o['sales_order_rows']} for m in mos)])
json.dump(dict(datos=datos),open(a.out,'w'),ensure_ascii=False)
print('MOs racks:',len(tv),'| pz:',sum(r['piezas'] for r in tv),'| faltan pz SO:',datos['faltaPz'],'| columnas:',[c[0] for c in usadas],'| SO sin MO:',datos['soSinMO'])
for r in tv: print(r['mo'],r['so'],r['nombre'],r['piezas'],r['entrega'],r['ops'])
