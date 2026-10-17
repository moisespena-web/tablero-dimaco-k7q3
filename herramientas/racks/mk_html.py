import re,json,sys
src=open('index.html').read()
D=json.load(open('/home/claude/racks/datos.json'))['datos']
def rep(old,new,count=1):
    global src
    n=src.count(old)
    assert n>=1, ('NO ENCONTRADO',old[:80])
    src=src.replace(old,new) if count==0 else src.replace(old,new,count)
rep('<h1>MO EN PROCESO · MAFESA</h1>','<h1>MO EN PROCESO · RACKS</h1>')
rep('<p>⚡ PROYECTO: Busbar para transformadores eléctricos</p>','<p>🏗️ PROYECTO: Diseño, fabricación y reparación de racks para el manejo de autopartes</p>')
# datos iniciales
i=src.index('<script>window.__DATOS__=');j=src.index('</script>',i)
src=src[:i]+'<script>window.__DATOS__='+json.dumps(D,ensure_ascii=False)+';'+src[j:]
# columnas dinamicas
rep('''var OPS=["Corte","Taladro","M65","CNC","Doblez","Limpieza & SQA"];
var LBL={"Corte":"CORTE","Taladro":"TALADRO","M65":"M65","CNC":"TM-2P","Doblez":"DOBLEZ","Limpieza & SQA":"LIMPIEZA"};
/* Color fijo por estación (Moisés, 11-oct-2026): el nombre de cada proceso siempre en su color, en toda la TV */
var CEST={"Corte":"#5AB0FF","Taladro":"#B79CFF","M65":"#F5D547","CNC":"#FF7EB6","Doblez":"#C9E24F","Limpieza & SQA":"#3FD9D9"};
function lblc(o){return '<span style="color:'+CEST[o]+'">'+LBL[o]+'</span>';}
var ORD={"Corte":0,"Taladro":1,"M65":2,"CNC":3,"Doblez":4,"Limpieza & SQA":5};''',
'''/* RACKS: las columnas vienen en los datos (D.ops = [[clave,etiqueta],...]); la franja es el color del cliente */
var OPS=["Corte","Laser","Router","Doblez","Armado","Pintura","Vestido"];
var LBL={"Corte":"CORTE","Laser":"LÁSER","Router":"ROUTER","Doblez":"DOBLEZ","Armado":"ARMADO","Pintura":"PINTURA","Vestido":"VESTIDO"};
/* Color fijo por estación (como MAFESA, 11-oct-2026) */
var CEST={"Corte":"#5AB0FF","Laser":"#FF9F43","Router":"#B79CFF","Doblez":"#C9E24F","Armado":"#FF7EB6","Pintura":"#3FD9D9","Vestido":"#FFD84D"};
function lblc(o){return '<span style="color:'+(CEST[o]||"#FFFFFF")+'">'+LBL[o]+'</span>';}
var ORD={};OPS.forEach(function(o,i){ORD[o]=i;});
function setOps(D){if(!D||!D.ops||!D.ops.length)return;OPS=D.ops.map(function(x){return x[0];});LBL={};ORD={};
  D.ops.forEach(function(x,i){LBL[x[0]]=x[1];ORD[x[0]]=i;});document.documentElement.style.setProperty("--nops",OPS.length);
  BLQ=D.bloques||[];BLQ.forEach(function(b){b[1].forEach(function(o){CEST[o]=b[2];});});}
/* 14-oct-2026 (Moisés): bloques de columnas (HABILITADO, LÁSER Y ROUTER, MAQUINADOS, ARMADO Y SOLDADURA, PINTURA Y VESTIDO), cada uno con su color */
var BLQ=[];
function BLQF(){if(!BLQ.length)return "";return '<div class="row head blq"><div class="stripe"></div><div class="mo"></div><div class="desc"></div><div class="pz"></div><div class="ops">'+
  BLQ.map(function(b){return '<div class="bq'+(b[1].length<2?' uno':'')+'" style="grid-column:span '+b[1].length+';border-color:'+b[2]+';color:'+b[2]+'">'+esc(b[0])+'</div>';}).join("")+'</div><div class="dl"></div></div>';}''')
