"""Arma var DATA=[...] de las 6 estaciones MAFESA (Corte, Taladro, M65, TM-2P, Doblez, Limpieza & SQA) desde Katana
y el tv_datos.json de build_entregas (mismo orden sec que la TV). Escrito el 9-nov-2026 (regla nocturna, PASO 2).
Uso: python3 datos_estaciones.py --repo R --tv tv_datos.json --mos F.. --ops F.. --morr F.. --var F.. --pie "9-nov 13:02" [--json salida.json]
Reemplaza en app-<est>/index.html solo var DATA=[...] y el pie "MOs de Katana al ..."; después correr gen.py."""
import json,re,argparse,glob
A=argparse.ArgumentParser()
A.add_argument('--repo',required=True); A.add_argument('--tv',required=True)
for k in ('mos','ops','morr','var'): A.add_argument('--'+k,nargs='+',required=True)
A.add_argument('--pie',required=True); A.add_argument('--json',default='')
a=A.parse_args()
L=lambda fs:[x for f in fs for x in json.load(open(f))['data']]
mos={m['id']:m for m in L(a.mos)}
ops={}
for o in L(a.ops): ops.setdefault(o['manufacturing_order_id'],[]).append(o)
rec={}
for r in L(a.morr): rec.setdefault(r['manufacturing_order_id'],[]).append(r)
var={v['id']:v for v in L(a.var)}
tv=json.load(open(a.tv))['rows']
def est(o):
    r=(o.get('resource_name') or '').strip(); n=(o.get('operation_name') or '').strip()
    if r in('TM-2P','Cuadrado Mafesa'): return 'TM-2P'
    if r=='Corte Mafesa' or n=='Corte': return 'Corte'
    if r=='Taladro Mafesa' or n=='Taladro' or n.upper().startswith('CNC'): return 'Taladro'
    if r=='M65' or n=='M65': return 'M65'
    if r=='Doblez Mafesa' or n=='Doblez': return 'Doblez'
    if r=='Limpieza & SQA' or n.startswith('Limpieza'): return 'Limpieza'
    return None
REC={'Corte':'Corte Mafesa','Taladro':'Taladro Mafesa','M65':'M65','TM-2P':'TM-2P','Doblez':'Doblez Mafesa','Limpieza':'Limpieza & SQA'}
ST={'COMPLETED':'done','IN_PROGRESS':'prog','PAUSED':'pausa'}
def merge(ss):
    if all(s=='done' for s in ss): return 'done'
    if 'prog' in ss: return 'prog'
    if 'pausa' in ss: return 'pausa'
    return 'none'
SLUG={'Corte':'corte','Taladro':'taladro','M65':'m65','TM-2P':'tm2p','Doblez':'doblez','Limpieza':'limpieza'}
out={s:[] for s in SLUG.values()}
for sec,r in enumerate(tv,1):
    m=mos[r['id']]; rs=sorted(ops.get(m['id'],[]),key=lambda o:o.get('rank') or 0)
    orden=[];grp={}
    for o in rs:
        e=est(o)
        if not e: continue
        if e not in grp: orden.append(e); grp[e]=[]
        grp[e].append(o)
    estado={e:merge([ST.get(o['status'],'none') for o in grp[e]]) for e in orden}
    ing=(rec.get(m['id']) or [None])[0]; iv=var.get(ing['variant_id']) if ing else None
    for e in orden:
        if estado[e]=='done': continue
        o=next((x for x in grp[e] if x['status']!='COMPLETED'),grp[e][0])
        d=dict(mo=r['mo'],sec=sec,nombre=r['nombre'],sku=r['sku'],piezas=int(m['planned_quantity'] or 0),entregadas=int(m.get('completed_quantity') or 0),
               ent=r.get('entrega',''),deadline=r.get('deadline',''),prio=bool(r.get('prio')),paso=o['operation_name'],recurso=o.get('resource_name') or '',
               planeado=round(float(o.get('planned_time_per_unit') or 0)),fuenteT='katana',recursoMal=(o.get('resource_name') or '')!=REC[e] and not (e=='TM-2P'),
               ruta=[[x,estado[x],x==e] for x in orden],ingSku=iv['sku'] if iv else '',ingNombre=(iv.get('product_or_material') or {}).get('name','') if iv else '',
               ingTot=round(float(ing['planned_quantity_per_unit'])*int(m['planned_quantity'] or 0),3) if ing else 0,ingUom='in',
               notas=(m.get('additional_info') or '').strip() or 'Sin notas.',hechas=0,rowId=o['id'])
        if e=='Limpieza':
            d['so']=(r.get('so') or '').replace(' · ',' - ')
            d['espera']=next((x for x in orden[:orden.index(e)] if estado[x]!='done'),'')
        out[SLUG[e]].append(d)
out['limpieza'].sort(key=lambda d:(1 if d['espera'] else 0,d['sec']))
def arr_end(t,i):
    dd=0
    for j in range(i,len(t)):
        if t[j]=='[': dd+=1
        elif t[j]==']':
            dd-=1
            if dd==0: return j+1
for slug,lst in out.items():
    p=f'{a.repo}/app-{slug}/index.html'; t=open(p).read()
    i=t.index('var DATA=[')+9; j=arr_end(t,i)
    t=t[:i]+json.dumps(lst,ensure_ascii=False)+t[j:]
    t=re.sub(r"MOs de Katana al [0-9]{1,2}-[a-z]{3} [0-9]{1,2}:[0-9]{2}",'MOs de Katana al '+a.pie,t)
    t=re.sub(r"PIE_ACT='[^']*'","PIE_ACT='"+a.pie+"'",t)
    open(p,'w').write(t); print(slug,len(lst),[d['mo'] for d in lst])
if a.json: json.dump(out,open(a.json,'w'),ensure_ascii=False)
