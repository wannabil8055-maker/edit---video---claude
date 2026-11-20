// ===== PART 3: MAHSYAR — scene overrides (uses helpers from scenes2.js) =====
function lightFig(x,y,s,a=1,o={}){person(x,y,s,{ghost:true,col:o.col??'rgba(255,250,235,.85)',legs:o.legs??'rgba(255,250,235,.75)',skin:o.skin??'rgba(255,252,240,.95)',hair:'rgba(0,0,0,0)',alpha:a,...o})}
function graveyard(t,crack){
  bg('#05070F','#0E1424');for(let i=0;i<60;i++)circ(rnd(i)*W,rnd(i+7)*800,1.5+rnd(i)*1.5,`rgba(255,255,255,${.3+.4*Math.sin(t*2+i)})`);
  X.fillStyle='#141A2B';X.fillRect(0,1000,W,920);
  for(let r=0;r<7;r++)for(let c=0;c<6;c++){const s=0.45+r*0.12;const gx=90+c*180+(r%2)*90-((s-0.45)*200),gy=1060+r*r*14+r*90;X.fillStyle='#232B42';X.beginPath();X.ellipse(gx,gy,70*s,26*s,0,0,7);X.fill();X.fillStyle='#2E3754';rr(gx-12*s,gy-70*s,24*s,60*s,6*s);X.fill();
    if(crack>0){const k=clamp(crack*1.5-(rnd(r*6+c)*0.5));glow(gx,gy,140*s*k,'rgba(255,250,230,.9)',k);X.fillStyle=`rgba(255,252,240,${.5*k})`;X.beginPath();X.moveTo(gx-20*s,gy);X.lineTo(gx-60*s,gy-1200);X.lineTo(gx+60*s,gy-1200);X.lineTo(gx+20*s,gy);X.fill()}}
}
function bigSun(t,y=260){glow(540,y,900,'rgba(255,190,90,.75)');glow(540,y,420,'rgba(255,240,200,1)');circ(540,y,230,'#FFF7E0');for(let i=0;i<24;i++){const a=i/24*Math.PI*2+t*0.1;X.strokeStyle='rgba(255,220,150,.25)';X.lineWidth=10;X.beginPath();X.moveTo(540+Math.cos(a)*260,y+Math.sin(a)*260);X.lineTo(540+Math.cos(a)*(380+30*Math.sin(t*3+i)),y+Math.sin(a)*(380+30*Math.sin(t*3+i)));X.stroke()}}
function crowd(t,y0=900,rows=9,a=1){for(let r=0;r<rows;r++){const s=0.12+r*0.07;const n=Math.floor(22-r*1.4);for(let c=0;c<n;c++){const x=(c+0.5)/n*W+(rnd(r*30+c)-.5)*40+Math.sin(t*1.5+c+r)*3;const y=y0+r*r*9+r*70;lightFig(x,y,s,a*(0.5+r*0.05),{aL:rnd(c+r)>.8?2.6:0.2,aR:-0.2})}}}
function heat(t,a=1){X.save();X.globalAlpha=0.08*a;for(let i=0;i<8;i++){X.fillStyle='#fff';X.fillRect(0,(t*120+i*240)%1920,W,30+10*Math.sin(t*4+i))}X.restore()}
function book(x,y,s,rot,col,flap,glowc){X.save();X.translate(x,y);X.rotate(rot);X.scale(s,s);if(glowc){X.shadowColor=glowc;X.shadowBlur=40}
  const f=Math.sin(flap)*0.6;X.fillStyle=col;X.save();X.transform(1,0,0,1,0,0);X.beginPath();X.moveTo(0,-50);X.lineTo(-80,-50+f*40);X.lineTo(-80,50+f*40);X.lineTo(0,50);X.fill();X.beginPath();X.moveTo(0,-50);X.lineTo(80,-50+f*40);X.lineTo(80,50+f*40);X.lineTo(0,50);X.fill();X.restore();
  X.fillStyle='#F5E6C8';X.beginPath();X.moveTo(0,-44);X.lineTo(-70,-44+f*40);X.lineTo(-70,44+f*40);X.lineTo(0,44);X.fill();X.beginPath();X.moveTo(0,-44);X.lineTo(70,-44+f*40);X.lineTo(70,44+f*40);X.lineTo(0,44);X.fill();X.restore()}
