#!/opt/homebrew/bin/python3
"""Build the static site (docs/, served by GitHub Pages) from data/games.json.

  build.py [--src ~/dream6800-mister]

Copies the program files and listings from the core's working tree (ref/dreamer/, not public there),
renders screenshots from the Verilator test dumps (tb/out/games/<test>.out) and writes the HTML."""
import html, json, os, re, shutil, sys
from PIL import Image

SRC = os.path.expanduser(sys.argv[sys.argv.index('--src') + 1] if '--src' in sys.argv else '~/dream6800-mister')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'docs')
CORE_URL = 'https://github.com/aminta/DREAM6800_MiSTer'
CORE_PUBLIC = False   # set True once the core repository is public
REPO_URL = 'https://github.com/aminta/DREAM6800_Programs'
BAUER_URL = 'http://www.mjbauer.biz/DREAM6800.htm'
ON, OFF, SCAN = (232, 236, 228), (12, 14, 12), (150, 154, 146)

def esc(s): return html.escape(str(s))

def dumps(test):
    t = open(f'{SRC}/tb/out/games/{test}.out').read()
    out = {}
    for d in re.split(r'^=== frame', t, flags=re.M)[1:]:
        lines = d.split('\n')
        label = lines[0].split(None, 1)[1].strip()
        rows = [l[1:65] for l in lines[2:34]]
        out[label] = rows
    return out

def shot(rows, path, scale=8):
    img = Image.new('RGB', (64 * scale, 32 * scale), OFF)
    px = img.load()
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != '#': continue
            for dy in range(scale):
                col = SCAN if dy == scale - 1 else ON
                for dx in range(scale): px[x * scale + dx, y * scale + dy] = col
    img.save(path, optimize=True)

def page(title, body, depth=0):
    up = '../' * depth
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><link rel="stylesheet" href="{up}style.css"></head>
<body><header><a class="home" href="{up}index.html">DREAM 6800 · DREAMER programs</a></header>
<main>{body}</main>
<footer><p>Programs © their authors, published in the DREAMER newsletter (N.S.W. 6800 Users Group, 1980-82) for DREAM 6800
owners to type in. Source and author are credited on every page. <b>Removal on request</b>: authors or their heirs can
<a href="{REPO_URL}/issues">open an issue</a> and the program is taken down. Site code and transcription notes: MIT.</p></footer>
</body></html>
'''

def badges(g):
    b = [g['ram'] + ' RAM']
    if g['joystick']: b.append('joystick')
    if g['status'] != 'verified': b.append('playable, see notes')
    return ''.join(f'<span class="badge">{esc(x)}</span>' for x in b)

def pubname(f): return 'Joystick Test.c8' if f == 'Joystick_Test.c8' else f
def srcname(f): return 'Joystick_Test.c8' if f == 'Joystick Test.c8' else f

def main():
    games = json.load(open(os.path.join(HERE, 'data/games.json')))
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    for d in ('files', 'listings', 'shots', 'games'): os.makedirs(f'{OUT}/{d}')
    shutil.copy(os.path.join(HERE, 'style.css'), OUT)
    open(f'{OUT}/.nojekyll', 'w').close()
    cards, nfiles = {}, 0
    for g in games:
        for f in g['files']:
            shutil.copy(f'{SRC}/ref/dreamer/progs/{srcname(f["file"])}', f'{OUT}/files/{pubname(f["file"])}'); nfiles += 1
        for l in g['listings']: shutil.copy(f'{SRC}/ref/dreamer/listings/{l}', f'{OUT}/listings/{l}')
        shots = []
        if g.get('test'):
            dd = dumps(g['test'])
            for i, lab in enumerate(g['shots']):
                name = f'{g["id"]}-{i + 1}.png'
                shot(dd[lab.strip()], f'{OUT}/shots/{name}'); shots.append(name)
        g['_shots'] = shots
        src = f'https://archive.org/details/{g["archive_item"]}'
        if g.get('pdf_page'): src += f'/page/n{g["pdf_page"] - 1}/mode/1up'
        pg = f'p. {g["page"]}' if g.get('page') else ''
        files = ''.join(
            f'<tr><td><a href="../files/{esc(pubname(f["file"]))}" download>{esc(pubname(f["file"]))}</a></td>'
            f'<td>{esc(f.get("label", ""))}</td><td>{esc(f["load"])}</td><td>{esc(f["run"])}</td></tr>' for f in g['files'])
        lists = ', '.join(f'<a href="../listings/{esc(l)}">{esc(l)}</a>' for l in g['listings'])
        ul = lambda xs: '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in xs) + '</ul>' if xs else '<p>None.</p>'
        body = f'''<h1>{esc(g["title"])}</h1>
