#!/usr/bin/env python3
"""QualityLayer concept diagrams: one source, a light and a dark SVG each.

Used by the README and the docs. Regenerate after a change:
    python3 scripts/diagrams.py static/img/diagrams
"""
import os
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
Theme = dict[str, str]

THEMES = {
    'light': dict(text='#1f2328', muted='#59636e', dim='#8c959f', line='#d0d7de', card='#f6f8fa', cardline='#d0d7de',
                  bg='#ffffff', blue='#2076c5', bluef='#e8f1fb', teal='#127a6e', tealf='#e3f4f1', violet='#6f4fc2',
                  violetf='#f0ebfb', amber='#9a5b00', amberf='#fff4dc', amberl='#e0a43a', ok='#1a7f37', s1='#2076c5',
                  s2='#127a6e', s3='#6f4fc2', off='#d8dee4', danger='#cf222e'),
    'dark': dict(text='#e6edf3', muted='#9198a1', dim='#6e7681', line='#3d444d', card='#151b23', cardline='#3d444d',
                 bg='#0d1117', blue='#5da3e5', bluef='#132235', teal='#5cc4b4', tealf='#10241f', violet='#b49aed',
                 violetf='#1e1830', amber='#e8b04f', amberf='#2a2112', amberl='#b07a1c', ok='#3fb950', s1='#5da3e5',
                 s2='#5cc4b4', s3='#b49aed', off='#30363d', danger='#f85149'),
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# The five steps, in order; Plan and Review wait for your approval.
STEPS = [('Discuss', 'violet'), ('Plan', 'amber'), ('Implement', 'blue'), ('Verify', 'teal'), ('Review', 'amber')]
GATES = {'Plan', 'Review'}


def T(x: float, y: float, s: str, size: float = 14, fill: str = 'text', weight: int = 400, anchor: str = 'start',
      mono: bool = False, *, c: Theme) -> str:
    """A text element; `fill` is a theme key or a literal colour."""
    return (f'<text x="{x}" y="{y}" font-family="{MONO if mono else SANS}" font-size="{size}" font-weight="{weight}" '
            f'fill="{c.get(fill, fill)}" text-anchor="{anchor}">{escape(s)}</text>')


def svg(w: float, h: float, body: str, title: str) -> str:
    """The canvas, with 2px to spare on every side so edge strokes are not clipped."""
    w, h = w + 4, h + 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="-2 -2 {w} {h}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n')


# ---------------------------------------------------------------- shared shapes
def node(c, x, y, w, h, title, sub, col, fill=None, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ''
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c[fill] if fill else c["card"]}" stroke="{c[col]}" stroke-width="{1 if col == "cardline" else 2}"{d}/>']
    out.append(T(x + 16, y + 28, title, 15, 'text', 650, c=c))
    for i, s in enumerate(sub if isinstance(sub, list) else [sub]):
        out.append(T(x + 16, y + 48 + i * 18, s, 13, 'muted', c=c))
    return ''.join(out)


def curve(c, x1, y1, x2, y2, col='line', dash=False, w=2):
    mx = (x1 + x2) / 2
    d = ' stroke-dasharray="4 5"' if dash else ''
    return f'<path d="M{x1} {y1} C{mx} {y1} {mx} {y2} {x2} {y2}" fill="none" stroke="{c[col]}" stroke-width="{w}"{d}/>'


def bars(c, x, y, widths, gap=14, h=6, col='line'):
    return ''.join(f'<rect x="{x}" y="{y + i * gap}" width="{w}" height="{h}" rx="3" fill="{c[col]}"/>' for i, w in enumerate(widths))


def card(c: Theme, x: float, y: float, w: float, h: float, stroke: str = 'cardline', fill: str = 'card',
         dash: bool = False, sw: float = 1) -> str:
    d = ' stroke-dasharray="5 4"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c[fill]}" stroke="{c[stroke]}" stroke-width="{sw}"{d}/>'


def arrow(c: Theme, x1: float, y1: float, x2: float, y2: float | None = None, col: str = 'muted', dash: bool = False) -> str:
    y2 = y1 if y2 is None else y2
    d = ' stroke-dasharray="4 4"' if dash else ''
    if y1 == y2:
        s = 1 if x2 > x1 else -1
        head = f'<path d="M{x2 - 7 * s} {y2 - 5} l{7 * s} 5 l{-7 * s} 5" fill="none" stroke="{c[col]}" stroke-width="1.8"/>'
    else:
        s = 1 if y2 > y1 else -1
        head = f'<path d="M{x2 - 5} {y2 - 7 * s} l5 {7 * s} l5 {-7 * s}" fill="none" stroke="{c[col]}" stroke-width="1.8"/>'
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c[col]}" stroke-width="1.8"{d}/>' + head


def mark(c: Theme, x: float, y: float, ok: bool = True) -> str:
    if ok:
        return f'<path d="M{x - 6} {y} l4 4 l8 -9" fill="none" stroke="{c["ok"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    return (f'<path d="M{x - 5} {y - 5} l10 10 M{x + 5} {y - 5} l-10 10" stroke="{c["danger"]}" stroke-width="2.4" '
            f'stroke-linecap="round"/>')


def pill(c: Theme, x: float, y: float, text: str, col: str = 'muted', w: float | None = None, mono: bool = False,
         fill: str = 'bg', stroke: str = 'cardline') -> str:
    w = w if w is not None else 18 + len(text) * (7.4 if mono else 6.6)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{c[fill]}" stroke="{c[stroke]}"/>'
            + T(x + w / 2, y + 15, text, 11.5, col, 600, 'middle', mono, c=c))


def button(c: Theme, x: float, y: float, w: float, text: str, primary: bool = False, h: float = 34) -> str:
    if primary:
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["blue"]}"/>'
                + T(x + w / 2, y + h / 2 + 4.5, text, 13, '#ffffff', 650, 'middle', c=c))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
            + T(x + w / 2, y + h / 2 + 4.5, text, 13, 'text', 600, 'middle', c=c))


def switch(c: Theme, x: float, y: float, on: bool = True) -> str:
    if on:
        return (f'<rect x="{x}" y="{y}" width="28" height="18" rx="9" fill="{c["blue"]}"/>'
                f'<circle cx="{x + 19}" cy="{y + 9}" r="6" fill="#ffffff"/>')
    return (f'<rect x="{x}" y="{y}" width="28" height="18" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
            f'<circle cx="{x + 9}" cy="{y + 9}" r="6" fill="{c["dim"]}"/>')


def diamond(c: Theme, x: float, y: float, r: float, fill: str = 'amberf', stroke: str = 'amber') -> str:
    return (f'<rect x="{x - r}" y="{y - r}" width="{2 * r}" height="{2 * r}" rx="3" transform="rotate(45 {x} {y})" '
            f'fill="{c[fill]}" stroke="{c[stroke]}" stroke-width="2"/>')


def doc_head(c: Theme, x: float, y: float, w: float, file: str, who: str) -> str:
    return (f'<line x1="{x}" y1="{y + 34}" x2="{x + w}" y2="{y + 34}" stroke="{c["cardline"]}"/>'
            + T(x + 16, y + 22, file, 12, 'muted', 500, mono=True, c=c) + T(x + w - 16, y + 22, who, 12, 'dim', 600, 'end', c=c))


def window(c, W, H, title='QualityLayer'):
    return (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{c["bg"]}" stroke="{c["cardline"]}" stroke-width="1.5"/>'
            f'<path d="M1 17 a16 16 0 0 1 16 -16 H{W - 17} a16 16 0 0 1 16 16 V40 H1 Z" fill="{c["card"]}"/>'
            f'<line x1="1" y1="40" x2="{W - 1}" y2="40" stroke="{c["cardline"]}"/>'
            + ''.join(f'<circle cx="{22 + i * 18}" cy="21" r="5" fill="{c["line"]}"/>' for i in range(3))
            + T(W / 2, 26, title, 12, 'dim', 500, 'middle', c=c))


def num(c: Theme, x: float, y: float, n: int) -> str:
    return (f'<circle cx="{x}" cy="{y}" r="12" fill="{c["blue"]}" stroke="{c["bg"]}" stroke-width="2.5"/>'
            + T(x, y + 4.5, str(n), 12.5, '#ffffff', 700, 'middle', c=c))


