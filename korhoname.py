#!/usr/bin/env python3
"""Korhoname: is a name free on Discogs and MusicBrainz?

For each candidate name, Korhoname looks up artists and labels on Discogs and MusicBrainz and separates two cases:
the exact spelling (accents, macrons and ligatures kept) and the matches once diacritics, ligatures and punctuation drop.
The verdict rests on the second: a conflict over a name turns on what the names share, so Ā-î-Ā counts as AIA. Discogs: the monthly data dump when reachable (every artist name, name variation and alias), else
the site search read through the r.jina.ai reader. MusicBrainz: its web service (artist, label, aliases).

    python3 korhoname.py "Marumero" "Egyensúly" "Ā"
    python3 korhoname.py --dump "Gy"        # read the whole Discogs dump (~500 MB, home connections)

Output: korhoname.md (the reading copy) and korhoname.json. Standard library only. MIT licence © 2026 Mauk Tenieb."""
import sys, re, json, gzip, time, unicodedata, urllib.request, urllib.parse, xml.etree.ElementTree as ET

UA = {'User-Agent': 'Mozilla/5.0 (compatible; Korhoname/1.0; +https://github.com/MaukTenieb/korhoname)'}

def fold(s):
    """Lower case, no diacritics, ligatures opened, Discogs's '(2)' suffix dropped, punctuation and spaces dropped."""
    s = re.sub(r'\s*\(\d+\)$', '', s or '')
    s = unicodedata.normalize('NFKD', s.casefold().replace('æ', 'ae').replace('œ', 'oe'))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[\W_]+', '', s)

def exact(s):
    """Lower case, diacritics kept, Discogs's '(2)' suffix dropped."""
    return unicodedata.normalize('NFC', re.sub(r'\s*\(\d+\)$', '', s or '')).casefold().strip()

def get(url, timeout=90, headers=None):
    return urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout)

def retry(fn, tries=5, base=6):
    for k in range(tries):
        try: return fn()
        except Exception as e:
            err = e; time.sleep(base + base * k)
    raise err

