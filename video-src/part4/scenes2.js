// ===== PART 2: THE SOLEH MAN — scene overrides =====
const G={emer:'#10B981',turq:'#2DD4BF',pearl:'#F8FAFC',honey:'#FBBF24',sage:'#7BAE7F',cream:'#FBEBD3',dawn:'#F2C14E'};
const tS=k=>TL.scenes[k].start, sgT=(sc,k)=>TL.segs[TL.scenes[sc].segs[k]];
function stamp(label,x,y,u0,col,size=110,rot=-0.15){if(u0<0)return;const k=clamp(u0/0.12);txt(label,x,y,size,col,{scale:lerp(2.2,1,k),rot,weight:900,alpha:k,stroke:8,sc:'#fff'})}
function sun(x,y,r){glow(x,y,r*4,'rgba(255,214,140,.7)');circ(x,y,r,'#FFE7A8')}
function gardenBG(t,a=1){
  X.save();X.globalAlpha*=a;
  bg('#E6FFF6','#BDF3DC');sun(780,330,90);
  // far hills
  X.fillStyle='#7EE0B5';X.beginPath();X.moveTo(0,980);for(let x=0;x<=W;x+=40)X.lineTo(x,930-60*Math.sin(x/170)-30*Math.sin(x/70));X.lineTo(W,H);X.lineTo(0,H);X.fill();
  X.fillStyle='#34D399';X.beginPath();X.moveTo(0,1130);for(let x=0;x<=W;x+=40)X.lineTo(x,1100-50*Math.sin(x/230+1)-20*Math.sin(x/90));X.lineTo(W,H);X.lineTo(0,H);X.fill();
  // pavilions far
  for(const [px,py,s] of [[230,900,0.6],[880,880,0.5]]){X.save();X.translate(px,py);X.scale(s,s);X.fillStyle='#F8FAFC';rr(-60,-110,120,110,8);X.fill();X.fillStyle=G.honey;X.beginPath();X.arc(0,-110,62,Math.PI,0);X.fill();X.restore()}
  // river
  X.fillStyle=G.turq;X.beginPath();X.moveTo(470,1000);X.bezierCurveTo(600,1200,300,1400,420,1600);X.lineTo(260,H);X.lineTo(820,H);X.bezierCurveTo(700,1500,760,1250,560,1000);X.closePath();X.fill();
  for(let i=0;i<30;i++){const k=((rnd(i)+t*0.15)%1);const yy=1000+k*920;const xx=lerp(515,540,k)+Math.sin(k*8)*120*k+(rnd(i+3)-.5)*160*k;X.globalAlpha=a*.7;X.fillStyle='#fff';rr(xx,yy,30+40*k,5,3);X.fill()}
  X.globalAlpha=a;
  X.fillStyle='#10B981';X.fillRect(0,1500,260,500);X.fillRect(820,1500,260,500);
  // trees with gold leaves
  for(const [tx,ty,s] of [[120,1500,1.1],[960,1480,1.0],[330,1120,0.55],[760,1110,0.5]]){X.save();X.translate(tx,ty);X.scale(s,s);X.fillStyle='#8B5E3C';rr(-22,-320,44,320,14);X.fill();
    for(let k=0;k<9;k++){const a2=k/9*Math.PI*2;X.fillStyle=k%3?'#22C55E':G.honey;circ(Math.cos(a2)*110,-380+Math.sin(a2)*80+Math.sin(t*1.5+k)*5,90,X.fillStyle)}
    for(let k=0;k<8;k++)circ(-90+rnd(k+tx)*180,-440+rnd(k)*160,10,'#FDE68A');X.restore()}
  // lanterns
  for(let i=0;i<10;i++){const lx=rnd(i+40)*W,ly=(rnd(i+41)*900+200-t*25*(0.5+rnd(i)))%1100;const yy=(ly+1100)%1100+100;glow(lx,yy,60,'rgba(255,214,120,.8)');X.fillStyle='#FBBF24';rr(lx-12,yy-18,24,36,8);X.fill()}
  motes(t,40,'rgba(251,191,36,1)',.6);
  X.restore();
}
function roomDawn(t,fray=0){
  bg('#FBE3C8','#F7C9A6');
  X.save();paper(true);X.fillStyle='#F3D2B0';rr(560,260,420,520,20);X.fill();paper(false);
  X.save();rr(580,280,380,480,12);X.clip();bg('#FFD9A0','#FFB48A');sun(770,640,60);X.fillStyle='rgba(120,90,140,.35)';for(let i=0;i<9;i++){const bh=80+rnd(i)*150;X.fillRect(580+i*44,760-bh,40,bh)}X.restore();
  X.strokeStyle='#E3B98F';X.lineWidth=12;X.beginPath();X.moveTo(770,280);X.lineTo(770,760);X.stroke();X.restore();
  glow(770,520,700,'rgba(255,220,160,.35)');
  X.save();paper(true);circ(240,420,90,'#FFF8EC');paper(false);X.strokeStyle='#5b4636';X.lineWidth=8;X.lineCap='round';X.beginPath();X.moveTo(240,420);X.lineTo(240+Math.cos(-2.2)*45,420+Math.sin(-2.2)*45);X.moveTo(240,420);X.lineTo(240+Math.cos(-1.57+t*0.3)*70,420+Math.sin(-1.57+t*0.3)*70);X.stroke();txt('FAJR',240,545,30,'rgba(91,70,54,.7)',{weight:800});X.restore();
  X.fillStyle='#EAC39E';X.fillRect(0,1250,W,700);
  // unrolled prayer mat
  X.save();paper(true);X.fillStyle='#7BAE7F';rr(160,1300,760,300,14);X.fill();paper(false);X.strokeStyle='#F2C14E';X.lineWidth=6;X.strokeRect(190,1325,700,250);X.fillStyle='#F2C14E';X.beginPath();X.moveTo(800,1340);X.lineTo(870,1450);X.lineTo(800,1560);X.fill();X.restore();
  // phone face down charging
  X.save();paper(true);X.fillStyle='#222';rr(880,1210,120,40,8);X.fill();X.restore();X.strokeStyle='#fff';X.lineWidth=3;X.beginPath();X.moveTo(1000,1230);X.quadraticCurveTo(1060,1260,1080,1200);X.stroke();
  // man seated reading with rehal
  const mx=430,my=1470;
  person(mx,my,1.0,{pose:'sit',col:'#F5F5F4',legs:'#E7E5E4',cap:'#fff',aL:2.3,aR:2.2,elL:0.9,elR:1.0,slump:0.08+0.04*Math.sin(t*2)});
  X.save();X.translate(560,1300);paper(true);X.strokeStyle='#8B5E3C';X.lineWidth=12;X.beginPath();X.moveTo(-70,60);X.lineTo(70,-40);X.moveTo(70,60);X.lineTo(-70,-40);X.stroke();X.fillStyle='#14532D';rr(-90,-90,180,70,8);X.fill();X.fillStyle='#FEF3C7';rr(-82,-84,78,58,4);X.fill();rr(4,-84,78,58,4);X.fill();X.restore();
  const [cx,cy]=chest(mx,my,1.0,'sit');
  for(let i=0;i<14;i++){const k=((t*0.35+rnd(i))%1);const lx=560+(rnd(i+9)-.5)*120+Math.sin(k*7+i)*40*k, ly=1220-k*700;X.globalAlpha=Math.sin(k*Math.PI);txt(['ا','ل','م','ق','ر','ن','ه','ي','ب','س'][i%10],lx,ly,40+20*rnd(i),'#E9B949',{font:'Amiri',weight:700,glow:'rgba(255,200,80,.9)'})}X.globalAlpha=1;
  return [cx,cy];
}
// ---------------- HOOK ----------------
S.hook=(u,d,t)=>{
  bg('#000','#04040a');
  const gold=clamp((u-0.6)/0.4), smile=ease(clamp((u-0.8)/0.6));
  if(u<1.7){X.save();X.lineWidth=7;X.strokeStyle=gold>0?`rgb(${lerp(255,245,gold)},${lerp(255,197,gold)},${lerp(255,66,gold)})`:'#fff';X.shadowColor=gold>0?'#F5C542':'#fff';X.shadowBlur=20+30*gold;X.beginPath();
    const prog=clamp(u/0.6);
    for(let i=0;i<=200;i++){const k=i/200;if(k>prog*1.2&&gold===0)break;const xx=lerp(k*W,540+Math.cos(Math.PI*(1-k))*300,smile);const bl=c=>Math.exp(-Math.pow((k-c)*60,2));let yy=1150-(bl(0.2)*180-bl(0.23)*90+bl(0.45)*170-bl(0.48)*80)*(1-smile);yy=lerp(yy,1050+Math.sin(Math.PI*k)*160,smile);if(i===0)X.moveTo(xx,yy);else X.lineTo(xx,yy)}X.stroke();X.restore()}
  if(u>0.6&&u<1.9){const k=eout((u-0.6)/0.12);txt('HE DIED…',W/2,560,130,'#fff',{scale:lerp(1.6,1,k),alpha:k*clamp((1.9-u)/0.2),weight:900})}
  if(u>1.0&&u<1.9){const k=back(clamp((u-1.0)/0.25));txt('…AND SMILED.',W/2,740,124,G.dawn,{scale:k,weight:900,glow:'#F5C542',gb:50,alpha:clamp((1.9-u)/0.2)});glow(540,1050,700*clamp((u-1)/0.5),'rgba(245,197,66,.35)')}
  if(u>1.4){ // door of light, fly through
    const k=ease(seg01(u,1.4,d));const z=lerp(0.3,9,Math.pow(k,2));
    X.save();X.globalAlpha=clamp((u-1.4)/0.3);X.translate(540,1000);X.scale(z,z);X.shadowColor='#FFE7A8';X.shadowBlur=80;X.fillStyle='#FFF4D6';X.beginPath();X.moveTo(-90,140);X.lineTo(-90,-60);X.arc(0,-60,90,Math.PI,0);X.lineTo(90,140);X.closePath();X.fill();X.restore();
    if(z>4){X.save();X.globalAlpha=clamp((z-4)/3);roomDawn(t);X.restore()}
    X.globalAlpha=clamp((u-2.4)/0.3);txt("Watch till the end. This could be YOU.",W/2,170,40,'#fff',{weight:800,stroke:8,sc:'#5b3a1e'});X.globalAlpha=1;
  }
};
S.s1=(u,d,t)=>{const [cx,cy]=roomDawn(t);thread(cx,cy,900,0,t,clamp(u/0.5));X.save();X.lineWidth=2;X.globalAlpha=.6;thread(cx+6,cy,880,0,t+1,clamp(u/0.8));X.restore();
  X.globalAlpha=clamp(1-u/0.8);txt("Watch till the end. This could be YOU.",W/2,170,40,'#fff',{weight:800,stroke:8,sc:'#5b3a1e'});X.globalAlpha=1;
  const k=clamp((u-0.4)/0.5);txt('اقْرَأْ',W/2,lerp(800,620,k),110,'#14532D',{font:'Amiri',weight:700,alpha:Math.sin(k*Math.PI),glow:'rgba(255,220,120,.9)'});};