function hellGlow(t,a=1,y=1920){X.save();X.globalAlpha*=a;glow(540,y+200,1300,'rgba(185,28,28,.9)');glow(540,y+200,700,'rgba(249,115,22,.6)');for(let i=0;i<40;i++){const k=((t*0.4+rnd(i))%1);circ(rnd(i+3)*W+Math.sin(t+i)*30,y-k*1400,2+rnd(i)*4,`rgba(253,186,116,${(1-k)*.8})`)}X.restore()}
function bridge(t,y=1000,sag=40,a=1){X.save();X.globalAlpha*=a;X.strokeStyle='#E5E7EB';X.lineWidth=3;X.shadowColor='#fff';X.shadowBlur=18;X.beginPath();X.moveTo(-50,y);X.quadraticCurveTo(540,y+sag,W+50,y);X.stroke();
  X.shadowBlur=0;X.strokeStyle='rgba(160,160,170,.6)';X.lineWidth=3;for(let i=0;i<9;i++){const hx=60+i*120,hy=y+sag*(1-Math.pow((hx-540)/590,2))*1;X.beginPath();X.moveTo(hx,hy);X.lineTo(hx+Math.sin(t*2+i)*6,hy+70);X.arc(hx+Math.sin(t*2+i)*6+12,hy+70,12,Math.PI,0,true);X.stroke()}X.restore()}
