#!/usr/bin/env python3
"""Build the profile's restrained Material 3 Expressive inspired SVG artwork.

No network requests. Optional FontTools outlines display glyphs from locally
installed fonts so that the published artwork looks the same on GitHub. Without
FontTools or those fonts, the SVG retains ordinary accessible text fallbacks.
"""
from pathlib import Path
from html import escape
from base64 import b64encode
import math
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FONT = "'Avenir Next','Google Sans','PingFang SC','Noto Sans CJK SC',sans-serif"
THEMES = {
    'light':dict(bg='#F5F7FB',surface='#E9EDF4',container='#DBE5F2',primary='#475F7D',ink='#1A2533',muted='#546171',outline='#C7D1DF',onprimary='#F3F6FC',secondary='#D4DBE5'),
    'dark':dict(bg='#151C25',surface='#202A36',container='#2C3D53',primary='#B4C8E3',ink='#E4EAF3',muted='#B8C2D0',outline='#414F62',onprimary='#23374F',secondary='#354352'),
}
FONTS={}
try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    for key,path,index in [
        ('latin-bold','/System/Library/Fonts/Avenir Next.ttc',0),
        ('latin','/System/Library/Fonts/Avenir Next.ttc',7),
        ('cjk-bold','/System/Library/Fonts/Hiragino Sans GB.ttc',2),
        ('cjk','/System/Library/Fonts/Hiragino Sans GB.ttc',0),
    ]:
        if Path(path).exists():
            f=TTFont(path,fontNumber=index)
            FONTS[key]=(f,f.getGlyphSet(),f.getBestCmap(),f['head'].unitsPerEm)
except ImportError:
    pass

def tx(x,y,label,size=24,color='#1A2533',weight=500):
    # Outlined text is limited to static artwork; the README repeats meaningful
    # content as selectable text, and each image has a descriptive alt attribute.
    if not FONTS:
        return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(label)}</text>'
    paths=[]
    cursor=float(x)
    for char in label:
        key='latin' if ord(char)<128 else 'cjk'
        if weight>=600:key+='-bold'
        entry=FONTS.get(key)
        if not entry:continue
        font,gs,cmap,em=entry
        glyph=cmap.get(ord(char))
        if not glyph:
            cursor+=size*.4
            continue
        pen=SVGPathPen(gs)
        gs[glyph].draw(pen)
        data=pen.getCommands()
        if data:
            paths.append(f'<path d="{data}" transform="translate({cursor:.3f} {y}) scale({size/em:.6f} {-size/em:.6f})"/>')
        cursor+=font['hmtx'][glyph][0]*size/em
    return f'<g fill="{color}" aria-label="{escape(label,quote=True)}">'+''.join(paths)+'</g>'