S.s2=(u,d,t)=>{
  bg('#FFF1DC','#FBD9B4');
  // bunting
  for(let r=0;r<2;r++){X.strokeStyle='#c9a27a';X.lineWidth=3;X.beginPath();X.moveTo(0,260+r*120);X.quadraticCurveTo(540,360+r*120,W,260+r*120);X.stroke();for(let i=0;i<12;i++){const bx=i*95+40,by=260+r*120+Math.sin(i/11*Math.PI)*90;X.fillStyle=[G.sage,G.dawn,'#F59E0B',G.turq,'#F472B6'][(i+r)%5];X.beginPath();X.moveTo(bx-28,by);X.lineTo(bx+28,by);X.lineTo(bx,by+55+Math.sin(t*3+i)*4);X.fill()}}
  X.fillStyle='#E9C49B';X.fillRect(0,1350,W,600);
  txt('YATIM COMMUNITY',W/2,560,56,'#92400E',{weight:900,ls:6});
  // man sitting with kids
  const [cx,cy]=chest(420,1640,1.0,'sit');
  const give=Math.sin(t*2.5)>0;
  person(420,1640,1.0,{pose:'sit',col:'#0F766E',aL:2.4,elL:0.8,aR:give?-1.4:2.3,elR:give?0.2:0.9});
  const kidsC=['#F59E0B','#EC4899','#3B82F6','#22C55E','#A855F7'];
  [[150,1700,1.0],[700,1660,1.15],[850,1700,0.95],[600,1760,0.9],[960,1740,1.05]].forEach(([kx,ky,ks],i)=>{const jump=i===1?Math.abs(Math.sin(t*5))*60:Math.abs(Math.sin(t*3+i))*10;kid(kx,ky-jump,ks,{col:kidsC[i],aL:i===1?2.8:0.4+0.3*Math.sin(t*4+i),aR:i===1?-2.8:-0.4,hair:'#3b2a1a'});
    if(i>0){X.save();X.translate(kx+30,ky-jump-140*ks);paper(true);X.fillStyle=['#EF4444','#2563EB','#16A34A','#9333EA','#F97316'][i];rr(-30,-30,60,60,12);X.fill();X.restore()}});
  // rising hearts -> threads
  for(let i=0;i<12;i++){const k=((t*0.4+rnd(i))%1);const hx=200+rnd(i+3)*700,hy=1400-k*900;X.globalAlpha=Math.sin(k*Math.PI);txt('♥',hx,hy,46,'#F472B6',{font:'DejaVu Sans',weight:500})}X.globalAlpha=1;
  thread(cx,cy,900,0,t,1);
  const sk=back(clamp((u-0.4)/0.25));X.save();X.translate(W/2,760);X.rotate(-0.06);X.scale(sk,sk);paper(true);X.fillStyle='#fff';rr(-300,-55,600,110,30);X.fill();paper(false);txt('Weekends = Orphans 💛',0,2,46,'#0F766E',{weight:900,font:'Mont, "Noto Color Emoji"'});X.restore();
};
S.s3=(u,d,t)=>{
  const p=u/d;bg('#0F1A3A','#1E2A55');for(let i=0;i<40;i++)circ(rnd(i)*W,rnd(i+5)*700,1.5+rnd(i+2)*2,`rgba(255,255,255,${.5+.5*Math.sin(t*2+i)})`);circ(860,240,60,'#FFF7D6');glow(860,240,200,'rgba(255,247,214,.35)');
  // house & door
  X.save();paper(true);X.fillStyle='#3B4A7A';rr(140,700,800,800,10);X.fill();X.fillStyle='#2A365F';X.beginPath();X.moveTo(100,720);X.lineTo(540,420);X.lineTo(980,720);X.fill();X.restore();
  const open=clamp((p-0.6)/0.2);
  X.fillStyle='#FFE7A8';rr(440,1080,200,420,6);X.fill();
  X.save();X.translate(440,1080);X.scale(1-open*0.85,1);X.fillStyle='#7C4A1E';rr(0,0,200,420,6);X.fill();circ(170,220,10,G.honey);X.restore();
  X.fillStyle='rgba(255,230,160,.5)';X.fillRect(250,860,120,120);X.fillRect(710,860,120,120);
  if(open>0){glow(540,1300,400*open,'rgba(255,220,150,.8)');wife(540,1500,0.85,open,t)}
  X.fillStyle='#141c3a';X.fillRect(0,1500,W,450);
  // envelope sliding under door
  const ek=clamp((p-0.25)/0.3);if(p<0.65){X.save();X.translate(lerp(380,540,ek),1495);paper(true);X.fillStyle='#FFF8EC';rr(-50,-14,100,28,4);X.fill();X.restore()}
  // hooded man walking away
  const wx=p<0.3?lerp(220,360,p/0.3):lerp(360,-200,clamp((p-0.42)/0.45));
  person(wx,1720,0.95,{pose:p>0.4?'walk':'stand',t,col:'#1F2937',legs:'#111827',skin:'#1F2937',hair:'#1F2937',aR:p<0.4?-1.2:0.3,elR:0.4,aL:0.2,flip:p>0.4});
  X.globalAlpha=clamp((p-0.15)/0.1);txt('Right hand gives.',W/2,300,58,'#FFF8EC',{weight:900,stroke:8,sc:'#0F1A3A'});txt('Left hand never knows.',W/2,380,44,'rgba(255,248,236,.6)',{weight:500,alpha:clamp((p-0.35)/0.1)});X.globalAlpha=1;
  if(open>0.5){txt('🤍',540,1000,70,'#fff',{font:'"Noto Color Emoji"',weight:500,scale:back(clamp((open-0.5)*3))})}
};
S.s4=(u,d,t)=>{
  bg('#BDE7FF','#FFF1DC');sun(820,300,80);
  const ev=TL.ev, tt=tS('s4')+u;
  X.fillStyle='#CDE8B0';X.fillRect(0,1400,W,600);
  const items=[['hyper','#EF4444',290,1520,0.72,'BUGATTI.'],['limo','#1F2937',770,1690,0.6,'ROLLS-ROYCE.'],['villa',null,540,1330,0.95,'VILLA.']];
  [2,0,1].forEach(i=>{const [k,col,x,y,s,label]=items[i];const td=ev.drops[i];if(tt<td-0.4)return;
    const fall=clamp((tt-(td-0.35))/0.35);let yy=lerp(-900,y,ein(fall));let sq=1;if(tt>td){const b=tt-td;sq=1-0.18*Math.exp(-b*10)*Math.cos(b*30)}
    X.save();X.translate(x,yy);X.scale(1/sq,sq);if(k==='villa')villa(0,0,s);else car(0,0,s,col,k);X.restore();
    if(tt>td)dust(x,y,clamp((tt-td)/1.0),24,520);
    if(tt>td-0.1){const lk=clamp((tt-td+0.1)/0.25);const ly=lerp(-100,330+i*140,back(lk));txt(label,W/2,ly,i===2?130:110,'#1F2937',{weight:900,stroke:10,sc:'#fff'});stamp('GIVEN.',W/2+330,375+i*140,tt-(ev.given+i*0.3),'#16A34A',48,-0.12)}
  });
  if(tt>ev.given+0.6){const k=clamp((tt-ev.given-0.6)/0.3);X.save();X.globalAlpha=k;X.translate(540,980);paper(true);X.fillStyle='#16A34A';rr(-260,-50,520,100,16);X.fill();paper(false);txt('🏠 ORPHAN HOME',0,2,48,'#fff',{weight:900,font:'Mont, "Noto Color Emoji"'});X.restore();
    for(let i=0;i<4;i++){const kx=lerp(100,420+i*60,clamp((tt-ev.given-0.6-i*0.1)/0.8));kid(kx,1440,0.7,{pose:'walk',t:t+i,col:['#F59E0B','#EC4899','#3B82F6','#22C55E'][i]})}}
  // man giving keys
  const gv=tt>ev.given;
  person(560,1650,0.8,{col:'#0F766E',aR:gv?-1.5:-0.2,elR:gv?0.2:0,aL:0.2});
  if(gv){const kk=clamp((tt-ev.given)/0.6);txt('🔑',lerp(640,420,kk),lerp(1400,1340,kk)-Math.sin(kk*Math.PI)*120,60,'#000',{font:'"Noto Color Emoji"',weight:500})}
  const [cx,cy]=chest(560,1650,0.8);thread(cx,cy,750,0,t,1);X.save();X.globalAlpha=.7;thread(cx+5,cy,740,0,t+.7,1);X.restore();
  const wl=Math.max(0,48_000_000-Math.floor(clamp((tt-ev.given)/1.5)*47_000_000));
  txt('Wealth: $'+wl.toLocaleString('en-US'),40,120,40,'#6B7280',{align:'left',weight:800});
  txt('Akhirah: +∞',W-40,120,46,'#B45309',{align:'right',weight:900,glow:'rgba(245,197,66,.8)',scale:1+0.05*Math.sin(t*6)});
};
S.s5=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s5')+u;const si=[0,1,2,3].filter(i=>tt>=ev.checks[i]-0.15).pop()??0;
  if(si===0){bg('#FFF8EC','#F3E3C3');X.save();X.translate(540,900);X.rotate(-0.05);paper(true);X.fillStyle='#FFFDF5';rr(-330,-380,660,760,16);X.fill();paper(false);txt('DEBTS',0,-310,56,'#7C2D12',{weight:900});
      for(let i=0;i<5;i++){X.strokeStyle='#d6c7a1';X.lineWidth=3;X.beginPath();X.moveTo(-280,-200+i*110);X.lineTo(280,-200+i*110);X.stroke();txt(['Ali  RM500','Bank  RM20k','Abu  RM1k','Car  RM80k','Shop  RM300'][i],-270,-235+i*110,36,'#57534e',{align:'left',weight:500});stamp('✔ PAID',170,-235+i*110,u-0.1-i*0.12,'#16A34A',40,-0.1)}X.restore()}
  else if(si===1){bg('#0B1640','#1A2B6B');circ(800,320,80,'#FFF7D6');circ(830,300,70,'#0E1A4C');for(let i=0;i<50;i++)circ(rnd(i)*W,rnd(i+3)*900,1.5+rnd(i)*2,`rgba(255,255,255,${.4+.5*Math.sin(t*3+i)})`);
    X.fillStyle='#1C2A5E';X.fillRect(0,1350,W,600);txt('3:00 AM',W/2,560,64,'#C7D2FE',{weight:900,ls:6});
    X.save();X.translate(540,1450);paper(true);X.fillStyle='#7BAE7F';rr(-260,-30,520,90,10);X.fill();X.fillStyle='#F5F5F4';X.beginPath();X.ellipse(-20,-60,170,70,0,Math.PI,0);X.fill();circ(-180,-20,48,'#c99a78');X.fillStyle='#fff';X.beginPath();X.ellipse(-190,-40,46,30,0,Math.PI,0);X.fill();X.restore();glow(540,1350,400,'rgba(199,210,254,.25)')}
  else if(si===2){bg('#FFD79A','#FFF3DC');sun(820,520,110);X.fillStyle='#EAC39E';X.fillRect(0,1350,W,600);txt('DHUHA',W/2,300,64,'#B45309',{weight:900,ls:10});
    X.save();X.fillStyle='rgba(255,236,170,.6)';X.beginPath();X.moveTo(820,520);X.lineTo(200,1500);X.lineTo(700,1600);X.fill();X.restore();
    X.save();paper(true);X.fillStyle='#7BAE7F';rr(220,1420,640,160,10);X.fill();X.restore();person(540,1500,1.0,{col:'#F5F5F4',legs:'#E7E5E4',cap:'#fff',aL:2.9,aR:-2.9,elL:0.5,elR:-0.5})}
  else {bg('#BFE6FF','#FFF8EC');X.save();paper(true);X.fillStyle='#F8FAFC';rr(240,700,600,700,10);X.fill();X.fillStyle=G.emer;X.beginPath();X.arc(540,700,240,Math.PI,0);X.fill();X.fillStyle='#F8FAFC';rr(110,450,70,950,10);X.fill();rr(900,450,70,950,10);X.fill();X.fillStyle=G.emer;X.beginPath();X.moveTo(100,450);X.lineTo(145,330);X.lineTo(190,450);X.fill();X.beginPath();X.moveTo(890,450);X.lineTo(935,330);X.lineTo(980,450);X.fill();X.restore();
    X.fillStyle='#7C4A1E';rr(470,1100,140,300,70);X.fill();X.fillStyle='#CDE8B0';X.fillRect(0,1400,W,600);
    const wk=clamp((tt-ev.checks[3])/1.0);person(lerp(150,520,wk),1640,0.8,{pose:'walk',t,col:'#F5F5F4',legs:'#E7E5E4',cap:'#fff'});for(let i=0;i<5;i++)if(wk>i*0.2)circ(lerp(150,520,i*0.2)+20,1660,8,G.honey)}
  // checklist
  const L=['Debt-free','Tahajjud','Dhuha','Masjid'];X.save();X.translate(60,1060);
  X.fillStyle='rgba(255,255,255,.85)';rr(-20,-70,420,330,24);X.fill();
  L.forEach((w,i)=>{const on=tt>=ev.checks[i];txt((on?'✔ ':'◻ ')+w,10,-20+i*72,44,on?'#16A34A':'#9CA3AF',{align:'left',weight:900,font:'Mont, DejaVu Sans',scale:on&&tt-ev.checks[i]<0.2?1.1:1})});X.restore();
};
S.s6=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s6')+u, dead=tt>ev.flatdeath;
  bg('#E6EEF5','#CAD7E3');X.save();paper(true);X.fillStyle='#F8FAFC';rr(600,250,380,460,16);X.fill();X.restore();X.fillStyle='#BFE6FF';X.fillRect(620,270,340,420);
  // bed
  X.save();paper(true);X.fillStyle='#94A3B8';rr(120,1250,760,40,10);X.fill();X.fillStyle='#F8FAFC';rr(140,1120,720,140,40);X.fill();X.fillStyle='#BFDBFE';rr(320,1100,560,120,40);X.fill();X.restore();
  circ(230,1110,60,'#c99a78');X.fillStyle='#1a1410';X.beginPath();X.ellipse(215,1085,55,40,0,Math.PI*0.9,Math.PI*1.9);X.fill();
  // raised finger
  if(!dead||tt-ev.flatdeath<0.5){X.strokeStyle='#c99a78';X.lineWidth=18;X.lineCap='round';X.beginPath();X.moveTo(420,1110);X.lineTo(420,1030);X.stroke();X.lineWidth=10;X.beginPath();X.moveTo(420,1030);X.lineTo(420,960);X.stroke()}
  txt('لَا إِلٰهَ إِلَّا اللّٰه',420,880,62,'#14532D',{font:'Amiri',weight:700,alpha:clamp(u/0.6),glow:'rgba(255,220,120,.9)'});
  // family
  kid(950,1600,1.3,{col:'#0EA5E9',aL:2.2,aR:2.4,elL:0.9,elR:0.9});phone(930,1360,40,70,0,(w,h)=>{X.fillStyle='#FEF3C7';X.fillRect(-w/2,-h/2,w,h)});
  wife(760,1620,0.9,1,t);person(130,1650,0.85,{col:'#57534E',aL:2.6,aR:-2.6,elL:0.8,elR:-0.8});
  // monitor
  X.save();X.translate(120,520);paper(true);X.fillStyle='#111827';rr(0,0,340,220,16);X.fill();paper(false);X.strokeStyle='#22C55E';X.lineWidth=4;X.beginPath();
  for(let i=0;i<=100;i++){const k=i/100;const ph=(k*2-t*0.9)%1;const bl=v=>Math.exp(-Math.pow(v*40,2));let yy=110-(dead?0:bl(((ph+1)%1)-0.5)*70);if(i===0)X.moveTo(20+k*300,yy);else X.lineTo(20+k*300,yy)}X.stroke();X.restore();
  if(dead){const k=clamp((tt-ev.flatdeath)/1.2);X.fillStyle=`rgba(255,244,214,${k*0.85})`;X.fillRect(0,0,W,H);glow(540,500,900*k,'rgba(255,220,140,.6)')}
};
function mercyAngel(x,y,s,a,t,i){X.save();X.translate(x,y);X.scale(s,s);X.globalAlpha*=a;
  for(const side of [-1,1]){X.strokeStyle='rgba(255,236,180,.55)';X.lineWidth=6;for(let f=0;f<5;f++){X.beginPath();X.moveTo(side*40,-260);X.quadraticCurveTo(side*(160+f*20),-360-f*20+Math.sin(t*3+i)*15,side*(90+f*30),-120+f*25);X.stroke()}}
  const g=X.createLinearGradient(0,-380,0,40);g.addColorStop(0,'rgba(255,255,255,.95)');g.addColorStop(1,'rgba(255,220,150,0)');X.fillStyle=g;X.beginPath();X.ellipse(0,-180,70,220,0,0,7);X.fill();
  glow(0,-330,110,'rgba(255,250,230,1)');circ(0,-330,42,'#FFFDF3');X.restore()}
