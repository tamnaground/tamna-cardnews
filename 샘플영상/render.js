// 사용법: node render.js [scene HTML 경로] [fps]
// timeline.json의 total(초)에 맞춰 프레임별 스크린샷을 frames/f%04d.png로 저장한다.
const playwright = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const htmlPath = process.argv[2] || 'scene_generated.html';
  const fps = parseInt(process.argv[3] || '30', 10);
  const total = JSON.parse(fs.readFileSync('timeline.json', 'utf8')).total;
  const nFrames = Math.ceil(total * fps);

  let browser;
  try {
    browser = await playwright.chromium.launch();
  } catch (e) {
    browser = await playwright.chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  }
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(htmlPath));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);

  fs.mkdirSync('frames', { recursive: true });
  for (let f = 0; f < nFrames; f++) {
    await page.evaluate(ms => window.seek(ms), (f / fps) * 1000);
    await page.screenshot({ path: `frames/f${String(f + 1).padStart(4, '0')}.png` });
    if (f % 60 === 0) console.log(`frame ${f}/${nFrames}`);
  }
  await browser.close();
  console.log(`done: ${nFrames} frames`);
})();
