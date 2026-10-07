"""Hojas de avance para anotar a pluma (temporal, pedido de Moisés 6-oct-2026) — una por estación MAFESA
(Corte, Taladro, TM-2P, Doblez, Limpieza & SQA), con las MOs que muestra cada app de estación.
Uso: python3 hojas_avance.py --repo <clon de tablero-dimaco-k7q3> --out <carpeta> --fs DD-MM_HH-MM [--racks]
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
AP=argparse.ArgumentParser(); AP.add_argument('--repo',default='/home/claude/tablero-dimaco-k7q3'); AP.add_argument('--out',default='/home/claude/hojas/out'); AP.add_argument('--fs',default=''); AP.add_argument('--racks',action='store_true')
ARGS=AP.parse_args(); REPO=ARGS.repo
EST=[('app-corte','Corte','MAFESA'),('app-taladro','Taladro','MAFESA'),('app-tm2p','TM-2P','MAFESA'),('app-doblez','Doblez','MAFESA'),('app-limpieza','Limpieza & SQA','MAFESA'),
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
COLS=[('#',18),('MO',48),('SKU',70),('Pieza',122),('Operación',60),('Entrega',40),('Faltan',62),
      ('Inicio',38),('Fin',38),('Piezas',40),('Inicio',38),('Fin',38),('Piezas',40),('Notas',0)]
def hoja(app,est,proy,out,hoy,hora):
    t=open('%s/%s/index.html'%(REPO,app)).read()
    mos=arr(t[t.index('mos:[{'):],'mos:[') if app=='app-tm2p' else arr(t,'var DATA=[')
    c=canvas.Canvas(out,pagesize=(W,H)); c.setTitle('Hoja de avance · '+est)
    x0=30; TW=W-60; fixed=sum(w for _,w in COLS); ws=[w or (TW-fixed) for _,w in COLS]
    RH=26; pag=[0]
    def cab():
        pag[0]+=1; y=H-28
        if LOGO:
            iw,ih=LOGO.getSize(); c.drawImage(LOGO,x0,y-30,width=34*iw/ih,height=34,mask='auto')
        c.setFillColor(INK); c.setFont('Helvetica-Bold',17); c.drawCentredString(W/2,y-8,'Hoja de avance · Estación %s'%est)
        c.setFont('Helvetica',9); c.setFillColor(MUT); c.drawCentredString(W/2,y-21,'%s · MOs de Katana al %s %s · hoja %d'%(proy,hoy,hora,pag[0]))
        c.setFillColor(INK); c.setFont('Helvetica',10)
        c.drawRightString(x0+TW,y-6,'Fecha: ____ / ____ / ______'); c.drawRightString(x0+TW,y-22,'Operador: ______________________')
        y-=44
        c.setFont('Helvetica',7.6); c.setFillColor(MUT)
        c.drawString(x0,y,'Por cada lapso de trabajo anota la hora de inicio, la hora de fin y cuántas piezas terminaste. "Faltan X de Y" = piezas que faltan en esta estación, de las Y de la MO.')
        y-=8
        # encabezado de grupos
        xs=x0
        gx=[x0+sum(ws[:7]),x0+sum(ws[:10]),x0+sum(ws[:13])]
        c.setFillColor(colors.HexColor('#E6E9EE')); c.rect(gx[0],y-12,gx[1]-gx[0],12,stroke=0,fill=1); c.rect(gx[1],y-12,gx[2]-gx[1],12,stroke=0,fill=1)
        c.setFillColor(INK); c.setFont('Helvetica-Bold',7.5); c.drawCentredString((gx[0]+gx[1])/2,y-9,'LAPSO 1'); c.drawCentredString((gx[1]+gx[2])/2,y-9,'LAPSO 2')
        y-=12
        c.setFillColor(colors.HexColor('#1F2A37')); c.rect(x0,y-15,TW,15,stroke=0,fill=1); c.setFillColor(colors.white); c.setFont('Helvetica-Bold',7.6)
        for (h,_),w in zip(COLS,ws): c.drawCentredString(xs+w/2,y-10.5,h); xs+=w
        return y-15
    y=cab()
    for i,m in enumerate(mos,1):
        if y-RH<40:
            c.showPage(); y=cab()
        plan,e,h,f,sig=pz(m)
        if m.get('prio'): c.setFillColor(colors.HexColor('#F7E2DC')); c.rect(x0,y-RH,TW,RH,stroke=0,fill=1)
        xs=x0; ty=y-11
        vals=[str(i),m['mo'],m.get('sku') or '—',m.get('nombre',''),m.get('paso') or m.get('opName') or '',fd(m.get('ent') or m.get('deadline') or '')]
        fonts=[('Helvetica',8),('Helvetica-Bold',8.4),('Courier-Bold',7.6),('Helvetica',7.8),('Helvetica',7.4),('Helvetica-Bold',8)]
        for k,(v,(fn,fs)) in enumerate(zip(vals,fonts)):
            c.setFillColor(INK); c.setFont(fn,fs); c.drawString(xs+3,ty,ell(c,v,fn,fs,ws[k]-6)); xs+=ws[k]
        if m.get('prio'): c.setFont('Helvetica-Bold',6.4); c.drawString(x0+sum(ws[:1])+3,y-21,'URGE')
        # Faltan X de Y + mini barra
        w=ws[6]; a_=f"{f:,}"; b_=f" de {plan:,}"
        c.setFont('Helvetica-Bold',9.5); wa=pdfmetrics.stringWidth(a_,'Helvetica-Bold',9.5); c.drawString(xs+3,ty,a_)
        c.setFont('Helvetica',6.8); c.setFillColor(MUT); c.drawString(xs+3+wa,ty,b_); c.setFillColor(INK)
        bx=xs+3; bw=w-6; T=plan or 1
        for n_,col in ((e,'#1F7A3A'),(h,'#5B9BD5'),(f,'#D5DAE0')):
            ww=bw*n_/T
            if ww>0: c.setFillColor(colors.HexColor(col)); c.rect(bx,y-RH+5,ww,4,stroke=0,fill=1); bx+=ww
        c.setFillColor(INK)
        if e or h:
            c.setFont('Helvetica',5.6); c.setFillColor(MUT)
            txt=(f"{e:,} entr. · " if e else '')+(f"{h:,} listas"+(f" → {sig}" if sig else '') if h else '')
            c.drawString(x0+sum(ws[:3])+3,y-RH+5,ell(c,txt,'Helvetica',5.6,ws[3]+ws[4]-6)); c.setFillColor(INK)
        xs+=w
        # casillas para escribir
        c.setStrokeColor(RULE); c.setLineWidth(.5)
        for k in range(7,len(ws)):
            c.rect(xs+2,y-RH+3,ws[k]-4,RH-6,stroke=1,fill=0); xs+=ws[k]
        c.setStrokeColor(colors.HexColor('#C9CED4')); c.line(x0,y-RH,x0+TW,y-RH); y-=RH
    # renglones libres para MOs que lleguen después
    c.setFont('Helvetica-Bold',8); c.setFillColor(INK)
    if y-RH*3-14<40: c.showPage(); y=cab()
    y-=6; c.drawString(x0,y-8,'MOs que lleguen después (anota MO y pieza):'); y-=12
    for _ in range(3):
        xs=x0; c.setStrokeColor(RULE)
        for k,w in enumerate(ws):
            if k in (1,2,3) or k>=7: c.rect(xs+2,y-RH+3,w-4,RH-6,stroke=1,fill=0)
            xs+=w
        y-=RH
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