S.s7=(u,d,t)=>{
  const p=u/d;bg('#FFF4D6','#F9D99A');glow(540,300,1100,'rgba(255,255,255,.8)');
  for(let i=0;i<60;i++){X.strokeStyle=`rgba(255,255,255,${.12+.08*Math.sin(t+i)})`;X.lineWidth=4;X.beginPath();X.moveTo(540,-100);X.lineTo(540+Math.cos(i/60*Math.PI)*1600,1600*Math.sin(i/60*Math.PI));X.stroke()}
  // rows of angels descending
  for(let r=0;r<3;r++)for(let c=0;c<5;c++){const i=r*5+c;const dk=eout(clamp((p-r*0.08-c*0.02)/0.4));const ax=120+c*210+(r%2)*60,ay=lerp(-200,560+r*260,dk)+Math.sin(t*1.5+i)*12;mercyAngel(ax,ay,0.75-r*0.12,dk*(0.95-r*0.2),t,i)}
  // soul rising gently, smiling body language
  const rise=ease(seg01(p,0.25,1));
  X.save();X.globalAlpha=0.85;person(540,lerp(1750,1350,rise),0.95,{ghost:true,col:'rgba(255,255,255,.9)',legs:'rgba(255,255,255,.8)',skin:'rgba(255,255,255,.95)',hair:'rgba(255,255,255,.4)',aL:0.9+0.1*Math.sin(t*2),aR:-0.9-0.1*Math.sin(t*2),elL:-0.3,elR:0.3});X.restore();
  glow(540,lerp(1500,1100,rise),300,'rgba(255,240,200,.7)');
  // shroud of light & scent mist
  for(let i=0;i<24;i++){const a2=t*0.8+i/24*Math.PI*2;circ(540+Math.cos(a2)*240,lerp(1500,1100,rise)+Math.sin(a2)*90,6,'rgba(251,191,36,.7)')}
  const vk=clamp((p-0.15)/0.2);
  txt('يَا أَيَّتُهَا النَّفْسُ الْمُطْمَئِنَّةُ',W/2,230,74,'#7C2D12',{font:'Amiri',weight:700,alpha:vk,glow:'rgba(255,255,255,.9)'});
  txt('"O reassured soul… return to your Lord,',W/2,320,34,'#92400E',{weight:800,alpha:vk});txt('well-pleased and pleasing." (89:27-28)',W/2,368,34,'#92400E',{weight:800,alpha:vk});
};
S.s8=(u,d,t)=>{
  const sc=TL.scenes.s8, tt=sc.start+u;const a=sgT('s8',0),b=sgT('s8',1);
  const cuts=[sc.start,(a.start+a.end)/2,b.start-0.1,(b.start+b.end)/2,sc.end];const shot=[0,1,2,3].filter(i=>tt>=cuts[i]).pop();const k=(tt-cuts[shot])/(cuts[shot+1]-cuts[shot]);
  if(shot===0){bg('#E8DCC8','#CDBB9C');X.save();paper(true);X.fillStyle='#A8A29E';rr(260,420,560,1180,30);X.fill();X.restore();X.save();X.translate(540,1010);X.rotate(Math.PI/2);kafan(0,0,2.4,1);X.restore();glow(540,1010,500,'rgba(255,230,160,.35)');
    X.strokeStyle='rgba(150,200,255,.8)';X.lineWidth=12;X.beginPath();X.moveTo(740,760);X.quadraticCurveTo(680,800,660,900);X.stroke();for(let i=0;i<24;i++){const dy=((t*600+i*60)%500);circ(640+Math.sin(i)*60,900+dy,5+rnd(i)*5,'rgba(170,215,255,.9)')}
    X.save();X.translate(820,700);X.rotate(-0.6);paper(true);X.fillStyle='#E7E5E4';rr(-60,-90,120,180,30);X.fill();X.restore()}
  else if(shot===1){bg('#F3EBDD','#E2D6C0');for(let i=0;i<6;i++){const fk=clamp(k*1.4-i*0.15);X.save();X.translate(540,960);X.scale(1,eout(fk));paper(true,6,18,'rgba(0,0,0,.25)');X.fillStyle=i%2?'#FFFDF7':'#F4F1EA';rr(-330+i*12,-560+i*30,660-i*24,1120-i*60,40);X.fill();X.restore()}X.globalAlpha=clamp(k*2-1);kafan(540,960,1.3);glow(540,960,400,'rgba(255,220,140,.4)');X.globalAlpha=1}
  else if(shot===2){bg('#FFE7C2','#F2D2A6');sun(820,300,70);for(let i=0;i<9;i++){X.fillStyle='#D6C7A9';rr(60+i*120,1250+((i%2)*40),60,110,30);X.fill()}
    const wx=lerp(-60,120,k);
    for(let r=0;r<3;r++)for(let i=0;i<9;i++){person(wx-200+i*150+r*70,1560+r*120,0.6+r*0.1,{pose:'walk',t:t+i*0.3+r,col:['#F5F5F4','#E7E5E4','#D6D3D1'][r],legs:'#A8A29E',skin:'#c99a78',cap:'#fff',aL:r===0?2.9:0.2,aR:r===0?-2.9:-0.2})}
    for(let i=0;i<4;i++)kid(wx+600+i*80,1860,1.0,{pose:'walk',t:t+i,col:['#F59E0B','#EC4899','#3B82F6','#22C55E'][i],aL:1.4,aR:-1.4});
    X.save();paper(true);X.fillStyle='#F8FAFC';rr(wx+80,1250,700,70,30);X.fill();X.fillStyle='#15803D';rr(wx+80,1225,700,50,20);X.fill();X.restore()}
  else {bg('#2b1d12','#1a120a');const close=clamp(k*1.1);const ow=lerp(520,0,close),oh=lerp(980,0,close);
    X.fillStyle='#3a2716';X.beginPath();X.moveTo(0,0);X.lineTo(W,0);X.lineTo(540+ow/2,960-oh/2);X.lineTo(540-ow/2,960-oh/2);X.fill();
    if(ow>2){X.fillStyle=grad('#FFE7C2','#F2C14E',960-oh/2,960+oh/2);X.fillRect(540-ow/2,960-oh/2,ow,oh)}
    glow(540,1500,500,'rgba(245,197,66,.35)');}
};
S.s9=(u,d,t)=>{const p=u/d;grave(t);const rise=eout(seg01(p,0,0.6));angels(t,rise,clamp((p-0.45)/0.12),lerp(800,0,rise));
  glow(540,1560,320,'rgba(245,197,66,.45)');kafanSit(540,1650,0.9,t);
  if(p>0.5){const k=clamp((p-0.5)/0.3);txt('MUNKAR & NAKIR',W/2,lerp(1100,1000,k),66,'#93c5fd',{weight:500,ls:16,glow:'#3b82f6',alpha:k})}};
