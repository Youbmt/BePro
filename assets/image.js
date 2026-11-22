function dims(){
  if(S.preset===PRESETS.length){const c=S.cu,k={cm:1,in:2.54,px:2.54/S.dpi}[c.u],a=+c.w*k,b=+c.h*k;return a>0&&b>0?[a,b]:null}
  let a=PRESETS[S.preset][1],b=PRESETS[S.preset][2];if(S.land)[a,b]=[b,a];return[a,b]}
function target(it){
  if(S.mode==='print'){const d=dims();if(!d)return null;return{w:Math.max(1,Math.round(d[0]/2.54*S.dpi)),h:Math.max(1,Math.round(d[1]/2.54*S.dpi)),fit:S.cover?'cover':'contain'}}
  if(S.mode==='resize'){const w=+S.w||0,h=+S.h||0;if(!w&&!h)return{w:it.w,h:it.h,fit:'stretch'};
    if(w&&h&&!S.lock)return{w,h,fit:'stretch'};
    const k=w&&h?Math.min(w/it.w,h/it.h):w?w/it.w:h/it.h;return{w:Math.max(1,Math.round(it.w*k)),h:Math.max(1,Math.round(it.h*k)),fit:'stretch'}}
  const k=S.max?Math.min(1,S.max/Math.max(it.w,it.h)):1;return{w:Math.round(it.w*k),h:Math.round(it.h*k),fit:'stretch'}
}
async function setDpi(b,d){const u=new Uint8Array(await b.arrayBuffer());
  if(u[2]===255&&u[3]===224&&u[6]===74&&u[7]===70){u[13]=1;u[14]=d>>8;u[15]=d&255;u[16]=d>>8;u[17]=d&255}
  return new Blob([u],{type:'image/jpeg'})}
