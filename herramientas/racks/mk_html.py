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
rep('''var OPS=["Corte","Taladro","CNC","Doblez","Limpieza & SQA"];
var LBL={"Corte":"CORTE","Taladro":"TALADRO","CNC":"TM-2P","Doblez":"DOBLEZ","Limpieza & SQA":"LIMPIEZA"};
var ORD={"Corte":0,"Taladro":1,"CNC":2,"Doblez":3,"Limpieza & SQA":4};''',
'''/* RACKS: las columnas vienen en los datos (D.ops = [[clave,etiqueta],...]); la franja es el color del cliente */
var OPS=["Corte","Laser","Router","Doblez","Armado","Pintura","Vestido"];
var LBL={"Corte":"CORTE","Laser":"LÁSER","Router":"ROUTER","Doblez":"DOBLEZ","Armado":"ARMADO","Pintura":"PINTURA","Vestido":"VESTIDO"};
var ORD={};OPS.forEach(function(o,i){ORD[o]=i;});
function setOps(D){if(!D||!D.ops||!D.ops.length)return;OPS=D.ops.map(function(x){return x[0];});LBL={};ORD={};
  D.ops.forEach(function(x,i){LBL[x[0]]=x[1];ORD[x[0]]=i;});document.documentElement.style.setProperty("--nops",OPS.length);}''')
rep('''function tipoDe(r){
  var s=r.ops.map''','''function tipoDe(r){
  if(r.color)return [r.cliente||"",r.color];
  var s=r.ops.map''')
rep('''var HEAD='<div class="row head">''','''function HEADF(){return '<div class="row head">''')
rep(''''</div><div class="dl">LÍMITE</div></div>';''',''''</div><div class="dl">LÍMITE</div></div>';}''')
rep('''var LEYT='<span class="leyt">'+TIPOS.map''','''var LEYT0='<span class="leyt">'+TIPOS.map''')
rep('''function render(D){try{renderMat(D);}''','''function leyCli(D){return '<span class="leyt">'+((D&&D.clientes)||[]).map(function(c){return '<span><b class="tpill" style="background:'+c[1]+'">&nbsp;</b> '+esc(c[0])+'</span>';}).join("")+'<span style="color:#8FA3BA;font-style:italic">· Franja = cliente</span></span>';}
var LEYT="";
function render(D){try{setOps(D);LEYT=leyCli(D);}catch(e){}try{renderMat(D);}''')
rep('''HEAD.replace("LÍMITE","ENTREGA"):HEAD)''','''HEADF().replace("LÍMITE","ENTREGA"):HEADF())''')
# sin recuadro de material en racks
rep('''function renderMat(D){var m=$('mat');''','''function renderMat(D){var m=$('mat');if(D&&D.proyecto==='racks'){m.hidden=true;return;}''')
# datos: racks/datos.json (sin buzón de MAFESA); avisos: los mismos de la planta
rep('''pedir([BUZON+"/tablero","datos.json",RAWG+"datos.json"],function(j){''','''pedir(["datos.json",RAWG+"racks/datos.json"],function(j){''')
rep('''pedir([BUZON+"/tablero/aviso","aviso.json",RAWG+"aviso.json"],''','''pedir([BUZON+"/tablero/aviso","../aviso.json",RAWG+"aviso.json"],''')
rep('<title>','<title>',1)
src=re.sub(r'<title>[^<]*</title>','<title>MO en proceso · Racks</title>',src,1)
src=re.sub(r'<span class="build">v[^<]*</span>','<span class="build">r2026-10-06a</span>',src,1)
# CSS para N columnas (7 en racks)
css='''
/* ---- RACKS: 7 estaciones ---- */
:root{--nops:7}
.ops{width:880px;grid-template-columns:repeat(var(--nops),minmax(0,1fr));gap:6px}
.ests{grid-template-columns:repeat(var(--nops),minmax(0,1fr))}
.apl{grid-template-columns:repeat(var(--nops),minmax(0,1fr))}
.pz{width:100px}#pages.compacto .mo{width:240px}.dl{width:170px}
.row.head .op{font-size:15px;letter-spacing:0}
#pages.compacto .op{font-size:14px;letter-spacing:0}
.app{font-size:27px}.apn{font-size:13px;letter-spacing:0}
#pages.compacto .tipo.soc{font-size:16px}
</style></head>'''
assert src.count('</style></head>')==1
src=src.replace('</style></head>',css)
open('racks/index.html','w').write(src)
print('ok',len(src))
