"""Paso 2 de la página de Racks (después de mk_html.py): agrupa por cliente con encabezado de cliente.
Pedido de Moisés (6-oct-2026). Si el cliente no cabe en una página, la siguiente repite el encabezado "(continúa)"."""
p='racks/index.html'; s=open(p).read()
def rep(old,new):
    global s
    assert s.count(old)==1,('NO ENCONTRADO/UNICO',old[:70]); s=s.replace(old,new)
rep('paginar(items,"PROGRAMA DE ENTREGAS","");',r'''function paginarCli(xs){
      if(!xs.length)return;
      ROWH_=ROWH+5;var SEPH=44,cabPx=hDisp-CAB,tot={},pages=[],cur=[],used=0,last=null;
      xs.forEach(function(r){var c=r.cliente||"";tot[c]=tot[c]||{n:0,pz:0};tot[c].n++;tot[c].pz+=r.piezas;});
      function cab(c,cont,col){var t=tot[c];return {sep:c.toUpperCase()+" · "+t.n+" MO"+(t.n>1?"s":"")+" · "+t.pz.toLocaleString("en-US")+" pz"+(cont?"  (continúa)":""),color:col};}
      xs.forEach(function(r){var c=r.cliente||"",nuevo=c!==last;
        if(cur.length&&used+altoR(r)+(nuevo?SEPH:0)>cabPx){pages.push(cur);cur=[];used=0;nuevo=true;}
        if(nuevo){cur.push(cab(c,c===last,r.color));used+=SEPH;}
        cur.push(r);used+=altoR(r);last=c;});
      if(cur.length)pages.push(cur);
      pages.forEach(function(pg,i){bloques.push(["PROGRAMA DE ENTREGAS"+(pages.length>1?" · "+(i+1)+"/"+pages.length:""),pg,null,""]);});
    }
    if(D.proyecto==="racks")paginarCli(items);else paginar(items,"PROGRAMA DE ENTREGAS","");''')
rep("""'<div class="sep'+(x.limp?' limp':'')+'">'+esc(x.sep)+'</div>'""",
    """'<div class="sep cli'+(x.limp?' limp':'')+'"'+(x.color?' style="border-left-color:'+x.color+'"':'')+'>'+esc(x.sep)+'</div>'""")
rep('#pages.compacto .tipo.soc{font-size:16px}','#pages.compacto .tipo.soc{font-size:16px}\n'
    '#pages.compacto .sep.cli{flex:none;height:36px;border-left:10px solid #8A93A6;background:#132233;border-radius:6px;'
    'padding:4px 14px 0;margin-top:4px;font-size:21px;letter-spacing:1.5px}')
open(p,'w').write(s); print('grupo ok')
# no dejar que una copia vieja de datos.json (caché de GitHub) pise los datos incrustados más nuevos
s=open(p).read()
old='RAWG="https://raw.githubusercontent.com/moisespena-web/tablero-dimaco-k7q3/main/",ultStamp="";'
assert s.count(old)==1
s=s.replace(old,'RAWG="https://raw.githubusercontent.com/moisespena-web/tablero-dimaco-k7q3/main/",ultStamp=(window.__DATOS__&&window.__DATOS__.stamp)||"";')
open(p,'w').write(s); print('stamp ok')
