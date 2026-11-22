const M=document.body.dataset.mode,tin=$('#tin'),tout=$('#tout'),tl=$('#tlist'),D1='٠١٢٣٤٥٦٧٨٩',D2='۰۱۲۳۴۵۶۷۸۹',opt=i=>{const e=document.getElementById(i);return e?e.value:''};
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
