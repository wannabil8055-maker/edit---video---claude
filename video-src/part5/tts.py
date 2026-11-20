import sys, json, numpy as np, soundfile as sf, subprocess
sys.path.insert(0, sys.argv[1]+"/build")
from script import SEG
from kokoro_onnx import Kokoro
S=sys.argv[1]; T=S+"/tts"
k=Kokoro(f"{T}/kokoro-v1.0.onnx", f"{T}/voices-v1.0.bin")
narr = 0.55*k.get_voice_style("am_michael")+0.45*k.get_voice_style("am_onyx")
man = k.get_voice_style("am_puck"); him = 0.6*k.get_voice_style("am_eric")+0.4*k.get_voice_style("am_adam")
out=[]
for i,(sc,kind,txt,cap,p) in enumerate(SEG):
    v = man if kind=="man" else him if kind=="him" else narr
    sp = {"narr":1.1,"soft":1.0,"warm":1.08,"angel":0.95,"man":1.0,"him":1.0}[kind]
    a,sr = k.create(txt, voice=v, speed=sp, lang="en-us")
    raw=f"{S}/vo/raw{i:02d}.wav"; fn=f"{S}/vo/seg{i:02d}.wav"
    sf.write(raw,a,sr)
    filt={"narr":"anull","soft":"volume=0.75,highpass=f=120",
          "warm":"anull",
          "angel":"asetrate=24000*0.72,aresample=24000,atempo=1.25,aecho=0.8:0.7:90|180:0.5|0.35,lowpass=f=5000,volume=1.6",
          "man":"tremolo=f=7:d=0.35,volume=0.9","him":"aecho=0.8:0.5:60:0.2,volume=1.05"}[kind]
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af",filt+",silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse","-ar","48000","-ac","1",fn],check=True)
    d=sf.info(fn).duration
    out.append(dict(i=i,scene=sc,kind=kind,text=txt,cap=cap,pause=p,dur=round(d,3),file=fn))
    print(i,kind,round(d,2),txt)
json.dump(out,open(f"{S}/build/vo.json","w"),indent=1)
