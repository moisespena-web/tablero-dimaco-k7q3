"""5a parte (11-oct-2026 · DL11OCT): arregla un choque de nombre en build_entregas.py.
En la reposición, la fecha límite de cada MO a crear se guardaba en `dl`, que es el mismo nombre del contador
de piezas entregadas; cuando crear.json traía renglones, el script tronaba más abajo
("'datetime.datetime' object is not subscriptable") y no se creaba nada. Se renombra a `dlx`. Idempotente."""
import sys,os
D=sys.argv[1] if len(sys.argv)>1 else '.'
p=os.path.join(D,'build_entregas.py')
t=open(p).read()
if 'DL11OCT' in t: print('ya (5a)')
else:
    a="        dl=dt.datetime.combine(dt.date.fromisoformat(x['entrega']),dt.time(19,0))"
    b="production_deadline_date=dl.strftime("
    assert t.count(a)==1 and t.count(b)==1,'parche_dl: NO ENCONTRADO'
    t=t.replace(a,a.replace('dl=','dlx=')).replace(b,b.replace('=dl.','=dlx.'))
    open(p,'w').write('# DL11OCT\n'+t); print('ok (5a)')
print('listo 5 (dl)')
