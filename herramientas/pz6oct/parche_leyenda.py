"""8a parte (9-nov-2026 · LEY9NOV): en el PDF de MO en proceso la leyenda "724 dobladas = ya hechas…" se encimaba
con la de la barra (entregadas / ya hechas → sig. / por hacer). La barra pasa a su propio renglón. Idempotente."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
p=os.path.join(D,'build_pdf_entregas.py')
if os.path.exists(p):
    t=open(p).read()
    a='''    c.drawString(x+32,y-2.2,"= ya hechas en esa estación (pasan a la siguiente) · Faltan X de Y = lo que falta entregar de la MO, igual que el Remaining de Katana"); x+=380'''
    b='''    c.drawString(x+pdfmetrics.stringWidth("724 dobladas","Helvetica-Bold",6.4)+3,y-2.2,"= ya hechas en esa estación (pasan a la siguiente) · Faltan X de Y = lo que falta entregar de la MO, igual que el Remaining de Katana"); y-=10; x=36  # LEY9NOV'''
    if 'LEY9NOV' in t or "y-=10; x=36" in t: print('ya (8a)')
    else:
        assert t.count(a)==1,'8a: no encontré la leyenda'; open(p,'w').write(t.replace(a,b)); print('ok (8a)')
print('listo 8 (leyenda)')
