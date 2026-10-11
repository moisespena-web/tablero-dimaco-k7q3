"""4a parte del parche de reportes (Moisés, 11-oct-2026 · COLOR11OCT):
"lo que se hace en los tableros, se hace en tabletas y archivos, es decir en todo".
- Cada estación tiene SU color (igual que la TV y las tabletas). En papel/blanco se usa el tono oscuro de cada color.
- La rayita de cada MO = color de la estación donde está la MO (verde si ya terminó todo).
- Se quitan los TIPOS (leyenda y columna): todos saben que va Corte → estaciones → Limpieza & SQA.
Uso: python3 parche_colores.py DIR  (lo llama parche_reportes.py al final). Idempotente. Imprime "listo 4 (colores)"."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
CP='{"Corte":"#1F6FD1","Taladro":"#6E4BD8","CNC":"#D6337F","Doblez":"#6F8C00","Limpieza & SQA":"#0E9C9C"}'
def patch(fn,pares,helper=None,after=None):
    p=os.path.join(D,fn)
    if not os.path.exists(p): print('no está (se omite)',fn); return
    t=open(p).read()
    if 'COLOR11OCT' in t: print('ya (4a)',fn); return
    for a,b in pares:
        n=t.count(a); assert n==1,('%s: NO ENCONTRADO (%d) -> %s'%(fn,n,a[:110])); t=t.replace(a,b)
    if helper:
        i=t.index(after)+len(after); t=t[:i]+helper+t[i:]
    open(p,'w').write('# COLOR11OCT\n'+t); print('ok (4a)',fn)

H_PY='''
# COLOR11OCT · color fijo por estación (Moisés 11-oct-2026; tono oscuro para fondo blanco)
CEST_P=%s
def est_act(r):
    return next((o for o,s in r.get("ops",[]) if s!="COMPLETED"),None)
def col_act(r):
    e=est_act(r); return CEST_P.get(e,"#1B8A4B") if e else "#1B8A4B"
''' % CP

# PDF
patch('build_pdf_entregas.py',[
 ('t=r.get("tipo","Mixto"); acc=colors.HexColor(TC.get(t,"#8A93A6")); prio=bool(r.get("prio"))',
  'acc=colors.HexColor(col_act(r)); prio=bool(r.get("prio"))'),
 ('c.setFillColor(PRIO_BAR if prio else acc); c.rect(36,y-RH,6.5 if prio else 2.6,RH,stroke=0,fill=1)',
  'c.setFillColor(PRIO_BAR if prio else acc); c.rect(36,y-RH,6.5 if prio else 2.6,RH,stroke=0,fill=1)'),
 ('''            if k in OPK.values() or k in ("piezas",): c.drawCentredString(cx+w/2,y-10.5,l)
            else: c.drawString(cx+2,y-10.5,l)''',
  '''            ko={v_:k_ for k_,v_ in OPK.items()}.get(k)
            if ko: c.setFillColor(colors.HexColor(CEST_P.get(ko,"#333333"))); c.drawCentredString(cx+w/2,y-10.5,l); c.rect(cx+3,y-14.2,w-6,1.6,stroke=0,fill=1); c.setFillColor(INK)
            elif k in ("piezas",): c.drawCentredString(cx+w/2,y-10.5,l)
            else: c.drawString(cx+2,y-10.5,l)'''),
 ('''    for tp in ["Tipo 1","Tipo 2","Tipo 3","Tipo 4","Tipo 5","Mixto"]:
        w=pill(c,x,y-3,tp.upper(),colors.HexColor(TC[tp])); c.setFillColor(colors.HexColor("#333333")); c.setFont("Helvetica",6.2)
        c.drawString(x+w+3,y-1,TPROC[tp]); x+=w+pdfmetrics.stringWidth(TPROC[tp],"Helvetica",6.2)+14
    c.setFont("Helvetica-Oblique",6.2); c.setFillColor(MUTED); c.drawString(x,y-1,"· Todas terminan en Limpieza & SQA")''',
  '''    for o_,l_ in (("Corte","CORTE"),("Taladro","TALADRO"),("CNC","TM-2P"),("Doblez","DOBLEZ"),("Limpieza & SQA","LIMPIEZA")):
        c.setFillColor(colors.HexColor(CEST_P[o_])); c.rect(x,y-3.4,4,8,stroke=0,fill=1); c.setFont("Helvetica-Bold",6.4); c.drawString(x+6,y-1,l_); x+=pdfmetrics.stringWidth(l_,"Helvetica-Bold",6.4)+16
    c.setFont("Helvetica-Oblique",6.2); c.setFillColor(MUTED); c.drawString(x,y-1,"= color de cada estación · la rayita de cada MO es la estación donde está")'''),
],helper=H_PY,after='from reportlab.lib.utils import ImageReader\n')

# Widget
patch('build_widget_entregas.py',[
 ('t=r.get("tipo","Mixto"); c=TC.get(t,"#8A93A6"); done=','c=col_act(r); done='),
 ('.card.cu{{background:#FBEFE7;border-color:#D9773F}}','.card.cu{{background:#FBEFE7;border-color:#D9773F;color:#16181D;padding:10px 12px;font-size:14px;font-weight:400;border-radius:10px}}'),
 ('''<span class="op {CLS.get(s,"none")}">{LBL.get(o,o)}''','''<span class="op {CLS.get(s,"none")}" style="border-top:3px solid {CEST_P.get(o,"#9CA3AF")}"><b style="color:{CEST_P.get(o,"#374151")}">{LBL.get(o,o)}</b>'''),
 ('''    ley="".join(f'<span><i style="background:{TC[k]}">{k.upper()}</i> {v}</span>' for k,v in TPROC.items())+'<span style="color:#6B7280;font-style:italic">· Todas terminan en Limpieza &amp; SQA</span>\'''',
  '''    ley="".join(f'<span><i style="background:{CEST_P[k]}">{LBL[k].upper()}</i></span>' for k in ("Corte","Taladro","CNC","Doblez","Limpieza & SQA"))+'<span style="color:#6B7280;font-style:italic">= color de cada estación · la rayita de cada MO es la estación donde está</span>\''''),
],helper=H_PY,after='E=html.escape\n')

# Excel: columna "Tipo" -> "Está en" (estación actual en su color); encabezados de estaciones en su color
patch('build_xlsx_mo.py',[
 ("H=['#','MO','# OC','Tipo','SKU',","H=['#','MO','# OC','Está en','SKU',"),
 ("occ,x['tipo'],x['sku'],","occ,{'CNC':'TM-2P','Limpieza & SQA':'Limpieza'}.get(est_act(x),est_act(x) or 'Terminada'),x['sku'],"),
 ("    ws.cell(r,5).fill=PatternFill('solid',fgColor='DCE8F5');",
  "    ws.cell(r,4).font=Font(bold=True,color=col_act(x)[1:]); ws.cell(r,4).border=Border(top=thin,bottom=thin,right=thin,left=Side(style='thick',color=col_act(x)[1:]))\n    ws.cell(r,5).fill=PatternFill('solid',fgColor='DCE8F5');"),
 ("ws.row_dimensions[HR].height=30",
  "ws.row_dimensions[HR].height=30\nfor o_,j_ in (('Corte',8),('Taladro',9),('CNC',10),('Doblez',11),('Limpieza & SQA',12)): ws.cell(HR,j_).fill=PatternFill('solid',fgColor=CEST_P[o_][1:])"),
],helper=H_PY+'from openpyxl.styles import Side\n',after='from openpyxl.drawing.image import Image\n')
print('listo 4 (colores)')
