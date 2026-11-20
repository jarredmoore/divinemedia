// 3D simplex: Ashima Arts / Ian McEwan, Stefan Gustavson (MIT).
const vertex=`attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}`;
const fragment=`
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 resolution;uniform float time;
vec3 mod289(vec3 x){return x-floor(x/289.)*289.;}
vec4 mod289(vec4 x){return x-floor(x/289.)*289.;}
vec4 permute(vec4 x){return mod289((x*34.+1.)*x);}
float noise(vec3 v){
 const vec2 C=vec2(1./6.,1./3.);const vec4 D=vec4(0.,.5,1.,2.);
 vec3 i=floor(v+dot(v,C.yyy)),x0=v-i+dot(i,C.xxx);
 vec3 g=step(x0.yzx,x0.xyz),l=1.-g,i1=min(g,l.zxy),i2=max(g,l.zxy);
 vec3 x1=x0-i1+C.xxx,x2=x0-i2+C.yyy,x3=x0-D.yyy;
 i=mod289(i);vec4 p=permute(permute(permute(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));
 vec3 ns=(1./7.)*D.wyz-D.xzx;
 vec4 j=p-49.*floor(p*ns.z*ns.z),x_=floor(j*ns.z),y_=floor(j-7.*x_);
 vec4 x=x_*ns.x+ns.yyyy,y=y_*ns.x+ns.yyyy,h=1.-abs(x)-abs(y);
 vec4 b0=vec4(x.xy,y.xy),b1=vec4(x.zw,y.zw),s0=floor(b0)*2.+1.,s1=floor(b1)*2.+1.,sh=-step(h,vec4(0.));
 vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy,a1=b1.xzyw+s1.xzyw*sh.zzww;
 vec3 p0=vec3(a0.xy,h.x),p1=vec3(a0.zw,h.y),p2=vec3(a1.xy,h.z),p3=vec3(a1.zw,h.w);
 vec4 norm=1.79284291400159-.85373472095314*vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3));
 p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
 vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.);m*=m;
 return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
void main(){
 vec2 uv=gl_FragCoord.xy/resolution,p=(uv-.5)*vec2(resolution.x/resolution.y,1.);
 float t=time/60.;vec2 drift=vec2(sin(t*6.283185),cos(t*6.283185))*.16;
 vec2 q=vec2(noise(vec3(p*.78+drift,t*.19)),noise(vec3(p*.78+3.7-drift,t*.17)));
 vec2 w=p*.86+q*.65;
 float a=noise(vec3(w+drift,t*.22))*.5+.5;
 float b=noise(vec3(w*.85+5.2,t*.18))*.5+.5;
 float c=noise(vec3(w*1.6-4.1,t*.21))*.5+.5;
 vec3 base=vec3(7.,8.,18.)/255.,indigo=vec3(27.,40.,115.)/255.;
 vec3 teal=vec3(15.,169.,140.)/255.,violet=vec3(101.,67.,207.)/255.,pink=vec3(214.,64.,143.)/255.;
 vec3 color=mix(indigo,violet,smoothstep(.32,.78,a));
 color=mix(color,teal,smoothstep(.60,.94,b)*.4);
 color=mix(color,pink,smoothstep(.48,.86,1.-a)*smoothstep(.2,.7,c)*.75);
 color=mix(base,color,.28+.4*smoothstep(.2,.85,c));
 float accent=noise(vec3(w*2.1+q*.35+8.,t*.14))*.5+.5;
 color=mix(color,vec3(255.,106.,42.)/255.,smoothstep(.84,.98,accent)*smoothstep(.5,.85,b)*.32);
 color=mix(color,vec3(99.,226.,255.)/255.,smoothstep(.84,.98,1.-accent)*smoothstep(.5,.85,a)*.25);
 color=mix(base*.65,color,1.-.48*smoothstep(.12,.85,length(uv-.5)));
 float grain=fract(52.9829189*fract(dot(mod(gl_FragCoord.xy,256.),vec2(.06711056,.00583715))))-.5;
 gl_FragColor=vec4(clamp(color+grain*.03,0.,1.),1.);
}`;

