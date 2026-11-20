import sys, json, numpy as np, soundfile as sf
S=sys.argv[1]; SR=48000
rng=np.random.default_rng(7)
vo=json.load(open(f"{S}/build/vo.json"))

# ---------- timeline ----------
t=1.4; segs=[]
for x in vo:
    segs.append(dict(i=x['i'],scene=x['scene'],kind=x['kind'],cap=x['cap'],start=round(t,3),end=round(t+x['dur'],3),file=x['file']))
    t+=x['dur']+x['pause']
TOTAL=round(t+0.2,2)
order=[]; 
for s in segs:
    if s['scene'] not in order: order.append(s['scene'])
scenes={}
for sc in order:
    ss=[s for s in segs if s['scene']==sc]
    scenes[sc]=dict(start=ss[0]['start']-0.25, segs=[s['i'] for s in ss])
scenes['hook']['start']=0.0
# visual lead-ins
for sc,lead in [('s7',0.2),('s11',0.05)]:
    scenes[sc]['start']-=lead
keys=order
for a,b in zip(keys,keys[1:]): scenes[a]['end']=scenes[b]['start']
scenes[keys[-1]]['end']=TOTAL
SEGI={s['i']:s for s in segs}
def seg(sc,k=0): return SEGI[scenes[sc]['segs'][k]]
ev={}
ev['blast']=0.7
ev['books']=seg('s2')['start']+0.1
ev['right']=seg('s3',0)['start']+0.6
ev['left']=seg('s3',1)['start']+0.3
ev['cubes']=[seg('s4',0)['start']+0.3+k*0.45 for k in range(6)]
ev['good']=seg('s4',1)['start']+0.05
ev['evil']=seg('s4',1)['start']+(seg('s4',1)['end']-seg('s4',1)['start'])*0.5
ev['drink']=seg('s5')['start']+1.3
ev['speeds']=[seg('s7',k)['start'] for k in range(7)]
ev['lightout']=seg('s8')['end']-0.5
ev['gates']=seg('s9')['start']+0.2
ev['cross']=[seg('s10')['start']+k*0.55 for k in range(2)]
ev['busy']=seg('s10')['end']-0.3
ev['fall']=seg('s11')['start']-0.05
json.dump(dict(total=TOTAL,scenes=scenes,segs=segs,ev=ev),open(f"{S}/build/timeline.json","w"),indent=1)
print("TOTAL",TOTAL); [print(k,round(v['start'],2),round(v['end'],2)) for k,v in scenes.items()]

# ---------- synth helpers ----------
N=int(TOTAL*SR)+SR
sfx=np.zeros(N); mus=np.zeros(N); vob=np.zeros(N)
def T(d): return np.arange(int(d*SR))/SR
def env(d,a=0.005,r=None,curve=4):
    n=int(d*SR); e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na)
    if r is None: e*=np.exp(-curve*np.linspace(0,1,n))
    else:
        nr=int(r*SR); e[-nr:]*=np.linspace(1,0,nr)
    return e
def filt(x,lo=None,hi=None):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); m=np.ones_like(f)
    if lo: m*=1/(1+(lo/np.maximum(f,1))**4)
    if hi: m*=1/(1+(f/hi)**4)
    return np.fft.irfft(X*m,len(x))
def noise(d): return rng.standard_normal(int(d*SR))
def sweep(f0,f1,d,shape='exp'):
    tt=T(d); 
    f=f0*(f1/f0)**(tt/d) if shape=='exp' else np.linspace(f0,f1,len(tt))
    return np.sin(2*np.pi*np.cumsum(f)/SR)
def add(buf,t0,x,g=1.0):
    i=int(t0*SR); 
    if i<0: x=x[-i:]; i=0
    x=x[:max(0,len(buf)-i)]; buf[i:i+len(x)]+=x*g
def norm(x): return x/(np.max(np.abs(x))+1e-9)
# sounds
def kick(d=0.4,f0=130,f1=42): return sweep(f0,f1,d)*env(d,0.002,curve=6)
def boom(d=2.5): return norm(sweep(70,32,d)*env(d,0.005,curve=3)+0.5*filt(noise(d),hi=120)*env(d,0.01,curve=4))
def thud(): 
    d=0.9; return norm(kick(d,95,32)*1.2+0.6*filt(noise(d),hi=300)*env(d,0.002,curve=8)+0.35*filt(noise(d),2000,6000)*env(d,0.001,curve=25))
