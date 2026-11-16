#!/usr/bin/env python3
"""Refresh a self-hosted GitHub public-data graphic without third-party widgets.

Uses only Python's standard library and official GitHub REST endpoints. The chart
counts public events, not commits or contributions; repository languages are counts
of each repository's primary language, not a measure of proficiency or code size.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import os
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
USER = 'lzy3090Ti'
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
BG, LINE, INK, MUTED, CYAN = '#0c1725','#294052','#eef6fc','#a0b7c8','#8be9ed'
COLORS = ['#8be9ed','#ffac8c','#badf99','#c3bbef','#e7c28c']

def api(path):
    headers = {'User-Agent': USER+'-profile','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer '+os.environ['GITHUB_TOKEN']
    req = urllib.request.Request('https://api.github.com/'+path, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as res:
                return json.load(res)
        except urllib.error.HTTPError as exc:
            if exc.code < 500 or attempt==2: raise
        except (urllib.error.URLError, TimeoutError):
            if attempt==2: raise
        time.sleep(2**attempt)

def tx(x,y,value,size=20,color=INK,weight=400,mono=False):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{MONO if mono else FONT}" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'

def render(snapshot,mobile=False,theme='light'):
    palettes = {
        'light':dict(bg='#E9EDF4',line='#C7D1DF',ink='#1A2533',muted='#546171',primary='#475F7D',track='#D6DFEA'),
        'dark':dict(bg='#202A36',line='#414F62',ink='#E4EAF3',muted='#B8C2D0',primary='#B4C8E3',track='#354352'),
    }
    p=palettes[theme]
    w,h=(640,780) if mobile else (1280,350)
    s=f'<rect width="{w}" height="{h}" rx="32" fill="{p["bg"]}"/>'
    def text(x,y,label,size=20,color=None,weight=400):
        return tx(x,y,label,size,color or p['ink'],weight)
    s+=text(32,54,'公开原创仓库  '+str(snapshot['original_repositories']),28,weight=600)
    if not mobile:s+=text(1055,52,snapshot['updated_utc']+' UTC',17,p['muted'])
    lx,ly=32,110
    s+=text(lx,ly,'仓库主语言',22,weight=600)
    languages=snapshot['primary_languages'][:5]
    max_count=max([n for _,n in languages],default=1)
    for i,(lang,count) in enumerate(languages):
        y=ly+35+i*33
        bx=210
        bw=338 if mobile else 290
        s+=text(lx,y,lang,19,p['muted'])
        s+=f'<rect x="{bx}" y="{y-12}" width="{bw}" height="12" rx="6" fill="{p["track"]}"/>'
        s+=f'<rect x="{bx}" y="{y-12}" width="{bw*count/max_count:.2f}" height="12" rx="6" fill="{p["primary"]}"/>'
        s+=text(bx+bw+18,y,count,18,p['primary'],600)
    s+=text(lx,ly+205,'按仓库数统计，展示前 5 种主语言。',16,p['muted'])
    ex,ey=(32,420) if mobile else (648,110)
    s+=text(ex,ey,'近 28 天公开事件',22,weight=600)
    events=snapshot['daily_public_events']
    graph_w=570 if mobile else 576
    graph_h=180 if mobile else 132
    base=ey+graph_h+45
    max_n=max([item['events'] for item in events],default=1) or 1
    s+=f'<path d="M{ex} {base}H{ex+graph_w}" stroke="{p["line"]}"/>'
    s+=text(ex,base-graph_h-8,max_n,13,p['muted'])
    s+=text(ex-2,base+4,0,13,p['muted'])
    bar_w=graph_w/28
    for i,item in enumerate(events):
        bh=item['events']/max_n*graph_h
        if bh:
            s+=f'<rect x="{ex+i*bar_w+4:.2f}" y="{base-bh:.2f}" width="{max(2,bar_w-7):.2f}" height="{bh:.2f}" rx="5" fill="{p["primary"]}"><title>{item["date"]}: {item["events"]} public events</title></rect>'
    s+=text(ex,base+29,events[0]['date'][5:],14,p['muted'])
    s+=text(ex+graph_w-56,base+29,events[-1]['date'][5:],14,p['muted'])
    if mobile:
        s+=f'<path d="M32 356H608" stroke="{p["line"]}"/>'
        s+=text(32,729,'数据更新于 '+snapshot['updated_utc']+' UTC',17,p['muted'])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{USER} 的公开仓库与活动</title><desc>主语言按公开原创仓库数统计，展示前 5 种。活动是最近 28 天的公开事件数，不等于提交数。数据更新于 {snapshot["updated_utc"]} UTC。</desc>{s}</svg>'

def main():
    repos=[]
    for page in range(1,101):
        batch=api(f'users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch)<100:break
    originals=[r for r in repos if not r['fork']]
    languages=Counter(r['language'] for r in originals if r.get('language'))
    now=datetime.now(timezone.utc)
    start=now.date()-timedelta(days=27)
    counts=Counter()
    # GitHub exposes at most 300 public events over its recent retention window.
    # Fetch all three pages to cover the 28-day interval where available.
    for page in range(1,4):
        batch=api(f'users/{USER}/events/public?per_page=100&page={page}')
        for event in batch:
            day=datetime.fromisoformat(event['created_at'].replace('Z','+00:00')).date()
            if start<=day<=now.date():counts[day.isoformat()]+=1
        if len(batch)<100:break
    snapshot={
        'username':USER,'updated_utc':now.strftime('%Y-%m-%d'),
        'original_repositories':len(originals),'excluded_forks':len(repos)-len(originals),
        'primary_languages':sorted(languages.items(),key=lambda p:(-p[1],p[0])),
        'daily_public_events':[{'date':(start+timedelta(days=i)).isoformat(),'events':counts[(start+timedelta(days=i)).isoformat()]} for i in range(28)],
        'source':'Official GitHub REST API; recent public events are limited to the latest 300.',
    }
    # Fetch everything before replacing assets; failures preserve the last good image.
    assets=ROOT/'assets'
    assets.mkdir(exist_ok=True)
    for name,body in [
        ('github-data.json',json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n'),
        ('activity.svg',render(snapshot)),('activity-mobile.svg',render(snapshot,True)),
        ('activity-dark.svg',render(snapshot,False,'dark')),('activity-mobile-dark.svg',render(snapshot,True,'dark')),
    ]:
        tmp=assets/(name+'.tmp')
        tmp.write_text(body,encoding='utf8')
        tmp.replace(assets/name)
    print(f'Updated {len(originals)} original repositories, {sum(counts.values())} public events in 28 days.')

if __name__=='__main__':main()
