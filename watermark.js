const cv=$('#wcv'),cx=cv.getContext('2d');let base=null,sel=null,drag=null,hist=[],nm='image';
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
