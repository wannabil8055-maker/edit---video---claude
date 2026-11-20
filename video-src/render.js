const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
const S=process.argv[2], mode=process.argv[3];
(async()=>{
 const tl=JSON.parse(fs.readFileSync(S+'/build/timeline.json'));
 const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
 const errs=[];pg.on('pageerror',e=>errs.push(e.message));pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await pg.goto('file://'+S+'/render/anim.html');await pg.evaluate(tl=>init(tl),tl);
 if(mode==='stills'){
   const times=process.argv[4].split(',').map(Number);fs.mkdirSync(S+'/stills',{recursive:true});
   for(const t of times){const d=await pg.evaluate(t=>frame(t,0.85),t);fs.writeFileSync(`${S}/stills/f_${t.toFixed(2)}.jpg`,Buffer.from(d.split(',')[1],'base64'))}
 } else {
   const fps=24,n=Math.round(tl.total*fps);
   const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-i',S+'/build/mix.wav','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-movflags','+faststart','-shortest',process.argv[4]],{stdio:['pipe','inherit','inherit']});
   const t0=Date.now();
   for(let i=0;i<n;i++){const d=await pg.evaluate(t=>frame(t,0.93),i/fps);const buf=Buffer.from(d.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%120===0)console.log('frame',i,'/',n,((Date.now()-t0)/1000).toFixed(0)+'s')}
   ff.stdin.end();await new Promise(r=>ff.on('close',r));
 }
 if(errs.length)console.log('ERRORS',[...new Set(errs)].slice(0,10));
 await b.close();
})();
