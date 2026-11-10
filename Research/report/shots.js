// Screenshots of the running IntelliERP application for the report (Chapter 4).
//   node shots.js            (backend on :8000, frontend on :5173)
const puppeteer = require('puppeteer-core');
const OUT = __dirname + '/assets/';
const BASE = 'http://localhost:5173';

async function login(page, user, pass) {
  await page.goto(BASE + '/login', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: OUT + 'ui-login.png' });
  await page.type('#username', user);
  await page.type('#password', pass);
  await Promise.all([page.waitForNavigation({ waitUntil: 'networkidle0' }), page.click('button[type=submit]')]);
}

async function shot(page, route, name, wait = 2500) {
  await page.goto(BASE + route, { waitUntil: 'networkidle0', timeout: 120000 });
  await new Promise(r => setTimeout(r, wait));
  await page.screenshot({ path: OUT + name });
  console.log('saved', name);
}

(async () => {
  const only = process.argv[2];
  const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: true,
    args: ['--no-sandbox'], defaultViewport: { width: 1440, height: 900 } });
  const page = await browser.newPage();
  await login(page, 'admin', 'admin123');
  const pages = [
    ['/dashboard', 'ui-dashboard.png'], ['/sales', 'ui-sales.png'], ['/inventory', 'ui-inventory.png'],
    ['/procurement', 'ui-procurement.png'], ['/approvals', 'ui-approvals.png'], ['/suppliers', 'ui-suppliers.png'],
    ['/analytics', 'ui-analytics.png'], ['/analytics/products/P082', 'ui-analytics-product.png'],
    ['/procurement/PO-18305', 'ui-po-ai-draft.png'], ['/ai-insights', 'ui-ai-insights.png'], ['/audit-logs', 'ui-audit.png'], ['/settings', 'ui-settings.png'],
  ];
  if (only !== 'chat') for (const [route, name] of pages) if (!only || name.includes(only)) await shot(page, route, name, 6000);
  if (only === 'chat' || !only) {
    await page.goto(BASE + '/ai-assistant', { waitUntil: 'networkidle0' });
    await page.type('input[placeholder^="Ask a question"]',
      'Should we reorder "The Gu" red shirt XML tag t-shirt (White) XL (P082)? If so, how many units and from which supplier?');
    await page.keyboard.press('Enter');
    // wait until the send button is enabled again (answer arrived), at most 3 minutes
    await page.waitForFunction(() => !document.querySelector('button[type=submit]').disabled ||
      document.body.innerText.includes('Create draft purchase order'), { timeout: 180000 });
    await new Promise(r => setTimeout(r, 3000));
    await page.screenshot({ path: OUT + 'ui-ai-assistant.png' });
    await page.screenshot({ path: OUT + 'ui-ai-assistant-full.png', fullPage: true });
    console.log('saved ui-ai-assistant.png');
  }
  await browser.close();
})();