async function proc(it,g){
  const t=target(it),pr=S.mode==='print';
  if(!t){it.err='أدخل العرض والارتفاع للمقاس المخصص.';return}
  if(t.w*t.h>3e7){it.err='الأبعاد المطلوبة كبيرة جداً، جرّب قياساً أصغر.';return}
  const[type,ext]=pr?FM.jpeg:FM[S.fmt];
  const c=document.createElement('canvas');c.width=t.w;c.height=t.h;
  const x=c.getContext('2d');x.imageSmoothingQuality='high';
  if(type==='image/jpeg'){x.fillStyle='#fff';x.fillRect(0,0,t.w,t.h)}
  let dx=0,dy=0,dw=t.w,dh=t.h;
  if(t.fit!=='stretch'){const k=(t.fit==='cover'?Math.max:Math.min)(t.w/it.w,t.h/it.h);dw=it.w*k;dh=it.h*k;dx=(t.w-dw)/2;dy=(t.h-dh)/2}
  x.drawImage(it.bmp,dx,dy,dw,dh);
  let blob=await new Promise(r=>c.toBlob(r,type,pr?.95:S.q/100));
  if(!blob){it.err='تعذّرت المعالجة، جرّب أبعاداً أصغر.';return}
  if(pr)blob=await setDpi(blob,S.dpi);
  if(g!==S.gen)return;
  const base=it.name.replace(/\.[^.]+$/,'')||'image';
  const nm=pr?base+'-'+dims().map(v=>+v.toFixed(1)).join('x')+'cm-'+S.dpi+'dpi.jpg':S.mode==='resize'?base+'-'+t.w+'x'+t.h+'.'+ext:base+'-compressed.'+ext;
  if(it.out)URL.revokeObjectURL(it.out.url);
  it.out={blob,url:URL.createObjectURL(blob),w:t.w,h:t.h,name:nm};
}
function queue(){clearTimeout(tm);tm=setTimeout(run,220)}
async function run(){
  const g=++S.gen;S.items.forEach(i=>{i.busy=true;i.err=null});draw();
  for(const it of S.items){
    if(g!==S.gen)return;
    try{await proc(it,g)}catch(e){it.err='تعذّرت معالجة هذه الصورة.'}
    if(g!==S.gen)return;
    it.busy=false;draw();
  }
}
async function add(list){
  const fs=[...list].filter(f=>f.type.startsWith('image/'));
  if(!fs.length){note('هذا الملف ليس صورة. اختر ملفاً بصيغة JPG أو PNG أو WebP.');return}
  let bad=0,full=false;
  for(const f of fs){
    if(S.items.length>=20){full=true;break}
    try{const b=await createImageBitmap(f);S.items.push({id:++uid,f,bmp:b,w:b.width,h:b.height,name:f.name||'image',src:URL.createObjectURL(f)})}catch(e){bad++}
  }
  if(full)note('الحد الأقصى 20 صورة في المرة الواحدة.');else if(bad)note('تعذّر فتح '+bad+' ملف. تأكد أنها صور بصيغة مدعومة.');
  queue();
}
async function save(it){
  const o=it.out;if(!o)return;
  if(DL){try{await DL.save({filename:o.name,data:o.blob})}catch(e){if(!e||e.code!=='declined')note('تعذّر حفظ الملف. اضغط مطولاً على الصورة المصغّرة لحفظها.')}}
  else{const a=document.createElement('a');a.href=o.url;a.download=o.name;document.body.appendChild(a);a.click();a.remove()}
}
function draw(){
  const L=$('#res');L.replaceChildren();
  let to=0,tn=0,done=0;
  S.items.forEach(it=>{
    const c=el('article','card'),th=el('img','th');th.alt='';th.src=it.out?it.out.url:it.src;c.append(th);
    const i=el('div','inf'),nm=el('div','nm',it.name);nm.dir='auto';i.append(nm);
    if(it.err)i.append(el('div','err',it.err));
    else if(it.busy||!it.out)i.append(el('div','mt','جارٍ المعالجة'));
    else{
      const o=it.out,m=el('div','mt');done++;to+=it.f.size;tn+=o.blob.size;
      m.append(nn(o.w+'×'+o.h+' px'));i.append(m);
      const s=el('div','mt');
      if(S.mode==='print'){s.append(nn(S.dpi+' DPI'),' ',nn(fmt(o.blob.size),'b'))}
      else{const old=el('s');old.append(nn(fmt(it.f.size)));const nw=el('b');nw.append(nn(fmt(o.blob.size)));s.append(old,' ',nw);
        const p=Math.round((1-o.blob.size/it.f.size)*100),bd=el('span','bd'+(p>0?'':' no'));
        if(p>0)bd.append(nn('−'+p+'%'));else bd.textContent='أكبر من الأصل';s.append(bd)}
      i.append(s);
    }
    c.append(i);
    const a=el('div','act'),d=el('button','btn s','تنزيل');d.disabled=!it.out||it.busy;d.onclick=()=>save(it);
    const r=el('button','lnk','إزالة');r.onclick=()=>{if(it.out)URL.revokeObjectURL(it.out.url);URL.revokeObjectURL(it.src);S.items=S.items.filter(z=>z!==it);draw()};
    a.append(d,r);c.append(a);L.append(c);
  });
  const sb=$('#sumbar');sb.hidden=!S.items.length;
  const sm=$('#sum');sm.replaceChildren();
  if(S.items.length&&done===S.items.length&&S.mode!=='print'&&to>0){
    const p=Math.round((1-tn/to)*100);
    sm.append('الإجمالي ',nn(fmt(to)),' إلى ',nn(fmt(tn)));
    if(p>0)sm.append(' ',nn('(−'+p+'%)'));
  }else sm.textContent=S.items.length+' صورة';
}
function sync(){
  $$('[data-m]').forEach(e=>e.hidden=!e.dataset.m.split(' ').includes(S.mode));
  $$('#tabs button').forEach(b=>b.setAttribute('aria-selected',b.dataset.t===S.mode));
  $$('#chips .chip').forEach((b,k)=>b.setAttribute('aria-pressed',k===S.preset));
  $$('#tg-o .chip').forEach(b=>b.setAttribute('aria-pressed',(b.dataset.v==='1')===S.land));
  $$('#tg-f .chip').forEach(b=>b.setAttribute('aria-pressed',(b.dataset.v==='1')===S.cover));
  const d=dims(),p=$('#pinfo'),cs=S.preset===PRESETS.length,r2=v=>+v.toFixed(2);
  $('#cust').hidden=!cs;$('#f-or').hidden=cs;
  if(d)p.replaceChildren('المقاس النهائي ',nn(r2(d[0])+' × '+r2(d[1])+' cm'),' = ',nn(r2(d[0]/2.54)+' × '+r2(d[1]/2.54)+' in'),' = ',nn(Math.round(d[0]/2.54*S.dpi)+' × '+Math.round(d[1]/2.54*S.dpi)+' px'));
  else p.textContent='أدخل العرض والارتفاع لتحديد المقاس.';
  $('#qv').textContent=S.q+'%';
  const png=S.fmt==='png'&&S.mode!=='print';$('#q').disabled=png;
}
PRESETS.forEach((p,k)=>{const b=el('button','chip',p[0]);b.append(el('small',null,p[1]+' × '+p[2]+' سم'));b.onclick=()=>{S.preset=k;sync();queue()};$('#chips').append(b)});
{const b=el('button','chip cu','مقاس مخصص');b.append(el('small',null,'سم أو إنش أو بكسل'));b.onclick=()=>{S.preset=PRESETS.length;sync();queue()};$('#chips').append(b)}
[['cw','w'],['ch','h']].forEach(([i,k])=>$('#'+i).oninput=e=>{S.cu[k]=e.target.value;sync();queue()});
$('#cu').onchange=e=>{S.cu.u=e.target.value;sync();queue()};
$$('#tabs button').forEach(b=>b.onclick=()=>{S.mode=b.dataset.t;sync();queue()});
$$('#tg-o .chip').forEach(b=>b.onclick=()=>{S.land=b.dataset.v==='1';sync();queue()});
$$('#tg-f .chip').forEach(b=>b.onclick=()=>{S.cover=b.dataset.v==='1';sync();queue()});
$('#q').oninput=e=>{S.q=+e.target.value;sync();queue()};
$('#fmt').onchange=e=>{S.fmt=e.target.value;sync();queue()};
$('#max').onchange=e=>{S.max=+e.target.value;queue()};
$('#dpi').onchange=e=>{S.dpi=+e.target.value;sync();queue()};
$('#w').oninput=e=>{S.w=e.target.value;queue()};
$('#h').oninput=e=>{S.h=e.target.value;queue()};
$('#lock').onchange=e=>{S.lock=e.target.checked;queue()};
$('#clr').onclick=()=>{S.gen++;S.items.forEach(i=>{if(i.out)URL.revokeObjectURL(i.out.url);URL.revokeObjectURL(i.src)});S.items=[];draw()};
const f=$('#file');f.onchange=()=>{add(f.files);f.value=''};
const dz=$('#drop');
['dragenter','dragover'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.add('over')}));
['dragleave','drop'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.remove('over')}));
dz.addEventListener('drop',ev=>add(ev.dataTransfer.files));
addEventListener('paste',ev=>{const fs=[...(ev.clipboardData&&ev.clipboardData.files||[])];if(fs.length)add(fs)});
sync();
$('#dall').onclick=async()=>{
  if(!window.JSZip){note('تعذّر تحميل مكتبة الضغط. أعد المحاولة.');return}
  const z=new JSZip(),u={};S.items.forEach(i=>{if(i.out){let n=i.out.name;while(u[n])n='_'+n;u[n]=1;z.file(n,i.out.blob)}});
  put('images.zip',await z.generateAsync({type:'blob'}))};
