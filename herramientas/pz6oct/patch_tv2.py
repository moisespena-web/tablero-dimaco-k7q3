"""TV (6-oct-2026, 2a parte, Moisés: "se ve genial en la estación, ponlo en el tablero"):
debajo de cada renglón va la misma barra GRUESA + leyenda de la estación
("1,200 entregadas · 724 listas → Limpieza · 1,576 faltan en Doblez"); la paginación cuenta la altura real.
Requiere patch_tv.py aplicado antes. Idempotente (PZ6OCT2)."""
import re,sys
f=sys.argv[1]; t=open(f).read()
if 'PZ6OCT2' in t: print('ya'); sys.exit()
def rep(a,b):
    global t; assert t.count(a)==1,('NO UNICO',a[:90],t.count(a)); t=t.replace(a,b)
old_bar=t[t.index('function barraTV(p){'):t.index('\n',t.index("'%;background:#2E3D52\"></i></div>';}",t.index('function barraTV(p){')))+1] if False else None
i=t.index('function barraTV(p){'); j=t.index('function celda(r,op){')
t=t[:i]+'''/* PZ6OCT2 · barra gruesa + leyenda como en las estaciones */
var NOMEST={"Corte":"Corte","Taladro":"Taladro","CNC":"TM-2P","Doblez":"Doblez","Limpieza & SQA":"Limpieza","Laser":"Láser","Router":"Router","Armado":"Armado","Pintura":"Pintura","Vestido":"Vestido"};
function barraTV(p){var T=p.plan||1,w=function(n){return (100*n/T).toFixed(2)+"%";};
  var b='<div class="pzw"><div class="pzbar"><i style="width:'+w(p.entr)+';background:#25A35A"></i><i style="width:'+w(p.listas)+';background:#3E8FD8"></i><i style="width:'+w(p.faltan)+';background:#2E3D52"></i></div>';
  if(p.entr+p.listas>0)b+='<div class="pzl">'+(p.entr?'<span><i style="background:#25A35A"></i>'+nf(p.entr)+' entregadas</span>':'')+
    (p.listas?'<span><i style="background:#3E8FD8"></i>'+nf(p.listas)+(p.listas===1?' lista':' listas')+(p.sig?' → '+esc(p.sig):' para entregar')+'</span>':'')+
    '<span><i style="background:#2E3D52"></i>'+nf(p.faltan)+' faltan'+(p.est?' en '+esc(p.est):'')+'</span></div>';
  return b+'</div>';}
function altoR(r){var p=pzMO(r);return ROWH_+(p.entr+p.listas>0?34:12);}
var ROWH_=53;
'''+t[j:]
# nombres legibles de estación en pzMO
rep('sig=LBL[r.ops[k][0]]||r.ops[k][0];','sig=NOMEST[r.ops[k][0]]||r.ops[k][0];')
rep('est:est?(LBL[est]||est):""','est:est?(NOMEST[est]||est):""')
# paginación por altura real
rep('''      var cab=Math.max(1,Math.floor((hDisp-CAB)/ROWH)),np=Math.ceil(xs.length/cab),per=Math.ceil(xs.length/np);
      for(var z=0,i=0;z<xs.length;z+=per,i++)bloques.push([tit+(np>1?" · "+(i+1)+"/"+np:""),xs.slice(z,z+per),null,cls]);''',
'''      ROWH_=ROWH;var cap=hDisp-CAB,pg=[],cur=[],h=0;
      xs.forEach(function(r){var a=altoR(r);if(cur.length&&h+a>cap){pg.push(cur);cur=[];h=0;}cur.push(r);h+=a;});
      if(cur.length)pg.push(cur);
      pg.forEach(function(p,i){bloques.push([tit+(pg.length>1?" · "+(i+1)+"/"+pg.length:""),p,null,cls]);});''')
css=('.row{flex-wrap:wrap;row-gap:3px;align-content:center}.pzw{flex-basis:100%;padding:0 0 3px 22px}'
     '.pzw .pzbar{position:static;height:9px;border-radius:5px}'
     '.pzl{display:flex;gap:4px 22px;margin-top:4px;font-size:17px;color:#C9D6E6;white-space:nowrap}'
     '.pzl i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}'
     '#pages.compacto .row{max-height:none;padding-top:4px}')
i=t.rindex('</style>'); t=t[:i]+css+t[i:]
t=re.sub(r'v2026-10-06b','v2026-10-06c',t)
open(f,'w').write(t); print('ok')