function kafanSit(x,y,s,t){X.save();X.translate(x,y);X.scale(s,s);X.shadowColor='rgba(245,197,66,.9)';X.shadowBlur=40;X.fillStyle='#FFF8E7';X.beginPath();X.moveTo(-120,0);X.quadraticCurveTo(-130,-260,-60,-330);X.lineTo(60,-330);X.quadraticCurveTo(130,-260,120,0);X.fill();X.beginPath();X.ellipse(0,-400,62,72,0,0,7);X.fill();X.restore()}
S.s10=(u,d,t)=>{
  const sc=TL.scenes.s10, tt=sc.start+u, ev=TL.ev;
  const na=[0,1,2].filter(i=>tt>=ev.ans[i]).length;
  grave(t);angels(t,1-na*0.15,1);
  if(na>0){const lv=na/3;glow(540,1300,700+500*lv,`rgba(245,197,66,${.25+.3*lv})`);X.fillStyle=`rgba(255,236,170,${.1*na})`;X.fillRect(0,0,W,H)}
  const qi=[0,1,2].filter(i=>tt>=ev.qs[i]).pop();const lq=qi!=null?tt-ev.qs[qi]:9;const ai=[0,1,2].filter(i=>tt>=ev.ans[i]).pop();const la=ai!=null?tt-ev.ans[ai]:9;
  if(lq<0.7){const r=eout(lq/0.7)*1100;X.strokeStyle=`rgba(96,165,250,${1-lq/0.7})`;X.lineWidth=26*(1-lq/0.7);X.beginPath();X.arc(540,400,r,0,7);X.stroke()}
  if(la<0.8){const r=eout(la/0.8)*1300;X.strokeStyle=`rgba(253,224,71,${1-la/0.8})`;X.lineWidth=40*(1-la/0.8);X.beginPath();X.arc(540,1300,r,0,7);X.stroke();if(la<0.08){X.fillStyle='rgba(255,240,180,.4)';X.fillRect(0,0,W,H)}}
  kafanSit(540,1650,0.9,t);glow(540,1450,300,'rgba(245,197,66,.5)');
  // deed shields
  ['📖','🧒','✉️','🕌'].forEach((e,i)=>{if(na<1)return;const a2=i/4*Math.PI*2+t*0.5;const sx=540+Math.cos(a2)*320,sy=1350+Math.sin(a2)*150;X.save();X.globalAlpha=clamp((tt-ev.ans[0])/0.4);glow(sx,sy,90,'rgba(253,224,71,.8)');circ(sx,sy,62,'rgba(255,248,220,.9)');txt(e,sx,sy+4,62,'#000',{font:'"Noto Color Emoji"',weight:500});X.restore()});
  const answering=ai!=null&&(qi==null||ev.ans[ai]>ev.qs[qi]);
  if(qi!=null&&!answering){const q=TL.segs[sc.segs[qi*2]].cap.split('|');const k=clamp(lq/0.18);txt(q[0],W/2,760,160,'#E8E4D9',{font:'Amiri',weight:700,scale:lerp(1.7,1,eout(k)),alpha:k,glow:'#3b82f6',gb:50});txt(q[1],W/2,940,56,'#bfdbfe',{weight:800,alpha:clamp((lq-0.2)/0.2),stroke:8,sc:'#05060a'})}
  if(answering){const w=['ALLAH.','ISLAM.','MUHAMMAD ﷺ.'][ai];const sub=['My Lord is Allah.','My religion is Islam.','My prophet is Muhammad ﷺ'][ai];const k=back(clamp(la/0.25));
    txt(w,W/2,800,ai===2?120:170,'#FDE68A',{weight:900,font:'Mont, Amiri',scale:k,glow:'#F59E0B',gb:60,stroke:6,sc:'#7C2D12'});txt(sub,W/2,990,50,'#FFF8EC',{weight:800,alpha:clamp((la-0.15)/0.2),stroke:8,sc:'#1a120a'})}
};
S.s11=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s11')+u;const open=ease(clamp(u/1.4));
  gardenBG(t,open);
  // grave walls sliding away
  X.save();X.globalAlpha=1-open*0.2;X.fillStyle='#120d08';X.fillRect(-open*700,0,520,H);X.fillRect(W-520+open*700,0,520,H);X.restore();
  // golden door
  const dk=clamp((tt-ev.door)/0.8);
  X.save();X.translate(540,1080);paper(true,0,60,'rgba(255,200,80,.9)');X.fillStyle='#FFF4D6';X.beginPath();X.moveTo(-170,300);X.lineTo(-170,-120);X.arc(0,-120,170,Math.PI,0);X.lineTo(170,300);X.closePath();X.fill();paper(false);
  glow(0,0,400*dk+60,'rgba(255,255,240,1)',dk);
  X.fillStyle='#D97706';X.save();X.scale(1-dk*0.95,1);X.beginPath();X.moveTo(-160,300);X.lineTo(-160,-120);X.arc(0,-120,160,Math.PI,0);X.lineTo(160,300);X.closePath();X.fill();X.strokeStyle='#FDE68A';X.lineWidth=8;X.stroke();X.restore();X.restore();
  // thread pulling
  thread(540,1600,560,0,t,clamp(1-dk));
  for(let i=0;i<30&&dk>0;i++){const a2=rnd(i)*Math.PI-Math.PI;const r=dk*700*rnd(i+2);X.strokeStyle=`rgba(255,240,200,${.4*(1-dk*0.5)})`;X.lineWidth=6;X.beginPath();X.moveTo(540,1000);X.lineTo(540+Math.cos(a2)*r*1.5,1000+Math.sin(a2)*r);X.stroke()}
  person(540,1750,0.9,{col:'#FFFFFF',legs:'#F5F5F4',cap:'#fff',aL:0.4,aR:-0.4,flip:false});
  if(u>0.6){const k=clamp((u-0.6)/0.4);txt('"My servant has',W/2,330,64,'#7C2D12',{font:'Amiri',weight:700,alpha:k*clamp((tt<ev.door?1:1-(tt-ev.door)/0.5)),glow:'#fff'});txt('spoken the truth."',W/2,420,64,'#7C2D12',{font:'Amiri',weight:700,alpha:k*clamp((tt<ev.door?1:1-(tt-ev.door)/0.5)),glow:'#fff'})}
  if(tt>ev.door+0.4)txt('As far as the eye can see.',W/2,360,50,'#065F46',{weight:900,alpha:clamp((tt-ev.door-0.4)/0.3),stroke:8,sc:'#fff'});
};
S.s12=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s12')+u;gardenBG(t,1);
  const sw=clamp((tt-ev.swipe)/0.35);
  if(sw<1){X.save();X.translate(540+sw*1100,900);X.rotate(sw*0.4);paper(true,14,40);X.fillStyle='#fff';rr(-400,-520,800,1040,40);X.fill();paper(false);
    X.save();rr(-380,-500,760,640,30);X.clip();X.fillStyle=grad('#38BDF8','#BAE6FD',-500,140);X.fillRect(-380,-500,760,640);X.fillStyle='#0EA5E9';X.fillRect(-380,0,760,140);X.fillStyle='#FDE68A';X.beginPath();X.ellipse(0,40,260,60,0,0,7);X.fill();X.strokeStyle='#7C4A1E';X.lineWidth=14;X.beginPath();X.moveTo(40,40);X.quadraticCurveTo(60,-120,20,-220);X.stroke();for(let k=0;k<5;k++){X.fillStyle='#16A34A';X.beginPath();X.ellipse(20+Math.cos(k*1.25)*70,-220+Math.sin(k*1.25)*28,80,20,k*1.25,0,7);X.fill()}X.restore();
    txt('HOLIDAY ISLAND',0,220,58,'#0F172A',{weight:900});txt('★★★★★  5D4N',0,290,36,'#F59E0B',{weight:800,font:'Mont, DejaVu Sans'});X.fillStyle='#F43F5E';rr(-220,350,440,100,50);X.fill();txt('✈ BOOK NOW',0,402,44,'#fff',{weight:900,font:'Mont, DejaVu Sans'});
    X.restore();if(tt>ev.swipe-0.1)txt('❌',540+sw*1100,500,150,'#000',{font:'"Noto Color Emoji"',weight:500,alpha:1-sw})}
  if(sw>0.5){const k=back(clamp((sw-0.5)/0.4+(tt-ev.swipe-0.35)/0.5));X.save();X.translate(W/2,330);X.scale(k,k);paper(true);X.fillStyle='rgba(255,255,255,.9)';rr(-360,-60,720,120,60);X.fill();paper(false);txt('Garden of Jannah ✔',0,2,54,'#047857',{weight:900,font:'Mont, DejaVu Sans'});X.restore()}
};
S.s13=(u,d,t)=>{
  const p=u/d;
  X.save();X.beginPath();X.rect(0,0,W,900);X.clip();bg('#FFF8EC','#F3E3C3');X.fillStyle='#E9D5B5';X.fillRect(0,720,W,200);
  X.save();paper(true);X.fillStyle='#7BAE7F';rr(150,760,780,70,10);X.fill();X.restore();
  person(350,800,0.7,{pose:'sit',col:'#0F766E',aL:2.7,aR:-2.7,elL:1.2,elR:-1.2});wife(640,810,0.6,1,t);kid(860,800,1.0,{col:'#F59E0B',aL:2.7,aR:-2.7,elL:1.2,elR:-1.2});
  X.save();X.translate(540,130);paper(true);X.fillStyle='#fff';rr(-330,-55,660,110,24);X.fill();paper(false);const pr=clamp(p/0.5);const done=pr>=1;
  txt(done?"Du'a: DELIVERED ✔":"Sending du'a…",0,-18,34,done?'#16A34A':'#334155',{weight:800,font:'Mont, DejaVu Sans'});X.fillStyle='#e5e7eb';rr(-280,18,560,18,9);X.fill();X.fillStyle='#16A34A';rr(-280,18,560*pr,18,9);X.fill();txt(Math.floor(pr*100)+'%',300,28,24,'#334155',{weight:800});X.restore();
  X.restore();
  X.fillStyle='#fff';X.fillRect(0,896,W,8);
  X.save();X.beginPath();X.rect(0,904,W,1016);X.clip();X.translate(0,500);gardenBG(t,1);X.restore();
  X.save();X.beginPath();X.rect(0,904,W,1016);X.clip();
  person(540,1760,0.8,{pose:'sit',col:'#fff',legs:'#F5F5F4',cap:'#fff',aL:2.6,aR:-2.6,elL:0.5,elR:-0.5});
  for(let i=0;i<8;i++){const k=((u*0.8+i*0.125)%1);const px=300+rnd(i)*480,py=lerp(900,1650,ein(k));glow(px,py,60,'rgba(253,224,71,.9)');X.fillStyle='#FBBF24';rr(px-22,py-22,44,44,8);X.fill();X.strokeStyle='#fff';X.lineWidth=4;X.beginPath();X.moveTo(px,py-22);X.lineTo(px,py+22);X.moveTo(px-22,py);X.lineTo(px+22,py);X.stroke()}
  const cnt=Math.floor(Math.pow(p,2)*9999)+1;txt('Rewards received: +'+cnt.toLocaleString('en-US')+(p>0.9?' … ∞':''),W/2,1850,44,'#065F46',{weight:900,stroke:8,sc:'#fff'});
  X.restore();
};
S.s14=(u,d,t)=>{
  gardenBG(t,1);
  // reclining under tree by river
  person(300,1720,1.0,{pose:'sit',col:'#fff',legs:'#F5F5F4',cap:'#fff',aL:2.9,aR:0.5,elL:1.3,slump:-0.25});
  X.save();X.translate(820,520);X.strokeStyle='#B45309';X.lineWidth=8;X.beginPath();X.moveTo(-80,-120);X.lineTo(80,-120);X.lineTo(10,0);X.lineTo(80,120);X.lineTo(-80,120);X.lineTo(-10,0);X.closePath();X.stroke();
  X.fillStyle='#FBBF24';X.beginPath();X.moveTo(-60,100);X.lineTo(60,100);X.lineTo(0,40);X.fill();for(let i=0;i<6;i++){const fy=((t*120+i*20)%110);circ(0,-5+fy,4,'#FDE68A')}glow(0,0,160,'rgba(253,224,71,.5)');X.restore();
  const tb=TL.ev.busy-tS('s14');
  stamp('BUSY.',W/2,1000,u-tb,'#16A34A',170,-0.15);
  if(u>tb+0.3)txt('enjoying 😊',W/2,1150,64,'#065F46',{weight:900,font:'Mont, "Noto Color Emoji"',scale:back(clamp((u-tb-0.3)/0.25)),stroke:8,sc:'#fff'});
};
S.cta=(u,d,t)=>{
  const p=u/d;bg('#0E2A2A','#123B33');glow(540,1700,900,'rgba(16,185,129,.35)');motes(t,50,'rgba(253,224,71,1)',.6);
  const k=eout(clamp(p/0.2));
  X.save();X.globalAlpha=k;X.shadowColor='rgba(245,197,66,1)';X.shadowBlur=30;X.strokeStyle='#FFE08A';X.lineWidth=7;rr(340,500,400,700,60);X.stroke();X.restore();
  const bat=Math.min(100,Math.floor(clamp((p-0.1)/0.5)*100));
  X.save();X.translate(540,700);X.globalAlpha=k;X.strokeStyle='#fff';X.lineWidth=5;rr(-90,-34,180,68,12);X.stroke();X.fillStyle='#fff';X.fillRect(90,-12,12,24);X.fillStyle='#22C55E';rr(-82,-26,164*bat/100,52,6);X.fill();txt(bat+'%',0,90,48,'#22C55E',{weight:900});X.restore();
  txt('⚡',540,950,120,'#FDE68A',{font:'DejaVu Sans',weight:500,alpha:k*(.6+.4*Math.sin(t*6))});
  txt('Part 1: "Who will answer for you?" ↗',W/2,380,34,'rgba(255,255,255,.85)',{weight:800,alpha:k,font:'Mont, DejaVu Sans'});
  const tk=clamp((p-0.25)/0.15);
  txt('WILL YOUR DEATH',W/2,1360,92,'#FDE68A',{weight:900,scale:back(tk),alpha:tk,glow:'rgba(245,197,66,.7)'});
  txt('LOOK LIKE THIS?',W/2,1470,92,'#FDE68A',{weight:900,scale:back(tk),alpha:tk,glow:'rgba(245,197,66,.7)'});
  const ck=clamp((p-0.45)/0.15);
  X.save();X.globalAlpha=ck;X.translate(W/2,1640);X.fillStyle='rgba(255,255,255,.14)';X.strokeStyle='#FFE08A';X.lineWidth=4;rr(-260,-55,520,110,55);X.fill();X.stroke();txt('Comment: AMEEN 🤲',0,3,46,'#fff',{weight:900,font:'Mont, "Noto Color Emoji"'});X.restore();
  txt('Share = sadaqah jariyah 🤍',W/2,1780,34,'rgba(255,255,255,.8)',{weight:600,alpha:ck,font:'Mont, "Noto Color Emoji"'});
  if(u>d-0.9){const fk=clamp((u-(d-0.9))/0.8);X.fillStyle=`rgba(0,0,0,${fk})`;X.fillRect(0,0,W,H);X.save();X.globalAlpha=fk;X.strokeStyle='#F5C542';X.lineWidth=7;X.shadowColor='#F5C542';X.shadowBlur=40;X.beginPath();for(let i=0;i<=60;i++){const kk=i/60;const xx=540+Math.cos(Math.PI*(1-kk))*300,yy=1050+Math.sin(Math.PI*kk)*160;if(i===0)X.moveTo(xx,yy);else X.lineTo(xx,yy)}X.stroke();X.restore()}
};