def rounded(x,y,w,h,r,fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'

def flower(cx,cy,r,fill):
    # A 12-lobed Material-esque shape. It represents the "soft box" rather than
    # acting as an unrelated decorative sparkle.
    points=[]
    for i in range(241):
        a=i/240*math.tau
        rr=r*(.925+.075*math.cos(12*a))
        points.append(f'{cx+rr*math.cos(a):.2f},{cy+rr*math.sin(a):.2f}')
    return '<path d="M'+' L'.join(points)+'Z" fill="'+fill+'"/>'

def code_mark(cx,cy,size,color):
    return f'<g transform="translate({cx} {cy}) scale({size/100})" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="m-24-22-23 22 23 22m48-44 23 22-23 22M9-32-9 32"/></g>'

def play_mark(cx,cy,size,color):
    return f'<path d="M{cx-size*.27} {cy-size*.43}Q{cx-size*.4} {cy-size*.5} {cx-size*.4} {cy-size*.3}V{cy+size*.3}Q{cx-size*.4} {cy+size*.5} {cx-size*.2} {cy+size*.4}L{cx+size*.43} {cy+size*.06}Q{cx+size*.54} {cy} {cx+size*.43} {cy-size*.06}Z" fill="{color}"/>'

CSS='.arrive{animation:arrive .75s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}@keyframes arrive{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}@media(prefers-reduced-motion:reduce){.arrive{animation:none}}'

def save(name,w,h,title,body,defs='',animated=False):
    p=ASSETS/name
    p.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">硬盒子和软盒子。克制的雾蓝灰、层次化色面与柔和形状。原创 GitHub 主页素材。</desc><!-- Design: Brand | M3 Expressive inspired | Color: muted blue tonal palette | Shape: soft square + scalloped circle | No gradients, glow, HUD, or decorative telemetry -->{f'<defs>{defs}</defs>' if defs else ''}{f'<style>{CSS}</style>' if animated else ''}{body}</svg>''',encoding='utf8')

for theme,p in THEMES.items():
    suffix='' if theme=='light' else '-dark'
    for mobile in [False,True]:
        w,h=(640,680) if mobile else (1280,480)
        s=rounded(0,0,w,h,40,p['surface'])
        if mobile:
            s+=tx(36,69,'硬盒子和软盒子',27,p['muted'])
            s+=tx(32,166,'写代码，',70,p['ink'],800)
            s+=tx(32,254,'也拍视频。',70,p['ink'],800)
            s+='<g class="arrive">'
            s+=f'<g transform="rotate(-9 391 443)">{rounded(265,317,252,252,68,p["primary"])}{code_mark(391,443,118,p["onprimary"])}</g>'
            s+=flower(202,480,104,p['container'])+play_mark(205,480,69,p['primary'])+'</g>'
            s+=tx(36,617,'lzy3090Ti',31,p['ink'],700)
            s+=tx(36,653,'学生开发者 · 科技内容创作者',19,p['muted'])
        else:
            s+=tx(52,66,'硬盒子和软盒子',24,p['muted'])
            s+=tx(47,177,'写代码，',80,p['ink'],800)
            s+=tx(47,279,'也拍视频。',80,p['ink'],800)
            s+=tx(52,374,'lzy3090Ti',38,p['ink'],700)
            s+=tx(54,421,'学生开发者 · 科技内容创作者',22,p['muted'])
            s+='<g class="arrive">'
            s+=f'<g transform="rotate(-9 979 217)">{rounded(831,69,296,296,82,p["primary"])}{code_mark(979,217,145,p["onprimary"])}</g>'
            s+=flower(858,340,116,p['container'])+play_mark(864,340,77,p['primary'])+'</g>'
        save('hero'+('-mobile' if mobile else '')+suffix+'.svg',w,h,'硬盒子和软盒子 · 写代码，也拍视频 · lzy3090Ti',s,animated=False)
    # Compact M3-style filled / tonal link buttons, not status badges.
    for name,label,kind,fill,ink in [
        ('github-link','看我的代码','code',p['container'],p['ink']),
        ('bilibili-link','去 B 站看看','video',p['primary'],p['onprimary']),
    ]:
        s=rounded(0,0,360,88,44,fill)
        if kind=='code':s+=code_mark(55,44,43,ink)
        else:
            s+=f'<g fill="none" stroke="{ink}" stroke-width="3.1" stroke-linecap="round"><rect x="30" y="29" width="48" height="34" rx="9"/><path d="m41 20 10 9m15-9-10 9M44 41v9m21-9v9"/></g>'
        s+=tx(102,55,label,28,ink,600)
        save(name+suffix+'.svg',360,88,label,s)
    # A track illustration communicates the F1 project without fabricating UI.
    s=rounded(0,0,1280,440,36,p['surface'])
    s+=tx(44,65,'最近的一个作品',23,p['muted'])
    s+=tx(40,151,'F1 Calendar',65,p['ink'],800)
    s+=tx(44,211,'赛历、倒计时、车队积分。',29,p['muted'])
    s+=tx(44,257,'把一整个赛季装进口袋。',29,p['muted'])
    s+=rounded(44,333,136,52,26,p['container'])+tx(72,368,'Flutter',25,p['ink'])
    s+=rounded(192,333,153,52,26,p['container'])+tx(217,368,'Android',25,p['ink'])
    s+=f'<g transform="translate(780 48)"><path d="M46 105Q8 35 85 26L276 5Q337 0 328 62L317 118Q310 143 336 164L376 197Q414 230 356 251L226 299Q183 312 170 268L159 230Q154 206 126 216L78 237Q20 259 24 205L30 158Q34 135 46 105Z" fill="none" stroke="{p["container"]}" stroke-width="64" stroke-linejoin="round"/><path d="M46 105Q8 35 85 26L276 5Q337 0 328 62L317 118Q310 143 336 164L376 197Q414 230 356 251L226 299Q183 312 170 268L159 230Q154 206 126 216L78 237Q20 259 24 205L30 158Q34 135 46 105Z" fill="none" stroke="{p["primary"]}" stroke-width="13" stroke-linejoin="round" stroke-linecap="round"/>'
    s+=f'<circle cx="166" cy="17" r="17" fill="{p["primary"]}"/>'
    s+='</g>'
    save('project-f1'+suffix+'.svg',1280,440,'F1 Calendar · Flutter Android 赛历客户端。右侧为原创赛道造型插画，并非应用界面。',s)
    s=rounded(0,0,1280,188,36,p['surface'])
    s+=flower(100,94,65,p['container'])+play_mark(104,94,48,p['primary'])
    s+=tx(194,81,'视频里见。',40,p['ink'],700)+tx(196,128,'硬件折腾、软件作品，还有科技影像。',25,p['muted'])
    s+=rounded(963,62,268,66,33,p['primary'])+tx(1002,106,'硬盒子和软盒子',25,p['onprimary'])
    save('channel'+suffix+'.svg',1280,188,'B 站 · 硬盒子和软盒子 · 点击进入视频频道',s)
    s=rounded(0,0,1280,108,32,p['surface'])
    s+=tx(40,66,'用热爱创造价值。',30,p['ink'])+tx(1021,64,'硬盒子和软盒子',19,p['muted'])
    save('footer'+suffix+'.svg',1280,108,'用热爱创造价值。硬盒子和软盒子。',s)

# Only remove artifacts from the superseded local draft.
for name in ['project-roll.svg','project-health.svg','project-random.svg']:
    (ASSETS/name).unlink(missing_ok=True)
print('Built M3E-inspired light / dark artwork. Text outlines:',bool(FONTS))
