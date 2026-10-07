"""Hace plantilla.html a partir de base_limpieza_6oct.html (la estación Limpieza tal como estaba el 6-oct-2026). Ya se corrió; para cambios de diseño editar plantilla.html y correr gen.py."""
import re,sys,os
R=sys.argv[1] if len(sys.argv)>1 else '../..'
t=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'base_limpieza_6oct.html')).read()
def rep(a,b,n=1):
    global t; c=t.count(a); assert c==n,('ESPERABA %d, HAY %d: %s'%(n,c,a[:90])); t=t.replace(a,b)
def rex(p,b):
    global t; t2,c=re.subn(p,lambda m:b,t,count=1,flags=re.S); assert c==1,('REGEX NO: '+p[:80]); t=t2
rep('<meta name="apple-mobile-web-app-title" content="Limpieza & SQA">','<meta name="apple-mobile-web-app-title" content="@@APPTIT@@">')
rep('<title>Estación Limpieza &amp; SQA · DIMACO</title>','<title>Estación @@TITH@@ · DIMACO</title>')
rep("MAQ='Limpieza & SQA', OPERADOR='Cynthia', KEY='dimaco_limpieza_v1';","MAQ=@@MAQJS@@, OPERADOR=@@OPJS@@, KEY='dimaco_@@SLUG@@_v1', PINOPS=@@PINOPS@@, ESPERA=@@ESPERA@@, RECURSO=@@RECJS@@;\nvar OPS=['Emiliano','[Operador 2]','[Operador 3]'];")
rep("PZD=window.PIEZAS_DOBLEZ||{}","PZD=@@USAPZD@@?(window.PIEZAS_DOBLEZ||{}):{}")
rex(r'var AVP=\{[^\n]*?\};','var AVP=null, AVPN=@@AVPN@@;   /* avance por proceso: se lee en vivo del datos.json de la TV (leerTV) */')
rex(r'var DATA=\[.*?\];\n','var DATA=@@DATA@@;\n')
rep("(t.match(/^[ \\t]*Limpieza[^\\n]*/gim)||[])","(t.match(new RegExp('^[ \\\\t]*@@NOTARE@@[^\\\\n]*','gim'))||[])")
rep("return ['LISTA PARA LIMPIEZA',","return ['@@LISTA@@',")
rep("dimaco_limpieza_","dimaco_@@SLUG@@_",n=t.count("dimaco_limpieza_"))
rep("app-limpieza/aviso.json","app-@@SLUG@@/aviso.json",n=t.count("app-limpieza/aviso.json"))
rep('white-space:nowrap">Estación Limpieza &amp; SQA</div>','white-space:nowrap">Estación @@TITH@@</div>')
rep("'+OPERADOR+' · <b style=\"color:'+syncTxt()[1]","'+E(opAct())+' · <b style=\"color:'+syncTxt()[1]")
rep('LIMPIEZA HOY · TIEMPO EFECTIVO','@@KPI@@ HOY · TIEMPO EFECTIVO')
rep('COLA DE LIMPIEZA &amp; SQA · LISTAS PRIMERO','@@COLA@@')
rep("""'<div style="font-size:12px;color:var(--tx2);margin:2px 0 4px"><b>'+E(m.so||'')+'</b>'+(m.espera?' · <b style="color:#FFC45C">aún en '+E(m.espera)+'</b>':' · <b style="color:#7FE3BC">lista para limpieza</b>')+'</div>'+""",
    """'<div style="font-size:12px;color:var(--tx2);margin:2px 0 4px">#'+m.sec+' <b class="pill" style="background:'+m.color+'">'+m.tipo+'</b>'+(m.so?' · <b>'+E(m.so)+'</b>':'')+(m.espera?' · <b style="color:#FFC45C">aún en '+E(m.espera)+'</b>':'')+'</div>'+""")
