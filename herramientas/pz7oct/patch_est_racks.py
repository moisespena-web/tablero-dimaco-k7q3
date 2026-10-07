"""PZ7OCT en las 5 estaciones de Racks (plantilla vieja + PZ6OCT): Faltan = Remaining de Katana (m.piezas = planeadas − entregadas).
Uso: python3 patch_est_racks.py REPO. Idempotente."""
import sys
R=sys.argv[1]
V={'app-habilitado':('cortadas','por cortar','Por cortar'),'app-laser':('cortadas','por cortar','Por cortar'),'app-armado1':('armadas','por armar','Por armar'),
   'app-pintura':('pintadas','por pintar','Por pintar'),'app-vestido':('vestidas','por vestir','Por vestir')}
for app,(h,po,pc) in V.items():
    p=f'{R}/{app}/index.html'; s=open(p,encoding='utf-8').read()
    if 'PZ7OCT' in s: print('ya',app); continue
    pares=[("(h===1?' lista':' listas')+(s?' → '+E(s):' para entregar')","' ya "+h+"'+(s?' → '+E(s):' → entregar')"),
           ("fmtN(f)+' faltan aquí</span>","fmtN(f)+' "+po+"</span>"),
           ("<b style=\"font-size:22px\">'+fmtN(faltaPz(m))+'</b><span class=\"ks\"> de","<b style=\"font-size:22px\">'+fmtN(m.piezas)+'</b><span class=\"ks\"> de"),
           ("<b style=\"font-size:26px\">'+fmtN(faltaPz(m))+'</b>","<b style=\"font-size:26px\">'+fmtN(m.piezas)+'</b>"),
           ("<span>Listas aquí <b style=\"font-size:22px\">'+fmtN(hz(m))+'</b></span><span>Faltan <b style=\"font-size:22px\">'+fmtN(falt)+'</b> de '+fmtN(m.plan)+'</span>","<span>Ya "+h+" <b style=\"font-size:22px\">'+fmtN(hz(m))+'</b></span><span>"+pc+" <b style=\"font-size:22px\">'+fmtN(falt)+'</b></span>"),
           ("Listas aquí <b>'+fmtN(hz(m))+'</b><br>Faltan <b>'+fmtN(falt)+'</b> de '+fmtN(m.plan)+'</div>","Ya "+h+" <b>'+fmtN(hz(m))+'</b><br>"+pc+" <b>'+fmtN(falt)+'</b></div>")]
    for a,b in pares:
        n=s.count(a); assert n==1,(app,a[:60],n); s=s.replace(a,b)
    s=s.replace('/* PZ6OCT · 6-oct-2026','/* PZ7OCT · 6-oct-2026 23:06: Faltan = Remaining de Katana. PZ6OCT · 6-oct-2026',1)
    open(p,'w',encoding='utf-8').write(s); print('ok',app)
