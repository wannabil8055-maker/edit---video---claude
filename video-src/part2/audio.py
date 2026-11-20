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
for sc,lead in [('s4',0.45),('s9',0.25),('s11',0.1)]:
    scenes[sc]['start']-=lead
keys=order
for a,b in zip(keys,keys[1:]): scenes[a]['end']=scenes[b]['start']
scenes[keys[-1]]['end']=TOTAL
SEGI={s['i']:s for s in segs}
def seg(sc,k=0): return SEGI[scenes[sc]['segs'][k]]
ev={}
ev['flat']=0.6; ev['smile']=1.0
ev['drops']=[seg('s4',k)['start']-0.08 for k in range(3)]
ev['given']=seg('s4',3)['start']+0.2
ev['checks']=[seg('s5')['start']+0.1+k*((seg('s5')['end']-seg('s5')['start'])/4) for k in range(4)]
ev['flatdeath']=seg('s6')['end']+0.35
ev['soil']=[seg('s8',1)['end']-1.25+0.22*k for k in range(4)]
ev['qs']=[seg('s10',k*2)['start']-0.05 for k in range(3)]
ev['ans']=[seg('s10',k*2+1)['start']-0.05 for k in range(3)]
ev['door']=seg('s11',1)['start']+1.2
ev['swipe']=seg('s12')['start']+0.9
ev['busy']=seg('s14')['end']-0.9
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
A(0.05,beep(),0.35); A(0.3,beep(),0.35); A(0.55,beep(0.5),0.3)
A(1.0,boom(1.5),0.7)
for k,f in enumerate((1046,1318,1568,2093,2637)): A(1.0+k*0.07,chime(f),0.25)
M(1.0,pad([261.6,329.6,392,523.2],2.6,2500,a=0.2,r=1.0),0.35)
A(1.9,whoosh(1.1,f0=400,f1=4000),0.4)
def birds(t0,d,g=0.08):
    for k in range(int(d*3)): A(t0+rnd_t(k)*d,chirp(),g)