def whistle(): return sweep(2200,500,0.4)*env(0.4,0.05,curve=1)*0.25
def tick(): return filt(noise(0.012),3000)*env(0.012,0.0005,curve=6)
def ting(): tt=T(0.4); return (np.sin(2*np.pi*1760*tt)+0.6*np.sin(2*np.pi*2637*tt))*env(0.4,0.002,curve=7)*0.5
def pop(): return sweep(350,1000,0.05)*env(0.05,0.002,curve=5)
def beep(d=0.12,f=1000): tt=T(d); return np.sin(2*np.pi*f*tt)*env(d,0.005,r=0.01)
def glass():
    d=1.2; x=filt(noise(d),2500)*env(d,0.001,curve=10)
    for _ in range(25):
        tt=T(0.3); g=np.sin(2*np.pi*rng.uniform(3000,8000)*tt)*env(0.3,0.001,curve=12)
        add_local(x,rng.uniform(0,0.8),g,0.15)
    return norm(x)
def add_local(buf,t0,x,g): i=int(t0*SR); x=x[:len(buf)-i]; buf[i:i+len(x)]+=x*g
def whoosh(d=0.8,rev=False,f0=300,f1=3000):
    n=noise(d); out=np.zeros_like(n); steps=16; L=len(n)//steps
    for k in range(steps):
        fc=f0*(f1/f0)**(k/steps); out[k*L:(k+1)*L]=filt(n[k*L:(k+1)*L+0],fc*0.6,fc*1.6)[:L] if (k+1)*L<=len(n) else 0
    e=np.sin(np.pi*np.linspace(0,1,len(n)))**2
    if rev: e=np.linspace(0,1,len(n))**3
    return norm(out*e)
def scratch():
    d=0.5; tt=T(d); n=noise(d); fc=800+600*np.sin(2*np.pi*9*tt)
    return norm(filt(n,400,3000)*np.abs(np.sin(2*np.pi*9*tt))*env(d,0.01,r=0.1))
def piano(f=220,d=3.0):
    tt=T(d); x=sum(np.sin(2*np.pi*f*h*tt)/h**1.3*np.exp(-tt*(1.2+h*0.6)) for h in range(1,8))
    return norm(x)*env(d,0.004,r=0.4)
def rain(d): n=filt(noise(d),800,7000)*0.3; 
def tone(f,d,kind='sin'):
    tt=T(d); ph=2*np.pi*f*tt
    return np.sin(ph) if kind=='sin' else 2*((f*tt)%1)-1
def heart():
    x=np.zeros(int(0.6*SR)); add_local(x,0,kick(0.2,70,40),1); add_local(x,0.22,kick(0.2,65,38),0.7); return x
def water(d):
    n=filt(noise(d),400,2500); tt=T(d); m=0.6+0.4*np.sin(2*np.pi*3.3*tt)*np.sin(2*np.pi*0.7*tt)
    x=n*m*0.4
    for _ in range(int(d*14)):
        b=sweep(rng.uniform(400,900),rng.uniform(1200,2200),0.04)*env(0.04,0.002,curve=4)
        add_local(x,rng.uniform(0,d-0.05),b,0.3)
    return norm(x)*env(d,0.1,r=0.3)
def rustle(d):
    n=filt(noise(d),1500,6000); e=np.abs(filt(noise(d),hi=12)); return norm(n*e)*env(d,0.05,r=0.2)
def step(): d=0.25; return norm(kick(d,90,50)*0.6+filt(noise(d),1500,5000)*env(d,0.001,curve=14)*0.5)
def soil(k):
    d=1.0; x=kick(d,80,35)+filt(noise(d),hi=900-180*k)*env(d,0.002,curve=6)*1.4
    return norm(filt(x,hi=1600-300*k))
def rumble(d): return norm(filt(noise(d),hi=70))*env(d,0.5,r=0.8)
def thunder():
    d=3.0; x=filt(noise(d),1000)*env(d,0.001,curve=14)+filt(noise(d),hi=180)*env(d,0.05,curve=2.5)*1.5
    return norm(x)
def static(d): n=noise(d)*(rng.random(int(d*SR))>0.3); return filt(n,1000)*env(d,0.002,r=0.02)*0.5
def chirp():
    d=0.12; tt=T(d); f=3200+1200*np.sin(2*np.pi*28*tt); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(d,0.005,r=0.03)
def pluck(f=660,d=1.5):
    p=int(SR/f); buf=rng.uniform(-1,1,p); out=np.zeros(int(d*SR))
    for i in range(len(out)):
        out[i]=buf[i%p]; buf[i%p]=0.996*0.5*(buf[i%p]+buf[(i+1)%p])
    return norm(out)
