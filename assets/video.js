window.VFT={"vextract": {"t": "استخراج الصوت من الفيديو", "d": "استخرج الصوت من أي فيديو بصيغة MP3 أو WAV.", "a": "video/*,audio/*", "h": "فيديو أو ملف صوتي", "go": "استخراج الصوت"}, "vcompress": {"t": "ضغط الفيديو", "d": "قلّل حجم الفيديو مع التحكم بمستوى الضغط والدقة.", "a": "video/*,audio/*", "h": "فيديو واحد، يُفضّل أقل من 500 MB", "go": "ضغط الفيديو"}, "vgif": {"t": "فيديو إلى GIF", "d": "حوّل مقطعاً من الفيديو إلى GIF متحرك.", "a": "video/*,audio/*", "h": "فيديو واحد، أول 10 ثوانٍ فقط", "go": "إنشاء GIF"}, "vtrim": {"t": "قص الفيديو", "d": "اقتطع جزءاً من الفيديو بتحديد البداية والنهاية.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "قص الفيديو"}, "vmute": {"t": "إزالة الصوت من الفيديو", "d": "احذف الصوت من الفيديو بدون إعادة ترميز.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "إزالة الصوت"}, "vconv": {"t": "تحويل صيغة الفيديو", "d": "حوّل الفيديو بين صيغتي MP4 وWebM.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "تحويل"}, "vwm": {"t": "إزالة العلامة المائية من الفيديو", "d": "طمس شعار أو علامة في ركن الفيديو بتحديد موضعها وحجمها.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "إزالة العلامة"}, "vshot": {"t": "استخراج صورة من الفيديو", "d": "التقط صورة PNG من أي لحظة في الفيديو.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "التقاط الصورة"}, "vspeed": {"t": "تسريع وإبطاء الفيديو", "d": "غيّر سرعة الفيديو من نصف السرعة إلى الضعف.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "تغيير السرعة"}, "vrot": {"t": "تدوير الفيديو", "d": "دوّر الفيديو 90 أو 180 درجة أو اقلبه.", "a": "video/*,audio/*", "h": "فيديو واحد", "go": "تطبيق"}};
let ff;
async function ffl(){
  if(ff)return ff;
  if(!window.FFmpegWASM||!window.FFmpegUtil)throw new Error('lib');
  const{FFmpeg}=FFmpegWASM,{toBlobURL}=FFmpegUtil,C='https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.6/dist/umd',W='https://cdn.jsdelivr.net/npm/@ffmpeg/ffmpeg@0.12.10/dist/umd',f=new FFmpeg();
  f.on('progress',({progress})=>{const m=document.querySelector('#fres .mt');if(m)m.textContent='جارٍ المعالجة '+Math.max(0,Math.min(100,Math.round(progress*100)))+'%'});
  await f.load({classWorkerURL:await toBlobURL(W+'/814.ffmpeg.js','text/javascript'),coreURL:await toBlobURL(C+'/ffmpeg-core.js','text/javascript'),wasmURL:await toBlobURL(C+'/ffmpeg-core.wasm','application/wasm')});
  return ff=f}
const ext=f=>(f.name.match(/\.[^.]+$/)||['.mp4'])[0],nm=(f,s)=>f.name.replace(/\.[^.]+$/,'')+s;
async function vrun(file,pre,args,out,mime){
  const f=await ffl(),inn='in'+ext(file);
  await f.writeFile(inn,new Uint8Array(await file.arrayBuffer()));
  const code=await f.exec(['-y',...pre,'-i',inn,...args,out]);
  let d;try{d=await f.readFile(out)}catch(e){}
  try{await f.deleteFile(inn);await f.deleteFile(out)}catch(e){}
  if(code!==0||!d||!d.length)throw new Error('ff');
  return new Blob([d],{type:mime})}
const dim=f=>new Promise((ok,no)=>{const v=document.createElement('video'),u=URL.createObjectURL(f);v.preload='metadata';v.onloadedmetadata=()=>{ok([v.videoWidth,v.videoHeight]);URL.revokeObjectURL(u)};v.onerror=()=>no(new Error('dim'));v.src=u});
window.VID={
 async vwm(f){const d=await dim(f),p=$('#vwp').value,W=Math.max(8,Math.round(d[0]*(+$('#vww').value||20)/100)),H=Math.max(8,Math.round(d[1]*(+$('#vwh').value||10)/100)),x=p[1]==='l'?2:d[0]-W-2,y=p[0]==='t'?2:d[1]-H-2;
  return[await vrun(f,[],['-vf','delogo=x='+x+':y='+y+':w='+W+':h='+H,'-c:v','libx264','-preset','veryfast','-crf','23','-c:a','copy'],'out.mp4','video/mp4'),nm(f,'-clean.mp4')]},
 async vshot(f){return[await vrun(f,['-ss',''+(+$('#vts').value||0)],['-frames:v','1'],'out.png','image/png'),nm(f,'-frame.png')]},
 async vspeed(f){const s=$('#vsp').value;return[await vrun(f,[],['-vf','setpts=PTS/'+s,'-af','atempo='+s,'-c:v','libx264','-preset','veryfast','-c:a','aac'],'out.mp4','video/mp4'),nm(f,'-speed'+s+'.mp4')]},
 async vrot(f){return[await vrun(f,[],['-vf',$('#vro').value,'-c:v','libx264','-preset','veryfast','-c:a','aac'],'out.mp4','video/mp4'),nm(f,'-rotated.mp4')]},
 async vextract(f){const x=$('#vf').value;return[await vrun(f,[],x==='mp3'?['-vn','-c:a','libmp3lame','-q:a','2']:['-vn'],'out.'+x,x==='mp3'?'audio/mpeg':'audio/wav'),nm(f,'.'+x)]},
 async vcompress(f){return[await vrun(f,[],['-vf',"scale=-2:'min(ih,"+$('#vh').value+")'",'-c:v','libx264','-crf',$('#vc').value,'-preset','veryfast','-c:a','aac','-b:a','128k'],'out.mp4','video/mp4'),nm(f,'-compressed.mp4')]},
 async vgif(f){return[await vrun(f,[],['-t','10','-vf','fps='+$('#vr').value+',scale='+$('#vw').value+':-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse'],'out.gif','image/gif'),nm(f,'.gif')]},
 async vtrim(f){const s=+$('#vs').value||0,e=+$('#ve').value||0;if(e<=s)throw Object.assign(new Error('u'),{u:'يجب أن تكون النهاية بعد البداية.'});
  return[await vrun(f,['-ss',''+s],['-t',''+(e-s),'-c','copy'],'out'+ext(f),f.type||'video/mp4'),nm(f,'-trimmed'+ext(f))]},
 async vmute(f){return[await vrun(f,[],['-an','-c:v','copy'],'out'+ext(f),f.type||'video/mp4'),nm(f,'-muted'+ext(f))]},
 async vconv(f){const x=$('#vt').value;return[await vrun(f,[],x==='mp4'?['-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac']:['-c:v','libvpx','-b:v','1M','-c:a','libopus'],'out.'+x,'video/'+x),nm(f,'.'+x)]}};
