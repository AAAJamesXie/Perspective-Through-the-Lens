/* Read-only browser checks of the site's real pages; only QA artifacts are written. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL, fileURLToPath } = require('url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const qa = path.join(root, 'qa');
  fs.mkdirSync(qa, { recursive: true });
  const browser = await chromium.launch({ headless: true,
    executablePath: process.env.BROWSER_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const results = [];
  try {
    for (const [name, file] of [['home','index.html'],['portrait','1/index.html'],
      ['street','2/index.html'],['dolly','3/index.html'],['color','part-two/index.html']]) {
      for (const width of [1440, 768, 390, 320]) {
        const page = await browser.newPage({ viewport: { width, height: 1000 } });
        const errors = [];
        page.on('pageerror', e => errors.push(e.message));
        const url = pathToFileURL(path.join(root, file)).href;
        await page.goto(url, { waitUntil: 'load' });
        await page.locator('img').evaluateAll(async images => {
          images.forEach(im => im.loading = 'eager');
          await Promise.all(images.map(im => im.decode().catch(() => {})));
        });
        const state = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth,
          h1: document.querySelectorAll('h1').length,
          brokenImages: [...document.images].filter(im => !im.complete || !im.naturalWidth).map(im => im.src),
          nav: [...document.querySelectorAll('.header-nav a')].map(a => ({ text: a.textContent.trim(), visible: a.getBoundingClientRect().width > 0 })),
          links: [...document.querySelectorAll('a[href]')].map(a => a.href)
        }));
        const missing = [];
        for (const href of state.links) {
          const target = new URL(href);
          if (target.protocol !== 'file:') continue;
          const targetPath = fileURLToPath(target);
          if (!fs.existsSync(targetPath)) missing.push(href);
          else if (target.hash && targetPath.endsWith('.html')) {
            const content = fs.readFileSync(targetPath, 'utf8');
            const id = decodeURIComponent(target.hash.slice(1));
            if (!content.includes(`id="${id}"`) && !content.includes(`id='${id}'`)) missing.push(href);
          }
        }
        if (width === 1440 || width === 390) {
          await page.screenshot({ path: path.join(qa, `${name}-${width}.png`) });
        }
        if (name === 'home' && width === 1440) {
          await page.screenshot({ path: path.join(qa, 'home-full.png'), fullPage: true });
          await page.getByRole('link', { name: 'Explore the studies' }).click();
          if (new URL(page.url()).hash !== '#part-one') throw new Error('Study anchor navigation failed.');
        }
        const result = { page: name, width, overflow: state.overflow, brokenImages: state.brokenImages,
          visibleNavLinks: state.nav.filter(a => a.visible).length, missingLinks: missing, pageErrors: errors };
        results.push(result);
        console.log(JSON.stringify(result));
        if (state.overflow || state.h1 !== 1 || state.brokenImages.length || missing.length || errors.length || result.visibleNavLinks !== 4) {
          throw new Error(`Browser validation failed: ${name} at ${width}px`);
        }
        await page.close();
      }
    }
    const reduced = await browser.newPage({ reducedMotion: 'reduce' });
    await reduced.goto(pathToFileURL(path.join(root, '3/index.html')).href);
    const src = await reduced.locator('picture img').evaluate(im => im.currentSrc);
    if (!src.endsWith('dolly-poster.jpg')) throw new Error('Reduced-motion poster is not selected.');
    fs.writeFileSync(path.join(qa, 'redesign-checks.json'), JSON.stringify({ results, reducedMotionPoster: true }, null, 2));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
