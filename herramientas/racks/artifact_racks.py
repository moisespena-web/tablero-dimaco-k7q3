"""Paso 4 (16-oct-2026, Moisés: "quiero que el proceso de aviso sea igual que el de mafesa"):
arma la copia de la TV RACKS que vive como Artifact de Claude (con sesión, sin PIN), con el botón "✏️ Aviso TV".
Igual que MAFESA: el aviso se guarda en la base del artifact (tv/aviso) y se empuja a Dropbox
"/Moises Peña/Dimaco/Tablero TV/racksaviso-AAAAMMDD-HHMMSS.json". El robot de GitHub (datos.yml) lo copia a
racks/aviso.json y la TV de piso (GitHub Pages /racks) lo muestra en ~1-2 min.
El prefijo "racksaviso-" (y no "aviso-") es a propósito: así el aviso de Racks NUNCA se mezcla con el de MAFESA
(ni el robot ni el Worker de Cloudflare lo toman como aviso de MAFESA).
Uso: python3 artifact_racks.py racks/index.html SALIDA.html   -> publicar SALIDA.html en el artifact de Racks
     (capabilities: db rules admin, mcp Dropbox create_file, user)."""
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, ('NO ENCONTRADO/UNICO', old[:80]); s = s.replace(old, new)
# en el artifact el aviso sale de la base (tv/aviso), no de GitHub: que el sondeo de GitHub no lo pise
rep('function cargarAviso(){', 'function cargarAviso(){if(window.__ART__)return;')
rep('if(!avisoPropio)aviso(j&&j.aviso);', 'if(!avisoPropio&&!window.__ART__)aviso(j&&j.aviso);')
JS = r'''
/* ---------- 16-oct-2026: AVISO TV de Racks desde el artifact de Claude (igual que MAFESA, sin PIN) ---------- */
(async function(){
  var db=null;
  if(window.claude&&typeof window.claude.use==="function"){try{db=await window.claude.use("db");}catch(e){db=null;}}
  if(!db)return;
  window.__ART__=true;
  var box=$("aviso"),txt=$("avisoTxt"),cur=null,primeraAviso=true,repetir=null;
  db.doc("tv/aviso").onSnapshot(function(s){
    var d=s.exists?s.data():null,t=(d&&typeof d.texto==="string")?d.texto.trim():"";
    var cambio=!primeraAviso&&(!cur||cur.actualizado!==(d&&d.actualizado));
    cur=d;primeraAviso=false;
    if(repetir){clearInterval(repetir);repetir=null;}
    if(!t){box.hidden=true;return;}
    txt.textContent=t;var alerta=d.nivel==="alerta";
    box.className="aviso"+(alerta?" alerta":"");box.hidden=false;
    if(cambio)evento(alerta?"alerta":"aviso",t);
    if(alerta)repetir=setInterval(function(){sonar("alerta");},300000);
  },function(e){});
  var user=await window.claude.use("user");
  var puede=user?await user.canEdit():false;
  if(!puede)return;
  var panel=$("panel"),ta=$("ptxt"),pn=$("pn"),msg=$("pmsg"),bI=$("lvInfo"),bA=$("lvAlerta"),fab=$("fab"),nivel="info";
  var ref=db.doc("tv/aviso");
  var CARPETA="/Moises Peña/Dimaco/Tablero TV/";
  var mcpP=window.claude.use("mcp").catch(function(){return null;});
  function selloMX(d){
    try{var p={};new Intl.DateTimeFormat("en-CA",{timeZone:"America/Mexico_City",year:"numeric",month:"2-digit",day:"2-digit",
      hour:"2-digit",minute:"2-digit",second:"2-digit",hourCycle:"h23"}).formatToParts(d).forEach(function(x){p[x.type]=x.value;});
      return p.year+p.month+p.day+"-"+p.hour+p.minute+p.second;
    }catch(e){var u=d.toISOString().replace(/[-:T]/g,"");return u.slice(0,8)+"-"+u.slice(8,14);}
  }
  function comoArreglar(c){
    if(c==="server_not_connected")return "Agrega Dropbox en claude.ai → Configuración → Conectores.";
    if(c==="needs_reauth")return "Reconecta Dropbox en claude.ai → Configuración → Conectores.";
    if(c==="not_in_manifest")return "Esta página no tiene permiso de Dropbox en tu sesión.";
    if(c==="consent_required")return "Falta autorizar Dropbox: vuelve a darle Publicar.";
    if(c==="selection_required")return "Tienes dos conectores de Dropbox; elige uno.";
    if(c==="blocked_by_policy"||c==="approval_required")return "Tu organización bloquea esa escritura.";
    return "";
  }
  function aDropbox(t,n,iso){
    return mcpP.then(function(m){
      if(!m)return Promise.reject({code:"server_not_connected"});
      return m.callTool("Dropbox","create_file",{path:CARPETA+"racksaviso-"+selloMX(new Date(iso))+".json",
        content:JSON.stringify({texto:t,nivel:n,actualizado:iso})});
    });
  }
  function setNivel(n){nivel=n;bI.className=n==="info"?"sel":"";bA.className=n==="alerta"?"sel rojo":"";}
  function abrir(){ta.value=(cur&&cur.texto)||"";pn.textContent=ta.value.length;
    setNivel(cur&&cur.nivel==="alerta"?"alerta":"info");msg.textContent="";panel.hidden=false;}
  function guardar(t,n,ok){
    msg.textContent="Enviando…";var iso=new Date().toISOString();
    ref.set({texto:t,nivel:n,actualizado:iso}).then(function(){
      msg.textContent=ok+" Empujando a la TV de piso…";
      aDropbox(t,n,iso).then(function(){msg.textContent=ok+" En la TV de piso de Racks en ~1-2 min.";},
        function(e){var c=(e&&e.code)||"error",d=comoArreglar(c);
          msg.textContent=ok+" No pude empujarlo a la TV de piso ("+c+")."+(d?" "+d:"");});
    },function(e){msg.textContent="No se pudo guardar ("+((e&&e.code)||"error")+").";});
  }
  ta.addEventListener("input",function(){pn.textContent=ta.value.length;});
  bI.onclick=function(){setNivel("info");};bA.onclick=function(){setNivel("alerta");};
  $("pgo").onclick=function(){var t=ta.value.trim();if(!t){msg.textContent="Escribe el aviso primero.";return;}guardar(t,nivel,"Publicado ✓");};
  $("pclr").onclick=function(){ta.value="";pn.textContent="0";guardar("","info","Aviso quitado ✓");};
  $("pcls").onclick=function(){panel.hidden=true;};
  [].forEach.call(document.querySelectorAll(".ptest button"),function(b){
    b.onclick=function(){var c=ac();if(c)c.resume().then(function(){estadoSonido();SON[b.getAttribute("data-s")]();});};});
  fab.onclick=abrir;
  function modo(){fab.hidden=!(innerWidth/innerHeight<1.2);}
  addEventListener("resize",modo);modo();
  var n=0,tt=0;$("logo").addEventListener("click",function(){var now=Date.now();n=(now-tt<1500)?n+1:1;tt=now;if(n>=3){n=0;abrir();}});
})();
'''
tail = '\n})();\n</script>\n</body></html>'
assert s.endswith(tail) or s.rstrip().endswith(tail.strip()), 'final inesperado'
i = s.rfind('})();\n</script>')
s = s[:i] + JS + s[i:]
open(out, 'w').write(s); print('artifact ok ->', out, len(s))
