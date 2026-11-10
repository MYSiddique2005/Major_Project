// Renders every figure in figures/*.html to assets/<name>.png (the element with id="fig", at 2x scale).
//   node render.js [name]
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

(async () => {
  const dir = path.join(__dirname, 'figures');
  const only = process.argv[2];
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.html') && (!only || f.startsWith(only)));
  const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 1000, deviceScaleFactor: 2 });
  for (const f of files) {
    await page.goto('file://' + path.join(dir, f), { waitUntil: 'networkidle0' });
    await page.waitForFunction(() => window.__ready !== false, { timeout: 30000 });
    await new Promise(r => setTimeout(r, 800));
    const el = await page.$('#fig');
    await el.screenshot({ path: path.join(__dirname, 'assets', f.replace('.html', '.png')) });
    console.log('rendered', f);
  }
  await browser.close();
})();