rep('var NOMEST={"Corte":"Corte","Taladro":"Taladro","M65":"M65","CNC":"TM-2P",','var NOMEST={"Corte":"Corte","Taladro":"Taladro","M65":"M65","CNC":"Maquinados","Diseño":"Diseño","RR":"R&R",')
rep('''function tipoDe(r){
  var s=r.ops.map''','''function tipoDe(r){
  if(r.color)return [r.cliente||"",r.color];
  var s=r.ops.map''')
rep('''var HEAD='<div class="row head">''','''function HEADF(){return BLQF()+'<div class="row head">''')
rep(''''</div><div class="dl">LÍMITE</div></div>';''',''''</div><div class="dl">LÍMITE</div></div>';}''')
# 11-oct-2026: la leyenda de MAFESA cambió a la de COBRE; en racks se renombra y se usa la de clientes
rep('''var LEYT='<span class="leyt">''','''var LEYT0='<span class="leyt">''')
rep('''function render(D){try{renderMat(D);}''','''function leyCli(D){return '<span class="leyt">'+((D&&D.clientes)||[]).map(function(c){return '<span><b class="tpill" style="background:'+c[1]+'">&nbsp;</b> '+esc(c[0])+'</span>';}).join("")+'<span style="color:#8FA3BA;font-style:italic">· Franja = cliente</span></span>';}
var LEYT="";
function render(D){try{setOps(D);LEYT=leyCli(D);}catch(e){}try{renderMat(D);}''')
rep('''HEAD.replace("LÍMITE","ENTREGA"):HEAD)''','''HEADF().replace("LÍMITE","ENTREGA"):HEADF())''')
# 13-oct-2026: MAFESA pinta la rayita con el color de la estación (11-oct); en racks la franja sigue siendo el color del cliente
rep('''<div class="stripe" style="background:'+(ea?CEST[ea]:'#25C083')+'"></div>''','''<div class="stripe" style="background:'+t[1]+'"></div>''')
# sin recuadro de material en racks
rep('''function renderMat(D){var m=$('mat');''','''function renderMat(D){var m=$('mat');if(D&&D.proyecto==='racks'){m.hidden=true;return;}''')
# datos: racks/datos.json (sin buzón de MAFESA)
# avisos (9-oct-2026, Moisés): Racks tiene SUS PROPIOS avisos en racks/aviso.json; ya NO lee el aviso de MAFESA
rep('''pedir([BUZON+"/tablero","datos.json",RAWG+"datos.json"],function(j){''','''pedir(["datos.json",RAWG+"racks/datos.json"],function(j){''')
rep('''pedir([BUZON+"/tablero/aviso","aviso.json",RAWG+"aviso.json"],''','''pedir([BUZON+"/tablero/racks/aviso","aviso.json",RAWG+"racks/aviso.json"],''')   # 16-oct-2026: buzón de Cloudflare primero (igual que MAFESA)
rep('<title>','<title>',1)
src=re.sub(r'<title>[^<]*</title>','<title>MO en proceso · Racks</title>',src,1)
src=re.sub(r'<span class="build">v[^<]*</span>','<span class="build">r2026-10-14b</span>',src,1)
# CSS para N columnas (7 en racks)
css='''
/* ---- RACKS: 7 estaciones ---- */
:root{--nops:7}
.ops{width:880px;grid-template-columns:repeat(var(--nops),minmax(0,1fr));gap:6px}
.ests{grid-template-columns:repeat(var(--nops),minmax(0,1fr))}
.apl{grid-template-columns:repeat(var(--nops),minmax(0,1fr))}
.pz{width:130px}.pz b{display:inline}.pz span{display:inline;margin-left:4px}#pages.compacto .mo{width:240px}.dl{width:170px}
.row.head .op{font-size:15px;letter-spacing:0}
#pages.compacto .op{font-size:14px;letter-spacing:0}
.app{font-size:27px}.apn{font-size:13px;letter-spacing:0}
#pages.compacto .tipo.soc{font-size:16px}
#pages.compacto .row.head.blq{min-height:0;height:32px;flex:none;padding-top:0;padding-bottom:0;background:none;border:none}
.row.head.blq .bq{border:2px solid;border-bottom:none;border-radius:8px 8px 0 0;font-size:14px;font-weight:800;letter-spacing:1px;
  display:flex;align-items:center;justify-content:center;text-align:center;height:30px;line-height:1.05;overflow:hidden;background:rgba(255,255,255,.04)}
.row.head.blq .bq.uno{font-size:11px;letter-spacing:.3px}
</style></head>'''
assert src.count('</style></head>')==1
src=src.replace('</style></head>',css)
# ---- 14-oct-2026 (Moisés): página CALIDAD RACKS, copia de la CALIDAD MAFESA con los datos del Tablero de Calidad de racks ----
# datos: racks/calidad.json (lo arma herramientas/racks/calidad_racks.py); departamentos de racks; "quién" = líder del depto.
import os
CALR=json.load(open('racks/calidad.json')) if os.path.exists('racks/calidad.json') else {"stamp":"","proyecto":"racks","incidencias":[]}
i=src.index('<script>window.__CAL__=');j=src.index('</script>',i)
src=src[:i]+'<script>window.__CAL__='+json.dumps(CALR,ensure_ascii=False)+';'+src[j:]
rep('var CDEP={cor:["CORTE","Corte"],tal:["TALADRO / TM-2P","Taladro"],dob:["DOBLEZ","Doblez"],lim:["LIMPIEZA","Limpieza & SQA"],cal:["INSPECCIÓN",null],ing:["PLANO / PROGRAMA",null],ext:["PROVEEDOR",null]};',
    'var CDEP={dis:["DISEÑO",null],hab:["HABILITADO","Corte"],las:["LÁSER","Laser"],arm:["ARMADO","Armado"],pin:["PINTURA","Pintura"],ves:["VESTIDO","Vestido"],cal:["INSPECCIÓN",null],ext:["PROVEEDOR",null]};')