# ---------------------------------------------------------------- the five steps
def flow(c):
    W, H = 1000, 280
    x0, cw = 130, 174
    cx = [x0 + i * cw + cw / 2 for i in range(5)]
    b = [f'<line x1="{cx[0]}" y1="62" x2="{cx[-1]}" y2="62" stroke="{c["line"]}" stroke-width="2"/>']
    for i, (n, col) in enumerate(STEPS):
        b.append(T(cx[i], 30, n, 16, 'text', 700, 'middle', c=c))
        b.append(diamond(c, cx[i], 62, 10) if n in GATES else f'<circle cx="{cx[i]}" cy="62" r="10" fill="{c[col]}"/>')
    you = ['Answer its questions', 'Comment, then approve', 'Start a fresh session', None, 'Try it, then approve']
    agent = ['Reads the code, asks', 'Writes the Plan', 'Builds test first', 'Another AI checks it', 'Writes the PR text']
    for row, (label, col, y, cells) in enumerate([('You', 'amber', 100, you), ('Your agent', 'blue', 166, agent)]):
        b.append(T(0, y + 28, label, 15, col, 700, c=c))
        for i, s in enumerate(cells):
            x = cx[i] - 80
            if s is None:
                b.append(f'<rect x="{x}" y="{y}" width="160" height="44" rx="10" fill="none" stroke="{c["off"]}" stroke-dasharray="4 4"/>')
                b.append(T(cx[i], y + 27, 'Nothing to do', 12, 'dim', 500, 'middle', c=c))
                continue
            fill, stroke = ('amberf', 'amberl') if row == 0 else ('card', 'cardline')
            b.append(f'<rect x="{x}" y="{y}" width="160" height="44" rx="10" fill="{c[fill]}" stroke="{c[stroke]}"/>')
            b.append(T(cx[i], y + 27, s, 12.5, 'text', 500, 'middle', c=c))
    ly = H - 8
    b.append(diamond(c, x0 + 8, ly - 5, 6))
    b.append(T(x0 + 24, ly, 'You approve here', 13, 'muted', c=c))
    b.append(f'<circle cx="{x0 + 178}" cy="{ly - 5}" r="7" fill="{c["blue"]}"/>')
    b.append(T(x0 + 192, ly, 'Your agent works on its own', 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'The five steps of a QualityLayer task: Discuss, Plan, Implement, Verify and Review. You approve the Plan before any code and the finished change at the end; your agent does the rest')


def track(here: str):
    """The five steps on one line, with the page's own step highlighted."""
    def draw(c: Theme) -> str:
        W, H = 1000, 112
        xs = [100 + i * 200 for i in range(5)]
        cur = [n for n, _ in STEPS].index(here)
        b = [T(0, 16, 'The five steps', 12, 'muted', 600, c=c)]
        b.append(f'<line x1="{xs[0]}" y1="52" x2="{xs[-1]}" y2="52" stroke="{c["line"]}" stroke-width="2"/>')
        if cur:
            b.append(f'<line x1="{xs[0]}" y1="52" x2="{xs[cur]}" y2="52" stroke="{c["blue"]}" stroke-width="2.5"/>')
        for i, (n, col) in enumerate(STEPS):
            x, gate = xs[i], n in GATES
            if i == cur:
                b.append(f'<circle cx="{x}" cy="52" r="17" fill="{c[col]}" fill-opacity="0.16"/>')
                b.append(diamond(c, x, 52, 9, 'amber', 'amber') if gate else f'<circle cx="{x}" cy="52" r="9" fill="{c[col]}"/>')
                b.append(T(x, 88, n, 13, 'text', 700, 'middle', c=c))
                b.append(T(x, 106, 'This page', 11, col, 600, 'middle', c=c))
            elif i < cur:
                b.append(diamond(c, x, 52, 5.5, 'blue', 'blue') if gate else f'<circle cx="{x}" cy="52" r="6" fill="{c["blue"]}"/>')
                b.append(T(x, 88, n, 12, 'muted', 500, 'middle', c=c))
            else:
                b.append(diamond(c, x, 52, 5.5, 'bg', 'line') if gate else f'<circle cx="{x}" cy="52" r="6" fill="{c["bg"]}" stroke="{c["line"]}" stroke-width="2"/>')
                b.append(T(x, 88, n, 12, 'muted', 500, 'middle', c=c))
        return svg(W, H, ''.join(b), f'The five steps, with {here} highlighted')
    return draw


# ---------------------------------------------------------------- slices, side by side, then Verify
def slices(c):
    W, H = 1000, 292
    b = []
    for name, xa, xz, col in [('Implement', 0, 610, 'blue'), ('Verify', 640, 1000, 'teal')]:
        b.append(f'<rect x="{xa}" y="0" width="{xz - xa}" height="4" rx="2" fill="{c[col]}"/>')
        b.append(T(xa, 26, name, 15, col, 650, c=c))

    def sl(x, y, w, col, title, line2, col2, check):
        out = [card(c, x, y, w, 80, stroke=col, sw=1.6)]
        out.append(T(x + 14, y + 24, title, 13.5, 'text', 650, c=c))
        out.append(T(x + 14, y + 44, line2, 12, col2, 600 if col2 == 'amber' else 400, c=c))
        out.append(mark(c, x + 20, y + 61))
        out.append(T(x + 32, y + 66, check, 11, 'blue', 500, mono=True, c=c))
        return ''.join(out)

    b.append(sl(0, 44, 190, 's1', 'Slice 1 · Export', 'T1, T2, each test first', 'muted', 'check slice 1 · exit 0'))
    b.append(arrow(c, 192, 84, 214))
    b.append(sl(216, 44, 214, 's3', 'Slice 3 · Large reports', 'Risky: new mail service', 'amber', 'check slice 3 · exit 0'))
    b.append(arrow(c, 432, 84, 454))
    b.append(card(c, 456, 44, 154, 80, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(470, 68, 'Checkpoint', 13.5, 'text', 650, c=c))
    b.append(T(470, 88, 'Runs slice 3’s', 12, 'muted', c=c))
    b.append(T(470, 106, 'scenarios', 12, 'muted', c=c))
    b.append(sl(0, 144, 300, 's2', 'Slice 2 · Filter the export', 'Side by side: shares no file with slice 1', 'muted', 'check slice 2 · exit 0'))
    b.append(f'<path d="M610 84 H625 V184 M300 184 H625" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(arrow(c, 625, 84, 644))
    b.append(arrow(c, 625, 184, 644))
    b.append(node(c, 646, 44, 170, 80, 'Polish', ['Leftover code,', 'missing tests, docs'], 'teal'))
    b.append(node(c, 646, 144, 170, 80, 'Security', ['Only when it crosses', 'a trust boundary'], 'teal', dash=True))
    b.append(curve(c, 816, 84, 838, 134, 'teal'))
    b.append(curve(c, 816, 184, 838, 134, 'teal', True))
    b.append(node(c, 838, 94, 154, 80, 'The judge', ['An AI that did not', 'write the code'], 'teal', 'tealf'))
    b.append(T(W / 2, 258, 'Slices that share no files build side by side, and only a risky slice gets a checkpoint.', 13, 'muted', 400, 'middle', c=c))
    b.append(T(W / 2, 278, 'Then Polish and Security run side by side, and one judge checks the whole change.', 13, 'muted', 400, 'middle', c=c))
    return svg(W, H, ''.join(b), 'Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and Security side by side, then one judge')


# ---------------------------------------------------------------- who does what
def agents(c):
    W, H = 1000, 420
    b = []
    b.append(node(c, 0, 170, 160, 80, 'You', ['Answer, then approve', 'the Plan and change'], 'amber', 'amberf'))
    b.append(curve(c, 160, 210, 185, 210, 'amberl'))
    b.append(node(c, 185, 170, 190, 80, 'Your agent', ['Discuss and Plan,', 'Opus 5.5 recommended'], 'blue', 'bluef'))
    b.append(curve(c, 375, 210, 400, 210, 'blue'))
    b.append(f'<rect x="400" y="150" width="120" height="120" rx="12" fill="{c["violetf"]}" stroke="{c["violet"]}" stroke-width="2"/>')
    b.append(T(416, 180, 'The Plan', 15, 'text', 650, c=c))
    for i in range(4):
        b.append(f'<rect x="416" y="{196 + i * 15}" width="{[88, 72, 84, 56][i]}" height="6" rx="3" fill="{c["violet"]}" fill-opacity="0.35"/>')
    b.append(curve(c, 520, 210, 545, 210, 'blue'))
    b.append(node(c, 545, 170, 190, 80, 'Implement session', ['You start it fresh,', 'Sonnet 5.5 recommended'], 'blue', 'bluef'))
    right = [(0, 'Slice helpers', ['Sonnet 5.5,', 'each task test first'], 'blue'),
             (88, 'Fix helpers', ['A fresh agent', 'for each failure'], 'blue'),
             (176, 'Polish and Security', ['Side by side,', 'after the build'], 'teal'),
             (264, 'The judge', ['Opus 5.5. It did not', 'write the code'], 'teal')]
    for y, t, s, col in right:
        b.append(curve(c, 735, 210, 770, y + 39, col))
        b.append(node(c, 770, y, 230, 78, t, s, 'cardline'))
        b.append(f'<circle cx="{980}" cy="{y + 22}" r="6" fill="{c[col]}"/>')
    b.append(curve(c, 460, 270, 460, 340, 'violet', True))
    b.append(node(c, 330, 340, 260, 68, 'Second opinion', 'Another vendor’s AI, on risky Plans', 'violet', dash=True))
    b.append(T(474, 300, 'Every helper works from the Plan,', 12, 'muted', c=c))
    b.append(T(474, 316, 'never from your chat', 12, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Who does what: you and your agent on Opus 5.5 discuss and write the Plan; the implement session you start on Sonnet 5.5 hands work to slice helpers and fix helpers; Polish and Security run side by side; a judge that did not write the code checks it; a second opinion from another vendor reviews risky Plans by itself')


# ---------------------------------------------------------------- the App window
def app(c):
    W, H = 1000, 600
    b = [window(c, W, H, 'CSV export · QualityLayer')]
    b.append(f'<path d="M1 41 H221 V{H - 1} H17 a16 16 0 0 1 -16 -16 Z" fill="{c["card"]}"/>')
    b.append(f'<line x1="221" y1="41" x2="221" y2="{H - 1}" stroke="{c["cardline"]}"/>')
    b.append(T(24, 72, 'QualityLayer', 15, 'text', 700, c=c))

    def task(y, name, step, sel=False, you=True):
        out = []
        if sel:
            out.append(f'<rect x="12" y="{y}" width="198" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        dash = '' if you else ' stroke-dasharray="3 3"'
        out.append(f'<circle cx="28" cy="{y + 14}" r="4.5" fill="none" stroke="{c["amber"] if you else c["blue"]}" stroke-width="2"{dash}/>')
        out.append(T(40, y + 18, name, 12.5, 'text', 500, c=c))
        out.append(T(200, y + 18, step, 10.5, 'dim', 400, 'end', mono=True, c=c))
        return ''.join(out)

    b.append(T(24, 108, 'Needs you', 12, 'amber', 650, c=c))
    b.append(task(124, 'CSV export', 'Plan', True))
    b.append(task(158, 'Invoice PDFs', 'Review'))
    b.append(T(24, 222, 'In progress', 12, 'muted', 650, c=c))
    for i, (n, st) in enumerate([('Webhooks', 'Implement'), ('SSO sync', 'Verify'), ('Rate limits', 'Discuss')]):
        b.append(task(238 + i * 34, n, st, you=False))
    x0 = 250
    b.append(T(x0, 78, 'CSV export', 20, 'text', 650, c=c))
    sx = x0
    for i, (s, _) in enumerate(STEPS):
        done, cur = i < 1, i == 1
        col = c['text'] if done else c['amber'] if cur else c['dim']
        if done:
            b.append(f'<circle cx="{sx + 5}" cy="106" r="5" fill="{c["text"]}"/>')
        else:
            b.append(f'<circle cx="{sx + 5}" cy="106" r="5" fill="none" stroke="{col}" stroke-width="2"/>')
        b.append(f'<text x="{sx + 16}" y="110" font-family="{SANS}" font-size="12.5" font-weight="{600 if cur else 400}" fill="{col}">{s}</text>')
        sx += 16 + len(s) * 7.2 + 24
    by = 128
    b.append(f'<rect x="222" y="{by}" width="{W - 223}" height="64" fill="{c["amberf"]}"/>')
    b.append(f'<rect x="222" y="{by}" width="4" height="64" fill="{c["amber"]}"/>')
    b.append(T(x0, by + 28, 'Your review · the Plan', 14, 'text', 650, c=c))
    b.append(T(x0, by + 48, 'Comment on any line or diagram, then decide.', 12.5, 'muted', c=c))
    b.append(button(c, W - 290, by + 16, 148, 'Request changes'))
    b.append(button(c, W - 130, by + 16, 100, 'Approve', True))
    cy = 218
    b.append(f'<rect x="{x0}" y="{cy}" width="410" height="350" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x0 + 18, cy + 30, 'What changes', 14, 'text', 650, c=c))

    def box(x, y, w, label, col, fill):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="9" fill="{c[fill]}" stroke="{c[col]}" stroke-width="1.8"/>'
                + T(x + w / 2, y + 27, label, 13, 'text', 600, 'middle', c=c))
    b.append(box(x0 + 22, cy + 140, 96, 'Reports', 'cardline', 'bg'))
    b.append(box(x0 + 160, cy + 140, 104, 'Exporter', 'violet', 'violetf'))
    b.append(box(x0 + 300, cy + 76, 92, 'Download', 'blue', 'bluef'))
    b.append(box(x0 + 300, cy + 204, 92, 'Email', 'blue', 'bluef'))
    b.append(f'<path d="M{x0 + 118} {cy + 162} H{x0 + 160}" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(curve(c, x0 + 264, cy + 162, x0 + 300, cy + 98, 'blue'))
    b.append(curve(c, x0 + 264, cy + 162, x0 + 300, cy + 226, 'blue', True))
    b.append(f'<rect x="{x0 + 100}" y="{cy + 262}" width="230" height="58" rx="10" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.5"/>')
    b.append(f'<path d="M{x0 + 205} {cy + 262} l7 -10 l7 10" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.5"/>')
    b.append(f'<rect x="{x0 + 204}" y="{cy + 261}" width="16" height="3" fill="{c["bg"]}"/>')
    b.append(f'<circle cx="{x0 + 124}" cy="{cy + 291}" r="12" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="1.5"/>')
    b.append(T(x0 + 124, cy + 295, 'A', 11, 'amber', 700, 'middle', c=c))
    b.append(T(x0 + 144, cy + 286, 'Anna', 12, 'text', 650, c=c))
    b.append(T(x0 + 144, cy + 304, 'Keep the column order', 12, 'muted', c=c))
    mx = x0 + 430
    b.append(f'<rect x="{mx}" y="{cy}" width="{W - mx - 30}" height="350" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(mx + 18, cy + 30, 'Interface mockup', 14, 'text', 650, c=c))
    b.append(T(W - 48, cy + 30, 'clickable', 11, 'dim', 500, 'end', mono=True, c=c))
    for i, on in enumerate([True, False, False, True]):
        ry = cy + 54 + i * 70
        b.append(f'<rect x="{mx + 18}" y="{ry}" width="{W - mx - 66}" height="56" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(bars(c, mx + 34, ry + 18, [[96, 120, 84, 104][i], 58], 14, 6, 'line'))
        tx = W - 102
        b.append(f'<rect x="{tx}" y="{ry + 17}" width="40" height="22" rx="11" fill="{c["blue"] if on else c["line"]}"/>')
        b.append(f'<circle cx="{tx + (29 if on else 11)}" cy="{ry + 28}" r="8" fill="#ffffff"/>')
    return svg(W, H, ''.join(b), 'The QualityLayer App: the task list, the five steps, the Plan under review with a diagram, a teammate’s comment, a clickable mockup, and Approve')


def app_marked(c: Theme) -> str:
    """The App drawing with numbered markers for the parts the App page explains."""
    marks = [(200, 108, 1), (236, 106, 2), (700, 144, 3), (652, 222, 4), (586, 478, 5), (968, 230, 6)]
    return app(c).replace('</svg>', ''.join(num(c, x, y, n) for x, y, n in marks) + '</svg>')


# ---------------------------------------------------------------- after the Plan is approved
def implement_start(c):
    W, H = 1000, 350
    b = [window(c, W, H, 'CSV export · QualityLayer')]
    x0 = 40
    b.append(mark(c, x0 + 8, 82))
    b.append(T(x0 + 26, 88, 'The Plan is approved', 18, 'text', 650, c=c))
    b.append(T(x0, 116, 'Start Implement in a fresh session, the way you like: terminal, IDE or desktop app.', 13.5, 'muted', c=c))
    b.append(f'<rect x="{x0}" y="136" width="{W - 2 * x0}" height="64" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x0 + 20, 174, '/ql implement csv-export', 16, 'text', 600, mono=True, c=c))
    b.append(button(c, W - x0 - 112, 151, 96, 'Copy', True))
    b.append(f'<circle cx="{x0 + 6}" cy="230" r="5" fill="{c["blue"]}"/>')
    b.append(T(x0 + 20, 235, 'Start a fresh session. Sonnet 5.5 recommended.', 14, 'text', 600, c=c))
    b.append(T(x0 + 20, 256, 'In Codex: $ql implement csv-export, with GPT-6.1 Sol.', 12.5, 'muted', c=c))
    b.append(f'<rect x="{x0}" y="276" width="{W - 2 * x0}" height="52" rx="10" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-opacity="0.6"/>')
    b.append(T(x0 + 18, 297, 'What runs', 11.5, 'blue', 700, c=c))
    b.append(T(x0 + 18, 316, '3 slices, slices 1 and 2 side by side, a checkpoint after slice 3 (new mail service), no security review.', 13, 'text', c=c))
    return svg(W, H, ''.join(b), 'After you approve the Plan, the App shows the prompt /ql implement csv-export with a Copy button and the advice to start a fresh session with Sonnet 5.5')


def implement_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = [card(c, 0, 0, 1000, 44, stroke='blue', fill='bluef', sw=1.4)]
    b.append(f'<circle cx="22" cy="22" r="5" fill="{c["blue"]}"/>')
    b.append(T(36, 27, 'Now: slices 1 and 2, side by side', 13, 'text', 600, c=c))
    b.append(T(980, 27, 'reported 1 min ago', 12, 'muted', 400, 'end', c=c))
    rows = [('s1', 'Slice 1', [('T1', 'done'), ('T2', 'done'), ('T3', 'verified')]),
            ('s2', 'Slice 2', [('T4', 'done'), ('T5', 'building')])]
    y = 62
    for col, name, tasks in rows:
        b.append(T(0, y + 18, name, 13, col, 650, c=c))
        for k, (t, state) in enumerate(tasks):
            x = 80 + k * 140
            b.append(f'<rect x="{x}" y="{y}" width="130" height="28" rx="7" fill="{c["bg"]}" stroke="{c[col] if state != "building" else c["cardline"]}"/>')
            if state == 'building':
                b.append(f'<circle cx="{x + 16}" cy="{y + 14}" r="5" fill="none" stroke="{c["blue"]}" stroke-width="2" stroke-dasharray="3 2"/>')
            else:
                b.append(mark(c, x + 16, y + 14))
            b.append(T(x + 30, y + 18.5, f'{t} {state}', 12, 'text', 600, c=c))
        y += 44
    b.append(T(540, 80, 'building: a helper is on it', 12, 'muted', c=c))
    b.append(T(540, 100, 'verified: its check passed', 12, 'muted', c=c))
    b.append(T(540, 120, 'done: its box is ticked', 12, 'muted', c=c))
    b.append(card(c, 0, 160, 1000, 166))
    b.append(T(18, 190, 'Checks · recorded by QualityLayer in 03-build.md', 14, 'text', 650, c=c))
    lines = [('slice 1 · 4f2a9c1 · bun test tests/export · exit 0 · 14s', 'text', None),
             ('task T5 · 4f2a9c1 · bun test tests/filter · exit 1 · 3s', 'danger', 'A fresh agent fixes it'),
             ('task T5 · 9b03e7d · bun test tests/filter · exit 0 · 3s', 'text', None)]
    for i, (t, col, note) in enumerate(lines):
        yy = 216 + i * 34
        b.append(f'<rect x="18" y="{yy}" width="964" height="26" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(32, yy + 17.5, t, 12, col, 500, mono=True, c=c))
        if note:
            b.append(T(966, yy + 17.5, note, 12, 'amber', 600, 'end', c=c))
    return svg(W, H, ''.join(b), 'The Implement tab: each task building, verified or done, two slices side by side, and the checks QualityLayer recorded with their exit codes')


def checkpoint_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = []
    top = [(0, 'Slice 3 built', 'cardline', 'bg'), (220, 'Its scenarios run', 'blue', 'bluef'), (440, 'Passed', 'ok', 'bg'),
           (660, 'Next slice', 'cardline', 'bg')]
    for x, t, col, fill in top:
        b.append(card(c, x, 20, 180, 56, stroke=col, fill=fill, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 90, 54, t, 14, 'text', 650, 'middle', c=c))
    for x in (0, 220, 440):
        b.append(arrow(c, x + 182, 48, x + 218))
    b.append(mark(c, 474, 48))
    b.append(T(90, 98, 'Risky: new mail service', 12, 'amber', 600, 'middle', c=c))
    b.append(T(870, 44, 'Tests, logs and a', 12, 'muted', c=c))
    b.append(T(870, 60, 'screenshot are kept', 12, 'muted', c=c))
    b.append(card(c, 220, 172, 180, 56, stroke='danger', fill='bg', sw=1.6))
    b.append(mark(c, 250, 200, False))
    b.append(T(318, 205, 'Failed', 14, 'text', 650, 'middle', c=c))
    b.append(arrow(c, 310, 78, 310, 170, 'danger'))
    b.append(f'<path d="M218 200 H150 V112" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M145 119 l5 -7 l5 7" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(T(0, 160, 'A fresh agent', 12, 'muted', c=c))
    b.append(T(0, 176, 'fixes it, then', 12, 'muted', c=c))
    b.append(T(0, 192, 'it runs again', 12, 'muted', c=c))
    b.append(arrow(c, 402, 200, 470))
    b.append(T(436, 190, '2 runs', 11.5, 'danger', 600, 'middle', c=c))
    b.append(card(c, 472, 152, 508, 96, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(490, 180, 'Stopped: the build waits for you', 14, 'text', 650, c=c))
    for i, (t, w) in enumerate([('Continue', 96), ('Pivot', 72), ('Abandon', 92)]):
        x = 490 + sum([96, 72, 92][:i]) + i * 10
        b.append(pill(c, x, 204, t, 'text', w))
    return svg(W, H, ''.join(b), 'A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to a fresh agent and runs again, and after two failed runs you decide')


# ---------------------------------------------------------------- Discuss and Plan
def discuss_ill(c: Theme) -> str:
    W, H = 1000, 320
    b = [card(c, 0, 0, 300, 316)]
    b.append(T(18, 28, 'In your agent’s chat', 12, 'dim', 600, c=c))
    b.append(T(18, 60, 'Question 3 of 5', 12, 'muted', 500, c=c))
    b.append(T(18, 84, 'Which reports need the export?', 14, 'text', 650, c=c))
    opts = [('All reports, with filters', 'Recommended', True), ('Only the sales report', None, False),
            ('Something else', None, False)]
    y = 102
    for t, sub, on in opts:
        h = 48 if sub else 36
        b.append(f'<rect x="18" y="{y}" width="264" height="{h}" rx="9" fill="{c["bluef"] if on else c["bg"]}" stroke="{c["blue"] if on else c["cardline"]}"/>')
        b.append(T(32, y + (20 if sub else 23), t, 13, 'text', 600 if on else 500, c=c))
        if sub:
            b.append(T(32, y + 38, sub, 11.5, 'blue', 600, c=c))
        y += h + 10
    b.append(T(18, 296, 'One question at a time', 12, 'dim', 500, c=c))
    b.append(arrow(c, 302, 158, 328))
    b.append(card(c, 330, 0, 360, 316))
    b.append(doc_head(c, 330, 0, 360, '00-discuss.md', 'In the App'))
    b.append(T(348, 64, 'Add a CSV export to the reports page', 15, 'text', 700, c=c))
    b.append(T(348, 92, 'PROBLEM', 11, 'dim', 700, c=c))
    b.append(T(348, 110, 'Support copies report tables by hand.', 13, 'muted', c=c))
    b.append(T(348, 142, 'DONE MEANS', 11, 'dim', 700, c=c))
    for i, t in enumerate(['An Export button on every report', 'Opens in a spreadsheet, same columns',
                           'Large reports arrive by email']):
        yy = 154 + i * 48
        b.append(card(c, 348, yy, 324, 38, fill='bg'))
        b.append(f'<circle cx="368" cy="{yy + 19}" r="10" fill="{c["violetf"]}" stroke="{c["violet"]}" stroke-width="1.5"/>')
        b.append(T(368, yy + 23.5, str(i + 1), 11.5, 'violet', 700, 'middle', c=c))
        b.append(T(388, yy + 24, t, 13, 'text', 500, c=c))
    b.append(arrow(c, 692, 158, 718, dash=True))
    b.append(T(705, 146, 'or', 12, 'dim', 600, 'middle', c=c))
    b.append(card(c, 720, 0, 280, 316, stroke='violet', dash=True, sw=1.4))
    b.append(T(738, 32, 'Too small?', 15, 'text', 650, c=c))
    for i, t in enumerate(['Done means fits one line,', 'it stays in one area of', 'the code, nothing to decide.']):
        b.append(T(738, 58 + i * 19, t, 12.5, 'muted', c=c))
    b.append(f'<line x1="738" y1="128" x2="982" y2="128" stroke="{c["cardline"]}"/>')
    b.append(T(738, 154, 'No task. A ready prompt', 13, 'text', 600, c=c))
    b.append(T(738, 173, 'for your plain agent:', 13, 'text', 600, c=c))
    b.append(button(c, 738, 190, 112, 'Run it here', True, 32))
    b.append(button(c, 860, 190, 70, 'Copy', False, 32))
    b.append(T(738, 258, 'You can still insist on', 12, 'dim', 500, c=c))
    b.append(T(738, 276, 'a QualityLayer task.', 12, 'dim', 500, c=c))
    return svg(W, H, ''.join(b), 'Discuss: your agent asks one question at a time with a recommendation and fills the Discuss document in the App; a change too small for QualityLayer gets a ready prompt for your plain agent instead')


def diagnose_ill(c: Theme) -> str:
    W, H = 1000, 250
    b = []
    cols = [('Reproduction', 'danger'), ('Root cause', 'amber'), ('Behaviour contract', 'ok')]
    for i, (t, col) in enumerate(cols):
        x = i * 340
        b.append(card(c, x, 0, 310, 246))
        b.append(f'<rect x="{x}" y="0" width="310" height="4" rx="2" fill="{c[col]}"/>')
        b.append(T(x + 18, 34, t, 15, 'text', 650, c=c))
        if i < 2:
            b.append(arrow(c, x + 314, 123, x + 336))
    b.append(f'<rect x="18" y="52" width="274" height="96" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(32, 78, '$ open /reports?page=2', 12, 'muted', 500, mono=True, c=c))
    b.append(T(32, 102, '  shows 49 of 50 rows', 12, 'text', 500, mono=True, c=c))
    b.append(mark(c, 38, 124, False))
    b.append(T(52, 129, 'The last row is missing', 12.5, 'danger', 600, c=c))
    b.append(T(18, 180, 'Happens on every page but the first.', 13, 'muted', c=c))
    b.append(f'<rect x="358" y="52" width="274" height="96" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(bars(c, 372, 68, [200, 150], 14, 6))
    b.append(f'<rect x="364" y="94" width="262" height="24" rx="5" fill="{c["amberf"]}"/>')
    b.append(T(372, 111, 'limit = pageSize - 1', 12, 'amber', 600, mono=True, c=c))
    b.append(bars(c, 372, 128, [170], 14, 6))
    b.append(T(358, 180, 'An off-by-one in the page query.', 13, 'muted', c=c))
    b.append(T(358, 200, 'api/reports/query.ts:57', 11.5, 'blue', 500, mono=True, c=c))
    for i, t in enumerate(['Every page shows all its rows', 'The last page may be shorter', 'Page size stays 50']):
        y = 64 + i * 40
        b.append(mark(c, 704, y, True))
        b.append(T(722, y + 5, t, 13, 'text', 500, c=c))
    b.append(T(698, 200, 'Fix: one test, one line.', 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Diagnosis of a bug: how to reproduce it, its root cause in the code, and the behaviour the fix must have')


def plan_ill(c: Theme) -> str:
    W, H = 1000, 340
    b = [card(c, 0, 0, 590, 336), doc_head(c, 0, 0, 590, '02-plan.md', 'You approve this')]
    b.append(T(18, 62, 'WHAT CHANGES', 11, 'dim', 700, c=c))
    for i, (t, col, fill) in enumerate([('Reports', 'cardline', 'bg'), ('Exporter', 'violet', 'violetf'), ('CSV file', 'blue', 'bluef')]):
        x = 18 + i * 150
        b.append(card(c, x, 74, 120, 36, stroke=col, fill=fill, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 60, 97, t, 12.5, 'text', 600, 'middle', c=c))
        if i < 2:
            b.append(arrow(c, x + 122, 92, x + 148))
    b.append(T(18, 142, 'DECISIONS MADE FOR YOU', 11, 'dim', 700, c=c))
    for i, t in enumerate(['Large reports go by email, not a download', 'Columns follow the table on screen']):
        y = 154 + i * 42
        b.append(f'<rect x="18" y="{y}" width="554" height="34" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(32, y + 22, t, 13, 'text', 500, c=c))
        b.append(T(558, y + 22, 'comment to change', 11.5, 'dim', 500, 'end', c=c))
    b.append(T(18, 262, 'Trust boundary: none', 12.5, 'text', 600, mono=True, c=c))
    b.append(T(18, 282, 'So Verify skips the security review.', 12.5, 'muted', c=c))
    b.append(button(c, 270, 288, 148, 'Request changes'))
    b.append(button(c, 428, 288, 144, 'Approve', True))
    b.append(card(c, 610, 0, 390, 336))
    b.append(T(628, 30, 'Slices and scenarios', 14, 'text', 650, c=c))
    b.append(T(628, 50, 'Drawn by the App from the details', 12, 'dim', 500, c=c))
    sl = [('s1', 'Slice 1 · Export one report', 'Side by side with slice 2', 'muted'),
          ('s2', 'Slice 2 · Filter the export', 'Side by side with slice 1', 'muted'),
          ('s3', 'Slice 3 · Large reports by email', 'Risky: new mail service', 'amber')]
    for i, (col, t, s, scol) in enumerate(sl):
        y = 68 + i * 50
        b.append(f'<rect x="628" y="{y}" width="4" height="40" rx="2" fill="{c[col]}"/>')
        b.append(T(642, y + 16, t, 13, 'text', 650, c=c))
        b.append(T(642, y + 34, s, 11.5, scol, 600 if scol == 'amber' else 400, c=c))
    b.append(T(628, 238, 'Scenarios', 13, 'text', 650, c=c))
    for i, t in enumerate(['Export a filtered report', '200,000 rows arrive by email']):
        y = 252 + i * 32
        b.append(f'<circle cx="638" cy="{y + 10}" r="5" fill="none" stroke="{c["teal"]}" stroke-width="2"/>')
        b.append(T(652, y + 14.5, t, 12.5, 'text', 500, c=c))
    return svg(W, H, ''.join(b), 'The Plan: what changes as a picture, the decisions made for you, the trust boundary line, Approve, and the slices and scenarios the App draws from the details')


# ---------------------------------------------------------------- Verify and Review
def verify_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = [card(c, 0, 0, 200, 326)]
    b.append(T(18, 30, 'Rounds', 13, 'muted', 650, c=c))
    for i, (t, ok, note) in enumerate([('Round 1', False, '2 gaps, fixed'), ('Round 2', True, 'All passed')]):
        y = 46 + i * 64
        b.append(card(c, 14, y, 172, 54, stroke='ok' if ok else 'cardline', fill='bg', sw=1.5 if ok else 1))
        b.append(mark(c, 34, y + 22, ok))
        b.append(T(50, y + 26, t, 13.5, 'text', 650, c=c))
        b.append(T(50, y + 44, note, 12, 'muted', c=c))
    groups = [('Recorded checks', [('Tests', 'PASS'), ('Lint and types', 'PASS'), ('Build', 'PASS')]),
              ('Done means', [('1  Export button', 'PASS'), ('2  Opens in a spreadsheet', 'PASS'), ('3  Email for large ones', 'PASS')]),
              ('Scenarios', [('Export a filtered report', 'PASS'), ('Export 200,000 rows', 'PASS')])]
    for g, (title, rows) in enumerate(groups):
        x = 224 + g * 262
        b.append(card(c, x, 0, 246, 326))
        b.append(T(x + 16, 30, title, 14, 'text', 650, c=c))
        for i, (t, r) in enumerate(rows):
            y = 48 + i * 44
            b.append(f'<rect x="{x + 12}" y="{y}" width="222" height="36" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(x + 24, y + 23, t, 12.5, 'text', 500, c=c))
            b.append(T(x + 222, y + 23, r, 11, 'ok', 700, 'end', mono=True, c=c))
        b.append(T(x + 16, 214, 'Evidence', 12, 'dim', 700, c=c))
        for k in range(3):
            ex = x + 16 + k * 72
            b.append(f'<rect x="{ex}" y="226" width="62" height="44" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(bars(c, ex + 8, 236, [44, 30, 38], 9, 4))
    return svg(W, H, ''.join(b), 'The Verify tab: rounds on the left, then the recorded checks, Done means and scenarios, each with PASS and its evidence')


def stopped_ill(c: Theme) -> str:
    W, H = 1000, 230
    b = []
    for i in range(2):
        x = i * 136
        b.append(card(c, x, 85, 120, 60, stroke='danger', fill='bg', sw=1.4))
        b.append(mark(c, x + 24, 115, False))
        b.append(T(x + 40, 120, f'Judge run {i + 1}', 13, 'text', 600, c=c))
    b.append(arrow(c, 258, 115, 290))
    b.append(card(c, 292, 75, 190, 80, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(310, 109, 'Stopped', 15, 'text', 650, c=c))
    b.append(T(310, 131, 'The choice is yours', 12.5, 'muted', c=c))
    opts = [('Continue', 'Keep the approach, try again'), ('Pivot', 'Agree on a new approach'),
            ('Abandon', 'Stop, keep the documents'), ('Accept as is', 'Go to Review, with what is open listed')]
    for i, (t, s) in enumerate(opts):
        y = i * 58
        b.append(curve(c, 482, 115, 530, y + 25, 'line'))
        b.append(card(c, 530, y, 470, 50))
        b.append(T(548, y + 31, t, 14, 'text', 650, c=c))
        b.append(T(672, y + 31, s, 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'When verification keeps failing: after two failed judge runs the task stops, and you choose to continue, pivot, abandon or accept it as is')


def review_ill(c: Theme) -> str:
    W, H = 1000, 350
    b = []
    tiles = [('11', 'tasks built'), ('4', 'checks recorded'), ('Round 2', 'judge passed'), ('1', 'plan change')]
    for i, (n, t) in enumerate(tiles):
        x = i * 252
        b.append(card(c, x, 0, 238, 74))
        b.append(T(x + 18, 36, n, 22, 'text', 700, c=c))
        b.append(T(x + 18, 58, t, 12.5, 'muted', c=c))
    b.append(card(c, 0, 90, 470, 196))
    b.append(T(18, 120, 'Try it yourself', 14, 'text', 650, c=c))
    for i, t in enumerate(['Open a report and press Export', 'Open the file in a spreadsheet', 'Export the 200,000-row report']):
        y = 138 + i * 44
        b.append(f'<circle cx="32" cy="{y + 16}" r="11" fill="none" stroke="{c["cardline"]}" stroke-width="1.5"/>')
        b.append(T(32, y + 20.5, str(i + 1), 12, 'muted', 650, 'middle', c=c))
        b.append(T(52, y + 21, t, 13, 'text', 500, c=c))
    b.append(card(c, 490, 90, 510, 196))
    b.append(T(508, 120, 'Files changed', 14, 'text', 650, c=c))
    for i, (f, add, rm) in enumerate([('api/reports/export.ts', 84, 0), ('api/reports/query.ts', 6, 4),
                                       ('web/reports/ExportButton.tsx', 41, 0), ('tests/export.test.ts', 120, 0)]):
        y = 138 + i * 34
        b.append(T(508, y + 16, f, 12, 'text', 500, mono=True, c=c))
        b.append(T(900, y + 16, f'+{add}', 12, 'ok', 600, 'end', mono=True, c=c))
        b.append(T(944, y + 16, f'-{rm}', 12, 'danger', 600, 'end', mono=True, c=c))
        b.append(f'<rect x="954" y="{y + 6}" width="28" height="10" rx="2" fill="{c["ok"]}" fill-opacity="0.6"/>')
    b.append(f'<rect x="0" y="300" width="1000" height="46" rx="12" fill="{c["amberf"]}"/>')
    b.append(T(18, 328, 'Your review · the finished change', 14, 'text', 650, c=c))
    b.append(button(c, 470, 307, 150, 'Request changes', h=32))
    b.append(button(c, 630, 307, 170, 'Create pull request', h=32))
    b.append(button(c, 812, 307, 176, 'Approve and ship', True, 32))
    return svg(W, H, ''.join(b), 'Review: what was built and checked, steps to try it, the files changed, Create pull request and the final approval')


def shipped_ill(c: Theme) -> str:
    W, H = 1000, 210
    b = [card(c, 0, 40, 200, 110, stroke='amber', fill='amberf', sw=1.6)]
    b.append(mark(c, 26, 76))
    b.append(T(42, 81, 'Approved', 15, 'text', 650, c=c))
    b.append(T(20, 108, 'Your final decision', 12.5, 'muted', c=c))
    b.append(arrow(c, 204, 95, 250))
    b.append(card(c, 252, 20, 300, 150))
    b.append(T(272, 50, 'The task keeps', 14, 'text', 650, c=c))
    for i, t in enumerate(['Every plan document', 'The build record and evidence', 'The pull request description']):
        y = 72 + i * 28
        b.append(f'<circle cx="280" cy="{y}" r="3.5" fill="{c["violet"]}"/>')
        b.append(T(292, y + 4.5, t, 13, 'muted', c=c))
    b.append(arrow(c, 556, 95, 600))
    b.append(f'<rect x="602" y="0" width="398" height="190" rx="14" fill="none" stroke="{c["line"]}" stroke-dasharray="6 5"/>')
    b.append(T(622, 26, 'Your own process', 12, 'dim', 700, c=c))
    for i, t in enumerate(['Pull request', 'Merge', 'Deploy']):
        x = 622 + i * 126
        b.append(card(c, x, 60, 106, 70, fill='bg'))
        b.append(T(x + 53, 100, t, 13.5, 'text', 600, 'middle', c=c))
        if i < 2:
            b.append(arrow(c, x + 108, 95, x + 124))
    b.append(T(622, 166, 'QualityLayer opens the pull request only when you click.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process')


def abandon_ill(c: Theme) -> str:
    W, H = 1000, 170
    b = []
    items = [('Abandon', 'Stops the work', 'The documents stay in your repository', 'danger'),
             ('Archive', 'Off the App’s task list', 'Restore brings it back', 'muted'),
             ('Delete', 'Archived tasks only', 'Asks first, then moves the files to the Trash', 'dim')]
    for i, (t, s, d, col) in enumerate(items):
        x = i * 340
        b.append(card(c, x, 0, 320, 166))
        b.append(f'<rect x="{x + 18}" y="20" width="34" height="34" rx="9" fill="{c["bg"]}" stroke="{c[col]}" stroke-width="1.6"/>')
        if i == 0:
            b.append(f'<rect x="{x + 28}" y="30" width="14" height="14" rx="2" fill="{c[col]}"/>')
        elif i == 1:
            b.append(f'<path d="M{x + 27} {33} h16 v11 h-16 z M{x + 25} {29} h20 v4 h-20 z" fill="none" stroke="{c[col]}" stroke-width="1.6"/>')
        else:
            b.append(f'<path d="M{x + 28} {32} h14 l-1.5 13 h-11 z M{x + 26} {30} h18 M{x + 32} {28} h6" fill="none" stroke="{c[col]}" stroke-width="1.6"/>')
        b.append(T(x + 66, 44, t, 16, 'text', 650, c=c))
        b.append(T(x + 18, 92, s, 13.5, 'text', 500, c=c))
        b.append(T(x + 18, 116, d, 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Abandon stops the work and keeps the documents; Archive hides a task; Delete removes an archived task after asking')


# ---------------------------------------------------------------- the App around the steps
def band_ill(c: Theme) -> str:
    W, H = 1000, 250
    b = [card(c, 0, 0, 1000, 246)]
    b.append(T(18, 28, 'Claude Code', 12, 'dim', 600, c=c))
    rows = [('While the Plan waits', 'amber', 'amberf', '◆ QL plan 2/5 · The Plan waits for you · CSV export', 'Open in the App ↗'),
            ('While it builds', 'blue', 'bluef', '◆ QL implement 3/5 · slice 2 of 4 · CSV export', None),
            ('When you are asked', 'amber', 'amberf', '◆ QL 1 ask for you · Dana on CSV export', '/ql answer')]
    for i, (label, col, fill, text, right) in enumerate(rows):
        y = 46 + i * 58
        b.append(T(18, y + 25, label, 12.5, 'muted', 500, c=c))
        b.append(f'<rect x="190" y="{y}" width="790" height="40" rx="6" fill="{c[fill]}"/>')
        b.append(f'<rect x="190" y="{y}" width="4" height="40" fill="{c[col]}"/>')
        b.append(T(208, y + 25, text, 12.5, 'text', 500, mono=True, c=c))
        if right:
            b.append(T(966, y + 25, right, 12.5, col, 600, 'end', mono=right.startswith('/'), c=c))
        else:
            b.append(f'<rect x="846" y="{y + 16}" width="120" height="8" rx="4" fill="{c["line"]}"/>')
            b.append(f'<rect x="846" y="{y + 16}" width="66" height="8" rx="4" fill="{c[col]}"/>')
    b.append(T(190, 230, '>', 14, 'muted', 600, mono=True, c=c))
    b.append(f'<rect x="206" y="218" width="8" height="16" fill="{c["muted"]}"/>')
    return svg(W, H, ''.join(b), 'The band above the Claude Code prompt: the Plan waits for you, how the build runs, or a teammate’s question for you')


def cost_ill(c: Theme) -> str:
    W, H = 1000, 290
    b = [card(c, 0, 0, 600, 286)]
    b.append(T(18, 30, 'Cost of this task', 15, 'text', 650, c=c))
    b.append(T(582, 30, 'estimated, list price', 12, 'dim', 500, 'end', c=c))
    steps = [('Discuss', 0.3, '$1.40', 'violet'), ('Plan', 0.5, '$2.30', 'amber'), ('Implement', 1.0, '$3.10', 'blue'),
             ('Verify', 0.6, '$2.20', 'teal'), ('Review', 0.1, '$0.30', 'amber')]
    for i, (n, m, usd, col) in enumerate(steps):
        y = 52 + i * 36
        b.append(T(18, y + 17, n, 13, 'text', 500, c=c))
        w = 300 * m
        b.append(f'<rect x="110" y="{y + 5}" width="{w}" height="16" rx="4" fill="{c[col]}" fill-opacity="0.75"/>')
        b.append(T(120 + w, y + 17, f'{m:.1f}M tokens · {usd}', 12, 'muted', c=c))
    b.append(f'<line x1="18" y1="240" x2="582" y2="240" stroke="{c["cardline"]}"/>')
    b.append(T(18, 266, 'Total 2.5M tokens · about $9.30', 13, 'text', 650, c=c))
    b.append(card(c, 620, 0, 380, 286))
    b.append(T(638, 30, 'Per helper', 15, 'text', 650, c=c))
    helpers = [('Slice helper 1', 'Sonnet 5.5', '0.3M'), ('Slice helper 2', 'Sonnet 5.5', '0.2M'),
               ('Checkpoint', 'Sonnet 5.5', '0.1M'), ('Polish', 'Sonnet 5.5', '0.2M'), ('Judge', 'Opus 5.5', '0.3M')]
    for i, (n, model, tok) in enumerate(helpers):
        y = 48 + i * 44
        b.append(f'<line x1="638" y1="{y}" x2="982" y2="{y}" stroke="{c["cardline"]}"/>')
        b.append(T(638, y + 27, n, 13, 'text', 500, c=c))
        b.append(T(800, y + 27, model, 12, 'muted', c=c))
        b.append(T(982, y + 27, tok, 12, 'text', 600, 'end', mono=True, c=c))
    return svg(W, H, ''.join(b), 'The cost view: tokens and estimated cost at list price for each step and each helper')


# ---------------------------------------------------------------- team
def team(c):
    W, H = 1000, 290
    b = []
    nodes = [('You ask', ['On a passage, diagram', 'or the whole Plan'], 'amber', 'amberf'),
             ('Slack DM', ['Opens the question', 'in their App'], 'cardline', None),
             ('They answer', ['Looks right, a change', 'or a reply'], 'cardline', None),
             ('Your agent', ['Reads the answer,', 'updates the Plan'], 'blue', 'bluef'),
             ('You decide', ['Only your approval', 'moves the task on'], 'amber', 'amberf')]
    xs = [i * 207 for i in range(5)]
    for i, (t, s, col, fill) in enumerate(nodes):
        b.append(node(c, xs[i], 30, 172, 96, t, s, col, fill))
        if i < 4:
            b.append(arrow(c, xs[i] + 174, 78, xs[i + 1] - 2, col='muted'))
    b.append(node(c, 414, 180, 172, 96, 'A guest with a link', ['Comments without', 'an account'], 'cardline', dash=True))
    b.append(f'<path d="M588 228 H707 V132" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M702 139 l5 -7 l5 7" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    return svg(W, H, ''.join(b), 'Plan review with your team: you ask a teammate about a part of the Plan, a Slack message opens it in their App, they answer, the answer reaches your agent, and you decide; a guest with a link can comment too')


def team_agents(c):
    W, H = 1000, 250
    b = [card(c, 0, 0, 230, 200)]
    b.append(T(16, 28, 'Dana’s App', 12, 'dim', 600, c=c))
    b.append(T(16, 54, 'An ask from you', 15, 'text', 650, c=c))
    b.append(T(16, 76, 'Work on it with your agent:', 12.5, 'muted', c=c))
    b.append(pill(c, 16, 92, 'Claude Code', 'text'))
    b.append(pill(c, 16 + 18 + 11 * 6.6 + 8, 92, 'Codex', 'text'))
    b.append(pill(c, 16, 122, 'Grok Bot', 'text'))
    b.append(T(16, 176, '/ql answer 7f3a', 12, 'blue', 500, mono=True, c=c))
    b.append(arrow(c, 232, 100, 258))
    b.append(node(c, 260, 0, 230, 200, 'Their agent', ['Reads the ask and the Plan,', 'looks at their own code,', 'asks them what it needs'], 'blue', 'bluef'))
    b.append(arrow(c, 492, 100, 518))
    b.append(node(c, 520, 0, 230, 200, 'A draft', ['Nothing is sent', 'without their yes'], 'cardline'))
    b.append(button(c, 536, 112, 64, 'Send', True, 30))
    b.append(button(c, 608, 112, 56, 'Edit', False, 30))
    b.append(button(c, 672, 112, 66, 'Discard', False, 30))
    b.append(arrow(c, 752, 100, 778))
    b.append(card(c, 780, 0, 220, 200, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(796, 28, 'Your App', 12, 'dim', 600, c=c))
    b.append(f'<circle cx="810" cy="66" r="14" fill="{c["bg"]}" stroke="{c["amber"]}" stroke-width="1.5"/>')
    b.append(T(810, 70.5, 'D', 12, 'amber', 700, 'middle', c=c))
    b.append(T(832, 62, 'Dana', 13, 'text', 650, c=c))
    b.append(T(832, 80, 'via Claude Code', 12, 'muted', 500, c=c))
    b.append(T(796, 116, 'Suggests a change', 13, 'amber', 600, c=c))
    b.append(T(796, 140, 'Reaches your agent', 12.5, 'muted', c=c))
    b.append(T(796, 158, 'like any answer', 12.5, 'muted', c=c))
    b.append(T(W / 2, 236, 'Their agent runs on their own computer. Codex uses $ql answer; Grok Bot gets the ql skill from the App.', 13, 'muted', 400, 'middle', c=c))
    return svg(W, H, ''.join(b), 'A teammate answers with their own agent: Claude Code, Codex or Grok Bot reads the ask and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent')


def team_timeline(c: Theme) -> str:
    W, H = 1000, 210
    b = []
    bands = [(0, 420, 'Discuss and Plan', 'violet', 'violetf'), (430, 680, 'Implement and Verify', 'blue', 'bluef'),
             (690, 1000, 'Review', 'amber', 'amberf')]
    for x1, x2, t, col, fill in bands:
        b.append(f'<rect x="{x1}" y="104" width="{x2 - x1}" height="44" rx="10" fill="{c[fill]}" stroke="{c[col]}" stroke-width="1.4"/>')
        b.append(T((x1 + x2) / 2, 131, t, 14, 'text', 650, 'middle', c=c))
    b.append(T(210, 176, 'Comments are cheap: nothing is built yet', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(555, 176, 'Your agent builds and checks', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(845, 176, 'Reviewed with its proof', 12.5, 'muted', 400, 'middle', c=c))
    callouts = [(40, 340, '1  Review the plan', 'Before any code is written', 'violet'),
                (650, 350, '2  Review the change', 'After the build, with its proof', 'amber')]
    for x, w, t, s, col in callouts:
        b.append(card(c, x, 0, w, 62, stroke=col, sw=1.6))
        b.append(T(x + 16, 26, t, 15, 'text', 700, c=c))
        b.append(T(x + 16, 47, s, 12.5, 'muted', c=c))
        b.append(f'<path d="M{x + w / 2} 62 V100" stroke="{c[col]}" stroke-width="1.8"/>')
        b.append(f'<path d="M{x + w / 2 - 5} 94 l5 7 l5 -7" fill="none" stroke="{c[col]}" stroke-width="1.8"/>')
    return svg(W, H, ''.join(b), 'Two moments for your team: review the plan before any code, and review the finished change after the build')


def team_change(c: Theme) -> str:
    W, H = 1000, 330
    b = []
    top = [(0, 'Build passed', 'Every check, with evidence', 'cardline'),
           (230, 'Team review', 'Why, how, and the proof', 'teal'),
           (500, 'Threads', '2 of 3 approved · 2 open', 'amber'),
           (770, 'Approve and ship', 'When every thread is settled', 'blue')]
    for x, t, s, col in top:
        b.append(card(c, x, 20, 220 if x < 770 else 230, 74, stroke=col, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 16, 50, t, 14.5, 'text', 650, c=c))
        b.append(T(x + 16, 72, s, 12, 'muted', c=c))
    for x1, x2 in ((222, 228), (452, 498), (722, 768)):
        b.append(arrow(c, x1, 57, x2))
    bottom = [(500, 'Back to your agent', '/ql review csv-export', 'blue', True), (230, 'Checked again', 'A new verify round', 'teal', False)]
    for x, t, s, col, mono in bottom:
        b.append(card(c, x, 190, 220, 74, stroke=col, sw=1.6))
        b.append(T(x + 16, 220, t, 14.5, 'text', 650, c=c))
        b.append(T(x + 16, 242, s, 12, 'blue' if mono else 'muted', 500, mono=mono, c=c))
    b.append(arrow(c, 610, 96, 610, 188, 'amber'))
    b.append(T(620, 146, 'open threads', 12, 'amber', 600, c=c))
    b.append(arrow(c, 498, 227, 452))
    b.append(arrow(c, 340, 188, 340, 96, 'teal'))
    b.append(T(350, 146, 're-review', 12, 'teal', 600, c=c))
    b.append(T(500, 290, 'Each thread ends', 12.5, 'muted', 500, c=c))
    for i, t in enumerate(['fixed', 'answered', 'replanned']):
        b.append(pill(c, 610 + i * 92, 276, t, 'text', 82))
    return svg(W, H, ''.join(b), 'Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again before the re-review')


def peers(c):
    W, H = 1000, 270
    b = []
    pos = {'a': (60, 40, 'Claude Code', 'Building the export', 'blue'), 'b': (60, 190, 'Claude Code', 'Fixing a flaky test', 'blue'),
           'c': (700, 40, 'Codex', 'Reviewing the Plan', 'violet'), 'd': (700, 190, 'Codex', 'Idle', 'violet')}
    links = [('a', 'c', 'Asks for a review'), ('b', 'd', 'Hands over a task'), ('a', 'b', 'Talks a problem through')]
    for f, t, lab in links:
        x1, y1 = pos[f][0] + 240, pos[f][1] + 36
        x2 = pos[t][0]
        if f == 'a' and t == 'b':
            b.append(f'<path d="M{pos[f][0] + 120} {pos[f][1] + 72} V{pos[t][1]}" stroke="{c["line"]}" stroke-width="2"/>')
            b.append(f'<rect x="{pos[f][0] + 40}" y="{(pos[f][1] + 72 + pos[t][1]) / 2 - 13}" width="160" height="26" rx="13" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(pos[f][0] + 120, (pos[f][1] + 72 + pos[t][1]) / 2 + 4, lab, 12, 'muted', 500, 'middle', c=c))
            continue
        b.append(f'<path d="M{x1} {y1} H{x2}" stroke="{c["line"]}" stroke-width="2"/>')
        b.append(f'<path d="M{x2 - 8} {y1 - 5} l8 5 l-8 5" fill="none" stroke="{c["line"]}" stroke-width="2"/>')
        b.append(f'<rect x="{(x1 + x2) / 2 - 80}" y="{y1 - 13}" width="160" height="26" rx="13" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T((x1 + x2) / 2, y1 + 4, lab, 12, 'muted', 500, 'middle', c=c))
    for x, y, name, what, col in pos.values():
        b.append(f'<rect x="{x}" y="{y}" width="240" height="72" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<circle cx="{x + 22}" cy="{y + 25}" r="6" fill="{c[col]}"/>')
        b.append(T(x + 38, y + 30, name, 15, 'text', 650, c=c))
        b.append(T(x + 22, y + 52, what, 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Claude Code and Codex sessions on one computer messaging each other')


# ---------------------------------------------------------------- getting started
def install_ill(c: Theme) -> str:
    W, H = 1000, 270
    b = [node(c, 0, 85, 220, 100, 'You install', ['From the download page,', 'the terminal installer', 'or Pilot Shell 11'], 'cardline')]
    b.append(arrow(c, 222, 135, 270))
    b.append(diamond(c, 300, 135, 22, 'amberf', 'amber'))
    b.append(T(300, 190, 'A screen?', 13, 'text', 650, 'middle', c=c))
    b.append(f'<path d="M322 135 C350 135 350 55 378 55" fill="none" stroke="{c["blue"]}" stroke-width="2"/>')
    b.append(f'<path d="M322 135 C350 135 350 215 378 215" fill="none" stroke="{c["muted"]}" stroke-width="2"/>')
    b.append(T(364, 44, 'yes', 12, 'blue', 600, 'middle', c=c))
    b.append(T(364, 236, 'no', 12, 'muted', 600, 'middle', c=c))
    b.append(node(c, 380, 10, 300, 90, 'The App', ['macOS, Windows, Linux desktop', 'Sets up the command line too'], 'blue', 'bluef'))
    b.append(node(c, 380, 170, 300, 90, 'Command line only', ['WSL2, dev containers, servers', 'Opens the App in your browser'], 'cardline'))
    b.append(arrow(c, 682, 55, 718))
    b.append(arrow(c, 682, 215, 718))
    b.append(node(c, 720, 10, 280, 90, 'Updates itself', ['The App and its command line,', 'together'], 'cardline'))
    b.append(card(c, 720, 170, 280, 90))
    b.append(T(736, 198, 'Updates by command', 15, 'text', 650, c=c))
    b.append(T(736, 222, 'qualitylayer update', 13, 'blue', 500, mono=True, c=c))
    return svg(W, H, ''.join(b), 'One rule: a machine with a screen gets the App, which updates itself; WSL2, dev containers and servers get the command line and open the App in a browser')


def firsttask_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    steps = [('Describe', 'the change'), ('Answer', 'its questions'), ('Approve', 'the Plan'), ('Start', 'Implement'),
             ('Follow', 'the build'), ('Read', 'the check'), ('Approve', 'the change')]
    you = {0, 1, 2, 3, 6}
    xs = [60 + i * 147 for i in range(len(steps))]
    b.append(f'<line x1="{xs[0]}" y1="70" x2="{xs[-1]}" y2="70" stroke="{c["line"]}" stroke-width="2"/>')
    for i, (t, s) in enumerate(steps):
        col = 'amber' if i in you else 'blue'
        b.append(f'<circle cx="{xs[i]}" cy="70" r="24" fill="{c["amberf" if i in you else "bluef"]}" stroke="{c[col]}" stroke-width="2"/>')
        b.append(T(xs[i], 76, str(i + 1), 16, col, 700, 'middle', c=c))
        b.append(T(xs[i], 124, t, 14, 'text', 650, 'middle', c=c))
        b.append(T(xs[i], 144, s, 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(xs[0] - 24, 22, 'You act at the amber steps; your agent does the rest', 12.5, 'muted', 500, c=c))
    return svg(W, H, ''.join(b), 'Your first task in seven steps: describe the change, answer its questions, approve the Plan, start Implement, follow the build, read the check, approve the change')


def update_ill(c: Theme) -> str:
    W, H = 1000, 160
    b = []
    cards = [('Checks daily', ['Or choose Check', 'for updates'], 'cardline', None),
             ('Asks you', ['In the tray: now', 'or later'], 'amber', 'amberf'),
             ('Waits on Windows', ['While agent commands', 'still run'], 'cardline', None),
             ('Both replaced', ['The App and its', 'command line'], 'blue', 'bluef')]
    for i, (t, s, col, fill) in enumerate(cards):
        x = i * 256
        b.append(node(c, x, 0, 230, 96, t, s, col, fill))
        if i < 3:
            b.append(arrow(c, x + 232, 48, x + 254))
    b.append(T(0, 134, 'Agents keep calling the same command. On WSL2, dev containers and servers, run', 13, 'muted', c=c))
    b.append(T(0, 154, 'qualitylayer update', 13, 'blue', 500, mono=True, c=c))
    return svg(W, H, ''.join(b), 'Updating the App: it checks daily, asks you in the tray, waits for running agent commands on Windows, and replaces the App and its command line together')


def move_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    cols = [('Carried over', 'ok', ['Your licence', 'Your plans in docs/plans', 'Your own settings and files']),
            ('Removed', 'cardline', ['Pilot Shell’s own files', 'Its agent settings entries', 'Its shell profile block']),
            ('Stays', 'ok', ['Tools Pilot Shell installed', 'Pilot Shell memories', 'Ask your agent to remove any'])]
    for i, (t, col, items) in enumerate(cols):
        x = i * 340
        b.append(card(c, x, 0, 320, 186, stroke=col, fill='card', sw=1 if col == 'cardline' else 1.6))
        b.append(T(x + 18, 32, t, 15, 'text', 650, c=c))
        for k, s in enumerate(items):
            y = 64 + k * 38
            last = i == 2 and k == 2
            if not last:
                b.append(mark(c, x + 26, y + 2) if col == 'ok' else f'<circle cx="{x + 24}" cy="{y + 1}" r="3.5" fill="{c[col if col != "cardline" else "dim"]}"/>')
            b.append(T(x + (18 if last else 40), y + 6, s, 13, 'dim' if last else 'text', 500, c=c))
    return svg(W, H, ''.join(b), 'Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell’s own parts are removed; the tools it installed and its memories stay')


# ---------------------------------------------------------------- reference
def settings_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = [card(c, 0, 0, 600, 326)]
    b.append(T(20, 30, 'Settings › Workflow', 15, 'text', 650, c=c))
    b.append(T(20, 50, 'For every project on this computer', 12.5, 'muted', c=c))
    rows = [('Workers in Claude Code', 'Sonnet 5.5'), ('Judge in Claude Code', 'Opus 5.5'),
            ('Codex reviews Claude Code’s work', 'GPT-6.1 Sol'),
            ('Claude Code reviews Codex’s work', 'Sonnet 5.5'), ('Notifications', True)]
    for i, (what, v) in enumerate(rows):
        y = 66 + i * 50
        b.append(f'<line x1="20" y1="{y}" x2="580" y2="{y}" stroke="{c["cardline"]}"/>')
        b.append(T(20, y + 31, what, 13.5, 'text', 500, c=c))
        if isinstance(v, bool):
            b.append(switch(c, 552, y + 16, v))
        else:
            b.append(f'<rect x="410" y="{y + 11}" width="170" height="30" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(422, y + 31, v, 12.5, 'text', 500, c=c))
            b.append(f'<path d="M562 {y + 23} l4 4 l4 -4" fill="none" stroke="{c["muted"]}" stroke-width="1.5"/>')
    b.append(card(c, 620, 0, 380, 326))
    b.append(T(640, 30, 'For one task', 15, 'text', 650, c=c))
    b.append(T(640, 50, 'Say it in words; your agent records it', 12.5, 'muted', c=c))
    chips = ['+security', '-security', '+checkpoint:all', '-checkpoint', '+second-opinion', '-second-opinion', '-ui-review']
    for i, ch in enumerate(chips):
        x = 640 + (i % 2) * 170
        y = 72 + (i // 2) * 34
        b.append(pill(c, x, y, ch, 'text', 160, mono=True))
    b.append(T(640, 230, '“Skip security” is recorded as', 12.5, 'muted', c=c))
    b.append(T(640, 250, '-security on this task.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Settings, Workflow: the Subagents and Second opinion cards and Notifications; and the overrides for one task, said in words')


def files_ill(c: Theme) -> str:
    W, H = 1000, 350
    b = [card(c, 0, 0, 640, 346)]
    b.append(T(18, 30, 'docs/plans/2026-10-03-csv-export/', 13.5, 'text', 700, mono=True, c=c))
    rows = [('00-discuss.md · 00-discuss-details.md', 'Discuss', 'pair'),
            ('01-research.md or 01-diagnosis.md', 'Research or diagnosis', 'blue'),
            ('02-plan.md · 02-plan-details.md', 'The Plan you approve', 'pair'),
            ('artifacts/', 'Mockups and diagrams', 'amber'),
            ('03-build.md · 03-build-details.md', 'The build record and checks', 'blue'),
            ('reviews/', 'Second-opinion findings', 'violet'),
            ('evidence/', 'Test output, logs, screenshots', 'teal'),
            ('pr-description.md', 'The pull request text', 'dim')]
    for i, (f, what, kind) in enumerate(rows):
        y = 50 + i * 36
        b.append(f'<line x1="26" y1="{y - 8}" x2="26" y2="{y + 14}" stroke="{c["line"]}"/>')
        b.append(f'<line x1="26" y1="{y + 6}" x2="38" y2="{y + 6}" stroke="{c["line"]}"/>')
        if kind == 'pair':
            b.append(f'<circle cx="48" cy="{y + 6}" r="4.5" fill="{c["amber"]}"/>')
            b.append(f'<circle cx="60" cy="{y + 6}" r="4.5" fill="{c["blue"]}"/>')
        else:
            b.append(f'<circle cx="54" cy="{y + 6}" r="4.5" fill="{c[kind]}"/>')
        b.append(T(74, y + 10.5, f, 12, 'text', 500, mono=True, c=c))
        b.append(T(622, y + 10.5, what, 12, 'muted', 400, 'end', c=c))
    b.append(card(c, 660, 0, 340, 346))
    b.append(T(678, 30, 'What the colours mean', 14, 'text', 650, c=c))
    leg = [('amber', 'For you: the short version you review'), ('blue', 'For the agent: contracts, files, detail'),
           ('teal', 'Evidence the checks kept'), ('violet', 'The other vendor’s review'), ('dim', 'Task records')]
    for i, (k, t) in enumerate(leg):
        y = 56 + i * 34
        b.append(f'<circle cx="686" cy="{y}" r="5" fill="{c[k]}"/>')
        b.append(T(700, y + 4.5, t, 12.5, 'text', 500, c=c))
    b.append(T(678, 250, 'All of it lives in your repository,', 12.5, 'muted', c=c))
    b.append(T(678, 270, 'next to your code, and goes into', 12.5, 'muted', c=c))
    b.append(T(678, 290, 'Git with the change.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'A task folder in docs/plans: the Discuss and Plan documents with their details, research or diagnosis, mockups, the build record, reviews, evidence and the pull request text')


def privacy_ill(c: Theme) -> str:
    W, H = 1000, 280
    b = [card(c, 0, 0, 420, 276, stroke='ok', sw=1.5)]
    b.append(T(18, 30, 'Stays on your computer', 14, 'text', 650, c=c))
    for i, t in enumerate(['Your code and the diff', 'Every plan document', 'Build evidence and logs', 'The App and its cost view']):
        y = 52 + i * 32
        b.append(mark(c, 30, y + 8))
        b.append(T(46, y + 13, t, 13, 'text', 500, c=c))
    b.append(T(18, 196, 'Your agent sends your code to its own provider,', 12, 'muted', c=c))
    b.append(T(18, 214, 'as it always does. QualityLayer does not change that.', 12, 'muted', c=c))
    b.append(card(c, 440, 0, 560, 126))
    b.append(T(458, 30, 'QualityLayer service', 14, 'text', 650, c=c))
    b.append(T(458, 54, 'A daily licence check, with a few anonymous events', 12.5, 'muted', c=c))
    b.append(T(458, 74, 'about steps and results. Never a name, path or text.', 12.5, 'muted', c=c))
    b.append(T(458, 104, 'qualitylayer telemetry off  ·  DO_NOT_TRACK=1', 12, 'blue', 500, mono=True, c=c))
    b.append(card(c, 440, 146, 560, 130, stroke='violet', sw=1.4))
    b.append(T(458, 176, 'Team service · only when you share', 14, 'text', 650, c=c))
    b.append(T(458, 200, 'The Plan and its progress, the title and step, comments.', 12.5, 'muted', c=c))
    b.append(T(458, 222, 'Encrypted on your machine; only your team can read it.', 12.5, 'muted', c=c))
    b.append(T(458, 252, 'Never your code, the diff or your logs.', 12.5, 'text', 600, c=c))
    return svg(W, H, ''.join(b), 'What stays on your computer, what the licence check sends, and what sharing sends to the team service')


DRAWINGS = [('flow', flow), ('slices', slices), ('agents', agents), ('app', app), ('app-marked', app_marked),
            ('implement-start', implement_start), ('implement', implement_ill), ('checkpoint', checkpoint_ill),
            ('discuss', discuss_ill), ('diagnose', diagnose_ill), ('plan', plan_ill),
            ('verify', verify_ill), ('stopped', stopped_ill), ('review', review_ill), ('shipped', shipped_ill),
            ('abandon', abandon_ill), ('band', band_ill), ('cost', cost_ill),
            ('team', team), ('team-agents', team_agents), ('team-timeline', team_timeline), ('team-change', team_change),
            ('peers', peers), ('install', install_ill), ('firsttask', firsttask_ill), ('update', update_ill),
            ('move', move_ill), ('settings', settings_ill), ('files', files_ill), ('privacy', privacy_ill)]
DRAWINGS += [(f'track-{n.lower()}', track(n)) for n, _ in STEPS]

os.makedirs(OUT, exist_ok=True)
for name, fn in DRAWINGS:
    for theme, c in THEMES.items():
        with open(os.path.join(OUT, f'{name}-{theme}.svg'), 'w') as f:
            f.write(fn(c))
print('ok')
