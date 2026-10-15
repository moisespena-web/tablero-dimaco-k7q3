"""Hojas de avance para anotar a pluma (temporal, pedido de Moisés 6-oct-2026) — una por estación MAFESA
(Corte, Taladro y TM-2P en una sola hoja, Limpieza & SQA; Doblez ya no lleva hoja desde el 15-oct-2026), con las MOs que muestra cada app de estación.
Uso: python3 hojas_avance.py --repo <clon de tablero-dimaco-k7q3> --out <carpeta> --fs DD-MM_HH-MM --tv <tv_datos.json de build_entregas> [--racks]
Correr DESPUÉS de actualizar las estaciones (regla 22:00, paso 3) para que salgan con las MOs de ese corte.
Archivos: "Hoja de avance - <Estación>_<FS>.pdf". Racks solo con --racks (por ahora Moisés pidió solo MAFESA)."""
import re,json,sys,datetime as dt
import argparse,glob,os
for _p in ['/mnt/skills/plugins/avance-operaciones/scripts']+glob.glob('/root/.claude/skills/**/avance-operaciones/scripts',recursive=True): sys.path.insert(0,_p)
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
try:
    from dimaco_brand import logo_reader; LOGO=logo_reader()
except Exception as e: LOGO=None; print('sin logo',e)
AP=argparse.ArgumentParser(); AP.add_argument('--repo',default='/home/claude/tablero-dimaco-k7q3'); AP.add_argument('--out',default='/home/claude/hojas/out'); AP.add_argument('--fs',default=''); AP.add_argument('--racks',action='store_true'); AP.add_argument('--tv',default='',help='tv_datos.json de build_entregas (trae reqCorte, MATCORTE15OCT)')
ARGS=AP.parse_args(); REPO=ARGS.repo
# TALTM11OCT (Moisés, 11-oct-2026, regla): Taladro y TM-2P van en UNA sola hoja — misma área y mismo líder (Fernando).
# SINDOBLEZ15OCT (Moisés, 15-oct-2026): "para doblez, ya no es necesario la hoja de avance".
EST=[('app-corte','Corte','MAFESA'),('app-taladro+app-tm2p','Taladro y TM-2P','MAFESA'),('app-limpieza','Limpieza & SQA','MAFESA'),
     ('app-habilitado','Habilitado','RACKS'),('app-laser','Láser y Router','RACKS'),('app-armado1','Armado y Soldadura 1','RACKS'),('app-pintura','Pintura','RACKS'),('app-vestido','Rotulado y Vestido','RACKS')]
MES=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
def arr(t,key):
    i=t.index(key)+len(key)-1; d=0
    for j in range(i,len(t)):
        c=t[j]
        if c=='[': d+=1
        elif c==']':
            d-=1
            if d==0: return json.loads(t[i:j+1].replace(',"st":nuevo()',''))
TV={r['mo']:r for r in json.load(open(REPO+'/datos.json'))['datos']['rows']}
def avN(s):
    m=re.search(r'(\d+)\s*/\s*(\d+)',s or ''); return (int(m.group(1)),int(m.group(2))) if m else None
def nota_pz(notas,clave):
    n=0
    for l in (notas or '').splitlines():
        if not l.strip().lower().startswith(clave.lower()): continue
        for m in re.finditer(r'(\d+)\s*/\s*(\d+)',l):
            a=l[m.start()-1:m.start()]; b=l[m.end():m.end()+1]
            if re.match(r'[\d/]',a or ' ') or re.match(r'[\d/]',b or ' '): continue
            n=int(m.group(1))
    return n
# PZ7OCT (Moisés, 6-oct-2026 23:06): "Faltan X de Y" = Remaining de Katana (planeadas − entregadas), igual que TV y estaciones.
HECHO={'Corte':'cortadas','Taladro':'taladradas','TM-2P':'maquinadas','Doblez':'dobladas','Limpieza':'limpias','Limpieza & SQA':'limpias'}
PORH={'Corte':'por cortar','Taladro':'por taladrar','TM-2P':'por maquinar','Doblez':'por doblar','Limpieza':'por limpiar','Limpieza & SQA':'por limpiar'}
def actual(m):
    r=m.get('ruta') or []; i=-1
    for k,x in enumerate(r):
        if x and (len(x)>2 and x[2] is True or (i<0 and 'TM-2P' in str(x[0]))): i=k
    nom=r[i][0] if i>=0 else ''; sig=''
    for x in r[i+1:] if i>=0 else []:
        if x and x[1] is not None: sig=str(x[0]).replace(' Sierra',''); break
    return nom,sig