rep('reclamo:"RECLAMO MAFESA"}','reclamo:"RECLAMO CLIENTE"}')
rep('<h2>CALIDAD MAFESA · ','<h2>CALIDAD RACKS · ')
rep('<span>RECLAMOS DE MAFESA</span>','<span>RECLAMOS DE CLIENTE</span>')
rep('["cor","tal","dob","lim","cal"].map(function(id,i){','["dis","hab","las","arm","pin","ves","cal"].map(function(id,i){')
rep('["ing","ext"].map(function(id){','["ext"].map(function(id){')
# en lugar de la etiqueta CU/AL va el cliente, y en lugar del SKU, la SO
rep('<span class="mt\'+(cu?\' cu\':\'\')+\'">\'+(cu?\'CU\':\'AL\')+\'</span>', '\'+(r.cliente?\'<span class="mt">\'+esc(r.cliente)+\'</span>\':\'\')+\'')
rep("esc(r.sku||\"\")+' · '+esc(r.producto||\"\")", "(r.so?'SO '+esc(r.so)+' · ':'')+esc(r.producto||\"\")")
rep('bloques.push(["CALIDAD MAFESA",null,"cal"]);','bloques.push(["CALIDAD RACKS",null,"cal"]);')
rep('pedir(["calidad.json",RAWG+"calidad.json"],','pedir(["calidad.json",RAWG+"racks/calidad.json"],')
# 14-oct-2026 (Moisés): ícono y nombre propios para el Dock/iPhone (antes heredaba los de MAFESA)
src=re.sub(r'<meta name="apple-mobile-web-app-title" content="[^"]*">','<meta name="apple-mobile-web-app-title" content="Tablero Racks">',src,count=1)
src=re.sub(r'<link rel="apple-touch-icon" href="[^"]*">','<link rel="apple-touch-icon" href="icon.png?v=r1014">',src,count=1)
src=re.sub(r'<link rel="icon" type="image/png" href="[^"]*">','<link rel="icon" type="image/png" href="icon.png?v=r1014">',src,count=1)
rep('CAB=26+28+10','CAB=26+28+10+34')   # + la fila de bloques (14-oct-2026)
open('racks/index.html','w').write(src)
print('ok',len(src))
