from pathlib import Path
import xml.etree.ElementTree as ET, html, re, json
from datetime import datetime

ROOT=Path(__file__).parent
EXPORT=ROOT/'puroyorumlar.WordPress.2026-11-15.xml'
OUT=ROOT/'docs'
BASE='https://ardasenbaklavaci.github.io/puro-yorumlar-'
NS={'wp':'http://wordpress.org/export/1.2/','content':'http://purl.org/rss/1.0/modules/content/','excerpt':'http://wordpress.org/export/1.2/excerpt/'}

def text(item, tag, default=''):
    return item.findtext(tag, default=default, namespaces=NS) or default

def slugify(value):
    return re.sub(r'[^a-z0-9-]+','-',value.lower()).strip('-') or 'sayfa'

def write_page(path, title, description, content, canonical, active=''):
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_title=html.escape(title)
    safe_desc=html.escape(description[:200], quote=True)
    document=f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title} | Puro Yorumları</title><meta name="description" content="{safe_desc}">
<meta name="google-site-verification" content="googlead5e55201919a23a.html">
<link rel="canonical" href="{html.escape(canonical,quote=True)}"><link rel="stylesheet" href="/styles.css">
</head><body><header class="site-header"><a class="brand" href="/">Puro Yorumları</a><nav><a href="/">Ana Sayfa</a><a href="/puro-nemlendirme-rehberi/">Nemlendirme Rehberi</a><a href="/puro-nereden-alinir/">Puro Nereden Alınır?</a><a href="/about/">Hakkında</a></nav></header>
<main>{content}</main><footer>© Puro Yorumları</footer></body></html>'''
    path.write_text(document,encoding='utf-8')

if OUT.exists():
    import shutil; shutil.rmtree(OUT)
OUT.mkdir(parents=True)
root=ET.parse(EXPORT).getroot(); channel=root.find('channel'); title=text(channel,'title','Puro Yorumları') if channel is not None else 'Puro Yorumları'
description='Puro dünyasını merak edenlerle deneyimlerimi ve kişisel yorumlarımı paylaşıyorum. Farklı puroları inceliyor; seçim, saklama ve puro kültürü üzerine öğrendiklerimi burada not ediyorum. Her yazı kendi gözlem ve değerlendirmelerimi yansıtır.'
posts=[]; pages=[]; urls=[]
# Download the exported WordPress media so the new site is self-contained.
import urllib.request
media_dir=OUT/'assets'; media_dir.mkdir(parents=True,exist_ok=True)
media_map={}
for attachment in root.findall('.//item'):
    if text(attachment,'wp:post_type')!='attachment': continue
    source=text(attachment,'wp:attachment_url')
    if not source: continue
    filename=Path(source.split('?',1)[0]).name
    if not filename: continue
    target=media_dir/filename
    try:
        request=urllib.request.Request(source,headers={'User-Agent':'Mozilla/5.0 (compatible; PuroYorumlariMigration/1.0)'})
        with urllib.request.urlopen(request,timeout=30) as response:
            data=response.read()
        if len(data)<100: raise ValueError('download response too small')
        target.write_bytes(data)
        media_map[source]='/assets/'+filename
    except Exception as exc:
        print(f'Media download failed: {source} ({exc})')
for item in root.findall('.//item'):
    typ=text(item,'wp:post_type'); status=text(item,'wp:status')
    if status!='publish' or typ not in ('post','page'): continue
    slug=text(item,'wp:post_name') or slugify(text(item,'title'))
    title_item=text(item,'title','Başlıksız')
    body=text(item,'content:encoded')
    body=re.sub(r'<!--.*?-->','',body,flags=re.S)
    
    for source, local in media_map.items(): body=body.replace(source,local)
    body=re.sub(r'\s+',' ',body).strip()
    date=text(item,'wp:post_date','2025-01-01 00:00:00')
    cats=[c.text for c in item.findall('category') if c.attrib.get('domain')=='category' and c.text]
    excerpt=re.sub('<[^>]+>',' ',text(item,'excerpt:encoded'))
    excerpt=html.unescape(re.sub(r'\s+',' ',excerpt)).strip()
    if not excerpt: excerpt=html.unescape(re.sub('<[^>]+>',' ',body)); excerpt=re.sub(r'\s+',' ',excerpt).strip()[:180]
    stamp=datetime.strptime(date[:10],'%Y-%m-%d')
    if typ=='post':
        url=f'/{stamp:%Y/%m/%d}/{slug}/'; folder=OUT/f'{stamp:%Y/%m/%d}/{slug}'
        content=f'<article><p class="date">{stamp:%d.%m.%Y}</p><h1>{html.escape(title_item)}</h1><div class="entry">{body}</div></article>'
        write_page(folder/'index.html',title_item,excerpt,content,BASE+url)
        posts.append({'title':title_item,'url':url,'date':stamp.isoformat(),'excerpt':excerpt,'categories':cats})
    else:
        url=f'/{slug}/'; folder=OUT/slug
        content=f'<article><h1>{html.escape(title_item)}</h1><div class="entry">{body}</div></article>'
        write_page(folder/'index.html',title_item,excerpt,content,BASE+url)
        pages.append({'title':title_item,'url':url})
    urls.append((BASE+url,stamp.strftime('%Y-%m-%d')))
posts.sort(key=lambda p:p['date'],reverse=True)
items=''.join(f'<article class="card"><p class="date">{datetime.fromisoformat(p["date"]):%d.%m.%Y}</p><h2><a href="{html.escape(p["url"],quote=True)}">{html.escape(p["title"])}</a></h2><p>{html.escape(p["excerpt"])}</p></article>' for p in posts)
content=f'<section class="intro"><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></section><section class="posts"><h2>Son yazılar</h2>{items}</section>'
write_page(OUT/'index.html',title,description,content,BASE+'/')
css='''*{box-sizing:border-box}body{margin:0;background:#f7f5f0;color:#29241f;font:18px/1.7 system-ui,-apple-system,Segoe UI,sans-serif}.site-header,main,footer{max-width:920px;margin:auto;padding:1rem 1.25rem}.site-header{display:flex;gap:2rem;align-items:center;justify-content:space-between;border-bottom:1px solid #ddd5c9}.brand{font-weight:800;font-size:1.35rem;color:#382a1e;text-decoration:none}nav{display:flex;gap:1rem;flex-wrap:wrap}a{color:#70492c}main{min-height:75vh}.intro{padding:2rem 0}.intro h1{font-size:2.5rem;margin:0}.card{background:#fff;padding:1.2rem 1.5rem;margin:1rem 0;border:1px solid #e6dfd4;border-radius:10px}.card h2{margin:.1rem 0}.date{font-size:.9rem;color:#766d63}article img{max-width:100%;height:auto}footer{border-top:1px solid #ddd5c9;color:#766d63;font-size:.9rem}'''
(OUT/'styles.css').write_text(css,encoding='utf-8')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nUser-agent: Googlebot\nAllow: /\nCrawl-delay: 0\n\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
(OUT/'_headers').write_text('/sitemap.xml\n  Content-Type: application/xml; charset=utf-8\n  Cache-Control: public, max-age=86400, must-revalidate\n  X-Content-Type-Options: nosniff\n\n/robots.txt\n  Content-Type: text/plain\n  Cache-Control: public, max-age=86400\n  X-Content-Type-Options: nosniff\n\n/*.xml\n  Content-Type: application/xml\n  Cache-Control: public, max-age=86400\n  X-Content-Type-Options: nosniff\n',encoding='utf-8')
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{html.escape(u)}</loc><lastmod>{d}</lastmod></url>\n' for u,d in [(BASE+'/',datetime.now().strftime('%Y-%m-%d'))]+urls)+'</urlset>\n'
(OUT/'sitemap.xml').write_text(sm,encoding='utf-8')
(OUT/'content-index.json').write_text(json.dumps({'site':title,'posts':posts,'pages':pages},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Generated {len(posts)} posts and {len(pages)} pages into {OUT}')
print(f'Root sitemap: {OUT / "sitemap.xml"}')
print(f'Downloaded {len(media_map)} media files into {media_dir}')