def pz(m):
    plan=int(m.get('piezas') or 0)
    if m.get('entregadas') is not None: e=int(m['entregadas'] or 0)
    else:
        tv=TV.get(m['mo']); y=max([avN(v)[1] for v in (tv or {}).get('av',{}).values() if avN(v)] or [0])
        e=max(0,(y or plan)-tv['piezas']) if tv and (y or plan)>tv['piezas'] else 0
        if y: plan=max(plan,y)
    nom,sig=actual(m); clave='TM-2P' if nom=='TM-2P' else nom
    h=max(0,nota_pz(m.get('notas'),clave)-e, int(m.get('hechas') or 0)-e)
    h=min(h,max(0,plan-e)); f=max(0,plan-e-h)
    return plan,e,h,f,sig
def fd(iso):
    try: d=dt.date.fromisoformat(iso[:10]); return '%d-%s'%(d.day,MES[d.month-1])
    except: return ''
def ell(c,t,f,s,w):
    t=str(t)
    while t and pdfmetrics.stringWidth(t,f,s)>w: t=t[:-1]
    return t
INK=colors.HexColor('#111111'); MUT=colors.HexColor('#666666'); RULE=colors.HexColor('#9AA0A6')
W,H=landscape(letter)
COLS0=[('#',18),('MO',48),('SKU',70),('Pieza',122),('Operación',60),('Entrega',40),('Por hacer',62),
      ('',58),('',58),('',58),('Notas',0)]   # HOJ9OCT: 3 cuadros sin leyenda + Notas con renglón libre
# SOL9OCT (Moisés, 9-oct-2026): la hoja de Corte lleva SIEMPRE las soleras a pedir a almacén.
# Por MO: material + soleras redondeadas hacia arriba (1 solera = 144 in; lámina u otra UOM: unidades completas).
# Si la MO ya está en material_surtido/surtido.json, se marca "surtida <fecha>" (regla MSURT7OCT: una sola vez).
# Abajo, recuadro "Pedir a almacén" consolidado por material, solo de las MOs aún no surtidas.
import math
SOL_IN=144.0
def surtido():
    try: return json.load(open(REPO+'/herramientas/material_surtido/surtido.json')).get('mos',{})
    except Exception: return {}
def sol(m):
    tot=float(m.get('ingTot') or 0); uom=(m.get('ingUom') or '').lower(); sku=m.get('ingSku') or ''
    if sku.upper().startswith('LAM') or 'LAMINA' in (m.get('ingNombre') or '').upper(): uom='hoja'   # las estaciones mandan ingUom 'in' aunque sea lámina
    if not sku or tot<=0: return sku,0,0,''
    if uom in ('in','pulg','"'): return sku,math.ceil(tot/SOL_IN-1e-9),tot,'in'
    return sku,math.ceil(tot-1e-9),tot,uom
def unidad(uom,n):
    if uom=='in': return 'solera' if n==1 else 'soleras'
    return {'hoja':'hoja','hojas':'hoja'}.get(uom,uom or 'pz')+('' if n==1 or not uom else ('s' if not (uom or '').endswith('s') else ''))