export function startMesh(canvas,{paused=false,onReady=()=>{}}={}){
 const media=matchMedia('(prefers-reduced-motion: reduce)'),connection=navigator.connection;
 let gl,program,buffer,shaders=[],frame=0,last=0,elapsed=0,drawn=-Infinity,inside=true,dead=false,lost=false,position,size,clock;
 const stop=()=>{cancelAnimationFrame(frame);frame=0;last=0};
 const resize=()=>{
  const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2),scale=Math.min(dpr,Math.sqrt(1200000/Math.max(1,r.width*r.height)));
  const w=Math.max(1,Math.round(r.width*scale)),h=Math.max(1,Math.round(r.height*scale));
  if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;return true}return false;
 };
 const draw=()=>{resize();gl.viewport(0,0,canvas.width,canvas.height);gl.uniform2f(size,canvas.width,canvas.height);gl.uniform1f(clock,elapsed);gl.drawArrays(gl.TRIANGLES,0,3);};
 const animated=()=>!paused&&!media.matches&&!connection?.saveData;
 const tick=now=>{
  frame=0;if(dead||lost||document.hidden||!inside)return;
  if(last)elapsed+=Math.min((now-last)/1000,.1);last=now;
  if(!animated()||now-drawn>=1000/24){draw();drawn=now}
  if(animated())frame=requestAnimationFrame(tick);else last=0;
 };
 const sync=()=>{stop();if(!dead&&!lost&&!document.hidden&&inside)frame=requestAnimationFrame(tick)};
 const changed=()=>{if(!lost&&program)sync()};
 const init=()=>{
  if(dead)return;
  try{
   gl=canvas.getContext('webgl',{alpha:false,antialias:false,depth:false,stencil:false,powerPreference:'low-power',preserveDrawingBuffer:false});
   if(!gl)throw Error('WebGL unavailable');
   program=gl.createProgram();shaders=[];
   for(const[type,source]of[[gl.VERTEX_SHADER,vertex],[gl.FRAGMENT_SHADER,fragment]]){
    const s=gl.createShader(type);shaders.push(s);gl.shaderSource(s,source);gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error('Shader unavailable');gl.attachShader(program,s);
   }
   gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Program unavailable');gl.useProgram(program);
   buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
   position=gl.getAttribLocation(program,'a');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
   size=gl.getUniformLocation(program,'resolution');clock=gl.getUniformLocation(program,'time');lost=false;
   // First draw is scheduled, so the CSS treatment paints before shader work.
   sync();canvas.dataset.mesh='webgl';onReady();
  }catch{lost=true;canvas.dataset.mesh='fallback';stop()}
 };
 const contextLost=e=>{e.preventDefault();lost=true;canvas.dataset.mesh='fallback';stop()};
 const restored=()=>{program=null;buffer=null;shaders=[];init()};
 const observer=typeof IntersectionObserver==='function'?new IntersectionObserver(([e])=>{inside=e.isIntersecting;changed()}):null;
 const resizer=typeof ResizeObserver==='function'?new ResizeObserver(changed):null;
 observer?.observe(canvas);resizer?.observe(canvas);addEventListener('resize',changed,{passive:true});document.addEventListener('visibilitychange',changed);media.addEventListener('change',changed);connection?.addEventListener?.('change',changed);
 canvas.addEventListener('webglcontextlost',contextLost);canvas.addEventListener('webglcontextrestored',restored);
 init();
 return {setPaused(value){if(paused!==value){paused=value;changed()}},destroy(){dead=true;stop();observer?.disconnect();resizer?.disconnect();removeEventListener('resize',changed);document.removeEventListener('visibilitychange',changed);media.removeEventListener('change',changed);connection?.removeEventListener?.('change',changed);canvas.removeEventListener('webglcontextlost',contextLost);canvas.removeEventListener('webglcontextrestored',restored);if(gl){if(buffer)gl.deleteBuffer(buffer);if(program)gl.deleteProgram(program);shaders.forEach(s=>gl.deleteShader(s));}canvas.dataset.mesh='fallback';}};
}
