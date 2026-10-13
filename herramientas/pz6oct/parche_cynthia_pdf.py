"""6a parte (Moisés, 12-oct-2026 · CYN12OCT): el PDF de MO en proceso se divide en 2.
Hoja(s) 1: solo las MOs que todavía usan máquinas (Corte, Taladro, TM-2P, Doblez), su TOTAL EN MÁQUINAS, leyendas y
"Material a utilizar". Salto de hoja y hoja aparte "MO en proceso · Limpieza & SQA (Cynthia)" con las MOs que solo
esperan Limpieza & SQA, la alarma de Cynthia y su TOTAL CYNTHIA. Idea: no confundir al personal de máquinas.
Se aplica sobre build_pdf_entregas.py ya parchado (partes 1 a 5). Idempotente. Imprime "listo 6 (cynthia)"."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
p=os.path.join(D,'build_pdf_entregas.py')
t=open(p).read()
if 'CYN12OCT' in t:
    print('ya (6a)')
else:
    # 1) la alarma de Cynthia sale de la hoja de máquinas (se pinta en su propia hoja)
    a='    al=D.get("alertaLimpieza")\n    if al:\n'
    assert t.count(a)==1,'parche_cynthia: alerta NO ENCONTRADA'
    t=t.replace(a,'    al=D.get("alertaLimpieza")\n    _hay_limp=any(x.get("grp")=="limp" for x in rows) and any(x.get("grp")!="limp" for x in rows)   # CYN12OCT\n    if al and not _hay_limp:\n')
    # 2) el cuerpo del ciclo de renglones pasa a una función para pintarlo en dos pasadas
    ini='    for i,r in enumerate(rows):\n        if r.get("grp")=="limp" and (i==0 or rows[i-1].get("grp")!="limp"):\n'
    fin='    c.setFillColor(BAND); c.rect(36,y-rh,TW,rh,stroke=0,fill=1); c.setFillColor(INK); c.setFont("Helvetica-Bold",7.2)\n    c.drawString(41,y-rh+4.6,f"TOTAL · {n}'
    assert t.count(ini)==1 and t.count(fin)==1,'parche_cynthia: ciclo de renglones NO ENCONTRADO'
    i0=t.index(ini); i1=t.index(fin)
    cuerpo=t[i0+len('    for i,r in enumerate(rows):\n'):i1]
    nuevo=('    def _fila(i,r,y):   # CYN12OCT\n'+cuerpo+'        return y\n'
           '    for i,r in enumerate(rows):\n'
           '        if _hay_limp and r.get("grp")=="limp": continue   # CYN12OCT: lo de Cynthia va en su propia hoja\n'
           '        y=_fila(i,r,y)\n')
    t=t[:i0]+nuevo+t[i1:]
    # 3) el total de la primera hoja es solo de máquinas
    c_='    c.drawString(41,y-rh+4.6,f"TOTAL · {n} Make orders ({n-len(nl)} en máquina + {len(nl)} con Cynthia)"); cx,cw=xs["piezas"]; c.drawCentredString(cx+cw/2,y-rh+4.6,f"{sum(calc(r)[\'pend\'] for r in rows):,} de {sum(calc(r)[\'plan\'] for r in rows):,}"); y-=rh\n'
    assert t.count(c_)==1,'parche_cynthia: TOTAL NO ENCONTRADO'
    t=t.replace(c_,'''    if _hay_limp:   # CYN12OCT
        nm=[x for x in rows if x.get("grp")!="limp"]
        c.drawString(41,y-rh+4.6,f"TOTAL EN MÁQUINAS · {len(nm)} Make orders  (Cynthia: {len(nl)} órdenes en la hoja aparte)"); cx,cw=xs["piezas"]; c.drawCentredString(cx+cw/2,y-rh+4.6,f"{sum(calc(x)['pend'] for x in nm):,} de {sum(calc(x)['plan'] for x in nm):,}"); y-=rh
    else:
'''+'    '+c_)
    # 4) hoja aparte de Cynthia, después de la de máquinas
    d_='    sc_=[]   # regla 5-oct'
    assert t.count(d_)==1,'parche_cynthia: fin de hoja NO ENCONTRADO'
    t=t.replace(d_,'''    if _hay_limp:   # CYN12OCT: hoja de Cynthia
        y=H-30
        if img:
            iw,ih=img.getSize(); c.drawImage(img,36,y-26,width=34*iw/ih,height=34,mask="auto")
        c.setFillColor(INK); c.setFont("Helvetica-Bold",16); c.drawCentredString(W/2,y-6,"MO en proceso · Limpieza & SQA (Cynthia)")
        c.setFont("Helvetica",9.5); c.setFillColor(MUTED); c.drawCentredString(W/2,y-19,f"Solo les falta Limpieza & SQA · no ocupan máquina · no cuentan en las {len(nm)} MOs del programa")
        c.setFont("Helvetica-Bold",10); c.setFillColor(INK); c.drawRightString(W-36,y-6,"Cliente: MAFESA")
        c.setFont("Helvetica",8.5); c.setFillColor(MUTED); c.drawRightString(W-36,y-18,date_str)
        if time_str: c.setFont("Helvetica",7.6); c.drawRightString(W-36,y-27,time_str)
        y-=44; c.setStrokeColor(RULE); c.line(36,y,W-36,y); y-=6
        if al:
            c.setStrokeColor(INK); c.setLineWidth(1.2); c.setFillColor(colors.HexColor("#FFFFFF")); c.roundRect(36,y-16,W-72,16,3,stroke=1,fill=1); c.setLineWidth(1)
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawString(44,y-11,"CYNTHIA: %d ÓRDENES (%d%%) ESPERAN LIMPIEZA & SQA — terminemos su limpieza e inspección y liberémoslas en Katana para que entren órdenes nuevas a las máquinas."%(al["n"],al["pct"]))
            y-=22
        y=HDR(y)
        for i,r in enumerate(rows):
            if r.get("grp")=="limp": y=_fila(i,r,y)
        c.setFillColor(BAND); c.rect(36,y-rh,TW,rh,stroke=0,fill=1); c.setFillColor(INK); c.setFont("Helvetica-Bold",7.2)
        c.drawString(41,y-rh+4.6,f"TOTAL CYNTHIA · {len(nl)} Make orders (solo Limpieza & SQA)"); cx,cw=xs["piezas"]; c.drawCentredString(cx+cw/2,y-rh+4.6,f"{sum(calc(x)['pend'] for x in nl):,} de {sum(calc(x)['plan'] for x in nl):,}"); y-=rh
        c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(36,34,W-36,34)
        c.setFont("Helvetica",6.2); c.setFillColor(MUTED); c.drawRightString(W-36,24,"DIMACO METALMECANICA · Hoja de Cynthia (Limpieza & SQA) · mismo programa que el tablero de TV")
        c.showPage()
'''+d_)
    open(p,'w').write('# CYN12OCT\n'+t); print('ok (6a)')
print('listo 6 (cynthia)')
