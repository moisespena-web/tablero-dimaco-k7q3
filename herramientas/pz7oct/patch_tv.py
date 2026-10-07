"""PZ7OCT (Moisés, 6-oct-2026 23:06): TV, estaciones y Katana dicen lo mismo.
El número grande es FALTAN = remaining de Katana (planeadas − entregadas) de TOTAL (planeadas).
La barra explica dónde están las que faltan: entregadas · ya <hechas> → siguiente · por <hacer> aquí.
Aplica a index.html (TV MAFESA) y racks/index.html. Idempotente. Uso: python3 patch_tv.py REPO [BUILD]"""
import sys,re
R=sys.argv[1]; BUILD=sys.argv[2] if len(sys.argv)>2 else None
VB='''/* PZ7OCT · 6-oct-2026 23:06 (Moisés): el número grande es el Remaining de Katana (FALTAN = planeadas − entregadas). */
var HECHO={"Corte":"cortadas","Taladro":"taladradas","TM-2P":"maquinadas","Doblez":"dobladas","Limpieza":"limpias","Láser":"cortadas en láser","Router":"ruteadas","Armado":"armadas","Pintura":"pintadas","Vestido":"vestidas"};
var PORH={"Corte":"por cortar","Taladro":"por taladrar","TM-2P":"por maquinar","Doblez":"por doblar","Limpieza":"por limpiar","Láser":"por cortar en láser","Router":"por rutear","Armado":"por armar","Pintura":"por pintar","Vestido":"por vestir"};
function hechoDe(e){return HECHO[e]||"hechas";}function porDe(e){return PORH[e]||"por hacer";}
'''
for f in ['index.html','racks/index.html']:
    p=f'{R}/{f}'; s=open(p,encoding='utf-8').read()
    if 'PZ7OCT' not in s:
        s=s.replace('/* PZ6OCT2 · barra gruesa',VB+'/* PZ6OCT2 · barra gruesa',1)
        s=s.replace('return {plan:plan,entr:entr,listas:h,faltan:Math.max(0,pend-h),est:est?(NOMEST[est]||est):"",sig:sig};}',
                    'return {plan:plan,entr:entr,pend:pend,listas:h,faltan:Math.max(0,pend-h),est:est?(NOMEST[est]||est):"",sig:sig};}',1)
        old="(p.listas?'<span><i style=\"background:#3E8FD8\"></i>'+nf(p.listas)+(p.listas===1?' lista':' listas')+(p.sig?' → '+esc(p.sig):' para entregar')+'</span>':'')+\n    '<span><i style=\"background:#2E3D52\"></i>'+nf(p.faltan)+' faltan'+(p.est?' en '+esc(p.est):'')+'</span></div>';"
        new="(p.listas?'<span><i style=\"background:#3E8FD8\"></i>'+nf(p.listas)+' ya '+hechoDe(p.est)+(p.sig?' → '+esc(p.sig):' → entregar')+'</span>':'')+\n    '<span><i style=\"background:#2E3D52\"></i>'+nf(p.faltan)+' '+porDe(p.est)+'</span></div>';"
        assert old in s,(f,'leyenda'); s=s.replace(old,new,1)
        old="'<div class=\"pz\" title=\"'+esc(pzMO(r).entr+' entregadas · '+pzMO(r).listas+' listas'+(pzMO(r).sig?' → '+pzMO(r).sig:'')+' · '+pzMO(r).faltan+' faltan'+(pzMO(r).est?' en '+pzMO(r).est:''))+'\"><b>'+nf(pzMO(r).faltan)+'</b>"
        new="'<div class=\"pz\" title=\"'+esc('Katana: '+pzMO(r).plan+' planeadas · '+pzMO(r).entr+' entregadas · '+pzMO(r).pend+' faltan')+'\"><b>'+nf(pzMO(r).pend)+'</b>"
        assert old in s,(f,'celda'); s=s.replace(old,new,1)
        old='var n=Math.max(0,a[0]-p.entr);return nf(n)+(n===1?" lista":" listas");}'
        new='var n=Math.max(0,a[0]-p.entr);return nf(n)+" "+hechoDe(NOMEST[op]||op);}'
        assert old in s,(f,'listasOp'); s=s.replace(old,new,1)
        s=s.replace('<i style="background:#3E8FD8;border-radius:2px"></i>Listas → sig.</span>','<i style="background:#3E8FD8;border-radius:2px"></i>Ya hechas → sig.</span>')
        s=s.replace('<i style="background:#2E3D52;border-radius:2px"></i>Faltan</span>','<i style="background:#2E3D52;border-radius:2px"></i>Por hacer</span>')
    if BUILD: s=re.sub(r'<span class="build">[rv][0-9a-z-]+</span>','<span class="build">'+(('r'+BUILD[1:]) if f.startswith('racks') else BUILD)+'</span>',s)
    open(p,'w',encoding='utf-8').write(s); print('ok',f)
# 2) EN PAUSA en la TV (Katana PAUSED) — celda roja con Ⅱ
for f in ['index.html','racks/index.html']:
    p=f'{R}/{f}'; s=open(p,encoding='utf-8').read()
    if 'op.pausa' not in s:
        s=s.replace('.op.prog .oplbl{color:#FFD37A}','.op.prog .oplbl{color:#FFD37A}\n.op.pausa{background:#2A1418;border-color:#7A2A2E}\n.op.pausa .dot{background:#E5484D;color:#fff;font-size:13px;display:flex;align-items:center;justify-content:center}\n.op.pausa .oplbl{color:#FFB3B6}',1)
        a='var c={COMPLETED:"done",IN_PROGRESS:"prog",PAUSED:"prog",NOT_STARTED:"none"}[st]||"none";\n  var k={done:"&#10003;",prog:"&#9679;",none:""}[c];'
        assert a in s,(f,'celda pausa')
        s=s.replace(a,'var c={COMPLETED:"done",IN_PROGRESS:"prog",PAUSED:"pausa",NOT_STARTED:"none"}[st]||"none";\n  var k={done:"&#10003;",prog:"&#9679;",pausa:"&#10074;&#10074;",none:""}[c];',1)
        s=s.replace('<span class="lg"><i style="background:var(--prog)"></i>En proceso</span>','<span class="lg"><i style="background:var(--prog)"></i>En proceso</span><span class="lg"><i style="background:#E5484D"></i>En pausa</span>',1)
    open(p,'w',encoding='utf-8').write(s); print('ok pausa',f)