rep("""'<div style="font-size:26px;font-weight:800;margin:4px 0">Limpieza &amp; SQA</div>'+""","""'<div style="font-size:26px;font-weight:800;margin:4px 0">'+E(m.paso||MAQ)+'</div>'+""")
rep("""Resource: <b style="color:var(--tx)">Limpieza &amp; SQA</b>""","""Resource: <b style="color:var(--tx)">'+E(m.recurso||RECURSO)+'</b>""")
rep('VISTA DE LIMPIEZA','@@VISTA@@')
rep("¿Cuántas piezas limpiaste en este lapso?","¿Cuántas piezas @@VERBO@@ en este lapso?")
rep("'+m.mo+' · Limpieza & SQA · '+OPERADOR+'</div>'","'+m.mo+' · '+E(m.paso||MAQ)+' · '+E(st.op||opAct())+'</div>'")
rep("La Limpieza &amp; SQA de <b>","El paso <b>'+E(m.paso||MAQ)+'</b> de <b>")
rep("'RESUMEN LIMPIEZA & SQA · '+OPERADOR+' · '","'RESUMEN @@KPI@@ · '+opAct()+' · '")
rep("L.push(mo+' · Limpieza & SQA · '","L.push(mo+' · '+MAQ+' · '")
rep("title:'Resumen Limpieza & SQA'","title:'Resumen '+MAQ")
rep("LIMPIEZA PARADA","@@PARADA@@",n=t.count("LIMPIEZA PARADA"))
rep("que estés limpiando","que estés @@GER@@")
rex(r"var LIM_PARADA=1e12, WA_URL='', WA_URL0='[^']*';","var LIM_PARADA=@@LIMP@@, WA_URL=@@WA@@;")
rep("estacion:'Limpieza & SQA'","estacion:@@WAEST@@")
rex(r"PILOTO · MOs de Katana al [0-9]{1,2}-[a-z]{3} [0-9]{1,2}:[0-9]{2}\.","PILOTO · MOs de Katana al @@PIE@@.")
rep("/* START sin PIN: el teléfono es de Miguel */","/* START: sin PIN cuando el teléfono es de un solo operador; con PIN (elegir operador) donde hay varios (TM-2P) */")

# ---- operador con PIN (de TM-2P) ----
rep("var S={pantalla:'lista',","var S={opSel:null,pin:'',pinErr:'',pinChk:false,pantalla:'lista',")
rep("function cur(){return S.mos[S.sel];}","function cur(){return S.mos[S.sel];}\nfunction opAct(){var m=S.pantalla==='detalle'&&cur();return (m&&m.st&&m.st.op)||(PINOPS?'—':OPERADOR);}")
rep("operador:OPERADOR,pin:(CONX&&CONX.pin)||''","operador:(x&&x.op)||OPERADOR,pin:(x&&x.pin)||(CONX&&CONX.pin)||''")
rep("""A.start=function(){upd(function(x){var t=Date.now();""","""A.start=function(){if(PINOPS){var st0=cur().st;S.pinErr='';S.modal='pin';S.opSel=st0.status==='pausa'?st0.op:null;S.pin='';return;}upd(function(x){var t=Date.now();""")
rep("A.pausa=function(){S.modal='pausa';};","""A.pausa=function(){S.modal='pausa';};
A.op=function(v){S.opSel=v;S.pin='';S.pinErr='';};
A.pinOk=function(){if(S.pinChk)return;
 if(enLinea()){S.pinChk=true;S.pinErr='';api('POST','/pin',{operador:S.opSel,pin:S.pin}).then(function(r){S.pinChk=false;
   if(r._status===403){S.pinErr='PIN incorrecto. Intenta de nuevo.';S.pin='';render();return;}iniciarTramo();render();guardar();})
  .catch(function(){S.pinChk=false;iniciarTramo();render();guardar();});return;}
 iniciarTramo();};
function iniciarTramo(){var op=S.opSel,pin=S.pin;upd(function(x){var t=Date.now();
 if(x.status==='pausa'&&x.op===op){x.paused+=t-x.pauseStart;x.pauseStart=null;}
 else{if(x.tramoStart){katEv('fin',x,x.runStart?t-x.runStart:0);cerrarTramo(x,0,'cambio de operador');}x.tramoStart=t;}
 x.op=op;x.pin=pin;x.runStart=t;x.status='prog';katEv('start',x,0);});S.modal=null;S.pin='';}""")
