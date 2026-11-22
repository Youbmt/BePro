import re,json,os,zipfile,subprocess
BASE=os.path.dirname(os.path.abspath(__file__))
SRC=BASE+'/src-image-workshop.html'
OUT=BASE+'/public'
SITE='https://bepro-gamma.vercel.app'
h=open(SRC,encoding='utf-8').read().replace('ورشة الصور','BePro')
css=h.split('<style>')[1].split('</style>')[0]
js=h.rsplit('<script>',1)[1].split('</script>')[0]
def blk(a,b):
    i=h.index(a);j=h.index(b,i);s=h[i+len(a):j].rstrip()
    assert s.endswith('</div>');return s[:-6].strip()
home=blk('<div id="v-home">','<div id="v-tool" hidden>')
tool=blk('<div id="v-tool" hidden>','<div id="v-file" hidden>')
fil=blk('<div id="v-file" hidden>','\n</div>\n\n<script>')
def rep(s,a,b):
    assert a in s,a;return s.replace(a,b)
P2W=r'''FT.towrd={t:'PDF إلى Word',d:'حوّل نص ملف PDF إلى مستند Word قابل للتحرير.',a:'application/pdf',h:'ملف PDF واحد يحتوي نصاً (وليس صوراً ممسوحة)',go:'تحويل إلى Word'};
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
'''
WMJS=r'''const cv=$('#wcv'),cx=cv.getContext('2d');let base=null,sel=null,drag=null,hist=[],nm='image';
async function wload(f){
  const b=await createImageBitmap(f),k=Math.min(1,3000/Math.max(b.width,b.height));
  cv.width=Math.round(b.width*k);cv.height=Math.round(b.height*k);cx.drawImage(b,0,0,cv.width,cv.height);
  base=cx.getImageData(0,0,cv.width,cv.height);hist=[];sel=null;nm=f.name.replace(/\.[^.]+$/,'');$('#wtool').hidden=false;wdraw()}
function wdraw(){
  cx.putImageData(base,0,0);
  if(sel){cx.save();cx.strokeStyle='#E5007D';cx.lineWidth=Math.max(2,cv.width/300);cx.setLineDash([8,6]);cx.strokeRect(sel.x,sel.y,sel.w,sel.h);cx.restore()}
  $('#wgo').disabled=!sel;$('#wundo').disabled=!hist.length}
const cl=(v,m)=>Math.max(0,Math.min(m,v)),pos=e=>{const r=cv.getBoundingClientRect();return[cl((e.clientX-r.left)*cv.width/r.width,cv.width),cl((e.clientY-r.top)*cv.height/r.height,cv.height)]};
cv.onpointerdown=e=>{drag=pos(e);cv.setPointerCapture(e.pointerId)};
cv.onpointermove=e=>{if(!drag)return;const[x,y]=pos(e);sel={x:Math.round(Math.min(drag[0],x)),y:Math.round(Math.min(drag[1],y)),w:Math.round(Math.abs(x-drag[0])),h:Math.round(Math.abs(y-drag[1]))};wdraw()};
cv.onpointerup=()=>{drag=null;if(sel&&(sel.w<3||sel.h<3))sel=null;wdraw()};
$('#wgo').onclick=()=>{
  hist.push(new ImageData(new Uint8ClampedArray(base.data),base.width,base.height));
  const{x,y,w,h}=sel,W=base.width,H=base.height,D=base.data,P=(i,j)=>(cl(j,H-1)*W+cl(i,W-1))*4,out=new Uint8ClampedArray(w*h*3);
  for(let j=0;j<h;j++)for(let i=0;i<w;i++){
    const t=(i+1)/(w+1),s=(j+1)/(h+1),L=P(x-1,y+j),R=P(x+w,y+j),T=P(x+i,y-1),B=P(x+i,y+h),a=1/Math.min(i+1,w-i),b=1/Math.min(j+1,h-j),o=(j*w+i)*3;
    for(let c=0;c<3;c++)out[o+c]=((D[L+c]*(1-t)+D[R+c]*t)*a+(D[T+c]*(1-s)+D[B+c]*s)*b)/(a+b)}
  for(let j=0;j<h;j++)for(let i=0;i<w;i++){const o=(j*w+i)*3,p=P(x+i,y+j);D[p]=out[o];D[p+1]=out[o+1];D[p+2]=out[o+2]}
  sel=null;wdraw()};
$('#wundo').onclick=()=>{if(hist.length){base=hist.pop();wdraw()}};
$('#wdl').onclick=()=>{if(!base)return;cx.putImageData(base,0,0);cv.toBlob(b=>{put(nm+'-clean.png',b);wdraw()},'image/png')};
const wf=$('#wfile');wf.onchange=e=>{const f=e.target.files[0];e.target.value='';if(f)wload(f).catch(()=>note('تعذّر فتح الصورة.'))};
const wd=$('#wdrop');
['dragenter','dragover'].forEach(e=>wd.addEventListener(e,ev=>{ev.preventDefault();wd.classList.add('over')}));
['dragleave','drop'].forEach(e=>wd.addEventListener(e,ev=>{ev.preventDefault();wd.classList.remove('over')}));
wd.addEventListener('drop',ev=>{const f=ev.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))wload(f).catch(()=>note('تعذّر فتح الصورة.'))});
'''
WMBODY='''<header>
  <a class="brand" href="/"><span class="strip" aria-hidden="true"><i></i><i></i><i></i><i></i></span>BePro<span class="back">الرئيسية</span></a>
  <h1>{H1}</h1>
  <p class="sub">{D}</p>
</header>
<div class="drop" id="wdrop"><i></i><i></i><i></i><i></i>
  <label class="zone" for="wfile"><span class="zt">أفلت صورتك هنا</span><span class="zh">JPG وPNG وWebP</span><span class="btn">اختر صورة</span></label>
  <input class="sr" type="file" id="wfile" accept="image/*">
</div>
<div id="msg" role="status" aria-live="polite"></div>
<section id="wtool" hidden>
  <p class="hint">حدّد منطقة العلامة بالسحب بإصبعك أو بالماوس على الصورة، ثم اضغط حذف. تعمل جيداً مع الشعارات الصغيرة والخلفيات البسيطة، وتصعب على الخلفيات المعقدة. استخدمها على صورك أنت.</p>
  <canvas id="wcv"></canvas>
  <div class="row"><button class="btn" id="wgo" disabled>حذف المنطقة</button><button class="btn" id="wundo" disabled>تراجع</button></div>
  <button class="btn" id="wdl">تنزيل الصورة</button>
</section>'''
NEWC='<a class="tl" href="/pdf-to-word"><span class="ic m"><svg viewBox="0 0 24 24"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/></svg></span><b>PDF إلى Word</b><p>حوّل نص ملف PDF إلى مستند Word.</p></a>\n    <a class="tl" href="/remove-watermark"><span class="ic y"><svg viewBox="0 0 24 24"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7M5 11l9 9"/></svg></span><b>إزالة العلامة المائية</b><p>امسح شعاراً من صورتك بتحديد المنطقة.</p></a>'
LEG='''
def legal(slug,h1,secs):
    body='<header><a class="brand" href="/"><span class="strip" aria-hidden="true"><i></i><i></i><i></i><i></i></span>BePro<span class="back">الرئيسية</span></a><h1>%s</h1></header><div class="legal">%s</div>'%(h1,''.join('<h2>%s</h2><p>%s</p>'%x for x in secs))
    W(slug+'.html',page(slug,'legal',h1+' | BePro',h1+' لموقع BePro.',body,'',''))
legal('privacy','سياسة الخصوصية',[('خصوصية ملفاتك','تُعالَج صورك وملفاتك داخل متصفحك على جهازك، ولا تُرفع إلى خوادمنا ولا نحتفظ بنسخة منها.'),('خدمات خارجية','تُحمَّل الخطوط من Google Fonts والمكتبات البرمجية من cdnjs وjsDelivr، وقد تتلقى هذه الجهات عنوان IP وبيانات المتصفح المعتادة عند التحميل. وتعمل أدوات الفيديو وPDF إلى Word بمكتبات تُحمَّل من هذه الشبكات وقت الاستخدام.'),('الإعلانات وملفات تعريف الارتباط','قد نعرض إعلانات من جهات خارجية مثل Google AdSense، وقد تستخدم ملفات تعريف الارتباط لعرض إعلانات مناسبة لاهتماماتك. يمكنك إدارة ذلك من إعدادات إعلانات Google أو من إعدادات متصفحك.'),('الإحصاءات','قد نستخدم أداة إحصاءات لمعرفة عدد الزيارات والصفحات الأكثر استخداماً دون تحديد هويتك.'),('التواصل','لأي استفسار عن هذه السياسة استخدم صفحة اتصل بنا.'),('آخر تحديث','22 نوفمبر 2026.')])
legal('about','من نحن',[('ما هو الموقع','BePro موقع أدوات مجانية للصور والملفات والفيديو، بلا تسجيل ولا علامات مائية.'),('كيف يعمل','تعمل الأدوات داخل متصفحك، فتبقى ملفاتك على جهازك.'),('اقتراحاتك','نضيف أدوات جديدة باستمرار، وتجد طريقة التواصل في صفحة اتصل بنا.')])
legal('contact','اتصل بنا',[('راسلنا','للاقتراحات أو الإبلاغ عن مشكلة أو طلب أداة جديدة، راسلنا على <a href="mailto:nukhbaarabtheme@gmail.com">nukhbaarabtheme@gmail.com</a>.')])
'''
FOPT2='''
  <div class="f" data-fm="p2img"><label for="pis">جودة الصور</label><select id="pis"><option value="1.5">عادية</option><option value="2" selected>عالية</option><option value="3">عالية جداً (أبطأ)</option></select></div>
  <div class="f" data-fm="p2cmp"><label for="pcl">مستوى الضغط</label><select id="pcl"><option value="1.8,0.75">خفيف</option><option value="1.4,0.6" selected>متوسط</option><option value="1.1,0.45">قوي</option></select><small>يحوّل الصفحات إلى صور، فيفقد النص القابل للتحديد.</small></div>
  <div class="f" data-fm="pdfrotate"><label for="pra">زاوية التدوير</label><select id="pra"><option value="90">90 درجة</option><option value="180">180 درجة</option><option value="270">270 درجة</option></select></div>
'''
fil=re.sub(r'(<section class="panel" id="fopt" hidden>.*?)(</section>)',lambda x:x.group(1)+FOPT2+x.group(2),fil,count=1,flags=re.S)
TXTJS=r'''const M=document.body.dataset.mode,tin=$('#tin'),tout=$('#tout'),tl=$('#tlist'),D1='٠١٢٣٤٥٦٧٨٩',D2='۰۱۲۳۴۵۶۷۸۹',opt=i=>{const e=document.getElementById(i);return e?e.value:''};
const O=['','واحد','اثنان','ثلاثة','أربعة','خمسة','ستة','سبعة','ثمانية','تسعة','عشرة','أحد عشر','اثنا عشر','ثلاثة عشر','أربعة عشر','خمسة عشر','ستة عشر','سبعة عشر','ثمانية عشر','تسعة عشر'],
T=['','','عشرون','ثلاثون','أربعون','خمسون','ستون','سبعون','ثمانون','تسعون'],
H=['','مائة','مائتان','ثلاثمائة','أربعمائة','خمسمائة','ستمائة','سبعمائة','ثمانمائة','تسعمائة'],
SC=[['','',''],['ألف','ألفان','آلاف'],['مليون','مليونان','ملايين'],['مليار','ملياران','مليارات']],
CUR={sar:[['ريال','ريالان','ريالات'],['هللة','هللتان','هللات']],aed:[['درهم','درهمان','دراهم'],['فلس','فلسان','فلوس']],kwd:[['دينار','ديناران','دنانير'],['فلس','فلسان','فلوس']],egp:[['جنيه','جنيهان','جنيهات'],['قرش','قرشان','قروش']],usd:[['دولار','دولاران','دولارات'],['سنت','سنتان','سنتات']]};
function w3(n){const h=n/100|0,r=n%100,p=[];if(h)p.push(H[h]);if(r){if(r<20)p.push(O[r]);else{const o=r%10;p.push(o?O[o]+' و'+T[r/10|0]:T[r/10|0])}}return p.join(' و')}
function aw(n){const g=[];while(n>0){g.push(n%1000);n=Math.floor(n/1000)}const p=[];for(let i=g.length-1;i>=0;i--){const v=g[i];if(!v)continue;p.push(i===0?w3(v):v===1?SC[i][0]:v===2?SC[i][1]:w3(v)+' '+(v<=10?SC[i][2]:SC[i][0]))}return p.join(' و')}
const part=(v,u)=>v===1?u[0]+' واحد':v===2?u[1]:aw(v)+' '+(v%100>=3&&v%100<=10?u[2]:u[0]);
const MODES={
 tshk:t=>t.replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]/g,''),
 tdig:t=>opt('tdir')==='h'?t.replace(/[0-9]/g,d=>D1[d]):t.replace(/[٠-٩]/g,d=>D1.indexOf(d)).replace(/[۰-۹]/g,d=>D2.indexOf(d)),
 tnum:t=>{const s=t.replace(/[٠-٩]/g,d=>D1.indexOf(d)).replace(/[^\d.]/g,'');if(!s)return'';const p=s.split('.'),n=+p[0],fr=+((p[1]||'')+'00').slice(0,2);if(!(n<1e12))return'الرقم كبير جداً';const c=CUR[opt('tcur')]||CUR.sar;
  const r=(n?part(n,c[0]):'')+(fr?(n?' و':'')+part(fr,c[1]):'');return r?'فقط '+r+' لا غير':'صفر '+c[0][0]},
 tcnt:t=>'الكلمات: '+(t.trim().match(/\S+/g)||[]).length+'\nالحروف (بالمسافات): '+t.length+'\nالحروف (بدون مسافات): '+t.replace(/\s/g,'').length+'\nالأسطر: '+(t?t.split('\n').length:0)+'\nالجمل: '+(t.match(/[.!؟?]+/g)||[]).length,
 tcln:t=>t.replace(/[ \t]+/g,' ').replace(/ ?\n ?/g,'\n').replace(/\n{3,}/g,'\n\n').trim()};
const NC='اأإآدذرزوؤءةى',AR=/[\u0621-\u064A]/,K=(s,k)=>[...s].map((c,i,a)=>AR.test(c)&&!NC.includes(c)&&a[i+1]&&AR.test(a[i+1])?c+k:c).join('');
const DEC=[s=>K(s,'ـ'),s=>K(s,'ـــ'),s=>'★彡 '+s+' 彡★',s=>'༺ '+s+' ༻',s=>'♥ '+s+' ♥',s=>'『 '+s+' 』',s=>'✿ '+s+' ✿',s=>'﴾ '+s+' ﴿',s=>'꧁ '+s+' ꧂'];
async function cp(s){try{await navigator.clipboard.writeText(s);note('تم النسخ.')}catch(e){note('تعذّر النسخ، انسخ النص يدوياً.')}}
function go(){
  const t=tin.value;
  if(M==='tdec'){tl.replaceChildren();if(!t.trim())return;DEC.forEach(f=>{const s=f(t.trim()),d=el('div','it'),b=el('button','btn s','نسخ');b.onclick=()=>cp(s);d.append(el('span',null,s),b);tl.append(d)});return}
  tout.value=MODES[M](t)}
tin.oninput=go;$$('select').forEach(x=>x.onchange=go);$('#tcopy').onclick=()=>cp(tout.value);
if(M==='tdec')$('#tbox').hidden=true;
'''
TXTBODY='''<header>
  <a class="brand" href="/"><span class="strip" aria-hidden="true"><i></i><i></i><i></i><i></i></span>BePro<span class="back">الرئيسية</span></a>
  <h1>{H1}</h1>
  <p class="sub">{D}</p>
</header>
{OPT}
<div class="f"><label for="tin">اكتب أو الصق النص هنا</label><textarea id="tin" rows="6" dir="auto"></textarea></div>
<div class="f" id="tbox"><label for="tout">النتيجة</label><textarea id="tout" rows="6" dir="auto" readonly></textarea><button class="btn" id="tcopy">نسخ النتيجة</button></div>
<div class="res" id="tlist"></div>
<div id="msg" role="status" aria-live="polite"></div>'''
TO={'tdig': '<section class="panel"><div class="f"><label for="tdir">التحويل</label><select id="tdir"><option value="h">إلى أرقام هندية (٠١٢)</option><option value="e">إلى أرقام إنجليزية (012)</option></select></div></section>', 'tnum': '<section class="panel"><div class="f"><label for="tcur">العملة</label><select id="tcur"><option value="sar">ريال سعودي</option><option value="aed">درهم إماراتي</option><option value="kwd">دينار كويتي</option><option value="egp">جنيه مصري</option><option value="usd">دولار أمريكي</option></select></div></section>'}
PREVJS=r'''const PJW='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
async function pdfThumb(f,w){
  if(!window.pdfjsLib)return null;
  try{pdfjsLib.GlobalWorkerOptions.workerSrc=PJW;
    const d=await pdfjsLib.getDocument({data:new Uint8Array(await f.arrayBuffer())}).promise,p=await d.getPage(1),s=w/p.getViewport({scale:1}).width,v=p.getViewport({scale:s}),c=document.createElement('canvas');
    c.width=v.width;c.height=v.height;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);await p.render({canvasContext:x,viewport:v}).promise;return c}catch(e){return null}}
function prev(f,name){
  const t=f.type||'',ext=(name.split('.').pop()||'').toUpperCase().slice(0,4),u=URL.createObjectURL(f);
  if(t.startsWith('image/')){const i=el('img','th');i.alt='';i.src=u;const g=el('img','pm');g.alt='';g.src=u;return[i,g]}
  if(t.startsWith('video/')){const v=el('video','pm');v.src=u+'#t=0.1';v.controls=true;v.muted=true;v.playsInline=true;v.preload='metadata';return[el('span','ic c',ext),v]}
  if(t.startsWith('audio/')){const a=el('audio','pm');a.src=u;a.controls=true;a.preload='metadata';return[el('span','ic m',ext),a]}
  const ic=el('span','ic '+(t==='application/pdf'?'y':'g'),ext);
  if(t==='application/pdf'||/\.pdf$/i.test(name))pdfThumb(f,160).then(c=>{if(c){c.className='th';ic.replaceWith(c)}});
  return[ic,null]}
function fsel(){
  const L=$('#fl');L.replaceChildren();
  F.files.forEach((f,k)=>{
    const c=el('article','card'),i=el('div','inf'),m=el('div','mt'),a=el('div','act'),x=el('button','lnk','إزالة');
    if(!f._pv)f._pv=prev(f,f.name);
    const p=f._pv[0],big=f._pv[1];
    m.append(nn(fmt(f.size)));i.append(el('div','nm',f.name),m);x.onclick=()=>{F.files.splice(k,1);fsel()};a.append(x);
    c.append(p,i,a);if(big&&!(f.type||'').startsWith('image/'))c.append(big);L.append(c)});
  $('#fgo').disabled=!F.files.length}
function fout(name,blob){
  const c=el('article','card'),i=el('div','inf'),m=el('div','mt'),b=el('button','btn s','تنزيل'),r=prev(new File([blob],name,{type:blob.type}),name);
  m.append(nn(fmt(blob.size)));i.append(el('div','nm',name),m);b.onclick=()=>put(name,blob);
  c.append(r[0],i,b);if(r[1])c.append(r[1]);$('#fres').append(c)}
'''
ix=js.index
A=js[:ix('function dims(){')]
A=rep(A,"$('#v-file').hidden?$('#msg'):$('#fmsg')","$('#fmsg')||$('#msg')")
A=rep(A,"S={mode:'compress'","S={mode:document.body.dataset.mode||'compress'")
IMG=js[ix('function dims(){'):ix('async function put(')]
PUT=js[ix('async function put('):ix("$('#dall')")]
DALL=js[ix("$('#dall')"):ix('const FT=')]
FIL=js[ix('const FT='):ix('function route(){')]
FIL=rep(FIL,"i.multiple=m!=='pdfsplit'","i.multiple=!/^(pdfsplit|pdfrotate|v|towrd|p2)/.test(m)")
FIL=rep(FIL,"F.mode==='pdfsplit'?ok.slice(0,1)","/^(pdfsplit|pdfrotate|v|towrd|p2)/.test(F.mode)?ok.slice(0,1)")
FIL=rep(FIL,"(img?f.type.startsWith('image/')","(F.mode[0]==='v'?/^(video|audio)\\//.test(f.type):img?f.type.startsWith('image/')")
FIL=rep(FIL,"else{b=await zipFiles(fl);n='files.zip'}","else if(m==='towrd'){[b,n]=await pdf2word(fl[0])}\n    else if(EXTRA[m]){[b,n]=await EXTRA[m](fl[0])}\n    else if(m[0]==='v'){[b,n]=await VID[m](fl[0])}\n    else{b=await zipFiles(fl);n='files.zip'}")
FIL=rep(FIL,"note(e&&e.message==='range'?","note(e&&e.u?e.u:e&&e.message==='range'?")
FIL=rep(FIL,"async function imgPdf(files,a4){","async function imgPdf(files,a4,sc){")
FIL=rep(FIL,"let pw=p.w*.75,ph=p.h*.75","let pw=p.w*(sc||.75),ph=p.h*(sc||.75)")
FIL=rep(FIL,"const j=await new Promise(r=>c.toBlob(r,'image/jpeg',.92));","const j=f.raw?f:await new Promise(r=>c.toBlob(r,'image/jpeg',.92));")
FIL=rep(FIL,"e.dataset.fm!==m","!e.dataset.fm.split(' ').includes(m)")
FIL,n1=re.subn(r'function fsel\(\)\{.*?\n(?=function fsetup)','',FIL,flags=re.S)
FIL,n2=re.subn(r'function fout\(.*?\n(?=async function imgPdf)','',FIL,flags=re.S)
assert n1==1 and n2==1
FIL=rep(FIL,"}catch(e){$('#fres').replaceChildren();note(","}catch(e){$('#fres').replaceChildren();if(e&&e.message&&!e.u&&e.message!=='range'){const d=el('div','mt',e.message);d.dir='ltr';$('#fres').append(d)}note(")
FIL=rep(FIL,"/^(video|audio)\\//.test(f.type)","(/^(video|audio)\\//.test(f.type)||/\\.(mp4|mov|m4v|webm|mkv|avi|3gp|mp3|wav|m4a|aac|ogg|opus|flac)$/i.test(f.name))")
FIL+=PREVJS
FIL+=P2W
FIL+="\nObject.assign(FT,window.VFT||{});\nfsetup(document.body.dataset.mode);\n"
# slug, mode, kind, h1, desc
P=[
('compress-images','compress','img','ضغط الصور','قلّل حجم صور JPG وPNG وWebP مع التحكم بالجودة، داخل جهازك.'),
('resize-images','resize','img','تغيير أبعاد الصور','غيّر عرض الصورة وارتفاعها بالبكسل مع حفظ النسبة.'),
('print-photos','print','img','تجهيز الصور للطباعة','جهّز صورك بمقاسات الطباعة الجاهزة أو مقاس مخصص بـ cm وin وpx.'),
('images-to-pdf','topdf','file','صور إلى PDF','اجمع صورك في ملف PDF واحد، صفحة لكل صورة.'),
('images-to-gif','togif','file','صور إلى GIF','حوّل صورة أو عدة صور إلى GIF متحرك.'),
('merge-pdf','pdfmerge','file','دمج ملفات PDF','اجمع عدة ملفات PDF في ملف واحد.'),
('split-pdf','pdfsplit','file','تقسيم PDF','استخرج صفحات محددة من PDF أو افصل كل صفحة في ملف.'),
('compress-files','zip','file','ضغط الملفات إلى ZIP','ضع أي ملفات داخل ملف ZIP واحد مضغوط.'),
('extract-audio','vextract','vid','استخراج الصوت من الفيديو','استخرج الصوت من أي فيديو بصيغة MP3 أو M4A أو OGG أو FLAC أو WAV.'),
('video-to-mp3','vmp3','vid','تحويل الفيديو إلى MP3','حوّل أي فيديو إلى ملف صوتي MP3 بجودة تختارها.'),
('compress-video','vcompress','vid','ضغط الفيديو','قلّل حجم الفيديو مع التحكم بمستوى الضغط والدقة.'),
('video-to-gif','vgif','vid','فيديو إلى GIF','حوّل مقطعاً من الفيديو إلى GIF متحرك.'),
('trim-video','vtrim','vid','قص الفيديو','اقتطع جزءاً من الفيديو بتحديد البداية والنهاية.'),
('mute-video','vmute','vid','إزالة الصوت من الفيديو','احذف الصوت من الفيديو بدون إعادة ترميز.'),
('convert-video','vconv','vid','تحويل صيغة الفيديو','حوّل الفيديو بين صيغتي MP4 وWebM.'),
('pdf-to-word','towrd','file','PDF إلى Word','حوّل نص ملف PDF إلى مستند Word قابل للتحرير.'),
('remove-watermark','wm','wm','إزالة العلامة المائية من الصور','امسح شعاراً أو علامة مائية من صورتك بتحديد المنطقة.'),
('remove-video-watermark', 'vwm', 'vid', 'إزالة العلامة المائية من الفيديو', 'طمس شعار أو علامة في ركن الفيديو بتحديد موضعها وحجمها.'),
('video-screenshot', 'vshot', 'vid', 'استخراج صورة من الفيديو', 'التقط صورة PNG من أي لحظة في الفيديو.'),
('video-speed', 'vspeed', 'vid', 'تسريع وإبطاء الفيديو', 'غيّر سرعة الفيديو من نصف السرعة إلى الضعف.'),
('rotate-video', 'vrot', 'vid', 'تدوير الفيديو', 'دوّر الفيديو 90 أو 180 درجة أو اقلبه.'),
('pdf-to-images', 'p2img', 'file', 'PDF إلى صور', 'حوّل صفحات PDF إلى صور JPG داخل ملف ZIP.'),
('compress-pdf', 'p2cmp', 'file', 'ضغط PDF', 'قلّل حجم PDF بتحويل صفحاته إلى صور مضغوطة.'),
('rotate-pdf', 'pdfrotate', 'file', 'تدوير صفحات PDF', 'دوّر كل صفحات PDF بزاوية 90 أو 180 أو 270 درجة.'),
('remove-tashkeel', 'tshk', 'txt', 'إزالة التشكيل من النص', 'احذف الحركات والتطويل من أي نص عربي بضغطة.'),
('convert-arabic-numbers', 'tdig', 'txt', 'تحويل الأرقام الهندية والإنجليزية', 'حوّل الأرقام بين ٠١٢ و012 داخل أي نص.'),
('number-to-arabic-words', 'tnum', 'txt', 'تفقيط الأرقام (رقم إلى كلمات)', 'اكتب المبلغ بالحروف العربية للشيكات والفواتير.'),
('arabic-text-decorator', 'tdec', 'txt', 'زخرفة الأسماء والنصوص العربية', 'زخرف اسمك بالتطويل والرموز وانسخه فوراً.'),
('word-counter', 'tcnt', 'txt', 'عدّاد الكلمات والحروف', 'احسب الكلمات والحروف والأسطر والجمل.'),
('clean-text', 'tcln', 'txt', 'تنظيف وتنسيق النص', 'احذف المسافات الزائدة والأسطر الفارغة المتكررة.')]
VH={'vextract':('فيديو أو ملف صوتي','استخراج الصوت'),'vmp3':('فيديو أو ملف صوتي','تحويل إلى MP3'),'vcompress':('فيديو واحد، يُفضّل أقل من 500 MB','ضغط الفيديو'),'vgif':('فيديو واحد، أول 10 ثوانٍ فقط','إنشاء GIF'),'vtrim':('فيديو واحد','قص الفيديو'),'vmute':('فيديو واحد','إزالة الصوت'),'vconv':('فيديو واحد','تحويل'),'vwm':('فيديو واحد','إزالة العلامة'),'vshot':('فيديو واحد','التقاط الصورة'),'vspeed':('فيديو واحد','تغيير السرعة'),'vrot':('فيديو واحد','تطبيق')}
VFT={m:{'t':h1,'d':d,'a':'video/*,audio/*','h':VH[m][0],'go':VH[m][1]} for s,m,k,h1,d in P if k=='vid'}
VIDJS="""window.VFT=__VFT__;
let ff;
async function ffl(){
  if(ff)return ff;
  if(!window.FFmpegWASM||!window.FFmpegUtil)throw new Error('lib');
  const{FFmpeg}=FFmpegWASM,{toBlobURL}=FFmpegUtil,C='https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/umd',W='https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.10/dist/umd',f=new FFmpeg();
  f.on('progress',({progress})=>{const m=document.querySelector('#fres .mt');if(m)m.textContent='جارٍ المعالجة '+Math.max(0,Math.min(100,Math.round(progress*100)))+'%'});
  await f.load({classWorkerURL:await toBlobURL(W+'/814.ffmpeg.js','text/javascript'),coreURL:await toBlobURL(C+'/ffmpeg-core.js','text/javascript'),wasmURL:await toBlobURL(C+'/ffmpeg-core.wasm','application/wasm')});
  return ff=f}
const ext=f=>(f.name.match(/\\.[^.]+$/)||['.mp4'])[0],nm=(f,s)=>f.name.replace(/\\.[^.]+$/,'')+s;
async function vrun(file,pre,args,out,mime){
  const f=await ffl(),inn='in'+ext(file);
  await f.writeFile(inn,new Uint8Array(await file.arrayBuffer()));
  const code=await f.exec(['-y',...pre,'-i',inn,...args,out]);
  let d;try{d=await f.readFile(out)}catch(e){}
  try{await f.deleteFile(inn);await f.deleteFile(out)}catch(e){}
  if(code!==0||!d||!d.length)throw new Error('ff');
  return new Blob([d],{type:mime})}
async function decodeAudio(f){const C=window.AudioContext||window.webkitAudioContext;if(!C)throw new Error('ctx');const c=new C();try{return await c.decodeAudioData(await f.arrayBuffer())}finally{c.close()}}
const tick=()=>new Promise(r=>setTimeout(r));
function pcmWav(ab){
  const ch=ab.numberOfChannels,sr=ab.sampleRate,n=ab.length,buf=new ArrayBuffer(44+n*ch*2),v=new DataView(buf),w=(o,s)=>{for(let i=0;i<s.length;i++)v.setUint8(o+i,s.charCodeAt(i))};
  w(0,'RIFF');v.setUint32(4,36+n*ch*2,true);w(8,'WAVEfmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,ch,true);v.setUint32(24,sr,true);v.setUint32(28,sr*ch*2,true);v.setUint16(32,ch*2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*ch*2,true);
  const d=[];for(let c=0;c<ch;c++)d.push(ab.getChannelData(c));let o=44;
  for(let i=0;i<n;i++)for(let c=0;c<ch;c++){const s=Math.max(-1,Math.min(1,d[c][i]));v.setInt16(o,s<0?s*32768:s*32767,true);o+=2}
  return new Blob([buf],{type:'audio/wav'})}
async function loadLame(){
  const ok=()=>{try{new lamejs.Mp3Encoder(1,44100,128);return true}catch(e){return false}};
  if(window.lamejs&&ok())return;
  for(const u of ['https://cdn.jsdelivr.net/npm/lamejs@1.2.1/lame.all.js','https://cdnjs.cloudflare.com/ajax/libs/lamejs/1.2.1/lame.min.js']){
    try{delete window.lamejs}catch(e){}
    await new Promise(r=>{const s=document.createElement('script');s.src=u;s.onload=s.onerror=r;document.head.appendChild(s)});
    if(window.lamejs&&ok())return}
  throw new Error('lame')}
async function pcmMp3(ab,kbps){
  await loadLame();
  const ch=Math.min(2,ab.numberOfChannels),enc=new lamejs.Mp3Encoder(ch,ab.sampleRate,kbps),out=[],B=1152*10;
  const f2i=a=>{const o=new Int16Array(a.length);for(let i=0;i<a.length;i++){const v=Math.max(-1,Math.min(1,a[i]));o[i]=v<0?v*32768:v*32767}return o};
  const L=f2i(ab.getChannelData(0)),R=ch>1?f2i(ab.getChannelData(1)):null,box=document.querySelector('#fres .mt');
  for(let i=0,k=0;i<L.length;i+=B,k++){
    const b=ch>1?enc.encodeBuffer(L.subarray(i,i+B),R.subarray(i,i+B)):enc.encodeBuffer(L.subarray(i,i+B));
    if(b.length)out.push(new Uint8Array(b));
    if(k%40===0){if(box)box.textContent='جارٍ المعالجة '+Math.round(i/L.length*100)+'%';await tick()}}
  const e=enc.flush();if(e.length)out.push(new Uint8Array(e));
  return new Blob(out,{type:'audio/mpeg'})}
const dim=f=>new Promise((ok,no)=>{const v=document.createElement('video'),u=URL.createObjectURL(f);v.preload='metadata';v.onloadedmetadata=()=>{ok([v.videoWidth,v.videoHeight]);URL.revokeObjectURL(u)};v.onerror=()=>no(new Error('dim'));v.src=u});
window.VID={
 async vwm(f){const d=await dim(f),p=$('#vwp').value,W=Math.max(8,Math.round(d[0]*(+$('#vww').value||20)/100)),H=Math.max(8,Math.round(d[1]*(+$('#vwh').value||10)/100)),x=p[1]==='l'?2:d[0]-W-2,y=p[0]==='t'?2:d[1]-H-2;
  return[await vrun(f,[],['-vf','delogo=x='+x+':y='+y+':w='+W+':h='+H,'-c:v','libx264','-preset','veryfast','-crf','23','-c:a','copy'],'out.mp4','video/mp4'),nm(f,'-clean.mp4')]},
 async vshot(f){return[await vrun(f,['-ss',''+(+$('#vts').value||0)],['-frames:v','1'],'out.png','image/png'),nm(f,'-frame.png')]},
 async vspeed(f){const s=$('#vsp').value;return[await vrun(f,[],['-vf','setpts=PTS/'+s,'-af','atempo='+s,'-c:v','libx264','-preset','veryfast','-c:a','aac'],'out.mp4','video/mp4'),nm(f,'-speed'+s+'.mp4')]},
 async vrot(f){return[await vrun(f,[],['-vf',$('#vro').value,'-c:v','libx264','-preset','veryfast','-c:a','aac'],'out.mp4','video/mp4'),nm(f,'-rotated.mp4')]},
 async vextract(f){const x=$('#vf').value,k=+$('#vb').value;if(x==='mp3'||x==='wav'){let a=null;try{a=await decodeAudio(f)}catch(e){}if(a){if(x==='wav')return[pcmWav(a),nm(f,'.wav')];try{return[await pcmMp3(a,k),nm(f,'.mp3')]}catch(e){note('تعذّر ترميز MP3 فتم إنشاء ملف WAV بدلاً منه.');return[pcmWav(a),nm(f,'.wav')]}}}const b=k+'k',A={mp3:['-c:a','libmp3lame','-b:a',b],m4a:['-c:a','aac','-b:a',b],ogg:['-c:a','libvorbis','-b:a',b],opus:['-c:a','libopus','-b:a',b],flac:['-c:a','flac'],wav:[]},M={mp3:'audio/mpeg',m4a:'audio/mp4',ogg:'audio/ogg',opus:'audio/ogg',flac:'audio/flac',wav:'audio/wav'};return[await vrun(f,[],['-vn',...A[x]],'out.'+x,M[x]),nm(f,'.'+x)]},
 async vcompress(f){return[await vrun(f,[],['-vf',"scale=-2:'min(ih,"+$('#vh').value+")'",'-c:v','libx264','-crf',$('#vc').value,'-preset','veryfast','-c:a','aac','-b:a','128k'],'out.mp4','video/mp4'),nm(f,'-compressed.mp4')]},
 async vgif(f){return[await vrun(f,[],['-t','10','-vf','fps='+$('#vr').value+',scale='+$('#vw').value+':-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse'],'out.gif','image/gif'),nm(f,'.gif')]},
 async vtrim(f){const s=+$('#vs').value||0,e=+$('#ve').value||0;if(e<=s)throw Object.assign(new Error('u'),{u:'يجب أن تكون النهاية بعد البداية.'});
  return[await vrun(f,['-ss',''+s],['-t',''+(e-s),'-c','copy'],'out'+ext(f),f.type||'video/mp4'),nm(f,'-trimmed'+ext(f))]},
 async vmute(f){return[await vrun(f,[],['-an','-c:v','copy'],'out'+ext(f),f.type||'video/mp4'),nm(f,'-muted'+ext(f))]},
 async vconv(f){const x=$('#vt').value;return[await vrun(f,[],x==='mp4'?['-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac']:['-c:v','libvpx','-b:v','1M','-c:a','libopus'],'out.'+x,'video/'+x),nm(f,'.'+x)]}};
""".replace("__VFT__",json.dumps(VFT,ensure_ascii=False))
VIDJS+="\nVID.vmp3=VID.vextract;\n"
VOPT='''
  <div class="row" data-fm="vextract vmp3"><div class="f"><label for="vf">صيغة الصوت</label><select id="vf"><option value="mp3">MP3</option><option value="m4a">M4A (AAC)</option><option value="ogg">OGG</option><option value="opus">Opus</option><option value="flac">FLAC</option><option value="wav">WAV</option></select></div><div class="f"><label for="vb">الجودة (kbps)</label><select id="vb"><option value="128">128</option><option value="192" selected>192</option><option value="320">320</option></select></div></div>
  <div class="row" data-fm="vcompress"><div class="f"><label for="vc">مستوى الضغط</label><select id="vc"><option value="26">خفيف (جودة أعلى)</option><option value="30" selected>متوسط</option><option value="35">قوي (حجم أصغر)</option></select></div><div class="f"><label for="vh">أقصى ارتفاع</label><select id="vh"><option value="1080">1080p</option><option value="720" selected>720p</option><option value="480">480p</option><option value="360">360p</option></select></div></div>
  <div class="row" data-fm="vgif"><div class="f"><label for="vr">إطارات في الثانية</label><select id="vr"><option value="8">8</option><option value="12" selected>12</option><option value="15">15</option></select></div><div class="f"><label for="vw">العرض</label><select id="vw"><option value="320">320 px</option><option value="480" selected>480 px</option><option value="640">640 px</option></select></div></div>
  <div class="row" data-fm="vtrim"><div class="f"><label for="vs">البداية (ثانية)</label><input type="number" id="vs" dir="ltr" min="0" step="any" value="0"></div><div class="f"><label for="ve">النهاية (ثانية)</label><input type="number" id="ve" dir="ltr" min="0" step="any" value="10"></div></div>
  <div class="f" data-fm="vconv"><label for="vt">التحويل إلى</label><select id="vt"><option value="mp4">MP4</option><option value="webm">WebM</option></select></div>

  <div class="row3" data-fm="vwm"><div class="f"><label for="vwp">موضع العلامة</label><select id="vwp"><option value="tr">أعلى يمين</option><option value="tl">أعلى يسار</option><option value="br" selected>أسفل يمين</option><option value="bl">أسفل يسار</option></select></div><div class="f"><label for="vww">العرض %</label><input type="number" id="vww" dir="ltr" min="1" max="80" value="20"></div><div class="f"><label for="vwh">الارتفاع %</label><input type="number" id="vwh" dir="ltr" min="1" max="80" value="10"></div></div>
  <div class="f" data-fm="vshot"><label for="vts">اللحظة (ثانية)</label><input type="number" id="vts" dir="ltr" min="0" step="any" value="1"></div>
  <div class="f" data-fm="vspeed"><label for="vsp">السرعة</label><select id="vsp"><option value="0.5">0.5x أبطأ</option><option value="0.75">0.75x</option><option value="1.25">1.25x</option><option value="1.5" selected>1.5x</option><option value="2">2x أسرع</option></select></div>
  <div class="f" data-fm="vrot"><label for="vro">العملية</label><select id="vro"><option value="transpose=1">تدوير 90° مع عقارب الساعة</option><option value="transpose=2">تدوير 90° عكس عقارب الساعة</option><option value="transpose=1,transpose=1">تدوير 180°</option><option value="hflip">قلب أفقي</option><option value="vflip">قلب رأسي</option></select></div>
'''
MORE=""".more{display:flex;flex-wrap:wrap;gap:8px;margin-top:36px;padding-top:20px;border-top:1px solid var(--line)}
.more b{width:100%;font-weight:600}
#wcv{display:block;width:100%;height:auto;margin:12px 0;border:1px solid var(--line);touch-action:none;cursor:crosshair}
#wtool .btn{width:100%}#wtool .row{margin-bottom:10px}
.legal h2{font-size:1.15rem;margin:28px 0 4px}.legal p{margin:0;color:var(--mut)}
.legal-nav a{margin-inline-end:14px;color:inherit}
textarea{width:100%;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--surf);color:var(--ink);font:inherit;resize:vertical}
#tbox .btn{margin-top:8px;width:100%}
.it{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 14px;background:var(--surf);border:1px solid var(--line);border-radius:12px;font-size:1.15rem}
.panel+.f{margin-top:16px}#tin{margin-bottom:12px}
.lang{display:flex;gap:14px;justify-content:flex-end;padding:2px 0 6px;font-size:.85rem}
.lang a{color:var(--mut);text-decoration:none}.lang a[aria-current]{color:var(--ink);font-weight:600}
.faq{margin-top:8px}\n.logo{width:36px;height:36px;border-radius:50%;object-fit:contain;flex:none}\n.cover{display:block;width:100%;height:auto;margin:22px 0 0;border-radius:16px}\n#fl{display:grid;gap:10px;margin:0 0 14px}\n.card{grid-template-columns:88px 1fr auto}\n.th{width:88px;height:88px}\n.card .ic{width:56px;height:56px}\n.pm{grid-column:1/-1;display:block;width:100%;max-height:260px;border-radius:10px;background:var(--line)}\naudio.pm{background:none;height:44px}
.more a{padding:6px 12px;border:1px solid var(--line);border-radius:99px;background:var(--surf);color:inherit;text-decoration:none;font-size:.85rem}
"""
ICON={'vid':'<rect x="2" y="5" width="14" height="14" rx="2"/><path d="M22 8l-6 4 6 4z"/>'}
cards=[];cols='cmy'
for n,(s,m,k,h1,d) in enumerate([p for p in P if p[2]=='vid']):
    cards.append('<a class="tl" href="/%s"><span class="ic %s"><svg viewBox="0 0 24 24">%s</svg></span><b>%s</b><p>%s</p></a>'%(s,cols[n%3],ICON['vid'],h1,d))
