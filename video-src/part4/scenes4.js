// ===== PART 4: DU'A — scene overrides (helpers from scenes2/3) =====
function nightSky(t,a=1){X.save();X.globalAlpha*=a;bg('#0B1033','#3B2A6B');for(let i=0;i<90;i++)circ(rnd(i)*W,rnd(i+7)*H*0.8,1.2+rnd(i+3)*2.2,`rgba(255,255,255,${.35+.5*Math.sin(t*2+i*1.7)})`);
  circ(820,300,70,'#F3F4F6');circ(850,280,62,'#1a1748');glow(800,300,260,'rgba(196,181,253,.25)');X.restore()}
function lantern(x,y,s,t,label,a=1){X.save();X.translate(x+Math.sin(t*1.3+x)*8,y);X.rotate(Math.sin(t*1.1+y)*0.05);X.scale(s,s);X.globalAlpha*=a;
  glow(0,0,170,'rgba(251,191,36,.6)');X.fillStyle='#F59E0B';X.shadowColor='#FBBF24';X.shadowBlur=40;X.beginPath();X.moveTo(-60,-70);X.quadraticCurveTo(-90,0,-55,75);X.lineTo(55,75);X.quadraticCurveTo(90,0,60,-70);X.closePath();X.fill();X.shadowBlur=0;
  X.fillStyle='#FDE68A';X.beginPath();X.moveTo(-40,-55);X.quadraticCurveTo(-62,0,-38,60);X.lineTo(38,60);X.quadraticCurveTo(62,0,40,-55);X.closePath();X.fill();
  X.fillStyle='#B45309';rr(-50,-82,100,14,6);X.fill();rr(-44,72,88,12,6);X.fill();
  if(label)txt(label,0,4,26,'#7C2D12',{weight:900});X.restore()}
function hands(x,y,s,a=1,glw=0){X.save();X.translate(x,y);X.scale(s,s);X.globalAlpha*=a;
  if(glw>0)glow(0,-60,300*glw,'rgba(251,191,36,.8)',glw);
  for(const sd of [-1,1]){X.save();X.scale(sd,1);X.fillStyle='#C99A78';X.strokeStyle='#A47A5C';X.lineWidth=4;
    X.beginPath();X.moveTo(8,0);X.bezierCurveTo(30,30,140,40,190,-20);X.bezierCurveTo(210,-50,200,-110,180,-140);X.bezierCurveTo(170,-150,150,-140,150,-120);X.lineTo(150,-70);X.bezierCurveTo(120,-40,60,-40,8,-60);X.closePath();X.fill();X.stroke();
    X.fillStyle='#2b2f4a';rr(60,10,160,260,40);X.fill();X.restore()}
  X.restore()}