class Check:
    def __init__(self, names):
        self.names = names
        self.hits = {n: [] for n in names}
        self.unread = {n: [] for n in names}
        self.route = ''

    def add(self, n, source, kind, name, url, note=''):
        key = (source, url)
        if any((h['source'], h['url']) == key for h in self.hits[n]): return
        self.hits[n].append({'source': source, 'type': kind, 'name': name, 'url': url, 'note': note,
                             'exact': exact(name) == exact(n)})

    # Discogs, whole database: the monthly dump listed on data.discogs.com
    def discogs_dump(self):
        D = 'https://data.discogs.com/'
        files = []
        for y in (time.gmtime().tm_year, time.gmtime().tm_year - 1):
            page = get(f"{D}?prefix={urllib.parse.quote(f'data/{y}/', safe='')}").read().decode()
            files = re.findall(r'\?download=(data%2F\d+%2Fdiscogs_(\d{8})_(artists|labels)\.xml\.gz)', page)
            if files: break
        latest = max(f[1] for f in files)
        want = {}
        for n in self.names: want.setdefault(fold(n), []).append(n)
        for key, date, kind in sorted(f for f in files if f[1] == latest):
            tag = kind[:-1]
            with gzip.open(get(f'{D}?download={key}', 600)) as f:
                for _, el in ET.iterparse(f):
                    if el.tag != tag: continue
                    names = [el.findtext('name') or ''] + [v.text or '' for v in el.findall('namevariations/name')]
                    if tag == 'artist': names += [v.text or '' for v in el.findall('aliases/name')]
                    for nm in names:
                        for n in want.get(fold(nm), []):
                            self.add(n, 'Discogs', tag, el.findtext('name'), f"https://www.discogs.com/{tag}/{el.findtext('id')}",
                                     '' if nm == el.findtext('name') else f'as “{nm}”')
                    el.clear()
        self.route = f'Discogs data dump {latest}'

    # Discogs, site search read through a reader proxy
    def discogs_search(self):
        for n in self.names:
            plain = ''.join(c for c in unicodedata.normalize('NFKD', n) if not unicodedata.combining(c))
            queries = list(dict.fromkeys([n, plain, re.sub(r'[\W_]+', '', plain)]))   # the name, without signs, without punctuation
            for kind, q in [(k, q) for k in ('artist', 'label') for q in queries]:
                body, ok = '', False
                for k in range(8):                                     # the reader is rate-limited: pace, then back off
                    time.sleep(3 if k == 0 else 10 * k)
                    u = f"https://r.jina.ai/https://www.discogs.com/search?q={urllib.parse.quote(q)}&type={kind}"
                    try: body = get(u, 120, {'X-No-Cache': 'true'}).read().decode()
                    except Exception as e: body = f'ERROR {e}'
                    if re.search(r'Search results for|No results|did not match|\d+ - \d+ of \d+', body): ok = True; break
                if not ok:
                    self.unread[n].append(f'Discogs {kind} search “{q}”')
                    open(f'unread-{fold(q) or "x"}-{kind}.txt', 'w').write(body); continue
                for name, url in re.findall(r'\[([^\[\]]+?)\]\((https://www\.discogs\.com/(?:artist|label)/[^)\s]+)', body):
                    name = re.sub(r'^Cover art missing: ', '', name)
                    if fold(name) == fold(n): self.add(n, 'Discogs', kind, name, url)
        self.route = self.route or 'Discogs site search (first page of results, best matches first)'

    def musicbrainz(self):
        for n in self.names:
            for ent in ('artist', 'label'):
                q = urllib.parse.quote(f'{ent}:"{n}" OR alias:"{n}"')
                try: d = retry(lambda: json.load(get(f'https://musicbrainz.org/ws/2/{ent}?query={q}&fmt=json&limit=100')))
                except Exception: self.unread[n].append(f'MusicBrainz {ent} search'); continue
                for a in d.get(ent + 's', []):
                    for nm in [a.get('name', '')] + [x.get('name', '') for x in a.get('aliases') or []]:
                        if fold(nm) == fold(n):
                            self.add(n, 'MusicBrainz', ent, a['name'], f"https://musicbrainz.org/{ent}/{a['id']}",
                                     a.get('disambiguation', '') + ('' if nm == a['name'] else f' as “{nm}”')); break
                time.sleep(1.2)

    # Trademarks: TMview (EUIPO's portal over the EU offices, INPI, WIPO, USPTO and 70-odd others), no key
    def trademarks(self, classes=('9', '41')):
        BUA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
               'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.tm = {}
        for n in self.names:
            plain = ''.join(c for c in unicodedata.normalize('NFKD', n) if not unicodedata.combining(c))
            rows, seen = [], set()
            for q in dict.fromkeys([plain, fold(n)]):
                for page in range(1, 6):
                    body = json.dumps({'page': str(page), 'pageSize': '100', 'criteria': 'C', 'basicSearch': q}).encode()
                    try:
                        d = retry(lambda: json.load(urllib.request.urlopen(urllib.request.Request(
                            'https://www.tmdn.org/tmview/api/search/results', data=body, headers=BUA), timeout=90)))
                    except Exception as e:
                        self.unread[n].append(f'TMview “{q}”'); break
                    if page == 1 and d.get('tradeMarks'):
                        open(f'tmview-sample-{fold(q) or "x"}.json', 'w').write(json.dumps(d['tradeMarks'][:3], ensure_ascii=False, indent=1))
                    for r in d.get('tradeMarks') or []:
                        mark = r.get('tmName') or r.get('markName') or r.get('wordMarkSpecification') or r.get('name') or ''
                        if isinstance(mark, list): mark = ' '.join(map(str, mark))
                        key = (r.get('office'), r.get('applicationNumber') or r.get('ST13') or mark)
                        if key in seen: continue
                        seen.add(key)
                        cls = [str(c) for c in (r.get('niceClasses') or [])]
                        if fold(mark) == fold(n):
                            rows.append({'mark': mark, 'office': r.get('office'), 'classes': cls, 'status': r.get('tradeMarkStatus') or r.get('status'),
                                         'applicant': r.get('applicantNames'), 'filed': (r.get('applicationDate') or '')[:10],
                                         'music': bool(set(cls) & set(classes)), 'id': r.get('ST13') or r.get('applicationNumber')})
                    if page >= (d.get('totalPages') or 1): break
                    time.sleep(1.5)
            self.tm[n] = rows

    def report(self):
        L = [f'# Korhoname — {time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}', '', f'Discogs route: {self.route}', '']
        out = {}
        for n in self.names:
            h = self.hits[n]; ex = [x for x in h if x['exact']]
            tm = getattr(self, 'tm', {}).get(n, [])
            # a conflict over a name turns on what the names share: the form without diacritics decides
            tm_music = [x for x in tm if x['music']]
            verdict = 'TAKEN' if h or tm_music else ('FREE' if not self.unread[n] else 'NO MATCH FOUND, BUT PART UNREAD')
            L.append(f'## {n} — {verdict}: {len(ex)} with the exact spelling, {len(h) - len(ex)} more once diacritics, ligatures and punctuation drop')
            if self.unread[n]: L.append(f'- unread: {", ".join(self.unread[n])}')
            for x in sorted(h, key=lambda x: (not x['exact'], x['source'])):
                L.append(f"- {'EXACT ' if x['exact'] else ''}{x['source']} {x['type']}: {x['name']} {('(' + x['note'].strip() + ')') if x['note'].strip() else ''} {x['url']}")
            if hasattr(self, 'tm'):
                L.append(f'- trademarks (TMview) on the shared form: {len(tm)}, of which {len(tm_music)} in classes 9 or 41 (recordings, entertainment)')
                for x in sorted(tm, key=lambda x: not x['music']):
                    L.append(f"  - {'MUSIC ' if x['music'] else ''}{x['mark']} — {x['office']} — classes {', '.join(x['classes'])} — {x['status']} — {x['applicant']} — {x['filed']} — {x['id']}")
            L.append('')
            out[n] = {'verdict': verdict, 'hits': h, 'trademarks': tm, 'unread': self.unread[n]}
        open('korhoname.md', 'w').write('\n'.join(L)); json.dump(out, open('korhoname.json', 'w'), ensure_ascii=False, indent=1)
        return '\n'.join(L)

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    names = [x.strip() for a in args for x in a.split(',') if x.strip()]
    if not names: sys.exit(__doc__)
    c = Check(names)
    if '--dump' in sys.argv:
        try: c.discogs_dump()
        except Exception as e: print('Discogs dump out of reach:', e, file=sys.stderr)
    if not c.route: c.discogs_search()
    c.musicbrainz()
    if '--no-trademarks' not in sys.argv: c.trademarks()
    print(c.report())
