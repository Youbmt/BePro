const FT={
 topdf:{t:'صور إلى PDF',d:'اجمع صورك في ملف PDF واحد، صفحة لكل صورة.',a:'image/*',h:'JPG وPNG وWebP',go:'إنشاء PDF'},
 togif:{t:'صور إلى GIF',d:'حوّل صورة أو عدة صور إلى GIF متحرك.',a:'image/*',h:'اختر صورتين أو أكثر لتحصل على حركة',go:'إنشاء GIF'},
 pdfmerge:{t:'دمج ملفات PDF',d:'اجمع عدة ملفات PDF في ملف واحد بترتيب اختيارك لها.',a:'application/pdf',h:'ملفات PDF',go:'دمج الملفات'},
 pdfsplit:{t:'تقسيم PDF',d:'استخرج صفحات محددة، أو افصل كل صفحة في ملف.',a:'application/pdf',h:'ملف PDF واحد',go:'تقسيم الملف'},
 zip:{t:'ضغط الملفات',d:'ضع أي ملفات داخل ملف ZIP واحد.',a:'',h:'أي نوع من الملفات',go:'ضغط إلى ZIP'}};
const F={mode:'',files:[],busy:false};
function fsel(){const L=$('#fl');L.replaceChildren();F.files.forEach(f=>{const r=el('div','mt');r.append(f.name+' ',nn(fmt(f.size)));L.append(r)});$('#fgo').disabled=!F.files.length}
function fsetup(m){const c=FT[m],i=$('#ffile');F.mode=m;F.files=[];
  $('#ft').textContent=c.t;$('#fd').textContent=c.d;$('#fh').textContent=c.h;$('#fgo').textContent=c.go;
  if(c.a)i.accept=c.a;else i.removeAttribute('accept');i.multiple=!/^(pdfsplit|pdfrotate|v|towrd|p2)/.test(m);
  $$('[data-fm]').forEach(e=>e.hidden=e.dataset.fm!==m);$('#fopt').hidden=!$$('#fopt [data-fm]:not([hidden])').length;
  $('#fres').replaceChildren();$('#fmsg').textContent='';fsel()}