for s,m,k,h1,d in P: home=home.replace('href="#%s"'%m,'href="/%s"'%s)
home,c=re.subn(r'<div class="tl off"><span class="ic g">MP4</span>.*?</div>','\n    '.join(cards),home,count=1,flags=re.S);assert c==1
home,c=re.subn(r'<div class="tl off"><span class="ic g">DOCX</span>.*?</div>',NEWC,home,count=1,flags=re.S);assert c==1
ICN={'vid':ICON['vid'],'file':'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>','txt':'<path d="M4 7V5h16v2M9 19h6M12 5v14"/>'}
NS=[p for p in P if p[1] in ['vwm', 'vshot', 'vspeed', 'vrot', 'p2img', 'p2cmp', 'pdfrotate', 'tshk', 'tdig', 'tnum', 'tdec', 'tcnt', 'tcln']]
cards2=['<a class="tl" href="/%s"><span class="ic %s"><svg viewBox="0 0 24 24">%s</svg></span><b>%s</b><p>%s</p></a>'%(x[0],cols[n%3],ICN[x[2]],x[3],x[4]) for n,x in enumerate(NS)]
home,c=re.subn(r'<div class="tl off"><span class="ic g">ع</span>.*?</div>','\n    '.join(cards2),home,count=1,flags=re.S);assert c==1
FONT='<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Readex+Pro:wght@300;400;500;600;700&display=swap" rel="stylesheet">'
ICO='<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Ctext y=\'.9em\' font-size=\'90\'%3E🖼️%3C/text%3E%3C/svg%3E">'
ICO='<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">\n<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">'
def page(slug,mode,title,desc,body,libs,scripts):
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/{slug}">
{ICO}
{FONT}
<link rel="stylesheet" href="/assets/style.css">
{libs}
</head>
<body data-mode="{mode}">
<div class="wrap">
<!--LANG-->
{body}
<nav class="fn legal-nav"><a href="/about">من نحن</a> <a href="/privacy">الخصوصية</a> <a href="/contact">اتصل بنا</a></nav>
</div>
{scripts}
</body>
</html>
'''
os.makedirs(OUT+'/assets',exist_ok=True)
W=lambda p,t:open(OUT+'/'+p,'w',encoding='utf-8').write(t)

import sys,html as HT
EMAIL='nukhbaarabtheme@gmail.com'
LANGS=['ar','en','fr'];LNAME={'ar':'العربية','en':'English','fr':'Français'}
SEGP=BASE+'/segments.json';TRP=BASE+'/tr.json'
SEGS=json.load(open(SEGP,encoding='utf-8')) if os.path.exists(SEGP) else []
TR=json.load(open(TRP,encoding='utf-8')) if os.path.exists(TRP) else {}
IDX={c:i for i,c in enumerate(SEGS)}
SEGRE=re.compile(r'[^<>"\'`\n\x00{}\[\];=\\]*[\u0600-\u06FF][^<>"\'`\n\x00{}\[\];=\\]*')
JSSRC={};LEFT=set()
STRIP='<span class="strip" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'
LOGO='<img class="logo" src="/assets/logo-96.png" alt="" width="36" height="36">'
COVER='<img class="cover" src="/assets/cover-1600.webp" srcset="/assets/cover-800.webp 800w, /assets/cover-1600.webp 1600w" sizes="(max-width:720px) 100vw, 720px" width="1600" height="600" alt="BePro: All Your Tools in One Place" fetchpriority="high">'
FAQ=('<section class="sec faq"><h2>أسئلة شائعة</h2>'
'<details><summary>هل أداة @@T@@ مجانية؟</summary><p>نعم، الأداة مجانية بالكامل وبلا تسجيل ولا علامة مائية على ملفاتك.</p></details>'
'<details><summary>هل تُرفع ملفاتي إلى خادم؟</summary><p>لا. تُعالَج الملفات داخل متصفحك على جهازك ولا تغادره.</p></details>'
'<details><summary>كيف أستخدم أداة @@T@@؟</summary><p>اختر ملفك، واضبط الخيارات إن وجدت، ثم اضغط زر المعالجة ونزّل النتيجة.</p></details></section>')
def segs(t):return [m.group().strip() for m in SEGRE.finditer(t) if m.group().strip()]
def add(c):
    if c not in IDX:IDX[c]=len(SEGS);SEGS.append(c)
def trs(c,l):
    if l=='ar':return c
    r=TR.get(str(IDX.get(c,-1)))
    return r[0 if l=='en' else 1] if r else c
def tr(t,l,wl=None):
    t=t.replace('\\n','\x00')
    for c in sorted(set(segs(t)),key=len,reverse=True):
        if wl is not None and c not in wl:continue
        add(c)
        if l!='ar':
            r=TR.get(str(IDX[c]))
            if r:t=t.replace(c,r[0 if l=='en' else 1])
    return t.replace('\x00','\\n')
def Wraw(p,t):
    f=OUT+'/'+p;os.makedirs(os.path.dirname(f),exist_ok=True);open(f,'w',encoding='utf-8').write(t)
def sw(slug,l):
    us='' if slug=='index' else slug
    return '<nav class="lang" aria-label="Language">'+' '.join('<a href="%s" hreflang="%s"%s>%s</a>'%(('/' if m=='ar' else '/'+m+'/')+us,m,' aria-current="page"' if m==l else '',LNAME[m]) for m in LANGS)+'</nav>'
def seo(l,slug,kind,title,desc,faq,BRN):
    us='' if slug=='index' else slug
    u=lambda m:SITE+('/' if m=='ar' else '/'+m+'/')+us
    q=lambda x:HT.escape(x,quote=True)
    loc={'ar':'ar_AR','en':'en_US','fr':'fr_FR'}[l]
    t=['<title>%s</title>'%HT.escape(title,quote=False),'<meta name="description" content="%s">'%q(desc),'<meta name="robots" content="index,follow,max-image-preview:large">','<meta name="theme-color" content="#1556E0">','<link rel="canonical" href="%s">'%u(l)]
    t+=['<link rel="alternate" hreflang="%s" href="%s">'%(m,u(m)) for m in LANGS]+['<link rel="alternate" hreflang="x-default" href="%s">'%u('ar')]
    t+=['<meta property="og:type" content="website">','<meta property="og:site_name" content="%s">'%q(BRN[l]),'<meta property="og:title" content="%s">'%q(title),'<meta property="og:description" content="%s">'%q(desc),'<meta property="og:url" content="%s">'%u(l),'<meta property="og:locale" content="%s">'%loc,'<meta property="og:image" content="%s/assets/og.jpg">'%SITE,'<meta name="twitter:card" content="summary_large_image">']
    if slug=='index':t.append('<meta name="msvalidate.01" content="4FF956B9E92FEBE2B4BFAFA05F206983">')
    C='https://schema.org';ld=[];home=SITE+('/' if l=='ar' else '/'+l+'/')
    if kind=='home':ld+=[{'@context':C,'@type':'WebSite','name':BRN[l],'url':u(l),'inLanguage':l,'description':desc},{'@context':C,'@type':'Organization','name':BRN[l],'url':SITE+'/','email':EMAIL,'logo':SITE+'/assets/logo-512.png'}]
    if kind=='tool':ld+=[{'@context':C,'@type':'WebApplication','name':title,'url':u(l),'description':desc,'applicationCategory':'UtilitiesApplication','operatingSystem':'Any','inLanguage':l,'isAccessibleForFree':True,'offers':{'@type':'Offer','price':'0','priceCurrency':'USD'}},{'@context':C,'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':BRN[l],'item':home},{'@type':'ListItem','position':2,'name':title,'item':u(l)}]}]
    if faq:
        pl=lambda z:HT.unescape(re.sub('<[^>]+>','',z))
        ld.append({'@context':C,'@type':'FAQPage','mainEntity':[{'@type':'Question','name':pl(a),'acceptedAnswer':{'@type':'Answer','text':pl(b)}} for a,b in faq]})
    return '\n'.join(t+['<script type="application/ld+json">%s</script>'%json.dumps(x,ensure_ascii=False) for x in ld])
SUF_AR=' أونلاين مجاناً | BePro';LEG_AR=' | BePro'
SUFF={'en':' Online, Free | %s','fr':' en ligne, gratuit | %s'}
def emit(slug,t):
    ti=re.search(r'<title>(.*?)</title>',t).group(1);de=re.search(r'<meta name="description" content="(.*?)">',t).group(1)
    if ti.endswith(SUF_AR):kind,h1='tool',ti[:-len(SUF_AR)]
    elif ti.endswith(LEG_AR):kind,h1='legal',ti[:-len(LEG_AR)]
    else:kind,h1='home',ti
    body=re.sub(r'<title>.*?</title>\n?|<meta name="description"[^>]*>\n?|<link rel="canonical"[^>]*>\n?','',t)
    body=body.replace('كل أدوات الصور التي تحتاجها في مكان واحد','كل أدواتك في مكان واحد').replace(STRIP,LOGO)
    if kind=='home':body=body.replace('</header>',COVER+'</header>',1)
    add('BePro');add(h1 if kind!='home' else ti)
    if kind=='home':add(de)
    if kind=='tool':add(de)
    for l in LANGS:
        BRN={m:trs('BePro',m) for m in LANGS}
        x=tr(body,l) if l!='ar' else body
        if l!='ar':
            for c in segs(x):LEFT.add(c)
        T=trs(h1,l) if kind=='tool' else ''
        x=x.replace('@@T@@',T)
        if kind=='home':title,desc=trs(ti,l),trs(de,l)
        elif kind=='tool':title,desc=(ti if l=='ar' else trs(h1,l)+SUFF[l]%BRN[l]),trs(de,l)
        else:title=trs(h1,l)+' | '+BRN[l];desc=title
        if l!='ar':
            x=re.sub(r'href="/(?!assets/)([^"]*)"',lambda m:'href="/%s/%s"'%(l,m.group(1)),x);x=re.sub(r'src="/assets/([\w-]+\.js)"',lambda m:'src="/assets/%s/%s"'%(l,m.group(1)),x)
        x=x.replace('<html lang="ar" dir="rtl">','<html lang="%s" dir="%s">'%(l,'rtl' if l=='ar' else 'ltr')).replace('<!--LANG-->',sw(slug,l))
        faq=re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>',x)
        x=x.replace('</head>',seo(l,slug,kind,title,desc,faq,BRN)+'\n</head>',1)
        Wraw(('' if l=='ar' else l+'/')+slug+'.html',x)
Wraw0=None
def W(p,t):
    if p.endswith('.html'):emit(p[:-5],t)
    else:
        if p.endswith('.js'):JSSRC[p]=t
        Wraw(p,t)
W('assets/style.css',css.replace('--c:#00A3D9','--c:#1F6FF2').replace('--y:#FFC72C','--y:#FFC21A').strip()+'\n'+MORE)
W('assets/common.js',A+PUT)
W('assets/image.js',IMG+DALL)
W('assets/files.js',FIL)
W('assets/video.js',VIDJS)
W('assets/watermark.js',WMJS)
W('assets/text.js',TXTJS)
SJ='<script defer src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>'
SP='<script defer src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>'
SPJ='<script defer src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>'
SL='<script defer src="https://cdnjs.cloudflare.com/ajax/libs/lamejs/1.2.1/lame.min.js"></script>'
SF='<script defer src="https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.10/dist/umd/ffmpeg.js"></script>\n<script defer src="https://cdn.jsdelivr.net/npm/@ffmpeg/util@0.12.1/dist/umd/index.js"></script>'
tag=lambda *n:'\n'.join('<script src="/assets/%s.js"></script>'%x for x in n)
W('index.html',page('','home','BePro: أدوات الصور والملفات والفيديو أونلاين مجاناً','أدوات مجانية بلا تسجيل: ضغط الصور، تغيير الأبعاد، تجهيز الطباعة، PDF، GIF، وأدوات الفيديو. تعمل داخل جهازك.',home.replace('href="/"','href="/"'),'',''))
for s,m,k,h1,d in P:
    others='<nav class="more"><b>أدوات أخرى</b>'+''.join('<a href="/%s">%s</a>'%(x[0],x[3]) for x in P if x[0]!=s)+'</nav>'
    if k=='img':
        b=re.sub(r'<h1>.*?</h1>','<h1>%s</h1>'%h1,tool,count=1,flags=re.S)
        b=re.sub(r'<p class="sub">.*?</p>','<p class="sub">%s</p>'%d,b,count=1,flags=re.S)
        b=re.sub(r'<div class="tabs".*?</div>','',b,count=1,flags=re.S)
        libs,sc=SJ,tag('common','image')
    elif k=='txt':
        b=TXTBODY.replace('{H1}',h1).replace('{D}',d).replace('{OPT}',TO.get(m,''));libs,sc='',tag('common','text')
    elif k=='wm':
        b=WMBODY.replace('{H1}',h1).replace('{D}',d);libs,sc='',tag('common','watermark')
    else:
        b=rep(fil,'<h1 id="ft"></h1>','<h1 id="ft">%s</h1>'%h1);b=rep(b,'<p class="sub" id="fd"></p>','<p class="sub" id="fd">%s</p>'%d)
        if k=='vid':
            b=re.sub(r'(<section class="panel" id="fopt" hidden>.*?)(</section>)',lambda x:x.group(1)+VOPT+x.group(2),b,count=1,flags=re.S)
            libs,sc=SF,tag('common','video','files')
        else:
            libs,sc=SJ+('\n'+SP if m.startswith('pdf') else '')+('\n'+SPJ if (m in('towrd','p2img','p2cmp','topdf') or m.startswith('pdf')) else ''),tag('common','files')
    b=b.replace('href="#home"','href="/"')+'\n'+FAQ+'\n'+others
    W(s+'.html',page(s,m,h1+' أونلاين مجاناً | BePro',d,b,libs,sc))
exec(LEG)
W('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>%s/%s</loc></url>\n'%(SITE,x) for x in ['']+[p[0] for p in P]+['about','privacy','contact'])+'</urlset>\n')
W('robots.txt','User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n'%SITE)
SL_=[p[0] for p in P]+['about','privacy','contact']
RW=[{'source':pre+'/'+x,'destination':pre+'/'+x+'.html'} for pre in ['','/en','/fr'] for x in SL_]+[{'source':'/en','destination':'/en/index.html'},{'source':'/fr','destination':'/fr/index.html'}]
Wraw('vercel.json',json.dumps({'cleanUrls':False,'rewrites':RW},indent=1)+'\n')
W('README.md','''# BePro

