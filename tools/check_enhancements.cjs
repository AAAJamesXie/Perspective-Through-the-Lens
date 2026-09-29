/* Read-only page checks; only screenshots and a QA record are written. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const dir = path.join(root, 'part-two');
  const qa = path.join(root, 'qa', 'bells-whistles');
  fs.mkdirSync(qa, { recursive: true });
  const browser = await chromium.launch({ headless: true,
    executablePath: process.env.BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' });
  try {
    const checks = [];
    for (const width of [1440, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(pathToFileURL(path.join(dir, 'index.html')).href, { waitUntil: 'load' });
      await page.locator('img').evaluateAll(images => Promise.all(images.map(im => im.decode())));
      const result = await page.evaluate(() => ({
        images: document.images.length,
        brokenImages: [...document.images].filter(im => !im.complete || !im.naturalWidth).map(im => im.src),
        overflow: document.documentElement.scrollWidth > innerWidth,
        methods: [...document.querySelectorAll('#bells-whistles h3')].map(h => h.textContent),
        anchors: [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href'))
          .filter(h => !document.getElementById(h.slice(1))),
        links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))
      }));
      const missing = result.links.filter(h => !/^(https?:|#)/.test(h))
        .filter(h => !fs.existsSync(path.resolve(dir, h.split('#')[0])));
      delete result.links;
      if (result.brokenImages.length || result.overflow || result.anchors.length || missing.length || errors.length)
        throw Error(JSON.stringify({ result, missing, errors }));
      await page.evaluate(() => document.querySelector('#bells-whistles').scrollIntoView({ behavior: 'instant' }));
      await page.screenshot({ path: path.join(qa, `intro-${width}.png`) });
      if (width === 1440) {
        await page.locator('#bells-whistles .experiment').nth(2).screenshot({ path: path.join(qa, 'white-balance.png') });
        await page.locator('#bells-whistles .experiment').nth(0).screenshot({ path: path.join(qa, 'cropping.png') });
      }
      checks.push({ width, ...result, missing, errors });
      await page.close();
    }
    fs.writeFileSync(path.join(qa, 'checks.json'), JSON.stringify(checks, null, 2));
    console.log(JSON.stringify(checks, null, 2));
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