rep(""" if(S.modal==='pausa'){h='<div class="ttl">¿Por qué se pausa?</div>""",""" if(S.modal==='pin'){var listo=!!S.opSel&&S.pin.length===4;
  h='<div class="ttl">'+(st.status==='pausa'?'¿Quién reanuda?':'¿Quién arranca?')+'</div><div class="g3">'+
   OPS.map(function(n){var on=S.opSel===n;return '<button type="button" '+act('op',n)+' style="min-height:52px;border-radius:12px;font-size:17px;font-weight:700;'+(on?'background:#0E3628;border:2px solid #25C083;color:#7FE3BC':'background:#18263A;border:1px solid #22344A;color:#EAF1F9')+'">'+E(n)+'</button>';}).join('')+'</div>'+
   (S.opSel?'<div style="display:flex;align-items:center;gap:12px"><span style="font-size:16px;color:var(--tx2)">PIN (4 dígitos)</span>'+[0,1,2,3].map(function(i){return '<span style="width:20px;height:20px;border-radius:50%;border:2px solid #8FA3BA;background:'+(i<S.pin.length?'#EAF1F9':'transparent')+'"></span>';}).join('')+'</div>'+teclado('pin'):'')+
   '<div style="min-height:22px;font-size:15px;font-weight:700;color:#FF6369">'+E(S.pinChk?'Revisando PIN…':(S.pinErr||''))+'</div><div style="display:flex;gap:10px"><button type="button" '+act('pinOk')+(listo?'':' disabled')+' style="flex-grow:1;min-height:56px;border-radius:12px;border:0;background:#25C083;color:#07121B;font-size:20px;font-weight:700;opacity:'+(listo?1:.3)+'">Iniciar lapso</button><button type="button" class="sec" '+act('cerrar')+'>Cancelar</button></div>';}
  else if(S.modal==='pausa'){h='<div class="ttl">¿Por qué se pausa?</div>""")
rep("quien=st.status==='pausa'?'En pausa: '+(st.motivos[st.motivos.length-1]||''):(st.status==='prog'?'Trabajando: '+OPERADOR:'')","quien=st.status==='pausa'?'En pausa: '+(st.motivos[st.motivos.length-1]||''):(st.status==='prog'?'Trabajando: '+(st.op||OPERADOR):'')")

# ---- avance por proceso en vivo (datos.json de la TV) ----
rep("((d&&d.datos&&d.datos.rows)||[]).forEach(function(r){if(r.mo&&r.piezas!=null)TVPZ[r.mo]=+r.piezas;});\n S.mos.forEach(pendEnt);",
    "((d&&d.datos&&d.datos.rows)||[]).forEach(function(r){if(r.mo&&r.piezas!=null)TVPZ[r.mo]=+r.piezas;});\n  ((d&&d.datos&&d.datos.avProc)||[]).forEach(function(a){if(String(a.p).toLowerCase()===String(AVPN).toLowerCase())AVP=a;});\n S.mos.forEach(pendEnt);")

