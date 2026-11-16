const { test } = require('node:test');
const assert = require('node:assert/strict');
const { parseCount, verifiedDouyin, render } = require('./update_social.cjs');

test('accepts zero and exact totals, flags abbreviated totals', () => {
  assert.deepEqual(parseCount('0'), { count: 0, approximate: false });
  assert.deepEqual(parseCount('1,927'), { count: 1927, approximate: false });
  assert.deepEqual(parseCount('1.2万'), { count: 12000, approximate: true });
});

test('missing or challenged figures cannot become zero followers', () => {
  for (const value of ['', '粉丝', '登录后查看', '-1', 'NaN', '2.5']) {
    assert.throws(() => parseCount(value));
  }
});

test('rejects another account even when its name or number is similar', () => {
  assert.throws(() => verifiedDouyin('硬盒子和软盒子 抖音号：94425926196', '粉丝\n1927'));
  assert.throws(() => verifiedDouyin('硬盒子和软盒子 抖音号：944259261950', '粉丝\n1927'));
  assert.throws(() => verifiedDouyin('另一个账号 抖音号：94425926195', '粉丝\n1927'));
  assert.deepEqual(verifiedDouyin('硬盒子和软盒子\n抖音号：94425926195\nIP属地：安徽', '粉丝\n1927'), { count: 1927, approximate: false });
});

test('shows the original fetch time in Beijing time and marks rounded counts', () => {
  const svg = render('douyin', { followers: 12000, approximate: true, updated_at: '2026-11-16T16:05:00.000Z' }, 'dark');
  assert.match(svg, /约 12,000 粉丝/);
  assert.match(svg, /2026-11-17 00:05/);
  assert.doesNotMatch(svg, /实时|LIVE/);
  const missing = render('douyin', null, 'light');
  assert.match(missing, /粉丝数暂不可用/);
  assert.doesNotMatch(missing, />0 粉丝</);
});
