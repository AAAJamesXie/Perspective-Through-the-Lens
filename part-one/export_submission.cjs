// Export the current public study pages at their actual desktop layout.
const {chromium}=require('playwright');
const {PDFDocument}=require('pdf-lib');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
(async()=>{
 const root=path.resolve(__dirname,'..'),out=path.join(__dirname,'submission'),qa=path.join(root,'qa/part-one');
 fs.mkdirSync(qa,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const merged=await PDFDocument.create(),checks=[];
 try{
  for(const folder of ['1','2','3']){
   const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(path.join(root,folder,'index.html')).href);
   await page.locator('img').evaluateAll(async ims=>{ims.forEach(im=>im.loading='eager');await Promise.all(ims.map(im=>im.decode()))});
   await page.evaluate(()=>document.fonts.ready);
   // Freeze only the GIF for deterministic PDF output, retaining its exact first frame.
   await page.locator('img[src$=".gif"]').evaluateAll((ims,data)=>Promise.all(ims.map(im=>{im.src=data;return im.decode()})), 'data:image/png;base64,'+fs.readFileSync(path.join(qa,'dolly-static.png')).toString('base64'));
   await page.emulateMedia({media:'screen'});
   const state=await page.evaluate(()=>({height:Math.ceil(Math.max(document.documentElement.scrollHeight,document.body.getBoundingClientRect().bottom))+16,width:document.documentElement.scrollWidth,broken:[...document.images].filter(im=>!im.complete||!im.naturalWidth).map(im=>im.src),mainText:document.querySelector('main').innerText}));
   if(state.width>1440||state.broken.length||errors.length)throw Error(JSON.stringify({folder,state,errors}));
   await page.addStyleTag({content:`@page{size:1440px ${state.height}px;margin:0}html{scroll-behavior:auto}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}`});
   await page.screenshot({path:path.join(qa,`website-source-${folder}.png`),fullPage:true});
   const bytes=await page.pdf({width:'1440px',height:`${state.height}px`,margin:{top:0,bottom:0,left:0,right:0},printBackground:true,preferCSSPageSize:true});
   const doc=await PDFDocument.load(bytes);
   if(doc.getPageCount()!==1)throw Error(`Expected one full-height page for study ${folder}`);
   for(const copied of await merged.copyPages(doc,[0]))merged.addPage(copied);
   checks.push({study:folder,pages:1,height:state.height,width:1440,brokenImages:0,mainText:state.mainText});
   await page.close();
  }
  merged.setTitle('SYDE 671 Assignment 1 - Part One');merged.setAuthor('James Xie');
  fs.writeFileSync(path.join(out,'part-one-report.pdf'),await merged.save());
  fs.writeFileSync(path.join(qa,'website-export-checks.json'),JSON.stringify(checks,null,2));
  console.log(JSON.stringify(checks.map(({mainText,...rest})=>rest)));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
