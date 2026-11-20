// ===== PART 5: AURAH & STYLE — scene overrides =====
const F5={rose:'#E8A0A8',sage:'#9CB59A',lilac:'#C4B5FD',emer:'#10B981',mocha:'#8B6B4A',navy:'#1E3A8A',gold:'#E9B949',cream:'#FFF8EC',blush:'#FDF2EC'};
const OUTFITS=[
 {kind:'abaya',hij:'#F5EBDD',top:'#0E9F6E',trim:F5.gold,label:'OOTD #1 · Elegant'},
 {kind:'cardigan',hij:F5.rose,top:F5.sage,bottom:'#F3E8DC',label:'OOTD #2 · Soft Girl'},
 {kind:'tunic',hij:'#F3F4F6',top:F5.lilac,bottom:F5.navy,label:'OOTD #3 · Campus'},
 {kind:'sport',hij:'#111827',top:'#F472B6',bottom:'#374151',label:'OOTD #4 · Sporty'},
];
const GREY={kind:'abaya',hij:'#9CA3AF',top:'#6B7280'};
// covered woman: y = feet. o: outfit fields + aL,aR (arm angles), sway
function hijabi(x,y,s,o={}){
  X.save();X.translate(x,y);X.scale(s*(o.flip?-1:1),s);X.globalAlpha*=o.alpha??1;paper(true,8,18);
  const skin='#D8A988', t=o.t??0, sw=(o.sway??1)*Math.sin(t*2.2)*6, k=o.kind??'abaya';
  X.lineCap='round';X.lineJoin='round';
  const top=o.top??'#0E9F6E', bot=o.bottom??top;
  // lower body / garment
  if(k==='abaya'){X.fillStyle=top;X.beginPath();X.moveTo(-70,-470);X.lineTo(70,-470);X.quadraticCurveTo(110,-200,130+sw,0);X.lineTo(-130+sw,0);X.quadraticCurveTo(-110,-200,-70,-470);X.fill();
    if(o.trim){paper(false);X.strokeStyle=o.trim;X.lineWidth=7;X.beginPath();X.moveTo(-126+sw,-10);X.lineTo(126+sw,-10);X.moveTo(0,-440);X.lineTo(sw*0.6,-10);X.stroke();paper(true,8,18)}}
  else if(k==='cardigan'){X.fillStyle=bot;X.beginPath();X.moveTo(-60,-470);X.lineTo(60,-470);X.quadraticCurveTo(100,-200,120+sw,0);X.lineTo(-120+sw,0);X.quadraticCurveTo(-100,-200,-60,-470);X.fill();
    X.fillStyle=top;for(const sd of [-1,1]){X.beginPath();X.moveTo(sd*10,-470);X.lineTo(sd*72,-470);X.quadraticCurveTo(sd*112,-260,sd*118+sw,-120);X.lineTo(sd*40+sw,-120);X.quadraticCurveTo(sd*30,-300,sd*10,-470);X.fill()}}
  else if(k==='tunic'){X.fillStyle=bot;rr(-78,-210,72,210,14);X.fill();rr(6,-210,72,210,14);X.fill();
    X.fillStyle=top;X.beginPath();X.moveTo(-64,-470);X.lineTo(64,-470);X.quadraticCurveTo(96,-300,108+sw,-170);X.lineTo(-108+sw,-170);X.quadraticCurveTo(-96,-300,-64,-470);X.fill()}
  else if(k==='sport'){X.fillStyle=bot;X.beginPath();X.moveTo(-70,-260);X.lineTo(-6,-260);X.lineTo(-20,-10);X.lineTo(-60,-10);X.fill();X.beginPath();X.moveTo(6,-260);X.lineTo(70,-260);X.lineTo(60,-10);X.lineTo(20,-10);X.fill();
    X.fillStyle='#fff';rr(-72,-22,58,26,10);X.fill();rr(14,-22,58,26,10);X.fill();
    X.fillStyle=top;X.beginPath();X.moveTo(-66,-470);X.lineTo(66,-470);X.quadraticCurveTo(92,-330,96+sw*0.5,-230);X.lineTo(-96+sw*0.5,-230);X.quadraticCurveTo(-92,-330,-66,-470);X.fill()}
  // arms (long sleeves)
  const sleeve=k==='cardigan'?top:top;X.strokeStyle=sleeve;X.lineWidth=30;
  const arm=(sx,ang,el)=>{X.beginPath();X.moveTo(sx,-450);const ex=sx+Math.sin(ang)*85,ey=-450+Math.cos(ang)*85;X.lineTo(ex,ey);const hx=ex+Math.sin(ang+el)*80,hy=ey+Math.cos(ang+el)*80;X.lineTo(hx,hy);X.stroke();X.fillStyle=skin;circ(hx,hy,14,skin);return [hx,hy]};
  const hL=arm(-56,o.aL??0.2,o.elL??0), hR=arm(56,o.aR??-0.2,o.elR??0);
  // hijab: head + drape over chest
  X.fillStyle=o.hij??'#F5EBDD';
  X.beginPath();X.ellipse(0,-560,62,70,0,0,7);X.fill();
  const drape=k==='sport'?-420:-330;
  X.beginPath();X.moveTo(-58,-560);X.quadraticCurveTo(-110,-470,-96+sw*0.3,drape);X.quadraticCurveTo(0,drape+40,96+sw*0.3,drape);X.quadraticCurveTo(110,-470,58,-560);X.closePath();X.fill();
  paper(false);
  // face (featureless)
  X.fillStyle=skin;X.beginPath();X.ellipse(0,-552,38,46,0,0,7);X.fill();
  X.strokeStyle='rgba(0,0,0,.08)';X.lineWidth=3;X.beginPath();X.ellipse(0,-556,52,60,0,0.15,Math.PI-0.15);X.stroke();
  if(o.pin){circ(44,-520,7,F5.gold)}
  X.restore();
  return {hL,hR};
}
function sparkles(x,y,r,t,n=14,col='#FDE68A'){for(let i=0;i<n;i++){const a=i/n*Math.PI*2+t*2;const rr2=r*(0.6+0.4*Math.sin(t*5+i));const sx=x+Math.cos(a)*rr2,sy=y+Math.sin(a)*rr2*1.3;X.save();X.translate(sx,sy);X.rotate(t*3+i);X.fillStyle=col;X.beginPath();for(let p=0;p<8;p++){const rad=p%2?4:14;X.lineTo(Math.cos(p*Math.PI/4)*rad,Math.sin(p*Math.PI/4)*rad)}X.fill();X.restore()}}
function crown(x,y,s,a=1){X.save();X.translate(x,y);X.scale(s,s);X.globalAlpha*=a;X.shadowColor='#FDE68A';X.shadowBlur=30;X.fillStyle=F5.gold;X.beginPath();X.moveTo(-70,30);X.lineTo(-80,-30);X.lineTo(-40,0);X.lineTo(0,-50);X.lineTo(40,0);X.lineTo(80,-30);X.lineTo(70,30);X.closePath();X.fill();circ(0,-50,9,'#fff');circ(-80,-30,7,'#fff');circ(80,-30,7,'#fff');X.restore()}
function studio(c1='#FDF2EC',c2='#F8E1D7'){bg(c1,c2);X.fillStyle='rgba(255,255,255,.35)';X.fillRect(0,1540,W,380)}
// ---------------- HOOK ----------------
S.hook=(u,d,t)=>{
  const ev=TL.ev;bg('#08080c','#14121c');
  const on=u>ev.spot;
  if(on){X.save();X.globalAlpha=clamp((u-ev.spot)/0.08);const g=X.createLinearGradient(0,0,0,1800);g.addColorStop(0,'rgba(255,248,230,.55)');g.addColorStop(1,'rgba(255,248,230,.05)');X.fillStyle=g;X.beginPath();X.moveTo(470,-50);X.lineTo(610,-50);X.lineTo(900,1750);X.lineTo(180,1750);X.fill();X.restore();
    X.fillStyle='rgba(255,248,230,.25)';X.beginPath();X.ellipse(540,1750,360,60,0,0,7);X.fill();
    hijabi(540,1740,1.55,{...OUTFITS[0],t,aL:0.5,elL:0.9,aR:-0.25,pin:true});sparkles(540,1100,420,t,12);
    for(let i=0;i<6;i++){const ft=0.3+i*0.09;if(u>ft&&u<ft+0.08){glow(rnd(i)>.5?60:1020,300+rnd(i+2)*1200,260,'rgba(255,255,255,1)')}}}
  const W4=[['WHO SAID',150,'#fff'],['MODEST',250,'#FDE68A'],["CAN'T BE",150,'#fff'],['STYLISH?',220,F5.rose]];
  W4.forEach(([w,size,col],i)=>{const tw=ev.words[i];if(u<tw)return;const k=eout((u-tw)/0.12);const out=u>2.4?clamp((u-2.4)/0.3):0;
    txt(w,W/2,[300,470,640,800][i],size*0.62,col,{weight:900,scale:lerp(1.7,1,k),alpha:k*(1-out),stroke:10,sc:'#08080c',ls:2})});
  if(u>2.4){const k=ease(seg01(u,2.4,d));X.save();X.translate(540,800);X.rotate(k*6.28);X.scale(1+k*6,1+k*6);X.globalAlpha=1-k;X.strokeStyle='#E9B949';X.lineWidth=8;X.beginPath();X.arc(0,-40,22,Math.PI,0);X.lineTo(0,-10);X.moveTo(-90,40);X.lineTo(0,-10);X.lineTo(90,40);X.closePath();X.stroke();X.restore();
    X.fillStyle=`rgba(253,242,236,${k})`;X.fillRect(0,0,W,H)}
  if(u>1.9)txt('Watch her glow up 👀',W/2,140,44,'#fff',{weight:800,font:'Mont, "Noto Color Emoji"',alpha:clamp((u-1.9)/0.3)*(u>2.6?1-clamp((u-2.6)/0.3):1)});
};
S.s1=(u,d,t)=>{
  bg('#E5E7EB','#D1D5DB');
  // wardrobe
  X.save();paper(true);X.fillStyle='#9CA3AF';rr(560,300,460,1100,20);X.fill();X.restore();X.fillStyle='#6B7280';rr(580,330,420,1050,10);X.fill();X.strokeStyle='#4B5563';X.lineWidth=8;X.beginPath();X.moveTo(590,420);X.lineTo(990,420);X.stroke();
  for(let i=0;i<5;i++){const hx=630+i*80;X.strokeStyle='#374151';X.lineWidth=4;X.beginPath();X.arc(hx,410,10,Math.PI,0);X.stroke();X.fillStyle=['#9CA3AF','#A3A3A3','#8B8B8B','#B0B0B0','#999'][i];rr(hx-34,430,68,420+Math.sin(t+i)*4,14);X.fill()}
  X.fillStyle='#CBD5E1';X.fillRect(0,1550,W,400);
  const sl=0.15+0.05*Math.sin(t*2);
  X.save();X.translate(330,1700);X.rotate(sl*0.1);hijabi(0,0,1.15,{...GREY,t,sway:0.3,aL:0.1,aR:-0.1});X.restore();
  // thought bubble
  const k=back(clamp((u-0.5)/0.3));X.save();X.translate(330,560);X.scale(k,k);X.fillStyle='#fff';circ(-60,300,18,'#fff');circ(-30,250,26,'#fff');X.beginPath();X.ellipse(0,0,230,170,0,0,7);X.fill();
  X.fillStyle='#9CA3AF';X.beginPath();X.moveTo(-70,90);X.quadraticCurveTo(-90,-80,0,-100);X.quadraticCurveTo(90,-80,70,90);X.lineTo(40,70);X.lineTo(15,90);X.lineTo(-15,70);X.lineTo(-40,90);X.closePath();X.fill();
  X.fillStyle='#374151';circ(-25,-20,8,'#374151');circ(25,-20,8,'#374151');X.strokeStyle='#374151';X.lineWidth=5;X.beginPath();X.arc(0,30,22,Math.PI*1.15,Math.PI*1.85);X.stroke();txt('boring?',0,140,36,'#6B7280',{weight:800});X.restore();
  const dk=clamp((u-1.2)/0.4);txt('Hijab = boring?',W/2,240,lerp(80,70,dk),'#6B7280',{weight:900,alpha:dk,rot:dk*0.05});
};
S.s2=(u,d,t)=>{
  bg('#FDE3C8','#F7B79B');sun(800,620,90);
  X.save();paper(true);X.fillStyle='#F3D2B0';rr(520,330,460,560,20);X.fill();X.restore();X.save();rr(540,350,420,520,12);X.clip();bg('#FFD3A0','#FF9F7A');sun(760,700,70);X.restore();
  X.fillStyle='#EAC39E';X.fillRect(0,1550,W,400);
  const {hL,hR}=hijabi(360,1720,1.15,{...GREY,hij:'#D6CFC7',top:'#A8A29E',t,aL:2.5,elL:0.9,aR:-2.5,elR:-0.9});
  // open Quran in hands
  X.save();X.translate(360,1720-1.15*395);paper(true);X.fillStyle='#14532D';rr(-95,-55,190,90,8);X.fill();X.fillStyle='#FEF3C7';rr(-88,-50,84,80,4);X.fill();rr(4,-50,84,80,4);X.fill();X.restore();
  for(let i=0;i<10;i++){const k=((t*0.35+rnd(i))%1);txt(['و','ل','ي','ض','ر','ب','ن','خ','م','ه'][i],360+(rnd(i+5)-.5)*200+Math.sin(k*6+i)*30,1250-k*600,40,'#B45309',{font:'Amiri',weight:700,alpha:Math.sin(k*Math.PI),glow:'rgba(255,220,120,.9)'})}
  const ak=clamp((u-0.8)/0.5);
  txt('وَلْيَضْرِبْنَ بِخُمُرِهِنَّ عَلَىٰ جُيُوبِهِنَّ',W/2,220,62,'#7C2D12',{font:'Amiri',weight:700,alpha:ak,glow:'rgba(255,255,255,.8)'});
  txt('"…let them draw their coverings over their chests" (24:31)',W/2,310,30,'#7C2D12',{weight:800,alpha:clamp((u-1.3)/0.4)});
  // golden thread measuring tape spiral
  const sk=clamp((u-1.8)/(d-2));if(sk>0){X.save();X.strokeStyle='#FDE68A';X.lineWidth=4;X.shadowColor='#E9B949';X.shadowBlur=18;X.beginPath();for(let i=0;i<=120*sk;i++){const kk=i/120;const yy=1720-kk*720;const xx=360+Math.cos(kk*20+t*2)*150*(1-kk*0.3);if(i===0)X.moveTo(xx,yy);else X.lineTo(xx,yy)}X.stroke();X.restore()}
};
S.s3=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s3')+u;studio();
  const cut=tt>ev.snip;const ck=clamp((tt-ev.snip-0.3)/0.3);
  txt('STYLE',W/2,620,150,F5.rose,{weight:900,stroke:10,sc:'#fff'});
  txt('DEEN',W/2,1150,150,F5.emer,{weight:900,stroke:10,sc:'#fff'});
  if(!cut){txt('OR',W/2,890,110,'#6B7280',{weight:900})}
  else if(ck<1){X.save();X.globalAlpha=1-ck;txt('O',W/2-60-ck*200,890+ck*300,110,'#6B7280',{weight:900,rot:-ck});txt('R',W/2+60+ck*200,890+ck*300,110,'#6B7280',{weight:900,rot:ck});X.restore()}
  if(cut){txt('WITHIN',W/2,890,110,F5.gold,{weight:900,scale:back(ck),glow:'#FDE68A'});if(ck>0.5){X.save();X.globalAlpha=clamp((ck-0.5)*2);X.strokeStyle=F5.emer;X.lineWidth=10;X.setLineDash([24,16]);X.beginPath();X.ellipse(540,860,470,420,0,0,7);X.stroke();X.restore()}}
  // scissors
  const sx=lerp(-200,540,eout(clamp((tt-(ev.snip-0.6))/0.6))),open2=Math.abs(Math.sin(t*16))*0.4*(cut?0:1);
  if(tt<ev.snip+0.5){X.save();X.translate(sx,890);for(const sd of [-1,1]){X.save();X.rotate(sd*open2);X.fillStyle=F5.gold;rr(-10,-8,170,16,8);X.fill();X.strokeStyle=F5.gold;X.lineWidth=10;X.beginPath();X.arc(-40,sd*30,28,0,7);X.stroke();X.restore()}X.restore()}
};
S.s4=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s4')+u;studio('#F5F3FF','#EDE9FE');
  X.save();X.translate(540,500);paper(true,10,30);X.fillStyle='#fff';rr(-420,-330,840,660,30);X.fill();paper(false);X.fillStyle='#C4B5FD';rr(-120,-370,240,70,20);X.fill();
  txt('MODEST CHECKLIST',0,-250,48,'#5B21B6',{weight:900});
  const items=['Covers all (except face & hands)','Loose, not tight','Thick, not see-through','Elegant, not attention-seeking'];
  items.forEach((it,i)=>{const on=tt>=ev.ticks[i];const y=-140+i*115;X.strokeStyle='#C4B5FD';X.lineWidth=5;rr(-370,y-30,60,60,12);X.stroke();txt(it,-280,y,38,on?'#1F2937':'#9CA3AF',{align:'left',weight:800});if(on)txt('✔',-340,y,60,'#16A34A',{weight:900,font:'DejaVu Sans',scale:back(clamp((tt-ev.ticks[i])/0.2))})});
  X.restore();
  // demo panel
  const ci=ev.ticks.filter(x=>tt>=x-0.1).length-1;
  X.save();X.translate(540,1090);
  if(ci===0){hijabi(0,260,0.7,{...OUTFITS[0],t});glow(0,260-0.7*552,80,'rgba(253,224,71,.8)');}
  else if(ci===1){X.fillStyle='#F87171';rr(-380,-80,240,60,30);X.fill();txt('tight ✖',-260,40,40,'#DC2626',{weight:900,font:'Mont, DejaVu Sans'});
    X.fillStyle=F5.sage;X.beginPath();X.moveTo(100,-140);for(let i=0;i<=10;i++)X.lineTo(100+i*30,-140+Math.sin(i*0.9+t*3)*24);X.lineTo(400,180);for(let i=10;i>=0;i--)X.lineTo(100+i*30,180+Math.sin(i*0.9+t*3+1)*24);X.fill();txt('flowy ✔',250,250,40,'#16A34A',{weight:900,font:'Mont, DejaVu Sans'})}
  else if(ci===2){glow(-260,-60,200,'rgba(255,255,200,.9)');X.save();X.globalAlpha=0.35;X.fillStyle='#F9A8D4';rr(-380,-150,240,260,20);X.fill();X.restore();X.strokeStyle='rgba(244,114,182,.6)';X.lineWidth=2;for(let i=0;i<12;i++){X.beginPath();X.moveTo(-380+i*20,-150);X.lineTo(-380+i*20,110);X.stroke()}txt('see-through ✖',-260,170,36,'#DC2626',{weight:900,font:'Mont, DejaVu Sans'});
    glow(260,-60,200,'rgba(255,255,200,.5)');X.fillStyle='#BE185D';rr(140,-150,240,260,20);X.fill();txt('thick ✔',260,170,40,'#16A34A',{weight:900,font:'Mont, DejaVu Sans'})}
  else if(ci===3){X.fillStyle='#A3E635';rr(-380,-150,240,260,20);X.fill();sparkles(-260,-20,110,t,10,'#F0ABFC');txt('flashy ✖',-260,170,40,'#DC2626',{weight:900,font:'Mont, DejaVu Sans'});
    X.fillStyle='#D6C3B0';rr(140,-150,240,260,20);X.fill();X.strokeStyle=F5.gold;X.lineWidth=4;X.strokeRect(160,-130,200,220);txt('elegant ✔',260,170,40,'#16A34A',{weight:900,font:'Mont, DejaVu Sans'})}
  X.restore();
};
S.s5=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s5')+u;const oi=ev.outfits.filter(x=>tt>=x).length-1;
  const cols=[['#FDF2EC','#FBCFE8'],['#ECFDF5','#A7F3D0'],['#FFF1F2','#FBCFE8'],['#EEF2FF','#C7D2FE'],['#FDF4FF','#F5D0FE']];
  const c=cols[oi+1];bg(c[0],c[1]);
  for(let i=0;i<30;i++){const k=((t*0.2+rnd(i))%1);circ(rnd(i+3)*W,H-k*H,6+rnd(i)*10,['#F9A8D4','#A7F3D0','#FDE68A','#C4B5FD'][i%4])}
  X.fillStyle='rgba(255,255,255,.4)';X.fillRect(0,1560,W,360);
  if(oi<0){const k=back(clamp(u/0.35));txt('GO STYLISH!',W/2,900,150,'#BE185D',{weight:900,scale:k,stroke:12,sc:'#fff',glow:'#F9A8D4'});sparkles(540,900,380,t,18);return}
  const lt=tt-ev.outfits[oi];const spin=clamp(lt/0.35);const sx=Math.abs(Math.cos((1-spin)*Math.PI));
  X.save();X.translate(540,0);X.scale(Math.max(0.05,sx),1);X.translate(-540,0);
  const o=OUTFITS[oi];hijabi(540,1720,1.5,{...o,t,aL:oi===3?2.2:0.4,elL:oi===3?1.2:0.8,aR:oi===2?-0.2:-0.3,pin:true});
  if(oi===2){X.fillStyle='#F5D0A9';rr(620,1100,120,140,16);X.fill();X.strokeStyle='#B45309';X.lineWidth=6;X.beginPath();X.arc(680,1100,40,Math.PI,0);X.stroke()}
  X.restore();
  if(spin<1)sparkles(540,1100,500*spin+100,t,20);
  // stitching gold thread
  X.save();X.strokeStyle='#FDE68A';X.lineWidth=4;X.shadowColor='#E9B949';X.shadowBlur=16;X.setLineDash([18,14]);X.lineDashOffset=-t*80;X.beginPath();X.ellipse(540,1200,330,620,0,0,7*clamp(lt/0.8));X.stroke();X.restore();
  // OOTD frame
  X.save();X.translate(540,260);X.rotate(-0.04);X.scale(back(clamp(lt/0.3)),back(clamp(lt/0.3)));paper(true);X.fillStyle='#fff';rr(-330,-62,660,124,20);X.fill();paper(false);txt(o.label,0,2,50,'#1F2937',{weight:900});X.restore();
  // camera flashes
  if(lt>0.3&&lt<0.6)glow(rnd(oi)>.5?80:1000,600,300,'rgba(255,255,255,.9)');
};
S.s6=(u,d,t)=>{
  bg('#FFF7E0','#FDE68A');glow(540,900,900,'rgba(255,255,255,.8)');motes(t,40,'rgba(233,185,73,1)',.6);
  for(let i=0;i<7;i++){const fx=120+i*140,fk=back(clamp((u-0.3-i*0.08)/0.4));X.save();X.translate(fx,1760);X.scale(fk,fk);X.strokeStyle='#16A34A';X.lineWidth=8;X.beginPath();X.moveTo(0,0);X.lineTo(0,-110);X.stroke();for(let p=0;p<5;p++)circ(Math.cos(p*1.26)*24,-120+Math.sin(p*1.26)*24,17,i%2?'#F9A8D4':'#FDE68A');circ(0,-120,10,'#F59E0B');X.restore()}
  hijabi(540,1720,1.45,{...OUTFITS[0],t,aL:0.3,aR:-0.3,pin:true});
  crown(540,1720-1.45*660,1.0,clamp((u-0.8)/0.5));
  const qk=clamp((u-0.6)/0.5);
  txt('"Allah is beautiful,',W/2,300,74,'#7C2D12',{font:'Amiri',weight:700,alpha:qk,glow:'#fff'});
  txt('and He loves beauty."',W/2,390,74,'#7C2D12',{font:'Amiri',weight:700,alpha:qk,glow:'#fff'});
  txt('(Sahih Muslim 91)',W/2,470,32,'#92400E',{weight:800,alpha:clamp((u-1.0)/0.4)});
};
S.s7=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s7')+u;studio('#FDF2EC','#FCE7F3');
  const sh=tt>ev.shatter;const headY=1720-1.4*660;
  hijabi(540,1720,1.4,{...OUTFITS[1],t,aL:0.3,aR:-0.3,pin:true});
  if(!sh){const k=eout(clamp(u/0.8));X.save();X.translate(540,lerp(-400,headY+120,k));X.strokeStyle='#6B7280';X.lineWidth=8;X.beginPath();X.arc(0,-60,200,Math.PI,0);X.stroke();for(let i=-4;i<=4;i++){X.beginPath();X.moveTo(i*45,-60-Math.sqrt(Math.max(0,40000-(i*45)**2)));X.lineTo(i*45,420);X.stroke()}X.beginPath();X.moveTo(-200,420);X.lineTo(200,420);X.stroke();X.restore()}
  else{const k=clamp((tt-ev.shatter)/0.6);for(let i=0;i<30;i++){const a=rnd(i)*Math.PI*2;circ(540+Math.cos(a)*k*500,headY+150+Math.sin(a)*k*500,6,`rgba(253,224,71,${1-k})`)}crown(540,headY,1.1,clamp((tt-ev.shatter-0.2)/0.4));sparkles(540,headY,140,t,8)}
  txt('NOT A CAGE ✖',W/2,260,80,sh?'rgba(107,114,128,.4)':'#6B7280',{weight:900,font:'Mont, DejaVu Sans',rot:sh?0.08:0});
  if(sh)txt('A CROWN 👑',W/2,380,100,F5.gold,{weight:900,font:'Mont, "Noto Color Emoji"',scale:back(clamp((tt-ev.shatter-0.2)/0.3)),glow:'#FDE68A',stroke:8,sc:'#fff'});
  const b=sgT('s7',1);if(tt>b.start-0.2){const k=eout(clamp((tt-b.start+0.2)/0.4));
    person(lerp(-150,140,k),1760,0.85,{col:'#1E3A8A',aR:-2.6,elR:-0.6,aL:0.2});person(lerp(1230,950,k),1760,0.8,{col:'#0F766E',flip:true,aR:-1.5,elR:0.3});
    txt('👍',lerp(-150,140,k)+60,1760-0.85*420,60,'#000',{font:'"Noto Color Emoji"',weight:500});
    X.save();X.translate(lerp(1230,950,k)-110,1760-0.8*290);paper(true);X.fillStyle=F5.rose;rr(-40,-40,80,80,10);X.fill();X.fillStyle=F5.gold;X.fillRect(-6,-40,12,80);X.restore()}
};
S.cta=(u,d,t)=>{
  const ev=TL.ev, tt=tS('cta')+u, p=u/d;studio('#FDF2EC','#FBCFE8');
  // magazine frame
  X.save();X.strokeStyle='#1F2937';X.lineWidth=10;X.strokeRect(50,120,980,1680);X.restore();
  txt('MODEST IS THE',W/2,240,64,'#1F2937',{weight:900,ls:4,alpha:clamp(u/0.3)});
  txt('NEW STYLISH',W/2,340,104,F5.rose,{weight:900,ls:2,alpha:clamp(u/0.3),stroke:8,sc:'#fff',scale:back(clamp(u/0.4))});
  OUTFITS.forEach((o,i)=>{const k=eout(clamp((u-0.2-i*0.15)/0.4));hijabi(lerp(W+200,180+i*240,k),1450,0.72,{...o,t:t+i,aL:0.3,aR:-0.3})});
  if(tt>ev.comment){const k=back(clamp((tt-ev.comment)/0.3));X.save();X.translate(700,560);X.scale(k,k);paper(true);X.fillStyle='#fff';rr(-260,-60,520,120,40);X.fill();paper(false);circ(-200,0,34,F5.lilac);txt('Emerald abaya 😍',30,2,40,'#1F2937',{weight:800,font:'Mont, "Noto Color Emoji"'});X.restore();
    for(let i=0;i<14;i++){const kk=clamp((tt-ev.comment-rnd(i)*1.5)/2);if(kk>0&&kk<1)txt('🤍',rnd(i+4)*W,lerp(1300,300,kk),40,'#000',{font:'"Noto Color Emoji"',weight:500,alpha:1-kk})}}
  const ck=clamp((p-0.3)/0.15);
  txt('Your fav modest OOTD? 👇',W/2,1600,58,'#1F2937',{weight:900,font:'Mont, "Noto Color Emoji"',alpha:ck});
  txt('Tag a sister who slays in hijab 🤍',W/2,1690,38,'#BE185D',{weight:800,font:'Mont, "Noto Color Emoji"',alpha:ck});
  txt('Share = sadaqah jariyah',W/2,1760,30,'#6B7280',{weight:700,alpha:ck});
  if(u>d-0.5){X.fillStyle=`rgba(8,8,12,${clamp((u-(d-0.5))/0.3)})`;X.fillRect(0,0,W,H)}
};