# ---- cola EN VIVO desde Katana (de TM-2P), para las 5 ----
VIVO=r'''
/* ============ COLA EN VIVO (6-oct-2026): con el teléfono conectado, las MOs se bajan de Katana por el servidor ============ */
var COLN={'Corte':'Corte','Taladro':'Taladro','CNC':'TM-2P','Doblez':'Doblez','Limpieza & SQA':'Limpieza'};
function mapaMO(k,dr,idx){var hoy=diaKey(Date.now()),cols=[],ruta=[];
 (k.ruta||[]).forEach(function(o){var c=COLN[o.nombre]||o.nombre;if(cols.indexOf(c)<0)cols.push(c);});
 cols.forEach(function(c){var ops=(k.ruta||[]).filter(function(o){return (COLN[o.nombre]||o.nombre)===c;}),
   s=ops.every(function(o){return o.status==='COMPLETED';})?'done':(ops.some(function(o){return o.status==='IN_PROGRESS'||o.status==='PAUSED';})?'prog':'none'),
   yo=ops.some(function(o){return o.paso===k.op.paso&&o.recurso===k.op.recurso&&o.status===k.op.status;})&&c===(COLN[(k.ruta.filter(function(o){return o.paso===k.op.paso&&o.recurso===k.op.recurso;})[0]||{}).nombre]||c);
   ruta.push([c,s,!!yo]);});
 if(!ruta.some(function(r){return r[2];})){var cm=COLN[MAQ==='Limpieza & SQA'?'Limpieza & SQA':MAQ==='TM-2P'?'CNC':MAQ]||MAQ;ruta.forEach(function(r){if(r[0]===cm)r[2]=true;});}
 var i=-1;ruta.forEach(function(r,j){if(r[2])i=j;});var antes=ruta.slice(0,Math.max(0,i)).filter(function(r){return r[1]!=='done';});
 var ing=(k.ingredientes||[])[0]||{};
 return armar({mo:k.mo,sec:idx>=0?idx+1:'–',nombre:k.nombre,sku:k.sku,piezas:k.piezas,entregadas:k.entregadas,hechas:k.hechas||0,
  ent:(dr&&dr.entrega)||k.deadline||hoy,deadline:k.deadline||hoy,prio:!!(dr&&(dr.grp==='urge'||dr.prio)),paso:k.op.paso,recurso:k.op.recurso,planeado:k.op.planeado,
  rowId:k.op.rowId,tiempoReal:k.op.tiempoReal,ruta:ruta,ingSku:ing.sku||'',ingNombre:ing.nombre||'',ingTot:ing.total||0,ingUom:ing.uom||'',
  notas:k.notas||'Sin notas.',so:(dr&&dr.so)||'',espera:ESPERA&&antes.length?antes[0][0]:''});}
function cargarCola(){if(!enLinea())return Promise.resolve();
 return Promise.all([api('GET','/cola'),fetch('../datos.json?x='+Date.now(),{cache:'no-store'}).then(function(r){return r.json();}).catch(function(){return null;}),api('GET','/operadores').catch(function(){return null;})])
 .then(function(res){var c=res[0],d=res[1],ops=res[2];
  if(!c||!c.ok){S.sync='err';S.conxMsg=(c&&c.error)||'Sin respuesta del servidor';if(!S.modal)render();return;}
  if(ops&&ops.ok&&ops.operadores&&ops.operadores.length)OPS=ops.operadores;
  var rows=(d&&d.datos&&d.datos.rows)||[],pos={};rows.forEach(function(r,i){pos[r.mo]=i;});rows.forEach(function(r){if(r.mo&&r.piezas!=null)TVPZ[r.mo]=+r.piezas;});
  var selMo=S.mos[S.sel]&&S.mos[S.sel].mo;S.mos.forEach(function(m){S.stK[m.mo]=m.st;});
  var lista=c.mos.map(function(k){var i=pos[k.mo]!=null?pos[k.mo]:-1,m=mapaMO(k,i>=0?rows[i]:null,i);
   m.st=Object.assign(nuevo(),S.stK[k.mo]||{});if(S.tReal[m.rowId]==null)S.tReal[m.rowId]=m.tiempoReal;return m;});
  lista.sort(function(a,b){if(ESPERA&&(!!a.espera)!==(!!b.espera))return a.espera?1:-1;var ia=pos[a.mo]!=null?pos[a.mo]:9999,ib=pos[b.mo]!=null?pos[b.mo]:9999;return ia-ib||(a.ent<b.ent?-1:a.ent>b.ent?1:0);});
  lista.forEach(pendEnt);if(!lista.length&&S.mos.length&&!c.mos.length){}S.mos=lista;var ni=-1;lista.forEach(function(m,i){if(m.mo===selMo)ni=i;});
  if(ni<0){S.sel=0;if(S.pantalla==='detalle'&&!S.modal)S.pantalla='lista';}else S.sel=ni;
  S.katHora=Date.now();S.sync=S.cola.length?'pend':'ok';S.conxMsg='';if(!S.modal)render();guardar();})
 .catch(function(){S.sync='err';S.conxMsg='Sin conexión';if(!S.modal)render();});}
'''
rep("/* ================================ VISTAS ================================ */",VIVO+"\n/* ================================ VISTAS ================================ */")
open('plantilla.html','w').write(t); print('plantilla ok',len(t))
t=open('plantilla.html').read()
rep("function reintentar(){if(enLinea())enviarCola();}","function reintentar(){if(!enLinea())return;cargarCola().then(enviarCola);}")
rep("S.conxMsg=r.ok?'✓ Conectado a Katana':'✗ '+(r.error||'No autorizado');render();}","S.conxMsg=r.ok?'✓ Conectado a Katana':'✗ '+(r.error||'No autorizado');render();if(r.ok)cargarCola();}")
i=t.index("cargar();if(PA.ult==null)"); j=t.index("\n",i)
t=t[:j]+"\nif(enLinea()){S.sync=S.cola.length?'pend':'off';cargarCola().then(enviarCola);}\nsetInterval(function(){if(enLinea()&&!S.modal){cargarCola();enviarCola();}},180000);"+t[j:]
open('plantilla.html','w').write(t); print('plantilla ok (en vivo)')
