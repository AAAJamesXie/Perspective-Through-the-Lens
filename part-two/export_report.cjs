/* Optional browser QA/PDF export. Uses an existing Playwright + Chrome install. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const root = __dirname;
  const output = path.join(root, 'submission');
  const qa = path.join(root, 'qa');
  fs.mkdirSync(output, { recursive: true });
  fs.mkdirSync(qa, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe'
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.join(root, 'index.html')).href, { waitUntil: 'load' });
    await page.evaluate(async () => { await document.fonts.ready; });
    const imageResults = await page.locator('img').evaluateAll(images => images.map(im => ({
      src: im.getAttribute('src'), loaded: im.complete && im.naturalWidth > 0
    })));
    if (imageResults.some(im => !im.loaded)) throw new Error('One or more report images failed to load.');
    const links = await page.locator('a').evaluateAll(anchors => anchors.map(a => a.getAttribute('href')));
    const missing = links.filter(href => !/^(https?:|#)/.test(href))
      .map(href => path.resolve(root, href.split('#')[0])).filter(file => !fs.existsSync(file));
    // This export creates the PDF; all other links must already exist.
    const unexpected = missing.filter(file => file !== path.join(output, 'part-two-report.pdf'));
    if (unexpected.length) throw new Error('Missing linked files: '+unexpected.join(', '));
    await page.screenshot({ path: path.join(qa, 'desktop.png') });
    await page.locator('#single').screenshot({ path: path.join(qa, 'experiments.png') });
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await mobile.goto(pathToFileURL(path.join(root, 'index.html')).href, { waitUntil: 'load' });
    await mobile.screenshot({ path: path.join(qa, 'mobile.png') });
    const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    await mobile.close();
    if (overflow) throw new Error('Mobile page overflows horizontally.');
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(output, 'part-two-report.pdf'), format: 'A4',
      printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
      headerTemplate: '<div></div>', footerTemplate: '<div style="width:100%;text-align:center;font-size:8px;color:#626b63">SYDE 671 · Part Two — <span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
    const result = { images: imageResults.length, loaded_images: imageResults.filter(i => i.loaded).length,
      internal_links_checked: links.filter(href => !/^(https?:|#)/.test(href)).length,
      mobile_horizontal_overflow: overflow, page_errors: errors };
    fs.writeFileSync(path.join(qa, 'browser-checks.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
    if (errors.length) throw new Error('Browser page errors occurred.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
