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
for sc,lead in [('s5',0.2)]:
    scenes[sc]['start']-=lead
keys=order
for a,b in zip(keys,keys[1:]): scenes[a]['end']=scenes[b]['start']
scenes[keys[-1]]['end']=TOTAL
SEGI={s['i']:s for s in segs}
def seg(sc,k=0): return SEGI[scenes[sc]['segs'][k]]
ev={}
ev['spot']=0.15; ev['drop']=0.85
ev['words']=[0.85,1.15,1.45,1.75]
ev['snip']=seg('s3')['start']+0.9
ev['ticks']=[seg('s4',k)['start']+0.15 for k in (1,2,3,4)]
ev['outfits']=[seg('s5',k)['start']-0.1 for k in (1,2,3,4)]
ev['shatter']=seg('s7',0)['start']+1.2
ev['comment']=seg('cta')['start']+1.5
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
# ---- humming nasheed bed (voice-only)
def rnd_t(k): return (np.sin(k*12.9898)*43758.5453)%1
def hum(f,d,vib=5.0,form=(320,850)):
    tt=T(d); fm=f*(1+0.006*np.sin(2*np.pi*vib*tt)*np.clip(tt/0.4,0,1))
    ph=2*np.pi*np.cumsum(fm)/SR; x=sum(np.sin(h*ph)/h**1.1 for h in range(1,14))
    y=filt(x,form[0]*0.6,form[0]*1.6)*1.0+filt(x,form[1]*0.7,form[1]*1.3)*0.35+filt(x,80,300)*0.5
    y+=filt(noise(d),300,2000)*0.015
    return norm(y)*env(d,min(0.25,d*0.3),r=min(0.35,d*0.4))
def melody(t0,notes,g=0.3,form=(320,850)):
    t=t0
    for f,d in notes:
        if f>0: M(t,hum(f,d*1.08,form=form),g)
        t+=d
    return t
def drone(t0,d,fs,g):
    for f in fs: M(t0,hum(f,d,vib=4.0),g)
Am=[220,261.6,329.6]; F=[174.6,220,261.6]; C=[130.8,164.8,196]; G=[196,246.9,293.7]; Dm=[146.8,174.6,220]
def chordbed(t0,d,ch,g=0.12): drone(t0,d,ch,g)
# HOOK
def snap(): d=0.08; return filt(noise(d),1500,7000)*env(d,0.001,curve=10)
def clap(): d=0.15; return filt(noise(d),900,6000)*env(d,0.002,curve=8)
def shutter(): x=np.zeros(int(0.12*SR)); add_local(x,0,tick(),1); add_local(x,0.05,filt(noise(0.05),2000,8000)*env(0.05,0.001,curve=6),0.6); return x
def chicbeat(t0,dur,g=0.5,lp=None):
    bpm=104; b=60/bpm; n=int(dur/(b/2)); buf=np.zeros(int((dur+1)*SR))
    prog=[(146.8,174.6,220),(130.8,164.8,196),(116.5,146.8,174.6),(130.8,164.8,196)]
    for i in range(n):
        tt0=i*b/2
        if i%4==0: add_local(buf,tt0,kick(0.3,110,48),0.7)
        if i%4==2: add_local(buf,tt0,snap(),0.5); add_local(buf,tt0,clap(),0.3)
        add_local(buf,tt0,filt(noise(0.025),7000)*env(0.025,0.001,curve=8),0.1)
        ch=prog[(i//8)%4]
        if i%2==0: add_local(buf,tt0,tone(ch[0]/2,0.22)*env(0.22,0.005,curve=3),0.45)
        if i%2==1: f=ch[(i//2)%3]*2; add_local(buf,tt0,(tone(f,0.16,'saw')*env(0.16,0.002,curve=7)),0.05); add_local(buf,tt0,piano(f*2,0.4)*0.3,0.12)
    buf=buf[:int(dur*SR)]
    if lp: buf=filt(buf,hi=lp)
    M(t0,buf*env(dur,0.02,r=0.2),g)
A(ev['spot'],kick(0.2,200,90),0.6); A(ev['spot'],tick(),0.6)
for k in range(5): A(0.3+k*0.09,shutter(),0.4)
A(ev['drop'],boom(1.2),0.6)
for tw in ev['words']: A(tw,kick(0.15,150,70),0.3)
A(2.3,whoosh(0.7,f0=300,f1=3000),0.35)
s1=sc('s1')['start']; s2=sc('s2')['start']; s3=sc('s3')['start']; s6=sc('s6')['start']; s7=sc('s7')['start']; c0=sc('cta')['start']
chicbeat(ev['drop'],s1-ev['drop']+0.3,0.5)
# s1 sad
M(s1+0.4,hum(220,0.5)*1,0.15); M(s1+0.9,hum(207.7,0.5),0.15); M(s1+1.4,hum(196,1.2),0.15)
A(s1+0.3,tick(),0.4); A(s1+2.5,filt(noise(0.8),200,1500)*env(0.8,0.2,r=0.4),0.15)
# s2 sincere
A(s2+0.2,rustle(0.5),0.25); chordbed(s2,s3-s2+0.4,F,0.12)
for k,f in enumerate((784,988,1175)): A(s2+1.5+k*0.2,chime(f),0.2)
# s3 onward beat
chicbeat(s3,s6-s3,0.42)
A(ev['snip'],filt(noise(0.1),3000,8000)*env(0.1,0.001,curve=6),0.5); A(ev['snip']+0.12,filt(noise(0.1),3000,8000)*env(0.1,0.001,curve=6),0.5); A(ev['snip']+0.4,pop(),0.5)
for tk in ev['ticks']: A(tk,tick(),0.5); A(tk+0.05,chime(1568),0.2); A(tk,rustle(0.4),0.15)
for k,to in enumerate(ev['outfits']):
    A(to-0.2,whoosh(0.5,f0=500,f1=4000),0.4); A(to+0.25,chime([1318,1568,1760,2093][k]),0.3); A(to+0.3,shutter(),0.35); A(to+0.45,shutter(),0.3)
chordbed(s6,s7-s6+0.4,C,0.13)
for k,f in enumerate((1568,1760,2093,2637)): A(s6+0.3+k*0.3,chime(f),0.15)
chicbeat(s7,TOTAL-s7,0.38)
A(ev['shatter'],glass(),0.4); A(ev['shatter']+0.2,chime(2637),0.3); A(ev['shatter']+0.25,chime(3136),0.2)
A(ev['comment'],pop(),0.5); A(ev['comment'],ting(),0.2)
for k in range(5): A(c0+0.5+k*0.3,shutter(),0.25)
A(TOTAL-0.5,kick(0.2,200,90),0.4)
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