const bY=(x,y=1000,sag=40)=>y+sag*(1-Math.pow((x-540)/590,2));
// ---------------- HOOK ----------------
S.hook=(u,d,t)=>{
  const ev=TL.ev;const cr=clamp((u-ev.blast)/0.6);
  if(u<1.8){graveyard(t,cr);
    if(cr>0&&cr<0.3){X.fillStyle=`rgba(255,255,255,${0.6*(1-cr/0.3)})`;X.fillRect(0,0,W,H)}
    X.strokeStyle='rgba(255,250,220,.8)';X.lineWidth=5;if(cr>0)for(let i=0;i<8;i++){X.beginPath();let x0=540,y0=1300,a=-Math.PI/2+(i-3.5)*0.4;X.moveTo(x0,y0);for(let k=0;k<6;k++){a+=(rnd(i*9+k)-.5)*.5;x0+=Math.cos(a)*120*cr;y0+=Math.abs(Math.sin(a))*40*cr+20;X.lineTo(x0,y0)}X.stroke()}
    if(u>1.0){const rk=clamp((u-1.0)/0.8);for(let i=0;i<10;i++)lightFig(120+i*95,lerp(1250,1050,rk)+(i%2)*60,0.5,rk)}}
  else {const k=ease(seg01(u,1.8,d));X.save();const z=lerp(2.2,1,k);X.translate(540,1100);X.scale(z,z);X.translate(-540,-1100);plain(t,k);X.restore();if(u<2.1){X.fillStyle=`rgba(255,255,255,${1-(u-1.8)/0.3})`;X.fillRect(0,0,W,H)}}
  if(u>ev.blast){const k1=eout((u-ev.blast)/0.15);txt('EVERY GRAVE',W/2,560,128,'#fff',{scale:lerp(1.7,1,k1),alpha:k1,weight:900,stroke:10,sc:'#000'});}
  if(u>ev.blast+0.35){const k2=eout((u-ev.blast-0.35)/0.15);txt('WILL OPEN.',W/2,720,140,'#FDE68A',{scale:lerp(1.7,1,k2),alpha:k2,weight:900,stroke:10,sc:'#000',glow:'#F59E0B',gb:40})}
  if(u>2.0)txt('Including yours.',W/2,170,48,'#fff',{weight:800,stroke:8,alpha:clamp((u-2)/0.3)});
};
function plain(t,k=1){bg('#F59E0B','#D6C3A5');bigSun(t,240);X.fillStyle='#C9A77C';X.fillRect(0,880,W,1100);crowd(t,880,9,1);heat(t,1)}
S.s1=(u,d,t)=>{plain(t);
  // close-up feet & sweat
  X.fillStyle='#B38B5E';X.fillRect(0,1600,W,320);
  lightFig(540,1880,1.25,1,{aL:2.7,aR:-0.2,elL:1.4});
  for(let i=0;i<14;i++){const k=((t*0.6+rnd(i))%1);txt('💧',300+rnd(i+2)*480,1500-k*500,30,'#000',{font:'"Noto Color Emoji"',weight:500,alpha:Math.sin(k*Math.PI)*.8})}
  const wob=Math.sin(t*6)*4;txt('DAY OF JUDGEMENT',W/2,600+wob,72,'#7C2D12',{weight:900,ls:6,alpha:clamp(u/0.6),stroke:6,sc:'#FFF7E0'});
};
S.s2=(u,d,t)=>{
  bg('#1E1B3A','#B45309');glow(540,200,800,'rgba(255,200,120,.35)');X.fillStyle='#8A6A45';X.fillRect(0,1250,W,700);crowd(t,1250,6,0.9);
  const p=u/d;
  for(let i=0;i<70;i++){const a0=rnd(i)*Math.PI*2;const r=380+rnd(i+1)*300;const sw=t*0.9+a0;let bx=540+Math.cos(sw)*r*(1+0.3*Math.sin(i)),by=650+Math.sin(sw*1.3)*r*0.55;
    const dive=clamp((p-0.55-rnd(i+4)*0.25)/0.25);const tx=rnd(i+9)*W,ty=1300+rnd(i+11)*400;bx=lerp(bx,tx,ein(dive));by=lerp(by,ty,ein(dive));
    book(bx,by,0.45+rnd(i+2)*0.35,Math.sin(t+i)*0.4,i%3?'#7C2D12':'#1E3A8A',t*14+i,null)}
  // flickering pages
  if(p<0.55){X.save();X.translate(540,1050);X.globalAlpha=0.9;paper(true);X.fillStyle='#F5E6C8';rr(-230,-150,460,300,14);X.fill();paper(false);const pg=Math.floor(t*6)%3;txt(['📱','🧎','✉️'][pg],0,0,120,'#000',{font:'"Noto Color Emoji"',weight:500});X.restore()}
};
S.s3=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s3')+u;
  X.save();X.beginPath();X.rect(0,0,W,950);X.clip();bg('#FFE7A8','#F2C14E');glow(540,400,700,'rgba(255,255,255,.7)');X.fillStyle='#E9C27A';X.fillRect(0,820,W,200);
  const rk=clamp((tt-ev.right)/0.5);
  person(540,900,0.95,{col:'#F8FAFC',legs:'#E7E5E4',cap:'#fff',aR:lerp(-0.2,-2.9,eout(rk)),elR:0,aL:0.3});
  book(lerp(800,560,eout(rk)),lerp(100,400,eout(rk)),0.9,0,'#B45309',rk<1?t*14:0.2,'rgba(253,224,71,1)');
  const [cx,cy]=chest(540,900,0.95);thread(cx,cy,500,0,t,1);
  txt('RIGHT HAND ✔',W/2,120,64,'#065F46',{weight:900,font:'Mont, DejaVu Sans',alpha:rk,stroke:8,sc:'#FFF7E0'});
  if(rk>0.7)txt('"Here, read my book!"',W/2,210,40,'#7C2D12',{weight:800,alpha:clamp((rk-0.7)*3)});
  X.restore();
  X.fillStyle='#000';X.fillRect(0,946,W,8);
  X.save();X.beginPath();X.rect(0,954,W,966);X.clip();bg('#1F2937','#0B0F19');
  const lk=clamp((tt-ev.left)/0.6);
  if(tt>ev.left-0.3){const kn=clamp((tt-ev.left-0.4)/0.4);
    person(540,1840,0.95,{col:'#4B5563',legs:'#374151',skin:'#6B7280',hair:'#1F2937',pose:kn>0.5?'kneel':'stand',aL:lerp(0.2,2.2,lk),elL:0.6,aR:2.6,elR:1.2,slump:kn*0.4});
    book(lerp(200,420,eout(lk)),lerp(1100,1500,eout(lk)),0.8,0.3,'#111827',lk<1?t*14:0.2,'rgba(0,0,0,.9)');
    for(let i=0;i<10;i++){const k=((t*0.5+rnd(i))%1);circ(420+Math.sin(k*6+i)*30,1480-k*300,12+k*20,`rgba(60,60,70,${.5*(1-k)})`)}
    txt('LEFT HAND ✖',W/2,1060,64,'#F87171',{weight:900,font:'Mont, DejaVu Sans',alpha:lk,stroke:8,sc:'#000'})}
  X.restore();
};
S.s4=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s4')+u;const good=tt>=ev.good, evil=tt>=ev.evil;
  bg(evil?'#2A0A0A':'#0F172A',evil?'#450A0A':'#1E293B');
  if(good&&!evil)glow(540,900,900,'rgba(253,224,71,.35)');if(evil)glow(540,900,900,'rgba(185,28,28,.4)');
  let ang=Math.sin(t*2)*0.06;
  if(good&&!evil){const b=tt-ev.good;ang=0.32-0.12*Math.exp(-b*4)*Math.cos(b*10)}
  if(evil){const b=tt-ev.evil;ang=-0.32+0.12*Math.exp(-b*4)*Math.cos(b*10)}
  // pillar
  X.save();paper(true);X.fillStyle='#E5E7EB';rr(510,560,60,1100,20);X.fill();rr(380,1620,320,60,20);X.fill();circ(540,560,50,G.honey);X.restore();
  X.save();X.translate(540,600);X.rotate(ang);X.fillStyle='#F3F4F6';rr(-440,-18,880,36,18);X.fill();
  const pans=[[-420,'L'],[420,'R']];
  pans.forEach(([px,side])=>{X.save();X.translate(px,0);X.rotate(-ang);X.strokeStyle='#D1D5DB';X.lineWidth=5;X.beginPath();X.moveTo(0,0);X.lineTo(-150,520);X.moveTo(0,0);X.lineTo(150,520);X.stroke();
    X.fillStyle=side==='R'?'#FDE68A':'#9CA3AF';X.beginPath();X.ellipse(0,530,190,50,0,0,Math.PI);X.fill();
    // cubes stacked
    const isR=side==='R';const n=ev.cubes.filter((c,i)=>(i%2===0)===isR&&tt>=c+0.3).length;
    for(let i=0;i<n;i++){X.fillStyle=isR?'#FBBF24':'#111827';X.shadowColor=isR?'#FDE68A':'#000';X.shadowBlur=20;rr(-110+(i%3)*75,470-Math.floor(i/3)*65,62,58,8);X.fill();X.shadowBlur=0}
    X.restore()});
  X.restore();
  // dropping cubes
  ev.cubes.forEach((c,i)=>{const k=(tt-(c-0.3))/0.6;if(k<0||k>1)return;const isR=i%2===0;const px=540+(isR?420:-420);X.fillStyle=isR?'#FBBF24':'#111827';X.shadowColor=isR?'#FDE68A':'#444';X.shadowBlur=25;rr(px-31,lerp(-80,1050,ein(k)),62,58,8);X.fill();X.shadowBlur=0;txt(isR?['🕌','🤲','📖'][Math.floor(i/2)]:'',px,lerp(-50,1080,ein(k)),34,'#000',{font:'"Noto Color Emoji"',weight:500})});
  txt('⚖ THE SCALE',W/2,250,62,'#E5E7EB',{weight:900,ls:6,font:'Mont, DejaVu Sans'});
  if(good&&!evil){const k=back(clamp((tt-ev.good)/0.25));txt('HEAVY GOOD = JOY',W/2,1780,70,'#FDE68A',{weight:900,scale:k,glow:'#F59E0B'});for(let i=0;i<30;i++){const kk=(tt-ev.good)*0.8;circ(540+420+(rnd(i)-.5)*400,1200-kk*600*rnd(i+1),5,'rgba(253,224,71,.8)')}}
  if(evil){const k=back(clamp((tt-ev.evil)/0.25));txt('HEAVY EVIL = RUIN',W/2,1780,70,'#F87171',{weight:900,scale:k,glow:'#991B1B'})}
};
S.s5=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s5')+u;const dr=tt>=ev.drink;
  bg('#CFFAFE','#ECFEFF');glow(540,1100,900,'rgba(255,255,255,.9)');
  X.save();X.translate(540,1150);paper(true,0,60,'rgba(103,232,249,.8)');X.fillStyle='#FFFFFF';X.beginPath();X.ellipse(0,0,480,200,0,0,7);X.fill();paper(false);
  for(let i=0;i<5;i++){const r=((t*60+i*80)%400);X.strokeStyle=`rgba(252,211,77,${.5*(1-r/400)})`;X.lineWidth=4;X.beginPath();X.ellipse(0,0,r*1.2,r*0.5,0,0,7);X.stroke()}X.restore();
  for(let i=0;i<16;i++){const a=i/16*Math.PI*2;const cx2=540+Math.cos(a)*520,cy2=1150+Math.sin(a)*230;glow(cx2,cy2,40,'rgba(253,224,71,.8)');X.fillStyle='#FDE68A';rr(cx2-14,cy2-20,28,34,6);X.fill()}
  person(540,1700,1.0,{col:'#F8FAFC',legs:'#E7E5E4',cap:'#fff',aR:dr?-2.6:-0.2,elR:dr?-1.5:0,aL:0.2,slump:dr?-0.1:0.2});
  if(dr){X.fillStyle='#FDE68A';rr(560,1240,30,40,6);X.fill()}
  if(dr){const w=clamp((tt-ev.drink)/0.8);X.fillStyle=`rgba(103,232,249,${.35*(1-w)})`;X.fillRect(0,H*(1-w),W,H*w)}
  txt('Never thirsty again.',W/2,400,70,'#0E7490',{weight:900,alpha:clamp((tt-ev.drink)/0.4),scale:1+0.02*Math.sin(t*5),stroke:6,sc:'#fff'});
  txt('THE POOL',W/2,250,50,'#0891B2',{weight:800,ls:10,alpha:clamp(u/0.4)});
};
S.s6=(u,d,t)=>{
  const tilt=ease(clamp(u/(d*0.8)));bg('#030305','#0B0306');
  X.save();X.translate(0,lerp(500,-200,tilt));hellGlow(t,1,2100);bridge(t,1000,30);X.restore();
  txt('SIRAT',W/2,300,120,'#E5E7EB',{weight:900,ls:20,alpha:clamp(u/0.5),glow:'#fff',gb:30});
  txt('thinner than hair · sharper than a sword',W/2,420,34,'rgba(229,231,235,.75)',{weight:500,alpha:clamp((u-0.5)/0.5)});
};
S.s7=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s7')+u;bg('#030305','#0B0306');hellGlow(t,1,1900);
  const si=Math.max(0,ev.speeds.filter(s=>tt>=s-0.05).length-1);const st=ev.speeds[si]-0.05, en=si<6?ev.speeds[si+1]-0.05:tS('s8');const k=clamp((tt-st)/(en-st));
  bridge(t,1000,30);
  const words=['BLINK.','LIGHTNING.','WIND.','BIRDS.','RUN.','WALK.','crawl…'];
  const prog=[k<0.15?0:1, ein(clamp(k*3)), eout(clamp(k*1.6)), ease(clamp(k*1.3)), clamp(k*1.1), clamp(k*0.55), clamp(k*0.18)][si];
  const x=lerp(80,1000,prog), y=bY(x);
  const gold=si<4;
  if(si===0&&k<0.2){X.fillStyle=`rgba(255,255,255,${.6*(1-k/0.2)})`;X.fillRect(0,0,W,H)}
  if(si===1){X.strokeStyle='#FEF9C3';X.lineWidth=8;X.shadowColor='#FDE047';X.shadowBlur=30;X.beginPath();X.moveTo(80,bY(80)-150);for(let i=1;i<=10;i++){const xx=lerp(80,x,i/10);X.lineTo(xx,bY(xx)-150+(i%2?-40:40))}X.stroke();X.shadowBlur=0}
  if(si===2){for(let i=0;i<20;i++){const xx=x-i*30;X.strokeStyle=`rgba(200,240,255,${.5*(1-i/20)})`;X.lineWidth=4;X.beginPath();X.arc(xx,bY(xx)-150,40+i*3,t*8+i,t*8+i+2);X.stroke()}}
  if(si===3){for(const side of [-1,1]){X.strokeStyle='rgba(255,240,200,.8)';X.lineWidth=5;X.beginPath();X.moveTo(x,y-200);X.quadraticCurveTo(x-60,y-260+side*Math.sin(t*20)*40,x-160,y-200+side*30);X.stroke()}}
  const pose=si===6?'kneel':(si>=4?'walk':'stand');
  const a=si===5?1.4:0.2;
  const lt=[1,1,1,1,0.7,0.45,0.15][si];
  glow(x,y-20,180*lt,'rgba(253,230,138,.9)',lt);
  if(!(si===0&&k>=0.15&&k<0.2))lightFig(x,y,0.6,1,{pose,t:t*(si===4?2:si===6?0.4:1),aL:si===6?2.0:a,aR:si===6?2.0:-a,elL:si===6?-1.0:0,elR:si===6?-1.0:0,slump:si===6?0.9:0});
  if(si===6){const fl=Math.sin(t*20)>0.3?1:0.3;glow(x+20,y,40,'rgba(253,186,116,1)',fl);hellGlow(t,0.5+0.3*Math.sin(t*3),1700)}
  const wk=clamp((tt-st)/0.15);
  const styles=[{col:'#fff',glow:'#fff'},{col:'#FEF08A',glow:'#FACC15',rot:-0.08},{col:'#BAE6FD',glow:'#38BDF8'},{col:'#FDE68A',glow:'#F59E0B'},{col:'#E5E7EB'},{col:'#9CA3AF'},{col:'#F87171'}];
  const sty=styles[si];const jx=si===6?(Math.random()-.5)*10:si===1?(Math.random()-.5)*16*(1-wk):0;
  txt(words[si],W/2+jx,560,si===6?90:150,sty.col,{weight:si===6?500:900,scale:lerp(1.6,1,eout(wk)),alpha:wk,glow:sty.glow,gb:40,rot:sty.rot,stroke:si===6?0:8,sc:'#000'});
};
S.s8=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s8')+u;bg('#000','#030305');hellGlow(t,0.6,2000);
  const mx=lerp(260,820,u/d), my=bY(mx);
  // reveal bridge only near lights
  X.save();X.beginPath();X.arc(mx,my,520,0,7);const out=tt>ev.lightout;const bx=lerp(120,300,u/d),by=bY(bx);if(!out){X.arc(bx,by,60+40*Math.random(),0,7)}X.clip();bridge(t,1000,30);X.restore();
  glow(mx,my-200,560,'rgba(253,230,138,.85)');
  lightFig(mx,my,0.65,1,{pose:'walk',t,aR:-2.6,elR:0.3});
  X.save();X.translate(mx+50,my-370);X.fillStyle='#FDE68A';X.shadowColor='#FBBF24';X.shadowBlur=60;X.beginPath();X.ellipse(0,0,26,46+6*Math.sin(t*12),0,0,7);X.fill();X.restore();
  // the flickerer behind
  lightFig(bx,by,0.6,0.45,{pose:out?'stand':'walk',t:t*0.3,aL:out?1.3:0.4,aR:out?-1.3:-0.4,col:'rgba(200,200,210,.5)',legs:'rgba(200,200,210,.4)',skin:'rgba(210,210,220,.6)'});
  if(!out){const fl=Math.random()>0.4?1:0.15;glow(bx+15,by,50,'rgba(253,186,116,1)',fl)}
  txt('Your deeds = your light.',W/2,400,64,'#FDE68A',{weight:900,alpha:clamp(u/0.5)*(out?0.4+0.6*(Math.random()>0.5?1:0):1),glow:'#F59E0B'});
};
S.s9=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s9')+u;const op=ease(clamp((tt-ev.gates)/1.0));
  if(op<1){bg('#FFF8E1','#FDE68A');glow(540,900,900,'rgba(255,255,255,.9)')}
  else gardenBG(t,1);
  if(op>=1||u>1.0){X.save();X.globalAlpha=clamp((u-1.0)/0.4);gardenBG(t,1);
    // palace
    X.save();X.translate(540,980);paper(true,10,30);X.fillStyle='#F8FAFC';rr(-260,-300,520,300,10);X.fill();X.fillStyle=G.honey;X.beginPath();X.arc(0,-300,160,Math.PI,0);X.fill();for(const px of [-230,230]){X.fillStyle='#F8FAFC';rr(px-30,-460,60,460,8);X.fill();X.fillStyle=G.honey;X.beginPath();X.arc(px,-460,34,Math.PI,0);X.fill()}paper(false);X.fillStyle='#FDE68A';rr(-50,-160,100,160,50);X.fill();X.restore();
    const wk=clamp((u-1.2)/(d-1.4));const px=lerp(300,540,wk), py=lerp(1800,1100,wk);
    person(px,py,lerp(0.9,0.45,wk),{pose:'walk',t,col:'#fff',legs:'#F5F5F4',cap:'#fff'});
    txt("You'll know your way home.",W/2,400,58,'#065F46',{weight:900,stroke:8,sc:'#fff',alpha:clamp((u-1.6)/0.4)});
    txt('🏠 ➜ 🏰',W/2,500,70,'#000',{font:'"Noto Color Emoji"',weight:500,alpha:clamp((u-2.0)/0.4)});
    X.restore()}
  if(u<1.4){X.save();X.globalAlpha=1-clamp((u-1.0)/0.4);
    X.save();X.translate(540,1100);X.shadowColor='#FBBF24';X.shadowBlur=60;X.fillStyle='#FFFBEB';rr(-330,-650,660,1000,40);X.fill();X.shadowBlur=0;
    glow(0,-150,600*op,'rgba(255,255,255,1)',op);
    for(const sd of [-1,1]){X.save();X.translate(sd*300,0);X.scale(1-op*0.9,1);X.fillStyle='#D97706';rr(sd<0?0:-300,-620,300,960,20);X.fill();X.strokeStyle='#FDE68A';X.lineWidth=6;X.strokeRect(sd<0?20:-280,-590,260,900);X.restore()}
    X.restore();txt('AR-RAYYAN',W/2,330,54,'#92400E',{weight:900,ls:12});X.restore()}
};
S.s10=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s10')+u;gardenBG(t,1);
  person(300,1720,1.0,{pose:'sit',col:'#fff',legs:'#F5F5F4',cap:'#fff',aL:2.9,aR:0.5,elL:1.3,slump:-0.25});wife(620,1740,0.75,1,t);kid(800,1740,1.0,{col:'#F59E0B'});
  ['🤕','😟','😴'].forEach((e,i)=>{const sx=240+i*300,sy=560;const show=clamp((u-i*0.25)/0.2);X.save();X.globalAlpha=show;circ(sx,sy,90,'rgba(255,255,255,.85)');txt(e,sx,sy+6,90,'#000',{font:'"Noto Color Emoji"',weight:500});
    const ct=i<2?ev.cross[i]:ev.cross[1]+0.55;if(tt>ct){const ck=clamp((tt-ct)/0.15);X.strokeStyle='#DC2626';X.lineWidth=16;X.lineCap='round';X.beginPath();X.moveTo(sx-60,sy-60);X.lineTo(sx-60+120*ck,sy-60+120*ck);X.moveTo(sx+60,sy-60);X.lineTo(sx+60-120*ck,sy-60+120*ck);X.stroke()}X.restore()});
  stamp('BUSY.',W/2,1000,tt-ev.busy,'#16A34A',170,-0.15);
};
S.s11=(u,d,t)=>{
  bg('#000','#050102');hellGlow(t,1,1900);
  const k=ein(clamp(u/(d*0.9)));
  bridge(t,lerp(600,-200,k),20);
  const s=lerp(0.8,0.08,k);X.save();X.translate(540,lerp(700,1500,k));X.rotate(k*4);lightFig(0,0,s,1-k*0.6,{col:'rgba(150,150,160,.7)',legs:'rgba(150,150,160,.6)',skin:'rgba(170,170,180,.8)',aL:2.6,aR:-2.6});X.restore();
  for(let i=0;i<50;i++){const kk=((t*0.8+rnd(i))%1);circ(rnd(i+5)*W,H-kk*H*1.2,3+rnd(i)*5,`rgba(253,186,116,${(1-kk)})`)}
  X.fillStyle=`rgba(0,0,0,${clamp((u-d*0.7)/(d*0.3))*0.6})`;X.fillRect(0,0,W,H);
};
S.cta=(u,d,t)=>{
  const p=u/d;
  X.save();X.beginPath();X.rect(0,0,W,960);X.clip();bg('#FFF8E1','#FDE68A');glow(540,250,700,'rgba(255,255,255,.9)');X.fillStyle='#FFFBEB';X.shadowColor='#FBBF24';X.shadowBlur=40;rr(400,120,280,380,30);X.fill();X.restore();
  X.save();X.beginPath();X.rect(0,960,W,960);X.clip();bg('#1a0505','#000');hellGlow(t,1,2000);X.restore();
  // hourglass
  X.save();X.translate(540,960);X.strokeStyle='#fff';X.lineWidth=8;X.beginPath();X.moveTo(-90,-140);X.lineTo(90,-140);X.lineTo(12,0);X.lineTo(90,140);X.lineTo(-90,140);X.lineTo(-12,0);X.closePath();X.fill&&0;X.stroke();
  X.fillStyle='#FDE68A';X.beginPath();X.moveTo(-70*(1-p*0.6),-120+p*70);X.lineTo(70*(1-p*0.6),-120+p*70);X.lineTo(8,-8);X.lineTo(-8,-8);X.fill();X.beginPath();X.moveTo(-70,120);X.lineTo(70,120);X.lineTo(70*(0.3+p*0.5)*0.6,120-p*70);X.lineTo(-70*(0.3+p*0.5)*0.6,120-p*70);X.fill();for(let i=0;i<5;i++)circ(0,(t*200+i*25)%120,3,'#FDE68A');X.restore();
  thread(540,1240,900,0,t,clamp(p*3));
  txt('Part 1 · Part 2 · Part 3',W/2,620,34,'#92400E',{weight:800,alpha:clamp(p*4)});
  const tk=clamp((p-0.15)/0.15);
  txt('YOU DECIDE',W/2,720,104,'#7C2D12',{weight:900,scale:back(tk),alpha:tk,stroke:8,sc:'#FFF8E1'});
  txt('YOUR NEXT LIFE.',W/2,1260,96,'#FDE68A',{weight:900,scale:back(tk),alpha:tk,glow:'#F59E0B',stroke:8,sc:'#000'});
  const ck=clamp((p-0.4)/0.15);
  X.save();X.globalAlpha=ck;X.translate(W/2,1600);X.fillStyle='rgba(255,255,255,.12)';X.strokeStyle='#FDE68A';X.lineWidth=4;rr(-370,-55,740,110,55);X.fill();X.stroke();txt('Which path is yours? Comment 👇',0,3,42,'#fff',{weight:900,font:'Mont, "Noto Color Emoji"'});X.restore();
  txt('Share = sadaqah jariyah 🤍',W/2,1740,34,'rgba(255,255,255,.8)',{weight:600,alpha:ck,font:'Mont, "Noto Color Emoji"'});
  if(u>d-0.9){const fk=clamp((u-(d-0.9))/0.8);X.save();X.globalAlpha=fk;graveyard(t,0);X.restore()}
};
