
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const PRESETS=[['جواز وهوية',3.5,4.5],['صورة شخصية',4,6],['صورة قياسية',10,15],['صورة كبيرة',13,18],['A5',14.8,21],['A4',21,29.7]];
const FM={jpeg:['image/jpeg','jpg'],webp:['image/webp','webp'],png:['image/png','png']};
const S={mode:document.body.dataset.mode||'compress',q:75,fmt:'jpeg',max:0,w:'',h:'',lock:true,preset:1,land:false,dpi:300,cover:true,cu:{w:'',h:'',u:'cm'},items:[],gen:0};
let uid=0,DL=null,tm;

function el(t,c,x){const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function nn(x,c){const s=el('span','n'+(c?' '+c:''),x);return s}
function fmt(b){return b<1048576?Math.round(b/1024)+' KB':(b/1048576).toFixed(1)+' MB'}
function note(t){const m=$('#fmsg')||$('#msg');m.textContent=t;if(t)setTimeout(()=>{if(m.textContent===t)m.textContent=''},5000)}

try{if(window.claude&&claude.use)claude.use('downloads').then(d=>{DL=d}).catch(()=>{})}catch(e){}

async function put(name,blob){
  if(DL){try{await DL.save({filename:name,data:blob})}catch(e){if(!e||e.code!=='declined')note('تعذّر حفظ الملف.')}}
  else{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove()}}
