#!/usr/bin/env python3
"""Regla Limpieza & SQA (Moisés, 3-oct-2026) para los scripts del skill tablero-entregas-mafesa.
Uso: python3 regla_limpieza.py build_entregas.py [build_pdf_entregas.py] [build_widget_entregas.py]
Idempotente: si el script ya trae la regla (marca '_limp'/'grp")=="limp"'), no lo toca.
- El objetivo de 19 cuenta solo MOs con trabajo de máquina pendiente; las que solo esperan Limpieza & SQA
  van al final (grp="limp") y no ocupan lugar.
- alertaLimpieza en tv_datos si >30% de los SKUs con MO abierta solo esperan Limpieza (None si no).
- PDF y widget: renglón/título "SOLO FALTA LIMPIEZA & SQA" antes del grupo; el widget muestra la alerta."""
import sys
P=[("_casi=set(pendops)<= {'Limpieza & SQA'},","_casi=set(pendops)<= {'Limpieza & SQA'},_limp=bool(o) and set(pendops)<= {'Limpieza & SQA'},"),
("r['grp']='urge' if r['prio'] else ('hoy' if S[i]==HOY else 'sig')","r['grp']='limp' if r['_limp'] else ('urge' if r['prio'] else ('hoy' if S[i]==HOY else 'sig'))"),
("tv.sort(key=lambda r:(0 if r['prio'] else 1, r['entrega'], r['_g'], r['_old']))","tv.sort(key=lambda r:(1 if r['_limp'] else 0, 0 if r['prio'] else 1, r['entrega'], r['_g'], r['_old']))   # regla 3-oct-2026: las que solo esperan Limpieza & SQA van al final"),
("huecos=max(0,a.objetivo-len(tv))","en_maq=sum(1 for r in tv if not r['_limp'])   # regla 3-oct-2026: el objetivo de 19 cuenta solo MOs con trabajo de máquina pendiente\nhuecos=max(0,a.objetivo-en_maq)"),
("en_programa=len(tv),","en_programa=en_maq,solo_limpieza=len(tv)-en_maq,"),
("for r in datos['rows']: r['nota']=''\n","""for r in datos['rows']: r['nota']=''
# ---------- alerta Limpieza & SQA para Cynthia (regla de Moisés, 3-oct-2026) ----------
# Si más del 30% de los SKUs con MO abierta solo esperan Limpieza & SQA, la TV muestra alarma roja con sirena.
sk_all={r['sku'] for r in tv}; sk_l={r['sku'] for r in tv if r['_limp']}
datos['alertaLimpieza']=(dict(n=sum(1 for r in tv if r['_limp']),skus=len(sk_l),total=len(sk_all),pct=round(100*len(sk_l)/len(sk_all)))
    if sk_all and len(sk_l)/len(sk_all)>0.30 else None)   # None explícito: update del tablero borra la alerta vieja
""")]
PDF=[("TW=x-36; n=len(rows); rh=","TW=x-36; n=len(rows)+(1 if any(r.get('grp')=='limp' for r in rows) else 0); rh="),
("    for i,r in enumerate(rows):\n        t=r.get(\"tipo\",\"Mixto\")",'''    for i,r in enumerate(rows):
        if r.get("grp")=="limp" and (i==0 or rows[i-1].get("grp")!="limp"):   # regla 3-oct-2026: grupo de Cynthia al final
            nl=sum(1 for x in rows if x.get("grp")=="limp")
            c.setFillColor(colors.HexColor("#FBECEC")); c.rect(36,y-rh,TW,rh,stroke=0,fill=1); c.setFillColor(INK); c.setFont("Helvetica-Bold",7.2)
            c.drawString(41,y-rh+4.4,f"SOLO FALTA LIMPIEZA & SQA (Cynthia) · {nl} órdenes · {sum(x['piezas'] for x in rows if x.get('grp')=='limp'):,} pz"); y-=rh
        t=r.get("tipo","Mixto")''')]
WID=[("    for i,r in enumerate(rows):\n        t=r.get(\"tipo\",\"Mixto\"); c=TC",'''    for i,r in enumerate(rows):
        if r.get("grp")=="limp" and (i==0 or rows[i-1].get("grp")!="limp"): cards.append('<h3 class="limp">SOLO FALTA LIMPIEZA &amp; SQA · Cynthia</h3>')
        t=r.get("tipo","Mixto"); c=TC'''),
("    mat=(f'<div class=\"falta\">",'''    al=D.get("alertaLimpieza")
    alh=(f'<div class="falta"><b>🚨 Cynthia: {al["n"]} órdenes ({al["pct"]}%) esperan Limpieza &amp; SQA.</b><div>Por favor terminemos su limpieza e inspección y liberémoslas en Katana para que entren órdenes nuevas a las máquinas.</div></div>') if al else ''
    mat=(f'<div class="falta">'''),
("{mat}{\"\".join(cards)}","{alh}{mat}{\"\".join(cards)}"),
(".foot{{","h3.limp{{color:#B42318;border-top:2px solid #B42318;padding-top:8px}}\n.foot{{")]

PDF2=[('f"TOTAL · {n} Make orders"','f"TOTAL · {len(rows)} Make orders"')]
def aplica(f,P):
    s=open(f).read()
    for a,b in P:
        if s.count(a)==1: s=s.replace(a,b)
        elif s.count(b.split(chr(10))[0])>=1: pass
        else: print('AVISO: no encontré',repr(a[:60]),'en',f)
    open(f,'w').write(s)
for f in sys.argv[1:]:
    s=open(f).read()
    if 'build_entregas' in f or 'Arma el programa de entregas' in s:
        if "_limp" in s: print('ya trae la regla:',f); continue
        aplica(f,P)
    elif 'import reportlab' in s or 'from reportlab' in s:
        if 'grupo de Cynthia' in s: print('ya trae la regla:',f); continue
        aplica(f,PDF+PDF2)
    else:
        if 'h3 class="limp"' in s: print('ya trae la regla:',f); continue
        aplica(f,WID)
    print('ok',f)
