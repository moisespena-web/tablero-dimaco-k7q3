"""Paso 3 de la página de Racks (después de mk_html.py y grupo.py).
15-oct-2026 (Moisés): nuevo diseño de la página de producción ("RACKS · ORDEN DE ATAQUE"), el que aprobó en el lienzo:
 - lista compacta agrupada por cliente (banda de color del cliente), una MO por renglón;
 - la raya izquierda = color del departamento donde está la MO; la ruta muestra cada operación
   (✓ terminada, llena = en proceso, contorno = pendiente; la pendiente donde está la MO, con su color);
 - "FALTAN X de total" (Remaining de Katana) y entrega (VENCIDA en rojo);
 - panel derecho: dónde están las MOs por departamento, cuello de botella, avance por proceso y SO sin MO;
 - logo de Marca Guanajuato Internacional en el encabezado.
En la página de producción se ocultan los KPIs y la franja de flujo (como ya pasa en CALIDAD).
La página CALIDAD RACKS NO cambia (pedido de Moisés)."""
p = 'racks/index.html'
s = open(p).read()


def rep(old, new):
    global s
    assert s.count(old) == 1, ('NO ENCONTRADO/UNICO', old[:80])
    s = s.replace(old, new)


CSS = r'''
/* ---- 15-oct-2026: diseño ORDEN DE ATAQUE (página de producción de racks) ---- */
#stage:has(.prk.on) .krow,#stage:has(.prk.on) #ests{display:none}
#logoGto{display:none;height:92px;background:#FFFFFF;border-radius:10px;padding:4px 6px;box-shadow:0 2px 10px rgba(0,0,0,.35)}
#stage:has(.prk.on) #logoGto{display:block}
.page.prk{flex-direction:column}
.rkw{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 430px;gap:24px}
.rkl{display:flex;flex-direction:column;gap:3px;min-height:0;overflow:hidden}
.rkt{display:flex;justify-content:space-between;align-items:center;height:30px;flex:none;font-size:16px;letter-spacing:2px;color:#9FB3C8}
.rkt b{color:#EAF1F9;font-size:18px}
.rkt span{letter-spacing:0;font-size:21px;color:#E8EDF2;font-weight:700}
.rkt em{font-style:normal;color:#FFB4B4}
.rkr,.rkch{display:grid;grid-template-columns:10px 100px minmax(0,1fr) 500px 150px 235px;gap:14px;align-items:center;padding-right:16px}
.rkch{height:22px;flex:none;font-size:13px;letter-spacing:1.5px;color:#7F8E9D}
.rkch .r{text-align:right}
.rkr{height:31px;flex:none;background:#161B22;border-radius:6px;overflow:hidden}
.rkr.v{background:#22161A}
.rkr.pr{box-shadow:inset 0 0 0 2px #FFB020}
.rks{display:block;height:100%}
.rkm{font-weight:800;font-size:22px;white-space:nowrap}
.rkn{font-size:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rkn small{font-size:15px;color:#8696A6;margin-left:9px}
.rkn .bdg{font-size:13px;font-weight:800;padding:2px 7px;border-radius:4px;background:#FFB020;color:#111;margin-left:9px;vertical-align:2px}
.rkrt{display:flex;gap:5px;overflow:hidden}
.rkc{font-size:15px;line-height:1;padding:5px 8px;border-radius:4px;border:1.5px solid #2A323C;color:#6E7A87;white-space:nowrap}
.rkc.ok{border-color:transparent;color:#56636F}
.rkc.ip{color:#0E1116;font-weight:700;border-color:transparent}
.rkc.ps{background:#E5484D;color:#FFFFFF;border-color:transparent;font-weight:700}
.rkc.cur{font-weight:700}
.rke{text-align:right;font-size:19px;white-space:nowrap}
.rke.v{color:#FFB4B4;font-weight:800}
.rkf{text-align:right;font-size:25px;font-weight:800;white-space:nowrap}
.rkf small{font-size:14px;font-weight:400;color:#9FB3C8;margin-left:6px}
.rkh{height:36px;flex:none;display:flex;align-items:center;gap:14px;padding:0 16px;border-radius:6px;color:#FFFFFF;font-size:24px;font-weight:800;margin-top:4px;letter-spacing:.5px}
.rkh span{font-size:17px;font-weight:600;opacity:.92;letter-spacing:0}
.rka{display:flex;flex-direction:column;gap:10px;min-height:0;overflow:hidden}
.rkcard{background:#161B22;border:2px solid #232A33;border-radius:10px;padding:12px 20px;display:flex;flex-direction:column;gap:6px}
.rkct{font-size:24px;font-weight:800;letter-spacing:.5px}
.rkln{display:grid;grid-template-columns:200px minmax(0,1fr) 56px;gap:12px;align-items:center;font-size:18px;font-weight:700}
.rkbar{height:13px;background:#232A33;border-radius:7px;overflow:hidden;display:flex}
.rkbar i{display:block;height:100%;border-radius:7px}
.rknu{text-align:right;font-variant-numeric:tabular-nums}
.rkap{display:grid;grid-template-columns:120px minmax(0,1fr) 92px;gap:12px;align-items:center;font-size:16px}
.rkbt{border-radius:10px;padding:12px 20px;border:2px solid;display:flex;flex-direction:column;gap:4px}
.rkbt .l{font-size:14px;letter-spacing:1.5px;font-weight:700}
.rkbt .g{font-size:30px;font-weight:800;line-height:1.05}
.rkbt .s{font-size:17px;color:#D5DEE8}
.rkso{font-size:16px;color:#B8C4D0;line-height:1.45}
</style></head>'''
assert s.count('</style></head>') == 1
s = s.replace('</style></head>', CSS)