def plip(): return sweep(500,1500,0.06)*env(0.06,0.002,curve=5)
def chime(f): tt=T(2.5); return sum(np.sin(2*np.pi*f*m*tt)*np.exp(-tt*(2+m)) for m in (1,2.76,5.4))*0.4
def pad(freqs,d,bright=900,a=1.5,r=1.5):
    tt=T(d); x=np.zeros(len(tt))
    for f in freqs:
        for det in (-0.25,0,0.25):
            x+=(2*(((f*(1+det/100))*tt+rng.random())%1)-1)
    x=filt(x,40,bright)*(1+0.15*np.sin(2*np.pi*0.2*tt))
    return norm(x)*env(d,a,r=r)
def screamish(d=1.4):
    tt=T(d); f=420+180*np.sin(2*np.pi*5*tt)+np.linspace(0,200,len(tt))
    x=sum(np.sin(2*np.pi*np.cumsum(f*h)/SR)/h for h in range(1,6))+0.3*noise(d)
    return norm(filt(x,200,900))*env(d,0.15,r=0.6)

def A(t0,x,g): add(sfx,t0,x,g)
def M(t0,x,g): add(mus,t0,x,g)
sc=lambda k: scenes[k]
# ---- HOOK
def rnd_t(k): return (np.sin(k*12.9898)*43758.5453)%1
def horn(d=2.2):
    tt=T(d); x=sum((2*((f*tt)%1)-1)*g for f,g in ((55,1),(82.4,0.7),(110,0.5),(164.8,0.25)))
    return norm(filt(x,30,1400))*env(d,0.08,r=0.9)
def fire(d):
    n=filt(noise(d),hi=500)*0.8+filt(noise(d),1500,6000)*(rng.random(int(d*SR))>0.995)*3
    tt=T(d); return norm(n*(0.7+0.3*np.sin(2*np.pi*0.6*tt)))
def flutter(d):
    x=np.zeros(int(d*SR))
    for k in range(int(d*40)):
        add_local(x,rnd_t(k)*(d-0.1),filt(noise(0.06),800,5000)*env(0.06,0.005,curve=4),0.4)
    return norm(x)*env(d,0.3,r=0.4)
