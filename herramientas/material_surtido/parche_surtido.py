"""Regla de Moisés (7-oct-2026, "MSURT7OCT"): cada MO pide su material UNA sola vez.

Problema: "Material a utilizar" sumaba lo que Katana dice que le falta consumir a cada MO abierta
(total_remaining_quantity de la receta). Katana no descuenta la solera cuando el almacén la entrega a piso,
sólo al cerrar la MO; así que el material de una MO salía en la lista todos los días y el almacén
volvía a surtirlo (el 7-oct se pidieron 101 barras cuando hacían falta 22).

Regla:
- "Material a utilizar" sólo lleva las MOs que todavía NO están en surtido.json (y cuyo Corte no está
  COMPLETED en Katana). Cada MO sale en la lista una sola vez: la primera corrida de las 22:00 después de crearse.
- Nunca salen los renglones WIP (solera ya cortada).
- La corrida de las 22:00 (y sus corridas manuales) corre build_entregas.py con MAT_SURTIDO_GUARDAR=1:
  al terminar agrega a surtido.json TODAS las MOs del programa y quita las que ya no están abiertas.
  Luego se hace commit de surtido.json junto con datos.json.
- Las corridas de los cortes del día (7:00, 12:00, 17:00) sólo leen surtido.json; no lo cambian.
- Si Moisés dice que a una MO no se le entregó su solera: quitarla de surtido.json y volverá a salir.

Uso: lo llama parche_reportes.py (no hace falta llamarlo aparte). python3 parche_surtido.py DIR
Idempotente (marca MSURT7OCT). Si un texto no se encuentra, falla: NO publicar reportes a medias."""
import sys, os
D = sys.argv[1] if len(sys.argv) > 1 else '.'
SURT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'surtido.json')


def patch(fn, pares):
    p = os.path.join(D, fn)
    if not os.path.exists(p):
        print('no está (se omite)', fn); return
    t = open(p).read()
    if 'MSURT7OCT' in t:
        print('ya (surtido)', fn); return
    for a, b in pares:
        n = t.count(a)
        assert n == 1, ('%s: NO ENCONTRADO (%d) -> %s' % (fn, n, a[:100]))
        t = t.replace(a, b)
    open(p, 'w').write('# MSURT7OCT\n' + t); print('ok (surtido)', fn)


patch('build_entregas.py', [
 ("""req=collections.Counter(); tvids={r['id'] for r in tv}
for rr in morr:
    if rr['manufacturing_order_id'] in tvids: req[rr['variant_id']]+=float(rr.get('total_remaining_quantity') or 0)
""",
  """# MSURT7OCT · regla 7-oct-2026 (Moisés): cada MO pide su material UNA sola vez (ver herramientas/material_surtido)
import os as _os
_SURT_F=%r
try: _SURT=json.load(open(_SURT_F))
except Exception: _SURT={'mos':{}}
_ya=set(_SURT.get('mos',{}))
_cortado={o['manufacturing_order_id'] for o in ops if o['operation_name']=='Corte' and o['status']=='COMPLETED'}
req=collections.Counter(); tvids={r['id'] for r in tv}; _mo_no={r['id']:r['mo'] for r in tv}; req_mos=collections.defaultdict(set)
for rr in morr:
    _mid=rr['manufacturing_order_id']
    if _mid not in tvids or _mo_no[_mid] in _ya or _mid in _cortado: continue
    _q=float(rr.get('total_remaining_quantity') or 0)
    if _q>0: req[rr['variant_id']]+=_q; req_mos[rr['variant_id']].add(_mo_no[_mid])
""" % SURT),
 ("""    falta=stk(m)<q)
    for m,q in sorted(req.items(),key=lambda x:(matfull.get(x[0],''),)) if q>0 and m in matfull]""",
  """    falta=stk(m)<q,mos=sorted(req_mos[m],key=lambda s:int(s.split('-')[-1]) if s.split('-')[-1].isdigit() else 0))
    for m,q in sorted(req.items(),key=lambda x:(matfull.get(x[0],''),)) if q>0 and m in matfull and not matfull.get(m,'').upper().startswith('WIP') and not str(matname.get(m,'')).upper().startswith('WIP')]
if _os.environ.get('MAT_SURTIDO_GUARDAR')=='1':   # sólo la corrida de las 22:00 marca como surtidas las MOs del programa
    _nuevo={k:v for k,v in _SURT.get('mos',{}).items() if k in _mo_no.values()}
    for _r in tv: _nuevo.setdefault(_r['mo'],NOW.strftime('%Y-%m-%dT%H:%M'))
    json.dump(dict(regla='MSURT7OCT: cada MO pide su material una sola vez; quitar una MO de aqui la hace volver a salir en Material a utilizar',mos=dict(sorted(_nuevo.items(),key=lambda kv:int(kv[0].split('-')[-1]) if kv[0].split('-')[-1].isdigit() else 0))),open(_SURT_F,'w'),ensure_ascii=False,indent=1)
    print('surtido.json:',len(_nuevo),'MOs ya surtidas')
print('Material a utilizar (solo MOs nuevas):',[(x['sku'],x['cantidad'],x['mos']) for x in requisicion])"""),
])

patch('build_pdf_entregas.py', [
 ("""    if req and y>120:
        y-=16; c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(36,y,"Material a utilizar"); y-=4""",
  """    if not req and y>60:   # MSURT7OCT
        y-=16; c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(36,y,"Material a utilizar: nada nuevo")
        c.setFont("Helvetica",7); c.setFillColor(MUTED); c.drawString(36,y-11,"Todas las MOs del programa ya recibieron su solera. Cada MO pide su material una sola vez."); y-=14
    if req and y>120:
        y-=16; c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(36,y,"Material a utilizar"); y-=4"""),
 ("""c.drawString(36,y-8,"Consolidado por material de las MOs del programa, redondeado hacia arriba a piezas completas (1 pieza de solera = 144 in).")""",
  """c.drawString(36,y-8,"Solo MOs nuevas (cada MO recibe su solera una sola vez): "+", ".join(sorted({mo for m in req for mo in m.get("mos",[])},key=lambda s:int(s.split("-")[-1])))+". Redondeado a piezas completas (1 pieza de solera = 144 in).")"""),
])

patch('build_widget_entregas.py', [
 ("""<h3>Material a utilizar</h3><table>""",
  """<h3>Material a utilizar</h3><div class="sub">Solo MOs nuevas (cada MO recibe su solera una sola vez){(": "+E(", ".join(sorted({mo for m in req for mo in m.get("mos",[])},key=lambda s:int(s.split("-")[-1]))))) if req else ": nada nuevo, todas las MOs ya recibieron su solera"}</div><table>"""),
])

patch('build_xlsx_mo.py', [
 ("""r+=3; ws.cell(r,1,'Material a utilizar').font=Font(bold=True,size=12,color=NAVY); r+=1""",
  """r+=3; ws.cell(r,1,'Material a utilizar').font=Font(bold=True,size=12,color=NAVY)
_rq=D.get('requisicion') or []; ws.cell(r,3,('Solo MOs nuevas (cada MO recibe su solera una sola vez): '+', '.join(sorted({mo for m in _rq for mo in m.get('mos',[])},key=lambda s:int(s.split('-')[-1])))) if _rq else 'Nada nuevo: todas las MOs del programa ya recibieron su solera.').font=Font(italic=True,color='595959'); r+=1   # MSURT7OCT"""),
])
print('listo 3 (surtido)')
