// 사용법: node shoot.js jobs.json
// jobs.json: [{ "html": "<절대경로>.html", "png": "<절대경로>.png" }, ...]
const playwright = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  let browser;
  try {
    browser = await playwright.chromium.launch();
  } catch (e) {
    browser = await playwright.chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  }
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const job of jobs) {
    await page.goto('file://' + job.html);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.png });
    console.log('shot:', job.png);
  }
  await browser.close();
})();
