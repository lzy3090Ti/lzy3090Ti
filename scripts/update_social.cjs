#!/usr/bin/env node
// Read public follower totals only. No login, cookies, private lists or API signing.
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const ASSETS = path.join(ROOT, 'assets');
const CHANNELS = {
  bilibili: {
    name: 'B 站', id: '1785338201',
    url: 'https://space.bilibili.com/1785338201',
    source: 'https://api.bilibili.com/x/relation/stat?vmid=1785338201',
  },
  douyin: {
    name: '抖音', id: '94425926195',
    url: 'https://www.douyin.com/user/MS4wLjABAAAA3HU4TboUtHCHguxY0ZzIw46G55uOswpWQBci_sNSrqvHt80IZRpi2f940pjvtylP',
  },
};
const PALETTES = {
  light: { surface: '#E9EDF4', ink: '#1A2533', muted: '#546171', primary: '#475F7D', container: '#DBE5F2' },
  dark: { surface: '#202A36', ink: '#E4EAF3', muted: '#B8C2D0', primary: '#B4C8E3', container: '#2C3D53' },
};

function parseCount(value) {
  const match = String(value).trim().replaceAll(',', '').match(/^(\d+(?:\.\d+)?)(万|亿)?$/);
  if (!match) throw new Error('Missing or invalid follower count');
  const count = Number(match[1]) * ({ 万: 10000, 亿: 100000000 }[match[2]] || 1);
  if (!Number.isSafeInteger(count) || count < 0) throw new Error('Invalid follower count');
  return { count, approximate: Boolean(match[2]) };
}

function verifiedDouyin(header, fans) {
  if (!header.includes('硬盒子和软盒子') || !/抖音号[：:]\s*94425926195(?!\d)/.test(header)) {
    throw new Error('Douyin profile identity did not match');
  }
  return parseCount(fans.replace(/^\s*粉丝\s*/, '').trim());
}

function escape(value) {
  return String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
}

function render(key, entry, theme) {
  const p = PALETTES[theme];
  const channel = CHANNELS[key];
  const count = entry ? `${entry.approximate ? '约 ' : ''}${entry.followers.toLocaleString('en-US')} 粉丝` : '粉丝数暂不可用';
  const stamp = entry ? new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(entry.updated_at)) : '';
  const status = stamp ? `最近获取 ${stamp} · 北京时间` : '点击进入我的频道';
  const font = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',Arial,sans-serif";
  const icon = key === 'bilibili'
    ? `<g fill="none" stroke="${p.primary}" stroke-width="3.2" stroke-linecap="round"><rect x="475" y="35" width="53" height="39" rx="10"/><path d="m486 24 11 11m18-11-11 11M490 48v11m22-11v11"/></g>`
    : `<path d="M508 28v38a13 13 0 1 1-10-12m10-26q3 18 19 18" fill="none" stroke="${p.primary}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="560" height="190" viewBox="0 0 560 190" role="img"><title>${escape(channel.name + ' · 硬盒子和软盒子 · ' + count)}</title><desc>${escape(status)}。定时获取的公开数据，可能有延迟；点击查看频道当前粉丝数。</desc><rect width="560" height="190" rx="32" fill="${p.surface}"/>${icon}<g font-family="${font}"><text x="28" y="49" font-size="27" font-weight="600" fill="${p.ink}">${channel.name}</text><text x="26" y="111" font-size="43" font-weight="600" fill="${p.primary}">${escape(count)}</text><text x="28" y="158" font-size="17" fill="${p.muted}">${escape(status)}</text></g></svg>\n`;
}

async function fetchBilibili() {
  const res = await fetch(CHANNELS.bilibili.source, {
    headers: { 'User-Agent': 'lzy3090Ti-profile/1.0', Referer: CHANNELS.bilibili.url },
    signal: AbortSignal.timeout(25000),
  });
  if (!res.ok) throw new Error(`Bilibili HTTP ${res.status}`);
  const body = await res.json();
  if (body.code !== 0 || String(body.data?.mid) !== CHANNELS.bilibili.id || !Number.isSafeInteger(body.data?.follower) || body.data.follower < 0) {
    throw new Error('Bilibili response did not contain a verified follower count');
  }
  return { followers: body.data.follower, approximate: false, source: CHANNELS.bilibili.source };
}

async function fetchDouyin() {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.PROFILE_CHROMIUM_PATH ? { executablePath: process.env.PROFILE_CHROMIUM_PATH } : {}),
  });
  try {
    const page = await browser.newPage({ locale: 'zh-CN' });
    // Keep the normal anonymous public page; do not solve challenges or use login state.
    await page.goto(CHANNELS.douyin.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForFunction(() => /\d/.test(document.querySelector('[data-e2e="user-info-fans"]')?.textContent || ''), null, { timeout: 45000 });
    const header = await page.locator('[data-e2e="user-info"]').innerText();
    const fans = await page.locator('[data-e2e="user-info-fans"]').innerText();
    const parsed = verifiedDouyin(header, fans);
    return { followers: parsed.count, approximate: parsed.approximate, source: CHANNELS.douyin.url };
  } finally {
    await browser.close();
  }
}

async function writeAtomic(name, body) {
  const target = path.join(ASSETS, name);
  await fs.writeFile(target + '.tmp', body, 'utf8');
  await fs.rename(target + '.tmp', target);
}

async function main() {
  await fs.mkdir(ASSETS, { recursive: true });
  let data = { schema_version: 1, channels: {} };
  try { data = JSON.parse(await fs.readFile(path.join(ASSETS, 'social-data.json'), 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  let failures = 0;
  for (const [key, getCount] of Object.entries({ bilibili: fetchBilibili, douyin: fetchDouyin })) {
    try {
      const entry = await getCount();
      data.channels[key] = { name: '硬盒子和软盒子', account_id: CHANNELS[key].id, url: CHANNELS[key].url, ...entry, updated_at: new Date().toISOString() };
      console.log(`${key}: ${entry.followers} followers`);
    } catch (error) {
      failures++;
      // Do not turn errors into zero followers or advance the old timestamp.
      console.warn(`::warning::${key} unavailable; retaining last successful count and timestamp. ${error.message.split('\n')[0]}`);
    }
    for (const theme of Object.keys(PALETTES)) {
      await writeAtomic(`${key}-followers${theme === 'dark' ? '-dark' : ''}.svg`, render(key, data.channels[key], theme));
    }
  }
  await writeAtomic('social-data.json', JSON.stringify(data, null, 2) + '\n');
  if (failures && process.env.GITHUB_STEP_SUMMARY) {
    await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, `\n${failures} platform(s) could not refresh. Last successful figures and their original timestamps were preserved.\n`);
  }
  // A fully failed refresh must be visible in Actions. Assets remain intact.
  if (failures === 2) process.exitCode = 1;
}

module.exports = { parseCount, verifiedDouyin, render, CHANNELS };
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
