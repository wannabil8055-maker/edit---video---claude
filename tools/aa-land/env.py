import subprocess, numpy as np
U="/root/.claude/uploads/ffb22ac1-847d-548f-85f3-a6d14c35e14b"
IDS=dict(C1="8483ee9e",C2="34acb93c",C3="93ba5df3",C4="ffcb6c5d",C5="580da4ef",C6="a83204c1",C7="de74bf62")
_cache={}
def env(c, hop=0.01):
    if c in _cache: return _cache[c]
    raw=subprocess.run(["ffmpeg","-v","error","-i",f"{U}/{IDS[c]}-8640019636340790741.mov","-af","highpass=f=250,lowpass=f=3500","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    x=np.frombuffer(raw,np.int16).astype(float)/32768; h=int(16000*hop)
    e=np.array([np.sqrt(np.mean(x[i:i+h*2]**2)) for i in range(0,len(x)-2*h,h)])
    db=20*np.log10(e+1e-9); _cache[c]=db; return db