<p class="by">{esc(g["author"] or "Author not credited")} · DREAMER no. {g["issue"]} ({esc(g["date"])}) {esc(pg)} {badges(g)}</p>
<div class="shots">{''.join(f'<img src="../shots/{s}" alt="{esc(g["title"])} screen {i + 1}" width="512" height="256">' for i, s in enumerate(shots))}</div>
<p class="desc">{esc(g["description"])}</p>
<h2>Keys</h2><p>{esc(g["keys"])}</p>
<h2>Files</h2><table><tr><th>File</th><th>Version</th><th>Load</th><th>Run</th></tr>{files}</table>
<p class="hint">Listing as transcribed (with notes): {lists}</p>
<h2>Source</h2><p><a href="{src}">DREAMER no. {g["issue"]} on archive.org</a>{(", " + esc(pg)) if pg else ""}{(" (PDF page " + str(g["pdf_page"]) + ")") if g.get("pdf_page") else ""}.
Author: {esc(g["author"] or "not credited in the newsletter")}.</p>
<h2>Corrections applied</h2>{ul(g["corrections"])}
<h2>Open doubts</h2>{ul(g["doubts"])}'''
        open(f'{OUT}/games/{g["id"]}.html', 'w').write(page(f'{g["title"]} – DREAM 6800', body, 1))
        thumb = f'<img src="shots/{shots[0]}" alt="" width="256" height="128" loading="lazy">' if shots else '<div class="noshot"></div>'
        cards.setdefault(g['issue'], []).append(
            f'<a class="card" href="games/{g["id"]}.html">{thumb}<b>{esc(g["title"])}</b>'
            f'<span>{esc(g["author"] or "uncredited")}</span>{badges(g)}</a>')
    dates = {g['issue']: g['date'] for g in games}
    sections = ''.join(f'<h2 id="n{i}">DREAMER no. {i} <small>{esc(dates[i])}</small></h2><div class="grid">{"".join(c)}</div>'
                       for i, c in sorted(cards.items()))
    index = f'''<h1>DREAMER programs for the DREAM 6800</h1>
<p>The <b>DREAM 6800</b> is a small Australian home computer by Michael J. Bauer, published as a build-it-yourself project in
<i>Electronics Australia</i> in 1979: a Motorola 6800, 1 KB of RAM, a hex keypad, a TV output of 64×32 pixels and
CHIPOS, a monitor with a CHIP-8 interpreter. Its users' newsletter, the <b>DREAMER</b> (1980-82), printed dozens of games
as hex listings to type in. Here they are as ready-to-load files: {len(games)} programs, {nfiles} files, each transcribed
from the scans, checked and run in a simulation of the machine.</p>
<p>Load them in the {(f'<a href="{CORE_URL}">DREAM 6800 MiSTer core</a>' if CORE_PUBLIC else "DREAM 6800 MiSTer core (release coming soon)")} (OSD: Load program) or type them in on real hardware.
CHIPOS and the machine's history: <a href="{BAUER_URL}">Michael Bauer's DREAM 6800 page</a>.</p>
<h2>File formats</h2>
<ul><li><b>.c8</b>: CHIP-8 program, loads at 0200. Start it with <code>C000</code> then <code>FN 3</code>.</li>
<li><b>.d68</b>: for programs that load elsewhere (often 0080) or need more than 1 KB: 2 bytes load address, 2 bytes run
address (big-endian), then the data. The MiSTer core starts it by itself.</li>
<li>Badges: <span class="badge">2K RAM</span> needs the memory expansion; <span class="badge">joystick</span> needs Bauer's
analog joystick (DREAMER no. 3), emulated by the core on the gamepad.</li></ul>
<p class="hint">Screenshots come from the simulation. Every page lists the corrections applied to the printed listing
(published errata, evidence in the article) and any doubt left. Found a mistake? <a href="{REPO_URL}/issues">Open an issue</a>.</p>
{sections}'''
    open(f'{OUT}/index.html', 'w').write(page('DREAMER programs for the DREAM 6800', index))
    print(f'{len(games)} games, {nfiles} files -> {OUT}')

main()
