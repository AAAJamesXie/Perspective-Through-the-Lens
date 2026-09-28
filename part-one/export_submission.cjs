// Export and inspect the actual local submission webpage in Chromium.
const {chromium} = require('playwright');
const path = require('path');
const fs = require('fs');
const {pathToFileURL, fileURLToPath} = require('url');
(async () => {
  const out = path.join(__dirname, 'submission');
  const browser = await chromium.launch({headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  try {
    const page = await browser.newPage({viewport:{width:1000,height:1200}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(out, 'webpage/index.html')).href);
    await page.locator('img').evaluateAll(ims => Promise.all(ims.map(im => im.decode())));
    await page.emulateMedia({media:'print'});
    const checks = await page.evaluate(() => ({
      sections: document.querySelectorAll('.page').length,
      brokenImages: [...document.images].filter(im => !im.complete || !im.naturalWidth).map(im=>im.src),
      contentOverlapsFooter: [...document.querySelectorAll('.page')].map((s,i)=>({page:i+1,footerTop:s.querySelector('footer').getBoundingClientRect().top,lastContentBottom:Math.max(...[...s.children].filter(el=>el.tagName!=='FOOTER' && getComputedStyle(el).display!=='none').map(el=>el.getBoundingClientRect().bottom))})),
      links:[...document.querySelectorAll('a[href]')].map(a=>a.href)
    }));
    if(checks.sections!==5 || checks.brokenImages.length || errors.length || checks.contentOverlapsFooter.some(x=>x.lastContentBottom>x.footerTop-8)) throw Error(JSON.stringify({checks,errors}));
    await page.pdf({path:path.join(out,'part-one-report.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
    for(const href of checks.links) if(href.startsWith('file:') && !fs.existsSync(fileURLToPath(href))) throw Error('Missing link: '+href);
    await page.emulateMedia({media:'screen'});
    await page.setViewportSize({width:390,height:844});
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    if(overflow) throw Error('Mobile overflow');
    const qa=path.join(__dirname,'..','qa','part-one');
    fs.mkdirSync(qa,{recursive:true});
    fs.writeFileSync(path.join(qa,'browser-checks.json'),JSON.stringify({checks,errors,mobileOverflow:overflow},null,2));
    console.log(JSON.stringify({pages:checks.sections,brokenImages:checks.brokenImages.length,mobileOverflow:overflow,footerClearances:checks.contentOverlapsFooter.map(x=>Math.round(x.footerTop-x.lastContentBottom))}));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