function fadd(list){
  const img=FT[F.mode].a==='image/*',ok=[...list].filter(f=>F.mode==='zip'||(F.mode[0]==='v'?/^(video|audio)\//.test(f.type):img?f.type.startsWith('image/'):f.type==='application/pdf'||/\.pdf$/i.test(f.name)));
  if(!ok.length){note('نوع الملف غير مناسب لهذه الأداة.');return}
  F.files=/^(pdfsplit|pdfrotate|v|towrd|p2)/.test(F.mode)?ok.slice(0,1):F.files.concat(ok).slice(0,50);fsel()}
function fout(name,blob){
  const c=el('article','card'),i=el('div','inf'),m=el('div','mt'),b=el('button','btn s','تنزيل');
  m.append(nn(fmt(blob.size)));i.append(el('div','nm',name),m);b.onclick=()=>put(name,blob);
  c.append(el('span','ic c',name.split('.').pop().toUpperCase()),i,b);$('#fres').append(c)}
async function imgPdf(files,a4,sc){
  const pg=[];
  for(const f of files){const b=await createImageBitmap(f),c=document.createElement('canvas');c.width=b.width;c.height=b.height;
    const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);x.drawImage(b,0,0);
    const j=f.raw?f:await new Promise(r=>c.toBlob(r,'image/jpeg',.92));pg.push({w:b.width,h:b.height,d:new Uint8Array(await j.arrayBuffer())})}
  const enc=new TextEncoder(),parts=[],off=[],n=pg.length;let len=0;
  const add=p=>{parts.push(p);len+=p.length},s=t=>add(enc.encode(t)),obj=(i,fn)=>{off[i]=len;s(i+' 0 obj\n');fn();s('\nendobj\n')};
  s('%PDF-1.4\n');
  obj(1,()=>s('<</Type/Catalog/Pages 2 0 R>>'));
  obj(2,()=>s('<</Type/Pages/Count '+n+'/Kids['+pg.map((_,k)=>(5+k*3)+' 0 R').join(' ')+']>>'));
  pg.forEach((p,k)=>{
    const i=3+k*3;let pw=p.w*(sc||.75),ph=p.h*(sc||.75),dw=pw,dh=ph,dx=0,dy=0;
    if(a4){pw=595;ph=842;const q=Math.min(pw/p.w,ph/p.h);dw=p.w*q;dh=p.h*q;dx=(pw-dw)/2;dy=(ph-dh)/2}
    const cs='q '+dw.toFixed(2)+' 0 0 '+dh.toFixed(2)+' '+dx.toFixed(2)+' '+dy.toFixed(2)+' cm /I Do Q';
    obj(i,()=>{s('<</Type/XObject/Subtype/Image/Width '+p.w+'/Height '+p.h+'/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/DCTDecode/Length '+p.d.length+'>>\nstream\n');add(p.d);s('\nendstream')});
    obj(i+1,()=>s('<</Length '+cs.length+'>>\nstream\n'+cs+'\nendstream'));
    obj(i+2,()=>s('<</Type/Page/Parent 2 0 R/MediaBox[0 0 '+pw.toFixed(2)+' '+ph.toFixed(2)+']/Resources<</XObject<</I '+i+' 0 R>>>>/Contents '+(i+1)+' 0 R>>'))});
  const tot=3+n*3,xo=len;s('xref\n0 '+tot+'\n0000000000 65535 f \n');
  for(let i=1;i<tot;i++)s(String(off[i]).padStart(10,'0')+' 00000 n \n');
  s('trailer\n<</Size '+tot+'/Root 1 0 R>>\nstartxref\n'+xo+'\n%%EOF');
  return new Blob(parts,{type:'application/pdf'})}
function lzw(px,o){
  let bits=9,next=258,buf=0,nb=0,blk=[];const dict=new Map();
  const emit=c=>{buf|=c<<nb;nb+=bits;while(nb>=8){blk.push(buf&255);buf>>=8;nb-=8;if(blk.length===255){o.push(255,...blk);blk=[]}}};
  emit(256);let cur=px[0];
  for(let i=1;i<px.length;i++){
    const s=px[i],key=cur<<8|s,v=dict.get(key);
    if(v!==undefined){cur=v;continue}
    emit(cur);if(next>=(1<<bits)&&bits<12)bits++;
    if(next<4096)dict.set(key,next++);else{emit(256);dict.clear();next=258;bits=9}
    cur=s}
  emit(cur);emit(257);if(nb>0)blk.push(buf&255);if(blk.length)o.push(blk.length,...blk);o.push(0)}
function gif(frames,w,h,delay){
  const o=[71,73,70,56,57,97],u=v=>o.push(v&255,v>>8&255);u(w);u(h);o.push(247,0,0);
  for(let r=0;r<6;r++)for(let g=0;g<6;g++)for(let b=0;b<6;b++)o.push(r*51,g*51,b*51);
  for(let i=216;i<256;i++)o.push(0,0,0);
  o.push(33,255,11,78,69,84,83,67,65,80,69,50,46,48,3,1,0,0,0);
  frames.forEach(d=>{
    o.push(33,249,4,0);u(Math.round(delay/10));o.push(0,0,44);u(0);u(0);u(w);u(h);o.push(0,8);
    const px=new Uint8Array(w*h),q=(i,c)=>Math.round(d[i*4+c]/51);
    for(let i=0;i<w*h;i++)px[i]=q(i,0)*36+q(i,1)*6+q(i,2);
    lzw(px,o)});
  o.push(59);return new Blob([Uint8Array.from(o)],{type:'image/gif'})}
async function mkGif(files,w0,delay){
  const fr=[];let w,h;
  for(const f of files){const b=await createImageBitmap(f);
    if(!w){w=Math.min(w0,b.width);h=Math.round(b.height*w/b.width)}
    const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,w,h);
    const k=Math.min(w/b.width,h/b.height);x.drawImage(b,(w-b.width*k)/2,(h-b.height*k)/2,b.width*k,b.height*k);
    fr.push(x.getImageData(0,0,w,h).data)}
  return gif(fr,w,h,delay)}
async function pdfMerge(files){
  const o=await PDFLib.PDFDocument.create();
  for(const f of files){const d=await PDFLib.PDFDocument.load(await f.arrayBuffer(),{ignoreEncryption:true});(await o.copyPages(d,d.getPageIndices())).forEach(p=>o.addPage(p))}
  return new Blob([await o.save()],{type:'application/pdf'})}