def wings(): d=0.25; return filt(noise(d),200,1500)*np.sin(np.pi*np.linspace(0,1,int(d*SR)))
A(0.0,filt(noise(0.7),hi=80)*np.linspace(0,1,int(0.7*SR)),0.4)
A(ev['blast'],horn(2.6),1.0); A(ev['blast'],boom(2.5),0.9); A(ev['blast']+0.05,thunder(),0.5)
for k in range(6): A(ev['blast']+0.1+k*0.08,filt(noise(0.3),300,2000)*env(0.3,0.002,curve=6),0.3)
A(1.6,whoosh(2.0,f0=150,f1=1200),0.35)
# ---- plain
p0=sc('hook')['start']+1.6; p1=sc('s2')['start']
M(p0,pad([41.2,61.7,82.4],p1-p0+0.5,350,a=1.0,r=0.6),0.35)
A(p0,filt(noise(p1-p0),200,2500)*env(p1-p0,0.8,r=0.5),0.1)
for k in range(int((p1-sc('s1')['start'])/0.85)): A(sc('s1')['start']+0.2+k*0.85,heart(),0.35)
A(sc('s1')['start'],filt(noise(p1-sc('s1')['start']),4000)*0.25,0.08)
# ---- books
A(ev['books'],flutter(2.3),0.55); A(ev['books']+0.3,whoosh(0.7,f0=300,f1=3000),0.35); A(ev['books']+1.2,whoosh(0.6,f0=500,f1=4000),0.3)
M(ev['books'],pad([73.4,110,146.8,155.6],sc('s4')['end']-ev['books'],900,a=1.0,r=0.6),0.25)
for j,f in enumerate((1046,1318,1568)): A(ev['right']+j*0.06,chime(f),0.35)
A(ev['left'],thud(),0.5); A(ev['left']+0.3,kick(0.3,60,40),0.3)
for k in range(6): A(ev['left']+0.4+k*0.45*(1-k*0.07),heart(),0.4)
# ---- mizan
creak=lambda: norm(filt(sweep(180,240,0.6,'lin')+0.5*noise(0.6)*0.2,100,1500))*env(0.6,0.05,r=0.2)
for k,tc in enumerate(ev['cubes']): A(tc,kick(0.35,90,45),0.55); A(tc+0.05,creak(),0.12)
A(ev['good']-0.3,creak(),0.2); A(ev['good'],boom(1.2),0.5)
for j,f in enumerate((523,659,784,1046)): A(ev['good']+0.05+j*0.06,chime(f),0.25)
A(ev['evil'],filt(tone(55,1.6,'saw')+tone(58.3,1.6,'saw'),hi=400)*env(1.6,0.02,curve=2),0.45); A(ev['evil'],thud(),0.5)
# ---- hawdh
h0=sc('s5')['start']; M(h0,pad([261.6,329.6,392,523.2],sc('s5')['end']-h0+0.4,3000,a=0.6,r=0.6),0.35)
A(h0,water(2.0),0.3); A(ev['drink'],kick(0.12,300,180),0.25); A(ev['drink']+0.2,kick(0.12,280,170),0.2)
for j,f in enumerate((1568,2093,2637)): A(ev['drink']+0.4+j*0.1,chime(f),0.25)
# ---- sirat
s0=sc('s6')['start']; s1=sc('s9')['start']
A(s0,fire(s1-s0),0.35); A(s0,filt(noise(s1-s0),200,1500)*env(s1-s0,0.5,r=0.5),0.18)
A(s0+0.3,tone(4200,2.5)*env(2.5,0.3,r=1.0),0.03)
M(s0,pad([36.7,55,73.4,77.8],s1-s0+0.3,400,a=0.6,r=0.5),0.3)
for k in range(int((s1-s0)/0.6)): A(s0+k*0.6,kick(0.2,70,40),0.3)
sp=ev['speeds']
A(sp[0],tick(),0.7); A(sp[0],beep(0.05,2400),0.2)
A(sp[1],thunder(),0.7)
A(sp[2],whoosh(0.7,f0=200,f1=3000),0.6)
for k in range(3): A(sp[3]+k*0.2,wings(),0.5)
for k in range(6): A(sp[4]+k*0.12,step(),0.35)
for k in range(3): A(sp[5]+k*0.35,step(),0.3)
A(sp[6],rustle(1.6),0.45); A(sp[6]+0.3,screamish(1.0),0.08); A(sp[6]+0.2,fire(1.2),0.4)
A(ev['lightout']-0.6,filt(noise(0.5),1500,6000)*(rng.random(int(0.5*SR))>0.9),0.25)
# ---- jannah
j0=sc('s9')['start']; j1=sc('s11')['start']
M(j0,pad([130.8,196,261.6,329.6,392],j1-j0+0.2,2600,a=0.8,r=0.2),0.42)
A(ev['gates'],kick(0.6,60,35),0.5); A(ev['gates'],whoosh(1.5,f0=200,f1=2500),0.35)
for k,f in enumerate((1046,1318,1568,2093)): A(ev['gates']+0.2+k*0.15,chime(f),0.25)
A(j0+1,filt(noise(j1-j0-1),300,3000)*env(j1-j0-1,0.5,r=0.3),0.05)
for k in range(int((j1-j0)*2)): A(j0+0.5+rnd_t(k)*(j1-j0-1),chirp(),0.07)
for k,tc in enumerate(ev['cross']): A(tc,pop(),0.35)
A(ev['busy'],thud(),0.45); A(ev['busy'],tick(),0.4)
# ---- fall
f0=ev['fall']; A(f0,whoosh(2.2,f0=2000,f1=100),0.55); A(f0+0.3,fire(2.5),0.55); A(f0,boom(2.0),0.4)
# ---- cta
c0=sc('cta')['start']
for k in range(int((TOTAL-c0)/0.85)): A(c0+0.3+k*0.85,heart(),0.3)
for k in range(int((TOTAL-c0)/0.5)): A(c0+0.2+k*0.5,tick(),0.15)
M(c0,pad([110,164.8,220],TOTAL-c0,800,a=1.0,r=1.5),0.25)
M(TOTAL-2.6,piano(110,2.6)+piano(164.8,2.6)*0.6+piano(261.6,2.6)*0.5,0.35)
# ---------- VO + ducking ----------
for s in segs:
    x,_=sf.read(s['file']); add(vob,s['start'],x,1.0)
vob=vob/np.max(np.abs(vob))*0.9
envv=np.abs(vob); k=int(0.15*SR); envv=np.convolve(envv,np.ones(k)/k,'same'); envv=np.clip(envv/0.05,0,1)
duck=1-0.55*envv
# hard silence after hammer
hs=he=0
mix=vob+sfx*0.55*(1-0.35*envv)+mus*duck*0.6

mix=mix[:int(TOTAL*SR)]
mix=np.tanh(mix*1.1)/1.1
sf.write(f"{S}/build/mix.wav",mix.astype(np.float32),SR)
print("audio ok",len(mix)/SR)