# COLOR11OCT · color fijo por estación (Moisés 11-oct-2026: lo de la TV va en todo; tono oscuro para papel)
CEST_P={'Corte':'#1F6FD1','Taladro':'#6E4BD8','TM-2P':'#D6337F','Doblez':'#6F8C00','Limpieza & SQA':'#0E9C9C','Limpieza':'#0E9C9C'}
# IMG15OCT (Moisés, 15-oct-2026): miniatura del SKU como en la tablet (mismas imágenes: app-tm2p/piezas.js y piezas-extra.js)
_IMGS=None
def imgs():
    global _IMGS
    if _IMGS is None:
        import base64,io
        from reportlab.lib.utils import ImageReader
        _IMGS={}
        for f_ in ('app-tm2p/piezas.js','piezas-extra.js'):
            try: s_=open(os.path.join(REPO,f_)).read()
            except Exception: continue
            for k_,b_ in re.findall(r'"([0-9A-Z][0-9A-Za-z.\-]+)"\s*:\s*"data:image/[a-z]+;base64,([A-Za-z0-9+/=]+)"',s_):
                if k_ in _IMGS: continue
                try: _IMGS[k_]=ImageReader(io.BytesIO(base64.b64decode(b_)))
                except Exception: pass
        print('miniaturas',len(_IMGS))
    return _IMGS