def rnd_t(k): return (np.sin(k*12.9898)*43758.5453)%1
def warmbeat(t0,dur,g=0.5):
    bpm=95; b=60/bpm; n=int(dur/b*2); buf=np.zeros(int((dur+1)*SR))
    prog=[(130.8,164.8,196),(110,130.8,164.8),(87.3,110,130.8),(98,123.5,146.8)]
    for i in range(n):
        tt0=i*b/2
        if i%4==0: add_local(buf,tt0,kick(0.3,90,45),0.5)
        if i%4==2: add_local(buf,tt0,filt(noise(0.12),900,5000)*env(0.12,0.002,curve=8),0.35)
        if i%2==1: add_local(buf,tt0,filt(noise(0.03),6000)*env(0.03,0.001,curve=8),0.08)
        if i%8==0:
            ch=prog[(i//8)%4]; add_local(buf,tt0,pad(list(ch),b*4,1800,a=0.05,r=0.4),0.35)
        if i%2==0:
            ch=prog[(i//8)%4]; f=ch[(i//2)%3]*2; add_local(buf,tt0,piano(f,0.6)*0.5,0.18)
    buf=buf[:int(dur*SR)]; M(t0,buf*env(dur,0.3,r=0.5),g)
# ---- ACT 1 life
d0=sc('s1')['start']; d1=sc('s6')['start']
warmbeat(d0,d1-d0,0.5)
birds(d0,2.5)
A(d0+0.5,filt(noise(0.35),800,5000)*env(0.35,0.02,curve=3),0.25)  # page turn
A(d0+1.6,filt(noise(0.35),800,5000)*env(0.35,0.02,curve=3),0.2)
s2=sc('s2')['start']
for k in range(5): A(s2+0.3+k*0.35,pop(),0.2)
for k in range(6): A(s2+0.2+k*0.25,chirp()*0.0+sweep(600+k*80,900+k*90,0.12)*env(0.12,0.01,r=0.04),0.08)
s3=sc('s3')['start']
for k in range(5): A(s3+0.1+k*0.4,step(),0.2)
A(s3+1.2,filt(noise(0.3),1500,6000)*env(0.3,0.01,r=0.1),0.3)
A(s3+2.2,filt(noise(0.6),200,900)*env(0.6,0.1,r=0.2),0.15)
A(s3+2.6,chime(1568),0.3)
for k,tdrop in enumerate(ev['drops']): A(tdrop-0.4,whistle(),0.7); A(tdrop,thud(),0.9)
for k in range(8): A(ev['given']+k*0.05,ting()*0.4,0.2)
A(ev['given']+0.3,beep(0.08,1400),0.2)
for k in range(5): A(ev['given']+0.6+k*0.12,pop(),0.25)
for k,tc in enumerate(ev['checks']): A(tc,kick(0.18,140,70),0.45); A(tc+0.02,chime([1046,1318,1568,2093][k]),0.2)
# ---- s6 sickness
s6=sc('s6')['start']
for k in range(int((ev['flatdeath']-s6)/0.9)): A(s6+0.2+k*0.9,beep(0.1,880),0.15)
A(ev['flatdeath'],beep(0.8,880)*np.linspace(1,0,int(0.8*SR)),0.15)
A(ev['flatdeath']+0.3,chime(1318),0.35); A(ev['flatdeath']+0.5,chime(1760),0.25)
M(s6,piano(220,3)+0.5*piano(277.2,3),0.3)
# ---- s7 angels of mercy
s7=sc('s7')['start']; d7=sc('s7')['end']-s7
M(s7,pad([261.6,329.6,392,493.9,587.3],d7+0.6,3000,a=1.2,r=1.0),0.45)
A(s7,whoosh(d7,f0=300,f1=2500),0.25)
for k in range(10): A(s7+0.3+k*0.4,chime([1568,2093,2637,1760,2349][k%5]),0.12)
for k in range(6): A(s7+0.5+k*0.6,filt(noise(0.25),300,1500)*env(0.25,0.05,r=0.1),0.12) # wings
# ---- s8 burial
a=seg('s8',0)['start']; A(a-0.1,water(1.4),0.4)
A(a+1.2,rustle(1.2),0.3)
for k in range(8): A(seg('s8',1)['start']-0.1+k*0.3,step(),0.25)
for k,ts in enumerate(ev['soil']): A(ts,soil(k),0.55)
s8=sc('s8'); M(s8['start'],pad([130.8,164.8,196],s8['end']-s8['start']+0.5,900),0.2)
# ---- grave
g0=sc('s9')['start']; g1=sc('s11')['start']
M(g0,pad([36.7,55,73.4],g1-g0+0.3,300,a=0.8,r=0.6),0.3)
A(g0,rumble(2.5),0.8); A(g0+0.5,thunder(),0.5)
for k,tq in enumerate(ev['qs']): A(tq,boom(1.4),0.75)
for k,ta in enumerate(ev['ans']):
    for j,f in enumerate((523.2,659.3,784,1046.5)[:2+k]): A(ta+j*0.05,chime(f*(1+k*0.12)),0.35)
    M(ta,pad([261.6*(1+k*0.12),329.6*(1+k*0.12),392*(1+k*0.12)],1.6,2500,a=0.05,r=0.8),0.3)
# ---- grave opens & garden
o0=sc('s11')['start']; o1=TOTAL
M(o0,pad([130.8,196,261.6,329.6,392],o1-o0,2600,a=1.5,r=2.5),0.4)
A(o0,whoosh(1.5,f0=200,f1=3000),0.35)
A(ev['door'],kick(0.5,70,40),0.6); A(ev['door']+0.1,whoosh(1.2,f0=500,f1=5000),0.4)
for k,f in enumerate((1046,1318,1568,2093)): A(ev['door']+0.2+k*0.15,chime(f),0.25)
riv=sc('s11')['start']+1.5
A(riv,filt(noise(o1-riv),300,3000)*env(o1-riv,1.0,r=1.5),0.06)
birds(riv,o1-riv-3,0.07)
s12=sc('s12')['start']
M(s12,(tone(523,0.25,'saw')*env(0.25,0.01,r=0.05)),0.06); M(s12+0.25,(tone(659,0.25,'saw')*env(0.25,0.01,r=0.05)),0.06); M(s12+0.5,(tone(784,0.35,'saw')*env(0.35,0.01,r=0.05)),0.06)
A(ev['swipe'],scratch(),0.4); A(ev['swipe']+0.05,whoosh(0.4,f0=600,f1=3000),0.3)
s13=sc('s13')['start']
for k in range(9): A(s13+0.3+k*0.38,chime([1568,1760,2093][k%3])*0.6,0.18); A(s13+0.3+k*0.38,whoosh(0.3,f0=1000,f1=4000)*0.4,0.12)
A(ev['busy'],thud(),0.45); A(ev['busy'],tick(),0.4); A(ev['busy']+0.3,chime(2093),0.2)
c0=sc('cta')['start']
for k in range(int((TOTAL-c0)/0.85)): A(c0+0.3+k*0.85,heart(),0.25)
for k in range(5): A(c0+0.4+k*0.35,beep(0.08,700+k*200),0.1)
M(TOTAL-2.6,piano(130.8,2.6)+piano(196,2.6)*0.6+piano(329.6,2.6)*0.5,0.35)
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