# logo de Marca Guanajuato (archivo racks/logo_gto.png), solo visible en la página de producción
rep('<div><div id="clock">--:--</div><div id="cdate"></div></div>',
    '<div><div id="clock">--:--</div><div id="cdate"></div></div>\n  <img id="logoGto" src="logo_gto.png" alt="Marca Guanajuato Internacional">')

JS = r'''/* ---------- 15-oct-2026 (Moisés): página de producción ORDEN DE ATAQUE ---------- */
function rkSO(r){return String(r.so||"").split(" · ")[0];}
function rkPaginar(xs,bloques,D){
  var stH=$("stage").clientHeight||1080,hh=(document.querySelector("header")||{}).offsetHeight||100,fh=(document.querySelector("footer")||{}).offsetHeight||40;
  var RH=34,SH=43,cap=stH-hh-fh-134;
  var tot={},pages=[],cur=[],used=0,last=null;
  xs.forEach(function(r){var c=r.cliente||"";tot[c]=tot[c]||{n:0,pz:0,v:0};tot[c].n++;tot[c].pz+=pzMO(r).pend;if(vencida(r))tot[c].v++;});
  xs.forEach(function(r){var c=r.cliente||"",nuevo=c!==last;
    if(cur.length&&used+RH+(nuevo?SH:0)>cap){pages.push(cur);cur=[];used=0;nuevo=true;}
    if(nuevo){var t=tot[c];cur.push({rkh:c,color:r.color,n:t.n,pz:t.pz,todas:t.v===t.n,cont:c===last});used+=SH;}
    cur.push(r);used+=RH;last=c;});
  if(cur.length)pages.push(cur);
  if(!pages.length)pages=[[]];
  pages.forEach(function(pg,i){bloques.push(["PROGRAMA DE ENTREGAS"+(pages.length>1?" · "+(i+1)+"/"+pages.length:""),pg,"rk"]);});
}
function rkFila(r){
  var p=pzMO(r),e=estacion(r),v=vencida(r),col=e?(CEST[e]||"#8A93A6"):"#25A35A";
  var ch=r.ops.map(function(o){var k=o[0],st=o[1],c=CEST[k]||"#8A93A6",lb=esc(NOMEST[k]||k),q=avN(r.av&&r.av[k]);
    if(st==="COMPLETED")return '<span class="rkc ok">'+lb+' ✓</span>';
    if(st==="IN_PROGRESS")return '<span class="rkc ip" style="background:'+c+'">'+lb+(q?' '+q[0]+'/'+q[1]:'')+'</span>';
    if(st==="PAUSED")return '<span class="rkc ps">'+lb+' ❚❚</span>';
    return k===e?'<span class="rkc cur" style="border-color:'+c+';color:'+c+'">'+lb+'</span>':'<span class="rkc">'+lb+'</span>';}).join("");
  var b="";
  if(r.prio)b+='<span class="bdg">URGE</span>';
  if(r.nota)b+='<span class="bdg">'+esc(r.nota)+'</span>';else if(fase(r)==="listo")b+='<span class="bdg">CERRAR MO</span>';
  var so=rkSO(r);
  return '<div class="rkr'+(v?' v':'')+(r.prio?' pr':'')+'"><i class="rks" style="background:'+col+'"></i>'+
   '<span class="rkm">'+esc(r.mo)+'</span>'+
   '<span class="rkn">'+esc(r.nombre)+(r.sku&&r.sku!==r.nombre?'<small>'+esc(r.sku)+'</small>':'')+(so?'<small>SO '+esc(so)+'</small>':'')+b+'</span>'+
   '<span class="rkrt">'+ch+'</span>'+
   '<span class="rke'+(v?' v':'')+'">'+(v?'VENCIDA ':'')+fmtF(r.entrega||r.deadline)+'</span>'+
   '<span class="rkf">FALTAN '+nf(p.pend)+'<small>de '+nf(p.plan)+(p.entr?' · '+nf(p.entr)+' entr.':'')+'</small></span></div>';
}
function rkLado(D){
  var rows=D.rows||[],B=D.bloques||[],h="";
  var cnt=B.map(function(b){var n=0,pz=0;rows.forEach(function(r){var e=estacion(r);if(e&&b[1].indexOf(e)>=0){n++;pz+=pzMO(r).pend;}});return {t:b[0],c:b[2],n:n,pz:pz};});
  var mx=0;cnt.forEach(function(x){mx=Math.max(mx,x.n);});
  if(cnt.length)h+='<div class="rkcard"><div class="rkct">DÓNDE ESTÁN LAS '+rows.length+' MOs</div>'+cnt.map(function(x){
    return '<div class="rkln"><span style="color:'+x.c+'">'+esc(x.t.charAt(0)+x.t.slice(1).toLowerCase())+'</span><span class="rkbar">'+(x.n?'<i style="width:'+(100*x.n/mx).toFixed(1)+'%;background:'+x.c+'"></i>':'')+'</span><span class="rknu">'+x.n+'</span></div>';}).join("")+'</div>';
  var top=null;cnt.forEach(function(x){if(x.n&&(!top||x.n>top.n))top=x;});
  if(top)h+='<div class="rkbt" style="border-color:'+top.c+';background:'+top.c+'26"><span class="l" style="color:'+top.c+'">CUELLO DE BOTELLA</span>'+
    '<span class="g">'+esc(top.t)+' · '+top.n+' de '+rows.length+' MOs</span><span class="s">'+nf(top.pz)+' pz esperando aquí. Reforzar este departamento.</span></div>';
  var AP=D.avProc||[];
  if(AP.length){var lk={};(D.ops||[]).forEach(function(o){lk[o[1]]=o[0];});
    h+='<div class="rkcard"><div class="rkct">AVANCE POR PROCESO</div>'+AP.map(function(x){var c=CEST[lk[x.p]]||"#8A93A6",nm=String(x.p);
      return '<div class="rkap"><span style="color:'+c+'">'+esc(nm.charAt(0)+nm.slice(1).toLowerCase())+'</span><span class="rkbar">'+(x.pct?'<i style="width:'+Math.max(2,x.pct)+'%;background:'+c+'"></i>':'')+'</span><span class="rknu">'+nf(x.h)+'/'+nf(x.t)+'</span></div>';}).join("")+'</div>';}
  var SS=D.soSinMO||[];
  if(SS.length){var g={},ord=[];SS.forEach(function(x){var a=String(x).split(" · "),c=a[1]||"";if(!g[c]){g[c]=[];ord.push(c);}g[c].push(a[0]);});
    h+='<div class="rkcard" style="flex:1;min-height:0;overflow:hidden"><div class="rkct">'+SS.length+' SO SIN MO</div><div class="rkso">'+
      ord.map(function(c){return '<b>'+esc(c)+':</b> '+g[c].map(esc).join(" · ");}).join("<br>")+'</div></div>';}
  return h;
}
function rkPagina(b,D){
  var rows=D.rows||[],pz=0,ve=0;rows.forEach(function(r){pz+=pzMO(r).pend;if(vencida(r))ve++;});
  var t='<div class="rkt"><b>'+esc(b[0])+'</b><span>'+rows.length+' MOs · '+nf(pz)+' pz por terminar'+(ve?' · <em>'+ve+' vencida'+(ve>1?'s':'')+'</em>':'')+'</span></div>';
  var ch='<div class="rkch"><span></span><span>MO</span><span>RACK · SKU · SO</span><span>RUTA · LLENA = DONDE ESTÁ AHORA</span><span class="r">ENTREGA</span><span class="r">PIEZAS</span></div>';
  var body=b[1].map(function(x){return x.rkh!=null?'<div class="rkh" style="background:'+(x.color||"#3A4552")+'">'+esc(x.rkh)+' <span>'+x.n+' MO'+(x.n>1?'s':'')+' · '+nf(x.pz)+' pz'+(x.todas?' · todas vencidas':'')+(x.cont?' · (continúa)':'')+'</span></div>':rkFila(x);}).join("");
  return '<div class="rkw"><section class="rkl">'+t+ch+body+'</section><aside class="rka">'+rkLado(D)+'</aside></div>';
}
function render0(D){'''
rep('function render0(D){', JS)

rep('if(D.proyecto==="racks")paginarCli(items);', 'if(D.proyecto==="racks")rkPaginar(items,bloques,D);')
rep('''if(b[2]==="mes"){''', '''if(b[2]==="rk"){var hr="";try{hr=rkPagina(b,D);}catch(e){}return '<div class="page prk'+(i===pagina?" on":"")+'">'+hr+'</div>';}
    if(b[2]==="mes"){''')
rep('<span class="build">r2026-10-14b</span>', '<span class="build">r2026-10-15</span>')
open(p, 'w').write(s)
print('diseno ok', len(s))