def hoja(app,est,proy,out,hoy,hora):
    COLS=COLS0 if est!='Corte' else [x if x[0]!='Operación' else ('Solera a pedir',112) for x in COLS0]
    if est=='Taladro y TM-2P': COLS=COLS[:7]+[('Dibujo',72)]+COLS[7:]   # IMG15OCT
    SURT=surtido() if est=='Corte' else {}; ped={}
    mos=[]; apps=app.split('+')
    for a_ in apps:
        t=open('%s/%s/index.html'%(REPO,a_)).read()
        ms=arr(t,'var DATA=[') if 'var DATA=[' in t else arr(t[t.index('mos:[{'):],'mos:[')
        for m_ in ms: m_['_est']='TM-2P' if a_=='app-tm2p' else ('Taladro' if a_=='app-taladro' else est)
        mos+=ms
    if len(apps)>1: mos.sort(key=lambda m_:(int(m_.get('sec') or 999),m_['_est']!='TM-2P'))   # orden de la TV; en la misma MO primero TM-2P
    # ACOMODO15OCT (Moisés, 15-oct-2026, 2a versión): TODO EN 1 HOJA. Primero urgencias; luego cobre (primero las que ya
    # tienen listo el corte); luego aluminio (primero las que ya tienen listo el corte). Dentro de cada grupo, orden de la TV.
    def _espera(m_):
        prev=None
        for e_,s_,me_ in (m_.get('ruta') or []):
            if me_:
                if s_ in ('prog','pausa'): return ''   # ya se está trabajando aquí
                break
            if s_!='done' and prev is None: prev=(e_,s_)
        if not prev: return ''
        return 'espera '+prev[0]+{'prog':' (en proceso)','pausa':' (en pausa)'}.get(prev[1],'')
    def _sincorte(m_):
        for e_,s_,me_ in (m_.get('ruta') or []):
            if me_: return False
            if e_=='Corte' and s_!='done': return True
        return False
    def _cu(m_): return (m_.get('ingSku') or '').upper().startswith('CU') or ' CU ' in ' '+(m_.get('nombre') or '').upper().replace('.',' ')+' '
    def _grp(m_): return 0 if m_.get('prio') else (1 if _cu(m_) else 2)
    BLOQ=len(apps)>1
    if BLOQ:
        for m_ in mos: m_['_esp']=_espera(m_); m_['_g']=_grp(m_)
        mos.sort(key=lambda m_:(m_['_g'],_sincorte(m_),int(m_.get('sec') or 999),m_['_est']!='TM-2P'))
    _pie=re.search(r'MOs de Katana al ([0-9]{1,2}-[a-z]{3}) ([0-9]{1,2}:[0-9]{2})',t)   # la hora del corte de datos, no la de impresión
    if _pie: hoy,hora=_pie.group(1),_pie.group(2)
    c=canvas.Canvas(out,pagesize=(W,H)); c.setTitle('Hoja de avance · '+est)
    x0=30; TW=W-60; fixed=sum(w for _,w in COLS); ws=[w or (TW-fixed) for _,w in COLS]
    RH=34 if est in ('Corte','Taladro y TM-2P') else 26; pag=[0]   # PZTRAMO15OCT: Corte lleva un 3er renglón (piezas por tramo)
    def cab():
        pag[0]+=1; y=H-28
        if LOGO:
            iw,ih=LOGO.getSize(); c.drawImage(LOGO,x0,y-30,width=34*iw/ih,height=34,mask='auto')
        t1='Hoja de avance · Estación '; partes=[(t1,INK)]+([('Taladro',colors.HexColor(CEST_P['Taladro'])),(' y ',INK),('TM-2P',colors.HexColor(CEST_P['TM-2P']))] if est=='Taladro y TM-2P' else [(est,colors.HexColor(CEST_P.get(est,'#1F2A37')))])
        xt=W/2-sum(c.stringWidth(p_,'Helvetica-Bold',17) for p_,_ in partes)/2; c.setFont('Helvetica-Bold',17)
        for p_,col_ in partes: c.setFillColor(col_); c.drawString(xt,y-8,p_); xt+=c.stringWidth(p_,'Helvetica-Bold',17)
        c.setFont('Helvetica',9); c.setFillColor(MUT); c.drawCentredString(W/2,y-21,'%s · MOs de Katana al %s %s · hoja %d'%(proy,hoy,hora,pag[0]))
        c.setFillColor(INK); c.setFont('Helvetica',10)
        c.drawRightString(x0+TW,y-6,'Fecha: ____ / ____ / ______'); c.drawRightString(x0+TW,y-22,'Operador: ______________________')
        y-=44
        c.setFont('Helvetica',7.6); c.setFillColor(MUT)
        c.drawString(x0,y,'"Por hacer X de Y" = piezas que faltan en ESTA estación, de las Y de la MO. Abajo de la pieza: entregadas, ya hechas aquí y por hacer.')
        y-=8
        xs=x0
        if est=='Taladro y TM-2P':
            c.setFillColor(colors.HexColor(CEST_P['Taladro'])); c.rect(x0,y-15,TW/2,15,stroke=0,fill=1); c.setFillColor(colors.HexColor(CEST_P['TM-2P'])); c.rect(x0+TW/2,y-15,TW/2,15,stroke=0,fill=1)
        else: c.setFillColor(colors.HexColor(CEST_P.get(est,'#1F2A37'))); c.rect(x0,y-15,TW,15,stroke=0,fill=1)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold',7.6)
        for (h,_),w in zip(COLS,ws): c.drawCentredString(xs+w/2,y-10.5,h); xs+=w
        return y-15
    y=cab()
    GN={0:'Urgentes',1:'Cobre',2:'Aluminio'}; _pg=[None]
    if BLOQ:   # alto de renglón para que quepa en 1 hoja (mín. 28)
        ng_=len({m_['_g'] for m_ in mos}); RH=max(28,min(34,int((y-36-12*ng_)/max(1,len(mos))))) 
    for i,m in enumerate(mos,1):
        if BLOQ and m['_g']!=_pg[0]:   # franja de grupo
            if y-12-RH<36: c.showPage(); y=cab()
            n_=sum(1 for x_ in mos if x_['_g']==m['_g']); col_={0:'#F7E2DC',1:'#F3E3D6',2:'#E8EDF3'}[m['_g']]
            c.setFillColor(colors.HexColor(col_)); c.rect(x0,y-12,TW,12,stroke=0,fill=1)
            c.setFillColor(colors.HexColor({0:'#B42318',1:'#8A4A22',2:'#1F2A37'}[m['_g']])); c.setFont('Helvetica-Bold',7.6)
            c.drawString(x0+6,y-8.8,'%s · %d %s'%(GN[m['_g']],n_,'renglón' if n_==1 else 'renglones')+('' if m['_g']==0 else ' · primero las que ya tienen listo el corte')); c.setFillColor(INK); y-=12; _pg[0]=m['_g']
        if y-RH<(36 if BLOQ else 40):
            c.showPage(); y=cab()
        plan,e,h,f,sig=pz(m); er=m.get('_est',est)
        if m.get('prio'): c.setFillColor(colors.HexColor('#F7E2DC')); c.rect(x0,y-RH,TW,RH,stroke=0,fill=1)
        xs=x0; ty=y-11
        op_=m.get('paso') or m.get('opName') or ''
        # TM-2P se distingue por color (rosa) — la columna es angosta para anteponer "TM-2P"
        vals=[str(i),m['mo'],m.get('sku') or '—',m.get('nombre',''),op_,fd(m.get('ent') or m.get('deadline') or '')]
        fonts=[('Helvetica',8),('Helvetica-Bold',8.4),('Courier-Bold',7.6),('Helvetica',7.8),('Helvetica',7.4),('Helvetica-Bold',8)]
        for k,(v,(fn,fs)) in enumerate(zip(vals,fonts)):
            if est=='Corte' and k==4:
                sku,n,tot,uom=sol(m); c.setFillColor(INK)
                if not sku: c.setFont('Helvetica',7.4); c.drawString(xs+3,ty,'— sin material en Katana')
                else:
                    c.setFont('Courier-Bold',7.2); c.drawString(xs+3,ty,ell(c,sku,'Courier-Bold',7.2,ws[k]-6))
                    # CORTEPEND15OCT (Moisés, 15-oct-2026): mientras la MO no termine Corte, el material SIGUE haciendo falta.
                    # La hoja ya no usa surtido.json ("ya surtida" confundía): pide las soleras de las piezas que faltan por cortar.
                    pl_=float(m.get('piezas') or 0); fc=f if pl_>0 else 0
                    need=tot*fc/pl_ if pl_>0 else 0
                    n=(math.ceil(need/SOL_IN-1e-9) if uom=='in' else math.ceil(need-1e-9)) if need>0 else 0
                    if n<=0:
                        c.setFont('Helvetica',6.6); c.setFillColor(MUT); c.drawString(xs+3,y-21,'corte terminado · nada que pedir'); c.setFillColor(INK)
                    else:
                        a_='%d %s'%(n,unidad(uom,n)); c.setFont('Helvetica-Bold',8.4); c.drawString(xs+3,y-21,a_)
                        det='(%s %s'%(f"{need:,.1f}".rstrip('0').rstrip('.'),uom)+(' · %s por cortar)'%f"{fc:,}" if fc<pl_ else ')')
                        c.setFont('Helvetica',6.2); c.setFillColor(MUT); c.drawString(xs+5+pdfmetrics.stringWidth(a_,'Helvetica-Bold',8.4),y-21,ell(c,det,'Helvetica',6.2,ws[k]-10-pdfmetrics.stringWidth(a_,'Helvetica-Bold',8.4))); c.setFillColor(INK)
                        q=ped.setdefault(sku,[0.0,uom,[]]); q[0]+=need; q[2].append(m['mo'])
                    # PZTRAMO15OCT (Moisés, 15-oct-2026): abajo de "N soleras / ya surtidas", las piezas que salen por tramo
                    # (tramo = solera de 144 in; largo por pieza = material de la MO en Katana ÷ piezas planeadas; sin merma de sierra).
                    pzs=float(m.get('piezas') or 0)
                    if uom=='in' and pzs>0 and tot>0:
                        lpz=tot/pzs; ppt=int(SOL_IN//lpz+1e-9)
                        c.setFont('Helvetica-Bold',7.2); c.setFillColor(INK); c.drawString(xs+3,y-30,ell(c,'%s pz por tramo (%s in c/u)'%(f"{ppt:,}",f"{lpz:,.3f}".rstrip('0').rstrip('.')),'Helvetica-Bold',7.2,ws[k]-6))
                xs+=ws[k]; continue
            c.setFillColor(colors.HexColor(CEST_P.get(er,'#1F2A37')) if k==4 else INK); c.setFont('Helvetica-Bold' if k==4 else fn,fs); c.drawString(xs+3,ty,ell(c,v,'Helvetica-Bold' if k==4 else fn,fs,ws[k]-6)); xs+=ws[k]
        if m.get('prio'): c.setFont('Helvetica-Bold',6.4); c.drawString(x0+sum(ws[:1])+3,y-21,'URGE')
        if BLOQ and m.get('_esp'):   # ACOMODO15OCT
            c.setFont('Helvetica-Bold',6.4); c.setFillColor(colors.HexColor('#B45309')); c.drawString(x0+sum(ws[:4])+3,y-21,ell(c,m['_esp'],'Helvetica-Bold',6.4,ws[4]+ws[5]-6)); c.setFillColor(INK)
        # Faltan X de Y + mini barra
        w=ws[6]; a_=f"{f:,}"; b_=f" de {plan:,}"   # PORHACER15OCT: lo que falta en ESTA estación
        c.setFont('Helvetica-Bold',9.5); wa=pdfmetrics.stringWidth(a_,'Helvetica-Bold',9.5); c.drawString(xs+3,ty,a_)
        c.setFont('Helvetica',6.8); c.setFillColor(MUT); c.drawString(xs+3+wa,ty,b_); c.setFillColor(INK)
        bx=xs+3; bw=w-6; T=plan or 1
        for n_,col in ((e,'#1F7A3A'),(h,'#5B9BD5'),(f,'#D5DAE0')):
            ww=bw*n_/T
            if ww>0: c.setFillColor(colors.HexColor(col)); c.rect(bx,y-RH+5,ww,4,stroke=0,fill=1); bx+=ww
        c.setFillColor(INK)
        if True:   # PORHACER15OCT: siempre dice cuántas faltan en esta estación
            c.setFont('Helvetica',5.6); c.setFillColor(MUT)
            txt=(f"{e:,} entregadas · " if e else '')+(f"{h:,} ya {HECHO.get(er,'hechas')}"+(f" → {sig}" if sig else '')+" · " if h else '')+f"{f:,} {PORH.get(er,'por hacer')}"
            c.drawString(x0+sum(ws[:3])+3,y-RH+4,ell(c,txt,'Helvetica',5.6,(ws[3] if (BLOQ and m.get('_esp')) else ws[3]+ws[4])-6)); c.setFillColor(INK)
        xs+=w
        # casillas para escribir
        c.setStrokeColor(RULE); c.setLineWidth(.5)
        for k in range(7,len(ws)):
            if COLS[k][0]=='Dibujo':   # IMG15OCT
                im_=imgs().get(m.get('sku') or '')
                if im_:
                    iw_,ih_=im_.getSize(); bw_,bh_=ws[k]-6,RH-6; sc_=min(bw_/iw_,bh_/ih_); dw_,dh_=iw_*sc_,ih_*sc_
                    c.drawImage(im_,xs+3+(bw_-dw_)/2,y-RH+3+(bh_-dh_)/2,width=dw_,height=dh_,mask='auto')
                else: c.setFont('Helvetica',6); c.setFillColor(MUT); c.drawCentredString(xs+ws[k]/2,y-RH/2-2,'sin dibujo'); c.setFillColor(INK)
            elif COLS[k][0]=='Notas': c.line(xs+4,y-RH+6,xs+ws[k]-4,y-RH+6)
            else: c.rect(xs+2,y-RH+3,ws[k]-4,RH-6,stroke=1,fill=0)
            xs+=ws[k]
        c.setStrokeColor(colors.HexColor('#C9CED4')); c.line(x0,y-RH,x0+TW,y-RH); y-=RH
    # HOJ9OCT: sin renglones libres para MOs que lleguen después (Moisés, 9-oct-2026)
    # MATCORTE15OCT (Moisés, 15-oct-2026): el recuadro "Material a utilizar" (el de MO en proceso, con stock) reemplaza a "Pedir a almacén".
    RQ=None
    if est=='Corte' and ARGS.tv:
        try: RQ=json.load(open(ARGS.tv)).get('reqCorte')
        except Exception as e_: print('sin reqCorte',e_)
    if est=='Corte' and RQ is not None:
        cw=[w_*TW/760 for w_ in (150,130,110,110,90,170)]; hd=['Material (SKU)','Tipo','Medida','Solicitar','Sobrante','Soleras en stock']; rr_=15
        hh=22+15+rr_*max(1,len(RQ))+14
        y-=10
        if y-hh<40: c.showPage(); y=cab()-6
        c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(x0,y-10,'Material a utilizar'); y-=18
        c.setFillColor(colors.HexColor('#E8EDF3')); c.rect(x0,y-15,sum(cw),15,stroke=0,fill=1); c.setFillColor(INK); c.setFont('Helvetica-Bold',8); xx=x0
        for h_,w_ in zip(hd,cw): c.drawString(xx+5,y-10.5,h_); xx+=w_
        y-=15
        if not RQ:
            c.setFont('Helvetica',8.4); c.drawString(x0+5,y-11,'Nada que pedir: las MOs de esta hoja ya terminaron su corte.'); y-=rr_
        for m_ in RQ:
            xx=x0; c.setFillColor(INK); c.setFont('Courier-Bold',8.4); c.drawString(xx+5,y-11,m_['sku']); xx+=cw[0]
            c.setFont('Helvetica',8.4); c.drawString(xx+5,y-11,m_.get('tipo','')); xx+=cw[1]; c.drawString(xx+5,y-11,m_.get('medida','')); xx+=cw[2]
            c.setFont('Helvetica-Bold',8.8); c.drawString(xx+5,y-11,'%s %s'%(f"{m_['cantidad']:,}",m_['unidad'])); xx+=cw[3]
            c.setFont('Helvetica',8.4); c.drawString(xx+5,y-11,('%s"'%m_['sobrante']) if m_.get('sobrante') else '—'); xx+=cw[4]
            c.setFont('Helvetica-Bold',8.6); c.setFillColor(colors.HexColor('#B42318') if m_.get('falta') else INK); c.drawString(xx+5,y-11,m_.get('stock','')); c.setFillColor(INK)
            c.setStrokeColor(RULE); c.setLineWidth(.4); c.line(x0,y-rr_,x0+sum(cw),y-rr_); y-=rr_
        mos_=sorted({mo for m_ in RQ for mo in m_.get('mos',[])},key=lambda s:int(s.split('-')[-1]) if s.split('-')[-1].isdigit() else 0)
        c.setFont('Helvetica-Oblique',7); c.setFillColor(MUT)
        c.drawString(x0,y-10,('MOs que aún no terminan Corte: '+', '.join(mos_)+'. ' if mos_ else '')+'Redondeado a piezas completas (1 pieza de solera = 144 in). En rojo: no alcanza el stock.'); c.setFillColor(INK); y-=14
    elif est=='Corte':
        y-=8; filas=sorted(ped.items()); hh=16+12*max(1,len(filas))
        if y-hh<40: c.showPage(); y=cab()-6
        c.setStrokeColor(INK); c.setLineWidth(.8); c.rect(x0,y-hh,TW,hh,stroke=1,fill=0)
        c.setFillColor(INK); c.setFont('Helvetica-Bold',8.6); c.drawString(x0+6,y-11,'PEDIR A ALMACÉN — soleras para lo que falta por cortar (consolidado por material, 1 solera = 144 in, redondeado hacia arriba)')
        yy=y-24
        if not filas: c.setFont('Helvetica',8); c.drawString(x0+10,yy,'Nada que pedir: las MOs de esta hoja ya terminaron su corte.')
        for sku,(tot,uom,mlist) in filas:
            n=math.ceil(tot/SOL_IN-1e-9) if uom=='in' else math.ceil(tot-1e-9)
            c.setFont('Helvetica-Bold',9); c.drawString(x0+10,yy,'%d %s'%(n,unidad(uom,n)))
            c.setFont('Courier-Bold',8); c.drawString(x0+80,yy,sku)
            c.setFont('Helvetica',7.4); c.setFillColor(MUT); c.drawString(x0+190,yy,'%s %s · %s'%(f"{tot:,.1f}".rstrip('0').rstrip('.'),uom,', '.join(mlist))); c.setFillColor(INK); yy-=12
        y-=hh
    c.setFont('Helvetica',7); c.setFillColor(MUT)
    c.drawString(x0,24,'DIMACO METALMECANICA · Hoja temporal mientras se aprende a usar la estación en la tablet. Lo anotado aquí se captura en Katana.')
    c.save(); return len(mos)
if __name__=='__main__':
    now=dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=6); hoy='%d-%s'%(now.day,MES[now.month-1]); hora=now.strftime('%H:%M')
    os.makedirs(ARGS.out,exist_ok=True)
    for app,est,proy in EST:
        if proy=='RACKS' and not ARGS.racks: continue
        nom='Hoja de avance - %s%s.pdf'%(est.replace('&','y'),('_'+ARGS.fs) if ARGS.fs else '')
        n=hoja(app,est,proy,os.path.join(ARGS.out,nom),hoy,hora); print(nom,n,'MOs')
