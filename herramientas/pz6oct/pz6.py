"""Regla de Moisés (6-oct-2026) para mostrar piezas en piso, TV, PDF, widget y Excel.
FALTAN X (en la estación actual) · de TOTAL (planeadas de la MO), y el desglose que siempre suma el total:
  entregadas (completed_quantity de Katana) + listas (hechas en la estación actual, ya pasan a la siguiente) + faltan = total.
Las notas de la MO traen el avance como "x/y" sobre la MO completa, por eso listas = x - entregadas.
Misma lógica que pzMO() del index.html de la TV y barraPz() de las estaciones."""
import re
LBL={"Corte":"Corte","Taladro":"Taladro","CNC":"TM-2P","Doblez":"Doblez","Limpieza & SQA":"Limpieza"}
def avN(s):
    m=re.search(r'(\d+)\s*/\s*(\d+)',s or '');return (int(m.group(1)),int(m.group(2))) if m else None
def calc(r):
    av=r.get('av') or {}; y=max([a[1] for a in (avN(v) for v in av.values()) if a] or [0])
    piezas=int(r.get('piezas') or 0); plan=int(r.get('plan') or y or piezas)
    entr=int(r['entr']) if r.get('entr') is not None else max(0,plan-piezas); pend=max(0,plan-entr)
    ops=r.get('ops') or []; est=next((o for o,s in ops if s!='COMPLETED'),None)
    i=[o for o,_ in ops].index(est) if est else -1
    sig=LBL.get(ops[i+1][0],ops[i+1][0]) if est and i+1<len(ops) else ''
    a=avN(av.get(est)) if est else None
    listas=min(pend,max(0,a[0]-entr)) if (est and a) else (0 if est else pend)
    return dict(plan=plan,entr=entr,listas=listas,faltan=max(0,pend-listas),est=LBL.get(est,est or ''),sig=sig)
def listas_op(r,op):
    a=avN((r.get('av') or {}).get(op));
    n=max(0,a[0]-calc(r)['entr']) if a else 0
    return ('%s %s'%(f"{n:,}",'lista' if n==1 else 'listas')) if a else ''
def enriquecer(rows,mos):
    """rows de tv_datos.json; mos = lista de MOs de Katana (todas las respuestas). Agrega plan y entr por MO."""
    by={m.get('order_no'):m for m in mos}
    for r in rows:
        m=by.get(r.get('mo'))
        if m: r['plan']=int(m.get('planned_quantity') or 0) or r.get('piezas'); r['entr']=int(m.get('completed_quantity') or 0)
    return rows