موقع ثابت (HTML/CSS/JS) بلا خطوة بناء. كل أداة صفحة مستقلة، والمنطق في assets.

## النشر
- Vercel: ارفع المجلد إلى GitHub ثم Import Project (Framework: Other). أو من الطرفية: npx vercel
- Cloudflare Pages: اربط المستودع، ولا حاجة لأمر بناء، ومجلد الإخراج هو الجذر.
- بعد شراء الدومين: استبدل https://example.com بدومينك في كل الملفات (الأمر: grep -rl example.com . | xargs sed -i 's#https://example.com#https://YOUR-DOMAIN#g').

## التجربة المحلية
npx serve .   (الروابط تبدأ بـ / فتحتاج خادماً محلياً)

## ملاحظات
- أدوات الفيديو تحمّل ffmpeg.wasm من jsDelivr وقت الاستخدام (تجريبية).
- صفحات الخصوصية و«من نحن» و«اتصل بنا» جاهزة (البريد مضبوط في contact.html).
- لإضافة أداة: أضف صفحتها، وسجّلها في الرئيسية وsitemap.xml.
''')

WL={'الكلمات:','الحروف (بالمسافات):','الحروف (بدون مسافات):','الأسطر:','الجمل:','نسخ','تم النسخ.','تعذّر النسخ، انسخ النص يدوياً.','الرقم كبير جداً'}
for n,t in JSSRC.items():
    for l in LANGS[1:]:Wraw('assets/%s/%s'%(l,n[7:]),tr(t,l,WL if n.endswith('text.js') else None))
urls=['']+[p[0] for p in P]+['about','privacy','contact']
lc=lambda m,x:SITE+('/' if m=='ar' else '/'+m+'/')+x
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
for x in urls:
    for m in LANGS:sm+='<url><loc>%s</loc><lastmod>2026-11-22</lastmod>'%lc(m,x)+''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>'%(y,lc(y,x)) for y in LANGS)+'<xhtml:link rel="alternate" hreflang="x-default" href="%s"/></url>\n'%lc('ar',x)
Wraw('sitemap.xml',sm+'</urlset>\n')
Wraw('robots.txt','User-agent: *\nAllow: /\n\n'+''.join('User-agent: %s\nAllow: /\n\n'%b for b in ['GPTBot','ChatGPT-User','OAI-SearchBot','ClaudeBot','Claude-User','PerplexityBot','Google-Extended','Applebot-Extended'])+'Sitemap: %s/sitemap.xml\n'%SITE)
Wraw('google60ca13bcba362b2f.html','google-site-verification: google60ca13bcba362b2f.html')
Wraw('yandex_9bdfb6ab04a3b424.html','<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n    </head>\n    <body>Verification: 9bdfb6ab04a3b424</body>\n</html>')
Wraw('ads.txt','# Replace the line below with the one shown in your Google AdSense account (Sites > ads.txt):\n# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n')
ll='# %s\n\n> Free online tools for images, PDF, video and Arabic text. Files are processed inside the visitor\'s browser and never uploaded. No sign-up, no watermark.\n\nSite languages: Arabic (%s/), English (%s/en/), French (%s/fr/).\n\n## Tools\n'%(trs('BePro','en'),SITE,SITE,SITE)
for p in P:ll+='- [%s](%s): %s\n'%(trs(p[3],'en'),lc('en',p[0]),trs(p[4],'en'))
Wraw('llms.txt',ll)
try:
    from PIL import Image,ImageDraw
    im=Image.new('RGB',(1200,630),'#F4F6FB');d=ImageDraw.Draw(im)
    for i,c in enumerate(['#00A3D9','#E5007D','#FFC72C','#12162B']):d.rectangle([i*300,0,i*300+299,28],fill=c)
    cx,cy=600,330
    d.ellipse([cx-170,cy-170,cx+170,cy+170],outline='#12162B',width=10);d.ellipse([cx-85,cy-85,cx+85,cy+85],outline='#00A3D9',width=10)
    d.line([cx,cy-240,cx,cy+240],fill='#12162B',width=10);d.line([cx-240,cy,cx+240,cy],fill='#12162B',width=10);d.ellipse([cx-24,cy-24,cx+24,cy+24],fill='#E5007D')
    os.makedirs(OUT+'/assets',exist_ok=True);im.save(OUT+'/assets/og.png')
except Exception as e:print('og image skipped',e)
json.dump(SEGS,open(SEGP,'w',encoding='utf-8'),ensure_ascii=False)
miss=[i for i in range(len(SEGS)) if str(i) not in TR]
if miss:
    print('MISSING',len(miss),'of',len(SEGS))
    for i in miss:print(i,'|',SEGS[i])
    sys.exit(2)
print('LEFTOVER',sorted(LEFT)[:30])
import shutil
for f in os.listdir(BASE):
    if f.startswith('brand-'):shutil.copy(BASE+'/'+f,OUT+('/' if f[6:] in('favicon.ico','site.webmanifest') else '/assets/')+f[6:])
if os.path.exists(OUT+'/assets/og.png'):os.remove(OUT+'/assets/og.png')
# checks
bad=0
for f in ['common','image','files','video','watermark','text']:
    try:
        r=subprocess.run(['node','--check',OUT+'/assets/%s.js'%f],capture_output=True,text=True)
        if r.returncode:bad+=1;print('SYNTAX',f,r.stderr[:300])
    except OSError:pass
for s,m,k,h1,d in P:
    t=open(OUT+'/%s.html'%s,encoding='utf-8').read()
    use=['common']+(['image'] if k=='img' else ['video','files'] if k=='vid' else ['watermark'] if k=='wm' else ['text'] if k=='txt' else ['files'])
    ids=set()
    for u in use:ids|=set(re.findall(r"\$\('#([\w-]+)'\)",open(OUT+'/assets/%s.js'%u,encoding='utf-8').read()))
    miss=[i for i in ids if 'id="%s"'%i not in t and i not in('msg','fmsg')]
    if miss:bad+=1;print('MISSING',s,miss)
if os.path.isdir('/mnt/user-data/outputs'):
    z=zipfile.ZipFile('/mnt/user-data/outputs/image-workshop-site.zip','w',zipfile.ZIP_DEFLATED)
    for r,_,fs in os.walk(OUT):
        for f in fs:z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),OUT))
    z.close()
print('pages',len(P)+1,'problems',bad)
