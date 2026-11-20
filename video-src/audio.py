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
for sc,lead in [('s4',0.45),('s6',0.3),('s7',0.0),('s9',0.6),('s14',0.2),('s11',0.05)]:
    scenes[sc]['start']-=lead
keys=order
for a,b in zip(keys,keys[1:]): scenes[a]['end']=scenes[b]['start']
scenes[keys[-1]]['end']=TOTAL
SEGI={s['i']:s for s in segs}
def seg(sc,k=0): return SEGI[scenes[sc]['segs'][k]]
ev={}  # named events (absolute times) for renderer
ev['beatcut']=0.8; ev['crack']=1.3
ev['drops']=[seg('s4',k)['start']-0.08 for k in range(3)]
ev['stamps']=[seg('s4',3)['start']+0.1+0.28*k for k in range(4)]
ev['crash']=seg('s6')['end']+0.45
ev['soil']=[seg('s8',3)['start']+0.15+0.45*k for k in range(4)]
ev['qs']=[seg('s10',k)['start']-0.05 for k in range(3)]
ev['hammer']=seg('s11',0)['end']+0.1
ev['snap']=ev['hammer']+0.9
ev['busy']=seg('s13')['end']-0.6
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
for k in range(5): A(0.05+k*0.15,tick(),0.5)
A(0.3,pop(),0.3); A(0.55,pop(),0.3)
# trendy beat 0-0.8
def beatbar(t0,dur,lp=None,g=1.0):
    bpm=140; b=60/bpm; n=int(dur/b/0.5)
    buf=np.zeros(int((dur+1)*SR))
    bass_notes=[55,55,65.4,49]
    for i in range(n):
        tt0=i*b*0.5
        if i%8 in (0,3,6): add_local(buf,tt0,kick(0.35),0.9)
        if i%8==4: add_local(buf,tt0,filt(noise(0.15),1200,8000)*env(0.15,0.001,curve=9),0.5)
        add_local(buf,tt0,filt(noise(0.03),7000)*env(0.03,0.001,curve=8),0.18)
        if i%2==0:
            f=bass_notes[(i//8)%4]; add_local(buf,tt0,tone(f,0.25)*env(0.25,0.005,curve=3),0.5)
        if i%4==2:
            f=[440,523,659,587][(i//4)%4]; add_local(buf,tt0,(tone(f,0.18,'saw')*env(0.18,0.002,curve=6)),0.08)
    buf=buf[:int(dur*SR)]
    if lp: buf=filt(buf,hi=lp)
    M(t0,buf*env(dur,0.01,r=0.05),g)
beatbar(0,0.8,None,0.8)
A(0.8,beep(),0.35); A(1.05,beep(),0.35); A(1.3,beep(0.9),0.3)
A(1.3,glass(),0.6); A(1.32,boom(),1.0)
A(sc('s1')['start']-0.6,whoosh(0.6,rev=True),0.5)
# ---- DUNYA (s1-s4) beat
d0=sc('s1')['start']; d1=sc('s5')['start']
beatbar(d0,d1-d0,lp=5000,g=0.55)
for k in range(10): A(d0+0.1+k*0.32,tick(),0.35)
A(d0+0.5,ting(),0.25); A(d0+1.6,ting(),0.2)
s2=sc('s2')['start']
for k in range(6): A(s2+0.2+k*0.3,pop(),0.25)
A(s2+0.4,whoosh(0.25,f0=800,f1=3000),0.3); A(s2+1.4,ting(),0.25)
A(sc('s2')['end']-0.5,kick(0.25,60,40),0.4)
s3=sc('s3')['start']
for k in range(8): A(s3+0.1+k*0.2,step(),0.35)
for k in range(14): A(s3+0.3+k*0.09,tick(),0.3)
for k,tdrop in enumerate(ev['drops']):
    A(tdrop-0.4,whistle(),0.8); A(tdrop,thud(),1.0)
A(ev['drops'][0]+0.15,filt(tone(55,1.2,'saw')+tone(82,1.2,'saw'),hi=600)*env(1.2,0.05,curve=2),0.35)
for k in range(10): A(ev['drops'][1]+0.3+k*0.04,ting()*0.3,0.3)
for k,ts in enumerate(ev['stamps']): A(ts,kick(0.18,140,70),0.5); A(ts,tick(),0.5)
A(ev['stamps'][0]-0.3,whoosh(0.9,f0=200,f1=1500),0.35)
# ---- s5 hajj missed
s5=sc('s5')['start']; A(s5,scratch(),0.6)
for k in range(int((sc('s5')['end']-s5)/0.5)): A(s5+0.3+k*0.5,tick(),0.35)
M(s5+0.2,piano(220,3.5),0.35); M(s5+1.4,piano(174.6,3),0.25)
# ---- s6 crash
s6=sc('s6')['start']; rdur=ev['crash']-s6+0.1
A(s6,filt(noise(rdur),900,7000)*env(rdur,0.2,r=0.05),0.12)
A(s6+0.5,ting(),0.3)
A(ev['crash']-1.0,filt(tone(220,1.0,'saw')+tone(277,1.0,'saw'),hi=1800)*np.linspace(0,1,int(SR))**2,0.35)
A(ev['crash']-0.55,filt(noise(0.55),2000,3500)*np.linspace(0.2,1,int(0.55*SR)),0.35)
A(ev['crash'],boom(2.0),1.0); A(ev['crash'],glass(),0.8); A(ev['crash'],filt(noise(0.6),hi=3000)*env(0.6,0.001,curve=5),0.9)
A(ev['crash']+0.4,tone(6800,3.0)*env(3.0,0.05,curve=2),0.05)
# ---- s7 soul
s7=sc('s7')['start']; d7=sc('s7')['end']-s7
A(s7,whoosh(d7,f0=150,f1=600)*0.6+filt(noise(d7),hi=400)*0.2,0.35)
for k in range(3): A(s7+0.2+k*0.9*(1+k*0.3),heart(),0.5*(1-k*0.25))
A(s7+1.6,screamish(),0.18)
# ---- s8 burial
s8=sc('s8'); a=seg('s8',0)['start']; A(a-0.15,water(1.5),0.45)
A(seg('s8',1)['start']-0.1,rustle(1.3),0.35)
for k in range(6): A(seg('s8',2)['start']-0.2+k*0.36,step(),0.3)
for k,ts in enumerate(ev['soil']): A(ts-0.15,filt(noise(0.2),1000,4000)*env(0.2,0.01,curve=4),0.2); A(ts,soil(k),0.9-0.12*k)
M(s8['start'],pad([110,130.8,164.8],s8['end']-s8['start']+1,700),0.22)
# ---- grave
g0=sc('s9')['start']; g1=sc('s13')['end']
M(g0,pad([36.7,55,73.4,77.8],g1-g0,300,a=1.0,r=2),0.35)
A(g0,rumble(2.5),0.9); A(g0+0.5,thunder(),0.6)
for k,tq in enumerate(ev['qs']): A(tq,boom(1.8),0.9); A(tq+0.05,thunder(),0.45)
mm=seg('s10',3)
for k in range(4): A(mm['start']+k*0.4,static(0.2),0.3)
A(ev['hammer']-0.45,whoosh(0.45,f0=100,f1=900),0.8)
A(ev['hammer'],kick(0.15,60,30),0.4)
bt=ev['hammer']+0.15
for k in range(6): A(bt+0.1+k*0.11,chirp(),0.12)
A(ev['snap'],pluck(659,1.6),0.5); A(ev['snap'],filt(noise(0.4),hi=150),0.4)
s12=sc('s12')['start']
for k in range(7): A(s12+0.4+k*0.55,plip(),0.25)
for k,f in enumerate((950,1400,1800)): A(s12+1.3+k*0.33,beep(0.3,f),0.15)
A(sc('s13')['start'],whoosh(2.5,f0=100,f1=500),0.35)
A(ev['busy'],thud(),0.6); A(ev['busy'],tick(),0.5)
M(s12,pad([110,130.8,164.8,196],sc('s12')['end']-s12+0.6,600),0.15)
# ---- hope
h0=sc('s14')['start']; h1=TOTAL
M(h0,pad([130.8,164.8,196,261.6],h1-h0,1400,a=1.2,r=2.5),0.32)
for k,f in enumerate((1046,1318,1568,2093)): A(h0+0.1+k*0.25,chime(f),0.3)
for k in range(10): A(h0+0.8+k*0.37*(1+(k%3)*0.4),chirp(),0.08)
for k in range(5): A(h0+3+k*0.9,chime([1568,1760,2093,1318,1568][k]),0.15)
c0=sc('cta')['start']
for k in range(int((TOTAL-c0)/0.9)): A(c0+0.3+k*0.9,beep(0.1,880),0.12)
A(c0+0.6,whoosh(0.9,f0=500,f1=4000),0.3)
M(TOTAL-2.6,piano(130.8,2.6)+piano(196,2.6)*0.6+piano(261.6,2.6)*0.5,0.35)

# ---------- VO + ducking ----------
for s in segs:
    x,_=sf.read(s['file']); add(vob,s['start'],x,1.0)
vob=vob/np.max(np.abs(vob))*0.9
envv=np.abs(vob); k=int(0.15*SR); envv=np.convolve(envv,np.ones(k)/k,'same'); envv=np.clip(envv/0.05,0,1)
duck=1-0.55*envv
# hard silence after hammer
hs=int(ev['hammer']*SR); he=int((ev['hammer']+0.12)*SR)
mix=vob+sfx*0.55*(1-0.35*envv)+mus*duck*0.6
mix[hs:he]*=np.linspace(1,0.05,he-hs)
mix=mix[:int(TOTAL*SR)]
mix=np.tanh(mix*1.1)/1.1
sf.write(f"{S}/build/mix.wav",mix.astype(np.float32),SR)
print("audio ok",len(mix)/SR)
