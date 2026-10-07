"""6-oct-2026 (Moisés): tarjeta de estación = Faltan X · de total + barra entregadas / listas → siguiente / faltan aquí;
estado EN PROCESO cuando ya hay piezas hechas aunque la tablet diga NO INICIADA. Idempotente (marca PZ6OCT)."""
import glob,re,sys
HELP=r"""/* PZ6OCT · 6-oct-2026 (Moisés): Faltan X de total + barra entregadas / listas -> siguiente estación / faltan aquí */
function fmtN(n){return (+n||0).toLocaleString('en-US');}
function faltaPz(m){return Math.max(0,m.piezas-hz(m));}
function sigEst(m){var r=m.ruta||[],i=-1;r.forEach(function(x,k){if(x&&(x[2]===true||(i<0&&/TM-2P/i.test(x[0]))))i=k;});
 if(i<0)return '';for(var k=i+1;k<r.length;k++){if(r[k]&&r[k][1]!==null&&r[k][1]!==undefined)return String(r[k][0]).replace(/ Sierra$/,'');}return '';}
function barraPz(m){var T=m.plan||m.piezas||1,e=m.entr||0,h=hz(m),f=faltaPz(m),s=sigEst(m),w=function(n){return (100*n/T).toFixed(2)+'%';};
 return '<div class="bpz"><div class="bpzb"><i style="width:'+w(e)+';background:#25A35A"></i><i style="width:'+w(h)+';background:#3E8FD8"></i><i style="width:'+w(f)+';background:#2E3D52"></i></div>'+
 '<div class="bpzl"><span><i style="background:#25A35A"></i>'+fmtN(e)+' entregadas</span><span><i style="background:#3E8FD8"></i>'+fmtN(h)+(s?' listas → '+E(s):' listas para entregar')+'</span><span><i style="background:#2E3D52"></i>'+fmtN(f)+' faltan aquí</span></div></div>';}
function estTxtM(m){return (m.st.status==='none'&&hz(m)>0)?'EN PROCESO':estTxt(m.st);}
function estStyM(m){return (m.st.status==='none'&&hz(m)>0)?estSty({status:'prog',op:''}):estSty(m.st);}
"""
CSS=".bpz{margin-top:7px}.bpzb{display:flex;height:9px;border-radius:5px;overflow:hidden;background:#2E3D52}.bpzb i{display:block;height:100%}.bpzl{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:5px;font-size:13px;color:#C9D6E6}.bpzl i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}"
ok=True
for f in sorted(glob.glob('app-*/index.html')):
    t=open(f).read()
    if 'PZ6OCT' in t: print('ya',f); continue
    tm='app-tm2p' in f
    # 1) helpers after hz()
    t,n1=re.subn(r'(function hz\(m\)\{[^\n]*?\}\n)',lambda x:x.group(1)+HELP,t,count=1)
    # 2) css
    css=CSS+('.fila{flex-wrap:wrap;row-gap:4px}.bpz{flex-basis:100%;margin:0 0 2px 26px}' if tm else '')
    t,n2=re.subn(r'(</style>)',lambda x:css+x.group(1),t,count=1)
    # 3) piezas
    if tm:
        old="""'<div style="width:120px;flex:none;text-align:right"><b style="font-size:28px">'+hz(m)+'/'+m.piezas+'</b><div style="font-size:14px;color:var(--tx2)">piezas</div></div>'+"""
        new="""'<div style="width:130px;flex:none;text-align:right;line-height:1.1"><div style="font-size:14px;color:var(--tx2)">Faltan</div><b style="font-size:32px">'+fmtN(faltaPz(m))+'</b><div style="font-size:14px;color:var(--tx2)">de '+fmtN(m.plan)+'</div></div>'+"""
        n3=t.count(old); t=t.replace(old,new)
        old2="""'<div style="width:170px;flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:6px"><span style="font-size:24px;font-weight:700">'+m.entrega+'</span>'+badge(m)+'</div></button>';"""
        n4=t.count(old2); t=t.replace(old2,old2.replace("'</div></button>';","'</div>'+barraPz(m)+'</button>';"))
    else:
        old="""<b style="font-size:19px">'+hz(m)+'/'+m.piezas+' <span class="ks" style="font-weight:400">pz</span></b></div>'+"""
        new="""<span style="text-align:right;white-space:nowrap"><span class="ks">Faltan </span><b style="font-size:22px">'+fmtN(faltaPz(m))+'</b><span class="ks"> de '+fmtN(m.plan)+'</span></span></div>'+barraPz(m)+"""
        n3=t.count(old); t=t.replace(old,new); n4=n3
    # 4) estado en la lista
    seg=t
    n5=0
    for a,b in (("estSty(st)+'\">'+E(estTxt(st))","estStyM(m)+'\">'+E(estTxtM(m))"),("estSty(st)+'\">'+E(estTxt(st))".replace('\\"','"'),"estStyM(m)+'\">'+E(estTxtM(m))".replace('\\"','"'))):
        c=t.count(a); 
        if c: t=t.replace(a,b,1); n5+=1; break
    print(f,n1,n2,n3,n4,n5)
    if not(n1==1 and n2==1 and n3>=1 and n4>=1 and n5==1): ok=False; print('  !! falta algo, no se escribe'); continue
    open(f,'w').write(t)
sys.exit(0 if ok else 1)