async function pdfSplit(f,spec){
  const d=await PDFLib.PDFDocument.load(await f.arrayBuffer(),{ignoreEncryption:true}),n=d.getPageCount();
  const mk=async ix=>{const o=await PDFLib.PDFDocument.create();(await o.copyPages(d,ix)).forEach(p=>o.addPage(p));return new Blob([await o.save()],{type:'application/pdf'})};
  spec=spec.replace(/[٠-٩]/g,c=>c.charCodeAt(0)-1632).trim();
  if(!spec){const z=new JSZip();for(let i=0;i<n;i++)z.file('page-'+(i+1)+'.pdf',await mk([i]));return[await z.generateAsync({type:'blob'}),'pages.zip']}
  const ix=[];spec.split(/[,،]/).forEach(p=>{const m=p.trim().match(/^(\d+)(?:\s*-\s*(\d+))?$/);if(m)for(let i=+m[1];i<=+(m[2]||m[1]);i++)if(i>=1&&i<=n)ix.push(i-1)});
  if(!ix.length)throw new Error('range');return[await mk(ix),'pages.pdf']}
async function zipFiles(files){
  const z=new JSZip(),u={};files.forEach(f=>{let n=f.name;while(u[n])n='_'+n;u[n]=1;z.file(n,f)});
  return z.generateAsync({type:'blob',compression:'DEFLATE',compressionOptions:{level:9}})}
async function fgo(){
  const m=F.mode;if(F.busy||!F.files.length)return;
  if((/^pdf/.test(m)&&!(window.PDFLib&&window.JSZip))||(m==='zip'&&!window.JSZip)){note('تعذّر تحميل مكتبة الأداة. تحقق من الاتصال وأعد المحاولة.');return}
  F.busy=true;$('#fgo').disabled=true;$('#fmsg').textContent='';$('#fres').replaceChildren(el('div','mt','جارٍ المعالجة'));
  try{let b,n;const fl=F.files;
    if(m==='topdf'){b=await imgPdf(fl,$('#fsz').value==='a4');n='images.pdf'}
    else if(m==='togif'){b=await mkGif(fl,+$('#fgw').value,+$('#fdl').value);n='animation.gif'}
    else if(m==='pdfmerge'){b=await pdfMerge(fl);n='merged.pdf'}
    else if(m==='pdfsplit'){[b,n]=await pdfSplit(fl[0],$('#fsp').value)}
    else if(m==='towrd'){[b,n]=await pdf2word(fl[0])}
    else if(EXTRA[m]){[b,n]=await EXTRA[m](fl[0])}
    else if(m[0]==='v'){[b,n]=await VID[m](fl[0])}
    else{b=await zipFiles(fl);n='files.zip'}
    $('#fres').replaceChildren();fout(n,b)
  }catch(e){$('#fres').replaceChildren();note(e&&e.u?e.u:e&&e.message==='range'?'اكتب أرقام صفحات صحيحة، مثل 1-3,5.':'تعذّرت المعالجة. تأكد أن الملفات سليمة وبالصيغة الصحيحة.')}
  F.busy=false;$('#fgo').disabled=!F.files.length}
