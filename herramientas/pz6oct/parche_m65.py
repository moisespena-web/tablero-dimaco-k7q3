"""9a parte (9-nov-2026 · M659NOV): la operación M65 (resource M65, estación nueva del 16-oct-2026) se perdía en
build_entregas.py (ORDOPS no la traía): una MO con M65 pendiente salía como "solo falta Limpieza & SQA" (grupo de Cynthia)
y en el PDF no se veía su M65. La TV ya tiene columna M65. Ahora: ops trae M65; el PDF lleva columna M65 (color papel
#A88600; en pantalla #F5D547). El Excel muestra M65 como estación actual (col. D) y en el desglose. Idempotente."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
def P(fn,pares):
    p=os.path.join(D,fn)
    if not os.path.exists(p): return
    t=open(p).read()
    if 'M659NOV' in t: print('ya (9a)',fn); return
    for a,b in pares:
        assert t.count(a)>=1,'9a %s: no encontré %s'%(fn,a[:80]); t=t.replace(a,b)
    open(p,'w').write('# M659NOV\n'+t); print('ok (9a)',fn)
P('build_entregas.py',[("ORDOPS=['Corte','Taladro','CNC','Doblez','Limpieza & SQA']","ORDOPS=['Corte','Taladro','M65','CNC','Doblez','Limpieza & SQA']")])
P('build_pdf_entregas.py',[
 ('"Taladro":"#6E4BD8","CNC"','"Taladro":"#6E4BD8","M65":"#A88600","CNC"'),
 ('LBL={"Corte":"Corte","Taladro":"Taladro","CNC"','LBL={"Corte":"Corte","Taladro":"Taladro","M65":"M65","CNC"'),
 ('OPK={"Corte":"corte","Taladro":"taladro","CNC"','OPK={"Corte":"corte","Taladro":"taladro","M65":"m65","CNC"'),
 ('("taladro","Taladro",34),("cnc","TM-2P",28)','("taladro","Taladro",34),("m65","M65",26),("cnc","TM-2P",28)'),
 ('("Taladro","TALADRO"),("CNC","TM-2P")','("Taladro","TALADRO"),("M65","M65"),("CNC","TM-2P")'),
 ('HECHO={"Corte":"cortadas","Taladro":"taladradas",','HECHO={"Corte":"cortadas","Taladro":"taladradas","M65":"hechas en M65",'),
 ('PORH={"Corte":"por cortar","Taladro":"por taladrar",','PORH={"Corte":"por cortar","Taladro":"por taladrar","M65":"por M65",'),
])
P('build_xlsx_mo.py',[
 ('"Taladro":"#6E4BD8","CNC"','"Taladro":"#6E4BD8","M65":"#A88600","CNC"'),
 ('LBL={"Corte":"Corte","Taladro":"Taladro","CNC"','LBL={"Corte":"Corte","Taladro":"Taladro","M65":"M65","CNC"'),
])
print('listo 9 (M65)')