function man(x,y,s,o={}){person(x,y,s,{pose:'sit',col:'#E7E5E4',legs:'#D6D3D1',cap:'#fff',aL:2.6,aR:-2.6,elL:1.0,elR:-1.0,...o})}
// ---------------- HOOK ----------------
S.hook=(u,d,t)=>{
  const ev=TL.ev;bg('#000','#05050c');
  const rise=eout(clamp(u/0.9));const burst=clamp((u-ev.burst)/0.5);
  if(u>2.2){const k=ease(seg01(u,2.2,d));X.save();X.globalAlpha=k;nightSky(t);X.restore()}
  const hy=lerp(2200,1500,rise)-(u>2.2?ease(seg01(u,2.2,d))*900:0);
  hands(540,hy,1.4,1,burst);
  const orb=clamp((u-0.3)/0.7)*(1-burst*0.3);
  if(u>0.3){glow(540,hy-120,lerp(20,160,orb),'rgba(253,230,138,1)');circ(540,hy-120,lerp(4,40,orb)*(1-burst*0.5),'#FFF7D6')}
  if(burst>0&&burst<1){for(let i=0;i<24;i++){const a=i/24*Math.PI*2;X.strokeStyle=`rgba(253,230,138,${1-burst})`;X.lineWidth=6;X.beginPath();X.moveTo(540+Math.cos(a)*80*burst,hy-120+Math.sin(a)*80*burst);X.lineTo(540+Math.cos(a)*900*burst,hy-120+Math.sin(a)*900*burst);X.stroke()}
    X.strokeStyle=`rgba(253,230,138,${1-burst})`;X.lineWidth=20*(1-burst);X.beginPath();X.arc(540,hy-120,1000*eout(burst),0,7);X.stroke()}
  const s1="IF YOU MADE DU'A TODAY…";const n=Math.floor(clamp(u/0.8)*s1.length);
  txt(s1.slice(0,n),W/2,560,70,'#fff',{weight:900,alpha:u>2.6?clamp((3.2-u)/0.6):1});
  if(u>ev.burst){const k=back(clamp((u-ev.burst)/0.3));txt('ALLAH CHOSE YOU.',W/2,720,86,'#FDE68A',{weight:900,scale:k,glow:'#F59E0B',gb:50,alpha:u>2.6?clamp((3.4-u)/0.8):1})}
  if(u>2.2)txt('This is not random.',W/2,170,46,'#fff',{weight:800,stroke:8,sc:'#0B1033',alpha:clamp((u-2.2)/0.3)});
};
S.s1=(u,d,t)=>{
  const p=u/d;nightSky(t);
  const z=lerp(1,3.2,ease(seg01(p,0.35,0.8)));
  X.save();X.translate(700,1150);X.scale(z,z);X.translate(-700,-1150);
  for(let i=0;i<9;i++){const bw=110,bh=400+rnd(i)*500,bx=i*125,by=1920-bh;X.fillStyle=i%2?'#151A42':'#1C2152';X.fillRect(bx,by,bw,bh);
    for(let r=0;r<12;r++)for(let c=0;c<3;c++){const id=i*100+r*3+c;const off=rnd(id)<p*1.3;const gold=(i===5&&r===4&&c===1);if(by+30+r*45>1900)continue;
      X.fillStyle=gold?'#FBBF24':off?'#0E1233':'rgba(253,230,138,.55)';X.fillRect(bx+15+c*32,by+30+r*45,20,26);if(gold)glow(bx+25+c*32,by+43+r*45,60,'rgba(251,191,36,.9)')}}
  X.restore();
  if(p>0.7){const k=clamp((p-0.7)/0.15);X.save();X.globalAlpha=k;bg('#1C1748','#2A2160');glow(540,900,700,'rgba(251,191,36,.25)');
    X.save();paper(true);X.fillStyle='#7BAE7F';rr(220,1500,640,200,14);X.fill();X.restore();man(540,1600,1.1);
    const [cx,cy]=chest(540,1600,1.1,'sit');const lk=clamp((TL.ev.lantern-tS('s1')-u)*-1/1.0);lantern(540,lerp(1150,700,eout(lk)),0.9,t,'',1);thread(540,1180,lerp(0,450,eout(lk)),0,t,1);X.restore()}
  const k1=clamp(u/0.4);txt('8,000,000,000 people',40,140,40,'#C4B5FD',{align:'left',weight:800,alpha:k1});
  if(p>0.6)txt('1 heart: YOU',40,200,46,'#FBBF24',{align:'left',weight:900,glow:'#F59E0B',alpha:clamp((p-0.6)/0.1)});
};
S.s2=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s2')+u;nightSky(t);
  const keyT=ev.key;
  if(tt<keyT-0.2){ // parchment quote
    const k=eout(clamp(u/0.6));X.save();X.translate(540,880);X.scale(1,k);paper(true,10,30);X.fillStyle='#F5E6C8';rr(-420,-380,840,760,20);X.fill();paper(false);X.fillStyle='#E7D3A8';rr(-440,-400,880,40,20);X.fill();rr(-440,360,880,40,20);X.fill();
    const lines=['"I don\'t worry about','the answer.','I worry about','making du\'a."'];const prog=clamp((u-0.4)/2.8);
    lines.forEach((ln,i)=>{txt(ln,0,-200+i*110,64,'#5B3A1E',{font:'Amiri',weight:700,alpha:clamp(prog*4-i)})});
    txt('— Umar ibn al-Khattab (attributed)',0,290,32,'#8B6B4A',{weight:800,alpha:clamp(prog*4-3)});X.restore();
  } else { // key & door
    const k=clamp((tt-(keyT-0.2))/0.6);
    X.save();X.translate(540,1000);paper(true,0,60,'rgba(251,191,36,.6)');X.fillStyle='#2A2160';X.beginPath();X.moveTo(-240,420);X.lineTo(-240,-200);X.arc(0,-200,240,Math.PI,0);X.lineTo(240,420);X.closePath();X.fill();paper(false);
    const op=ease(clamp((tt-keyT-0.3)/0.8));glow(0,0,500*op+40,'rgba(255,240,200,1)',op);
    X.save();X.scale(1-op*0.9,1);X.fillStyle='#6D28D9';X.beginPath();X.moveTo(-220,410);X.lineTo(-220,-200);X.arc(0,-200,220,Math.PI,0);X.lineTo(220,410);X.closePath();X.fill();X.strokeStyle='#FDE68A';X.lineWidth=6;X.stroke();circ(0,80,26,'#FBBF24');X.restore();X.restore();
    // key flying in
    const kx=lerp(-100,540,eout(k)),ky=lerp(1700,1080,eout(k));X.save();X.translate(kx,ky);X.rotate(lerp(-1,0,k)+(tt>keyT?clamp((tt-keyT)/0.25)*1.57:0));X.fillStyle='#FBBF24';X.shadowColor='#FDE68A';X.shadowBlur=30;X.beginPath();X.arc(-60,0,36,0,7);X.fill();X.fillStyle='#1C1748';circ(-60,0,14,'#2A2160');X.fillStyle='#FBBF24';rr(-30,-9,110,18,6);X.fill();rr(50,0,14,30,4);X.fill();rr(70,0,10,22,4);X.fill();X.restore();
    if(tt>keyT+0.5)txt("The du'a IS the sign.",W/2,380,70,'#FDE68A',{weight:900,glow:'#F59E0B',scale:back(clamp((tt-keyT-0.5)/0.3))});
  }
};
S.s3=(u,d,t)=>{
  nightSky(t);glow(540,600,800,'rgba(251,191,36,.18)');
  const fill=clamp(u/(d*0.8));
  // pouring light
  X.save();X.strokeStyle='rgba(253,230,138,.85)';X.lineWidth=40+10*Math.sin(t*6);X.lineCap='round';X.shadowColor='#FBBF24';X.shadowBlur=50;X.beginPath();X.moveTo(540,-50);X.quadraticCurveTo(560+Math.sin(t*2)*20,500,540,1150);X.stroke();X.restore();
  hands(540,1420,1.5,1,0.6+0.4*fill);
  X.save();X.beginPath();X.ellipse(540,1290,220,70*fill+10,0,0,7);X.fillStyle='rgba(253,230,138,.95)';X.shadowColor='#FBBF24';X.shadowBlur=40;X.fill();X.restore();
  if(fill>0.8){for(let i=0;i<8;i++){const k=((t*0.8+rnd(i))%1);circ(330+rnd(i+3)*420,1300+k*500,8,`rgba(253,230,138,${1-k})`)}
    for(let i=0;i<7;i++){const fx=150+i*130,fk=clamp((fill-0.8)*5-i*0.05);X.save();X.translate(fx,1900);X.scale(fk,fk);X.strokeStyle='#10B981';X.lineWidth=8;X.beginPath();X.moveTo(0,0);X.lineTo(0,-120);X.stroke();for(let pp=0;pp<5;pp++)circ(Math.cos(pp*1.26)*26,-130+Math.sin(pp*1.26)*26,18,i%2?'#F9A8D4':'#FDE68A');circ(0,-130,12,'#F59E0B');X.restore()}}
  txt('Never empty.',W/2,330,96,'#FDE68A',{weight:900,glow:'#F59E0B',alpha:clamp((u-0.6)/0.4),scale:1+0.03*Math.sin(t*4)});
  txt('(Abu Dawud 1488)',W/2,420,30,'rgba(253,230,138,.7)',{weight:600,alpha:clamp((u-0.9)/0.4)});
};
S.s4=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s4')+u;nightSky(t);
  man(540,1700,1.0);
  const icons=['📚','💰','🚗','📱'];
  icons.forEach((e,i)=>{const pt=i<3?ev.pops[i]:ev.pops[2]+0.15;const gone=clamp((tt-pt)/0.2);if(gone>=1)return;const a=t*0.9+i*1.57;const ix=540+Math.cos(a)*330,iy=1250+Math.sin(a)*170;
    X.save();X.globalAlpha=1-gone;circ(ix,iy,85*(1-gone*0.8),'rgba(255,255,255,.15)');txt(e,ix,iy+5,90*(1-gone*0.9),'#000',{font:'"Noto Color Emoji"',weight:500});X.restore()});
  const bk=clamp((tt-ev.big)/0.5);
  const fin=tt>ev.pops[2]+0.3;
  if(fin){const k=eout(clamp((tt-ev.pops[2]-0.3)/0.6));lantern(540,lerp(1300,800,k),lerp(0.8,3.0,k),t,'',1)}
  if(tt>ev.big){txt('ASK BIG.',W/2,420,lerp(90,170,eout(clamp((tt-ev.big)/0.6))),'#FDE68A',{weight:900,glow:'#F59E0B',gb:50,scale:back(bk),stroke:8,sc:'#1C1748'})}
};
S.s5=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s5')+u;
  const lv=ev.levels.filter(x=>tt>=x).length;const prog=clamp((tt-ev.levels[0])/(ev.levels[4]-ev.levels[0]+0.3));
  // layered skies scrolling down as lantern rises
  const scroll=ease(prog)*2600;
  const cols=[['#0B1033','#3B2A6B'],['#3B2A6B','#6D5BB0'],['#6D5BB0','#A7C4F0'],['#A7C4F0','#D1FAE5']];
  bg('#0B1033','#3B2A6B');
  X.save();X.translate(0,scroll);
  for(let i=0;i<4;i++){X.fillStyle=grad(cols[i][1],cols[i][0],-i*900+1920-900,-i*900+1920);X.fillRect(0,-i*900+1920-900,W,900);
    X.fillStyle='rgba(255,255,255,.25)';for(let c=0;c<5;c++){X.beginPath();X.ellipse(rnd(i*9+c)*W,-i*900+1020+rnd(c)*100,180,40,0,0,7);X.fill()}}
  for(let i=0;i<60;i++)circ(rnd(i)*W,1920-rnd(i+3)*3000,2,`rgba(255,255,255,${.4+.4*Math.sin(t*2+i)})`);
  X.restore();
  if(prog>0.85){const k=clamp((prog-0.85)/0.15);X.save();X.globalAlpha=k;gardenBG(t,1);X.restore();txt('الفردوس الأعلى',W/2,330,96,'#065F46',{font:'Amiri',weight:700,alpha:k,glow:'#fff',gb:30})}
  lantern(540,lerp(1400,1150,prog),1.6,t,'',1);thread(540,1950,lerp(400,700,prog),0,t,1);
  // level meter
  const levels=[1,10,50,90,100];const cur=lv>0?levels[lv-1]:1;
  X.save();X.translate(980,560);X.fillStyle='rgba(255,255,255,.2)';rr(-20,0,40,900,20);X.fill();X.fillStyle='#FBBF24';rr(-20,900-900*cur/100,40,900*cur/100,20);X.fill();X.restore();
  txt(cur===100?'Level 100: AL-FIRDAUS':'Level '+cur,W/2,cur===100?470:520,cur===100?60:70,cur===100?'#FDE68A':'#fff',{weight:900,stroke:8,sc:'#1C1748',glow:cur===100?'#F59E0B':null,scale:lv>0&&tt-ev.levels[lv-1]<0.2?1.15:1});
  if(cur===100)txt('(Bukhari 2790)',W/2,545,30,'#fff',{weight:700,stroke:6,sc:'#065F46'});
};
S.s6=(u,d,t)=>{
  const ev=TL.ev, tt=tS('s6')+u;nightSky(t);glow(540,1000,800,'rgba(196,181,253,.2)');
  const cards=[['🎁','Given now'],['🏆','Saved for Akhirah'],['🛡️','Harm turned away']];
  cards.forEach(([e,l],i)=>{const ct=ev.cards[i];const k=clamp((tt-ct+0.1)/0.4);if(k<=0)return;const cy=600+i*300;
    X.save();X.translate(540,cy);X.scale(1,Math.abs(Math.cos((1-eout(k))*Math.PI/2)));paper(true,10,30);X.fillStyle='rgba(255,255,255,.95)';rr(-420,-125,840,250,40);X.fill();paper(false);
    circ(-280,0,95,i===0?'#FDE68A':i===1?'#FCD34D':'#BFDBFE');txt(e,-280,6,100,'#000',{font:'"Noto Color Emoji"',weight:500,scale:i===0?1+0.1*Math.sin(t*8):1});
    txt(l,90,-10,52,'#1C1748',{weight:900});txt('✔',330,60,56,'#16A34A',{weight:900,font:'DejaVu Sans',alpha:clamp((tt-ct-0.3)/0.2)});X.restore();
    if(i===2&&tt>ct){const rk=clamp((tt-ct)/0.5);if(rk<1){txt('🪨',lerp(800,620,rk),lerp(1000,1300,rk),70,'#000',{font:'"Noto Color Emoji"',weight:500})}else{txt('🪨',lerp(620,950,clamp((tt-ct-0.5)/0.5)),lerp(1300,1100,clamp((tt-ct-0.5)/0.5)),60,'#000',{font:'"Noto Color Emoji"',weight:500,alpha:1-clamp((tt-ct-0.5)/0.5)})}}});
  txt("Every du'a is ANSWERED.",W/2,330,64,'#FDE68A',{weight:900,glow:'#F59E0B',alpha:clamp(u/0.4)});
  txt('(Ahmad 11133)',W/2,410,30,'rgba(253,230,138,.7)',{weight:600,alpha:clamp((u-0.4)/0.4)});
};
S.s7=(u,d,t)=>{
  nightSky(t);
  // window with rain
  X.save();paper(true);X.fillStyle='#2A2160';rr(240,260,600,640,24);X.fill();X.restore();X.save();rr(260,320,560,600,16);X.clip();bg('#151A42','#2A2160');for(let i=0;i<40;i++)circ(260+rnd(i)*560,320+rnd(i+4)*600,1.5,'#fff');X.strokeStyle='rgba(180,200,255,.5)';X.lineWidth=2;for(let i=0;i<50;i++){const rx=260+rnd(i)*560,ry=(rnd(i+9)*700+t*700)%700+300;X.beginPath();X.moveTo(rx,ry);X.lineTo(rx-5,ry+30);X.stroke()}X.restore();
  X.fillStyle='#1C1748';X.fillRect(0,1500,W,500);
  // sujud figure
  X.save();X.translate(540,1560);paper(true);X.fillStyle='#7BAE7F';rr(-300,-20,600,90,10);X.fill();X.fillStyle='#E7E5E4';X.beginPath();X.ellipse(-20,-60,180,75,0,Math.PI,0);X.fill();circ(-190,-20,48,'#c99a78');X.fillStyle='#fff';X.beginPath();X.ellipse(-200,-40,46,30,0,Math.PI,0);X.fill();X.restore();
  glow(540,1450,400,'rgba(251,191,36,.3)');
  const pills=['🌙 Last third of the night','🧎 In sujud','🌧️ When it rains','🕌 Between adhan & iqamah'];
  pills.forEach((pl,i)=>{const k=back(clamp((u-0.2-i*0.5)/0.25));if(k<=0)return;X.save();X.translate(540,1030+i*105);X.scale(k,k);X.fillStyle='rgba(255,255,255,.92)';rr(-330,-42,660,84,42);X.fill();txt(pl,0,3,34,'#1C1748',{weight:900,font:'Mont, "Noto Color Emoji"'});X.restore()});
  for(let i=0;i<10;i++){const k=((t*0.15+rnd(i))%1);lantern(rnd(i+20)*W,1500-k*1500,0.35,t+i,'',Math.sin(k*Math.PI)*.9)}
};
S.cta=(u,d,t)=>{
  const ev=TL.ev, tt=tS('cta')+u, p=u/d;nightSky(t);
  // comment box
  const k=eout(clamp(u/0.4));X.save();X.translate(540,lerp(1500,1150,k));paper(true,10,30);X.fillStyle='#fff';rr(-440,-90,880,180,40);X.fill();paper(false);
  const msg='Ya Allah, grant me Jannatul Firdaus 🤲';const n=Math.floor(clamp((tt-ev.type)/2.0)*[...msg].length);
  circ(-360,0,40,'#C4B5FD');txt([...msg].slice(0,n).join(''),-300,0,34,'#111827',{align:'left',weight:700,font:'Mont, "Noto Color Emoji"'});
  if(tt<ev.type+2.1&&Math.sin(t*10)>0){X.fillStyle='#111827';const w=(()=>{X.font='700 34px Mont';return X.measureText([...msg].slice(0,n).join('')).width})();X.fillRect(-300+w+4,-20,4,40)}
  X.restore();
  const sent=tt>ev.type+2.2;
  if(sent){for(let i=0;i<24;i++){const kk=clamp((tt-ev.type-2.2-rnd(i)*1.2)/2.0);if(kk<=0)continue;const hx=rnd(i+3)*W,hy=lerp(1400,200,kk);if(kk<0.6)txt(i%3?'Ameen 🤍':'🤲',hx,hy,i%3?34:50,'#fff',{weight:800,font:'Mont, "Noto Color Emoji"',alpha:1-kk*0.6});else lantern(hx,hy,0.3,t+i,'',1-kk)}}
  txt("Comment your du'a 🤲",W/2,500,76,'#FDE68A',{weight:900,glow:'#F59E0B',font:'Mont, "Noto Color Emoji"',scale:back(clamp((u-0.3)/0.3))});
  txt('Reply AMEEN to others',W/2,610,44,'#fff',{weight:800,alpha:clamp((u-0.8)/0.3)});
  txt('Share = sadaqah jariyah 🤍',W/2,1750,36,'rgba(255,255,255,.85)',{weight:700,alpha:clamp((u-1.2)/0.3),font:'Mont, "Noto Color Emoji"'});
  if(u>d-0.9){const fk=clamp((u-(d-0.9))/0.8);X.fillStyle=`rgba(0,0,0,${fk})`;X.fillRect(0,0,W,H);hands(540,lerp(2300,1700,fk),1.4,fk,0)}
};