$('#fgo').onclick=fgo;
$('#ffile').onchange=e=>{fadd(e.target.files);e.target.value=''};
const fdz=$('#fdrop');
['dragenter','dragover'].forEach(e=>fdz.addEventListener(e,ev=>{ev.preventDefault();fdz.classList.add('over')}));
['dragleave','drop'].forEach(e=>fdz.addEventListener(e,ev=>{ev.preventDefault();fdz.classList.remove('over')}));
fdz.addEventListener('drop',ev=>fadd(ev.dataTransfer.files));
FT.towrd={t:'PDF إلى Word',d:'حوّل نص ملف PDF إلى مستند Word قابل للتحرير.',a:'application/pdf',h:'ملف PDF واحد يحتوي نصاً (وليس صوراً ممسوحة)',go:'تحويل إلى Word'};
const esc=t=>t.replace(/[<>&]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
async function pdf2word(f){
  if(!window.pdfjsLib||!window.JSZip)throw new Error('lib');
  pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  const doc=await pdfjsLib.getDocument({data:new Uint8Array(await f.arrayBuffer())}).promise,ps=[];let any=false;
  for(let p=1;p<=doc.numPages;p++){
    const tc=await(await doc.getPage(p)).getTextContent(),rows=[];
    tc.items.forEach(it=>{if(!it.str.trim())return;const y=Math.round(it.transform[5]);let r=rows.find(r=>Math.abs(r.y-y)<4);if(!r)rows.push(r={y,a:[]});r.a.push(it)});
    rows.sort((a,b)=>b.y-a.y);
    const ls=rows.map(r=>{const rtl=/[\u0600-\u06FF]/.test(r.a.map(i=>i.str).join(''));r.a.sort((a,b)=>rtl?b.transform[4]-a.transform[4]:a.transform[4]-b.transform[4]);return{t:r.a.map(i=>i.str).join(' ').replace(/\s+/g,' ').trim(),rtl}});
    if(ls.length)any=true;ps.push(ls)}
  if(!any)throw Object.assign(new Error('u'),{u:'لم أجد نصاً في الملف. قد يكون صوراً ممسوحة تحتاج OCR.'});
  const body=ps.map((ls,i)=>ls.map(l=>'<w:p><w:pPr>'+(l.rtl?'<w:bidi/>':'')+'</w:pPr><w:r><w:rPr>'+(l.rtl?'<w:rtl/>':'')+'</w:rPr><w:t xml:space="preserve">'+esc(l.t)+'</w:t></w:r></w:p>').join('')+(i<ps.length-1?'<w:p><w:r><w:br w:type="page"/></w:r></w:p>':'')).join('');
  const z=new JSZip(),X='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
  z.file('[Content_Types].xml',X+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>');
  z.file('_rels/.rels',X+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>');
  z.file('word/document.xml',X+'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+body+'</w:body></w:document>');
  return[await z.generateAsync({type:'blob',mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}),f.name.replace(/\.[^.]+$/,'')+'.docx']}
FT.p2img={t:'PDF إلى صور',d:'حوّل صفحات PDF إلى صور JPG داخل ملف ZIP.',a:'application/pdf',h:'ملف PDF واحد',go:'تحويل إلى صور'};
FT.p2cmp={t:'ضغط PDF',d:'قلّل حجم PDF بتحويل صفحاته إلى صور مضغوطة.',a:'application/pdf',h:'ملف PDF واحد',go:'ضغط الملف'};
FT.pdfrotate={t:'تدوير صفحات PDF',d:'دوّر كل صفحات PDF بزاوية 90 أو 180 أو 270 درجة.',a:'application/pdf',h:'ملف PDF واحد',go:'تدوير الملف'};
async function pgs(f,sc,q){
  if(!window.pdfjsLib||!window.JSZip)throw new Error('lib');
  pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  const doc=await pdfjsLib.getDocument({data:new Uint8Array(await f.arrayBuffer())}).promise,o=[];
  for(let p=1;p<=doc.numPages;p++){const pg=await doc.getPage(p),vp=pg.getViewport({scale:sc}),c=document.createElement('canvas');c.width=vp.width;c.height=vp.height;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);await pg.render({canvasContext:x,viewport:vp}).promise;o.push(await new Promise(r=>c.toBlob(r,'image/jpeg',q)))}
  return o}
const bn=f=>f.name.replace(/\.[^.]+$/,'');
const EXTRA={
 async p2img(f){const o=await pgs(f,+$('#pis').value,.9),z=new JSZip();o.forEach((b,i)=>z.file('page-'+(i+1)+'.jpg',b));return[await z.generateAsync({type:'blob'}),bn(f)+'-images.zip']},
 async p2cmp(f){const[s,q]=$('#pcl').value.split(',').map(Number),o=await pgs(f,s,q);o.forEach(b=>b.raw=1);return[await imgPdf(o,false,1/s),bn(f)+'-compressed.pdf']},
 async pdfrotate(f){const d=await PDFLib.PDFDocument.load(await f.arrayBuffer(),{ignoreEncryption:true}),a=+$('#pra').value;d.getPages().forEach(p=>p.setRotation(PDFLib.degrees((p.getRotation().angle+a)%360)));return[new Blob([await d.save()],{type:'application/pdf'}),bn(f)+'-rotated.pdf']}};

Object.assign(FT,window.VFT||{});
fsetup(document.body.dataset.mode);
