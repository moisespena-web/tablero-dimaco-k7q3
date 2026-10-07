"""TV MAFESA (y de ahí Racks vía mk_html.py): columna FALTAN (faltan en la estación actual · de total) + barra
entregadas / listas -> siguiente / faltan; casillas con avance = 'N listas'. 6-oct-2026 (Moisés). Idempotente (PZ6OCT)."""
import re,sys
f=sys.argv[1]; t=open(f).read()
if 'PZ6OCT' in t: print('ya'); sys.exit()
def rep(a,b):
    global t; assert t.count(a)==1,('NO UNICO',a[:90],t.count(a)); t=t.replace(a,b)
HELP='''/* PZ6OCT · 6-oct-2026 (Moisés): FALTAN X de total + barra entregadas / listas -> siguiente / faltan en la estación actual.
   plan = planeadas de la MO; entr = entregadas (completed_quantity); el av "x/y" de las notas cuenta sobre la MO completa. */
function avN(s){var m=/(\\d+)\\s*\\/\\s*(\\d+)/.exec(s||"");return m?[+m[1],+m[2]]:null;}
function pzMO(r){var y=0;for(var k in (r.av||{})){var a=avN(r.av[k]);if(a)y=Math.max(y,a[1]);}
  var plan=r.plan||y||r.piezas,entr=r.entr!=null?+r.entr:Math.max(0,plan-r.piezas),pend=Math.max(0,plan-entr);
  var est=estacion(r),i=-1,sig="";r.ops.forEach(function(o,k){if(o[0]===est)i=k;});
  for(var k=i+1;i>=0&&k<r.ops.length;k++){sig=LBL[r.ops[k][0]]||r.ops[k][0];break;}
  var a=est&&r.av?avN(r.av[est]):null,h=est?Math.min(pend,a?Math.max(0,a[0]-entr):0):pend;
  return {plan:plan,entr:entr,listas:h,faltan:Math.max(0,pend-h),est:est?(LBL[est]||est):"",sig:sig};}
function listasOp(r,op){var a=avN(r.av&&r.av[op]);if(!a)return "";var p=pzMO(r);return nf(Math.max(0,a[0]-p.entr))+" listas";}
function barraTV(p){var T=p.plan||1,w=function(n){return (100*n/T).toFixed(2)+"%";};
  return '<div class="pzbar"><i style="width:'+w(p.entr)+';background:#25A35A"></i><i style="width:'+w(p.listas)+';background:#3E8FD8"></i><i style="width:'+w(p.faltan)+';background:#2E3D52"></i></div>';}
'''
rep('function celda(r,op){',HELP+'function celda(r,op){')
rep("""<span class="oplbl'+(a?' avn':'')+'">'+(a?esc(a):LBL[op])+'</span></div>';""",
    """<span class="oplbl'+(a?' avn':'')+'">'+(a?esc(listasOp(r,op)||a):LBL[op])+'</span></div>';""")
rep("""'<div class="pz"><b>'+r.piezas+'</b><span>pz</span></div>'+""",
    """'<div class="pz" title="'+esc(pzMO(r).entr+' entregadas · '+pzMO(r).listas+' listas'+(pzMO(r).sig?' → '+pzMO(r).sig:'')+' · '+pzMO(r).faltan+' faltan'+(pzMO(r).est?' en '+pzMO(r).est:''))+'"><b>'+nf(pzMO(r).faltan)+'</b><span>de '+nf(pzMO(r).plan)+'</span></div>'+""")
rep("""'<div class="dl"><b>'+fmtF(r.entrega||r.deadline)+'</b>'+b+'</div></div>';""",
    """'<div class="dl"><b>'+fmtF(r.entrega||r.deadline)+'</b>'+b+'</div>'+barraTV(pzMO(r))+'</div>';""")
rep("""'<div class="pz">CANT.</div>""","""'<div class="pz">FALTAN</div>""")
rep('<span class="lg"><i style="background:var(--none)"></i>No iniciada</span>',
    '<span class="lg"><i style="background:var(--none)"></i>No iniciada</span>'
    '<span class="lg" style="margin-left:18px"><i style="background:#25A35A;border-radius:2px"></i>Entregadas</span>'
    '<span class="lg"><i style="background:#3E8FD8;border-radius:2px"></i>Listas → siguiente estación</span>'
    '<span class="lg"><i style="background:#2E3D52;border-radius:2px"></i>Faltan en la estación</span>')
css='.row{position:relative}.row.head .pz{text-align:right}.pz b{display:block;line-height:1}.pz span{display:block;margin:2px 0 0;font-size:14px}'\
    '.pzbar{position:absolute;left:14px;right:14px;bottom:2px;height:5px;border-radius:3px;overflow:hidden;display:flex;background:#2E3D52;opacity:.95}.pzbar i{display:block;height:100%}'
i=t.rindex('</style>'); t=t[:i]+css+t[i:]
t=re.sub(r'v2026-10-06a','v2026-10-06b',t)
open(f,'w').write(t); print('ok')
