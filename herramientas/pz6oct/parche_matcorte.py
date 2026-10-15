"""7a parte (Moisés, 15-oct-2026 · MATCORTE15OCT): "en la MO ya no es necesario colocar el material a utilizar, lo que
sí es importante es colocar este recuadro en la hoja de avance de corte y quitar el actual, este nos dice más".
1) build_entregas.py: además de `requisicion`, arma `reqCorte` = el mismo recuadro (Material · Tipo · Medida · Solicitar ·
   Sobrante · Soleras en stock) para TODAS las MOs del programa que aún no terminan Corte (sin el filtro de surtido.json:
   mientras no se corte, el material hace falta). Va en tv_datos.json y lo lee herramientas/hojas_avance.py --tv.
2) MO en proceso (PDF, widget y Excel): ya no lleva "Material a utilizar".
Se aplica después de las partes 1 a 6. Idempotente. Imprime "listo 7 (material corte)"."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
def rd(f): return open(os.path.join(D,f)).read()
def wr(f,t): open(os.path.join(D,f),'w').write(t)
TAG='MATCORTE15OCT'

# 1) build_entregas.py
f='build_entregas.py'
if os.path.exists(os.path.join(D,f)):
    t=rd(f)
    if TAG not in t:
        a="print('Material a utilizar (solo MOs nuevas):'"
        assert t.count(a)==1,'matcorte: print requisicion NO ENCONTRADO'
        blk='''# MATCORTE15OCT: recuadro de material para la hoja de avance de Corte (todas las MOs sin Corte terminado)
_reqc=collections.Counter(); _reqc_mos=collections.defaultdict(set)
for rr in morr:
    _mid=rr['manufacturing_order_id']
    if _mid not in tvids or _mid in _cortado: continue
    _q=float(rr.get('total_remaining_quantity') or 0)
    if _q>0: _reqc[rr['variant_id']]+=_q; _reqc_mos[rr['variant_id']].add(_mo_no[_mid])
reqCorte=[dict(sku=matname.get(m,str(m)),tipo=' '.join(matfull.get(m,'').split()[:2]),medida=' '.join(matfull.get(m,'').split()[2:]),
    cantidad=math.ceil(q/BARRA-1e-9) if 'Solera' in matfull.get(m,'') else math.ceil(q),unidad='pzas' if 'Solera' in matfull.get(m,'') else 'hojas',
    exacto=round(q/BARRA,2) if 'Solera' in matfull.get(m,'') else round(q,3),
    sobrante=int(round(math.ceil(q/BARRA-1e-9)*BARRA-q)) if 'Solera' in matfull.get(m,'') else None,
    stock=_stocktxt(stk(m),q) if 'Solera' in matfull.get(m,'') else '%g hojas'%(stk(m)-q),
    falta=stk(m)<q,mos=sorted(_reqc_mos[m],key=lambda s:int(s.split('-')[-1]) if s.split('-')[-1].isdigit() else 0))
    for m,q in sorted(_reqc.items(),key=lambda x:(matfull.get(x[0],''),)) if q>0 and m in matfull and not matfull.get(m,'').upper().startswith('WIP') and not str(matname.get(m,'')).upper().startswith('WIP')]
print('Material para Corte (hoja de avance):',[(x['sku'],x['cantidad'],x['mos']) for x in reqCorte])
'''
        t=t.replace(a,blk+a,1)
        b='requisicion=requisicion,'
        assert t.count(b)==1,'matcorte: datos requisicion NO ENCONTRADO'
        t=t.replace(b,'requisicion=requisicion,reqCorte=reqCorte,',1)
        wr(f,t); print('ok (7a)',f)
    else: print('ya (7a)',f)

# 2a) PDF
f='build_pdf_entregas.py'
if os.path.exists(os.path.join(D,f)):
    t=rd(f)
    if TAG not in t:
        a='    req=D.get("requisicion") or []\n'; b='    if not req and y>60:   # MSURT7OCT\n'
        assert t.count(a)==1 and t.count(b)==1,'matcorte: PDF material NO ENCONTRADO'
        t=t.replace(a,'    req=[]   # MATCORTE15OCT: el Material a utilizar ya no va en MO en proceso (va en la hoja de avance de Corte)\n',1).replace(b,'    if False:   # MATCORTE15OCT\n',1)
        wr(f,t); print('ok (7a)',f)
    else: print('ya (7a)',f)

# 2b) widget
f='build_widget_entregas.py'
if os.path.exists(os.path.join(D,f)):
    t=rd(f)
    if TAG not in t:
        i=t.find('<h3>Material a utilizar</h3>'); j=t.find('{rq}</table>',i)
        assert i>0 and j>i,'matcorte: widget material NO ENCONTRADO'
        t=t[:i]+t[j+len('{rq}</table>'):]
        wr(f,'# MATCORTE15OCT\n'+t); print('ok (7a)',f)
    else: print('ya (7a)',f)

# 2c) Excel
f='build_xlsx_mo.py'
if os.path.exists(os.path.join(D,f)):
    t=rd(f)
    if TAG not in t:
        i=t.find('# material a utilizar\n'); j=t.find('ws.page_setup.orientation=',i)
        assert i>0 and j>i,'matcorte: Excel material NO ENCONTRADO'
        t=t[:i]+'# MATCORTE15OCT: sin Material a utilizar (va en la hoja de avance de Corte)\n'+t[j:]
        wr(f,t); print('ok (7a)',f)
    else: print('ya (7a)',f)
print('listo 7 (material corte)')
