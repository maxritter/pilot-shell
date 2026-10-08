#!/usr/bin/env python3
"""QualityLayer concept diagrams: one source, a light and a dark SVG each.

Used by the README and the docs. Regenerate after a change:
    python3 scripts/diagrams.py [static/img/diagrams]
"""
import os
import sys
from xml.sax.saxutils import escape

OUT = sys.argv[1] if len(sys.argv) > 1 else 'static/img/diagrams'
Theme = dict[str, str]

THEMES = {
    'light': dict(text='#1f2328', muted='#59636e', dim='#656d76', line='#d0d7de', card='#f6f8fa', cardline='#d0d7de',
                  bg='#ffffff', blue='#2076c5', blueink='#1a649f', bluef='#e8f1fb', violet='#6f4fc2',
                  violetf='#f0ebfb', amber='#9a5b00', amberf='#fff4dc', amberl='#e0a43a', ok='#6f4fc2',
                  off='#d8dee4', danger='#cf222e', onblue='#ffffff'),
    'dark': dict(text='#e6edf3', muted='#9198a1', dim='#8b949e', line='#3d444d', card='#151b23', cardline='#3d444d',
                 bg='#0d1117', blue='#5da3e5', blueink='#5da3e5', bluef='#132235', violet='#b49aed',
                 violetf='#1e1830', amber='#e8b04f', amberf='#2a2112', amberl='#b07a1c', ok='#b49aed',
                 off='#30363d', danger='#f85149', onblue='#0d1117'),
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# The five steps, in order; Plan and Review wait for your approval.
STEPS = [('Discuss', 'blue'), ('Plan', 'amber'), ('Implement', 'blue'), ('Verify', 'violet'), ('Review', 'amber')]
GATES = {'Plan', 'Review'}


def T(x: float, y: float, s: str, size: float = 14, fill: str = 'text', weight: int = 400, anchor: str = 'start',
      mono: bool = False, *, c: Theme) -> str:
    """A text element; `fill` is a theme key or a literal colour."""
    if fill == 'blue':
        fill = 'blueink'
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
                + T(x + w / 2, y + h / 2 + 4.5, text, 13, 'onblue', 650, 'middle', c=c))
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
            + T(x, y + 4.5, str(n), 12.5, 'onblue', 700, 'middle', c=c))


# ---------------------------------------------------------------- the five steps
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
# ---------------------------------------------------------------- who does what

# ---------------------------------------------------------------- the App window

# ---------------------------------------------------------------- after the Plan is approved

# ---------------------------------------------------------------- Discuss and Plan

# ---------------------------------------------------------------- Verify and Review

# ---------------------------------------------------------------- the App around the steps

# ---------------------------------------------------------------- team

def team(c):
    W, H = 1000, 290
    b = []
    nodes = [('You ask', ['On a passage, diagram', 'or the whole Plan'], 'amber', 'amberf'),
             ('Slack message', ['Opens the question', 'in their App'], 'cardline', None),
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


def move_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    cols = [('Carried over', 'ok', ['Your licence', 'Your plans in docs/plans', 'Your own settings and files']),
            ('Removed', 'cardline', ['Pilot Shell’s own files', 'Its agent settings entries', 'Its shell profile block']),
            ('Stays', 'ok', ['Tools Pilot Shell installed', 'Pilot Shell memories', 'Ask your agent to remove any'])]
    for i, (t, col, items) in enumerate(cols):
        x = i * 340
        b.append(card(c, x, 0, 320, 186, stroke='cardline', fill='card'))
        b.append(T(x + 18, 32, t, 15, 'text', 650, c=c))
        for k, s in enumerate(items):
            y = 64 + k * 38
            last = i == 2 and k == 2
            if not last:
                b.append(mark(c, x + 26, y + 2) if col == 'ok' else f'<circle cx="{x + 24}" cy="{y + 1}" r="3.5" fill="{c[col if col != "cardline" else "dim"]}"/>')
            b.append(T(x + (18 if last else 40), y + 6, s, 13, 'dim' if last else 'text', 500, c=c))
    return svg(W, H, ''.join(b), 'Moving from Pilot Shell 11: your licence, plans and own files carry over; Pilot Shell’s own parts are removed; the tools it installed and its memories stay')


# ---------------------------------------------------------------- reference
def files_ill(c: Theme) -> str:
    W, H = 1000, 350
    b = [card(c, 0, 0, 640, 346)]
    b.append(T(18, 30, 'docs/plans/2026-10-06-csv-export/', 13.5, 'text', 700, mono=True, c=c))
    rows = [('01-discuss.md', 'The problem, Done means, what you decided', 'amber'),
            ('02-plan.md', 'The Plan you approve', 'amber'),
            ('03-implement.md', 'The build, kept current by QualityLayer', 'amber'),
            ('04-verify.md', 'The proof for every point', 'amber'),
            ('05-review.md', 'What changed: the pull request text', 'amber'),
            ('design/', 'Interactive pages · local, out of Git', 'lock'),
            ('evidence/', 'Pictures and recordings', 'violet'),
            ('agent/', 'The agents’ details, logs and records', 'blue')]
    for i, (f, what, kind) in enumerate(rows):
        y = 50 + i * 34
        b.append(f'<line x1="26" y1="{y - 10}" x2="26" y2="{y + 14}" stroke="{c["line"]}"/>')
        b.append(f'<line x1="26" y1="{y + 6}" x2="38" y2="{y + 6}" stroke="{c["line"]}"/>')
        if kind == 'lock':
            b.append(lock(c, 49, y - 1, 'muted'))
        else:
            b.append(f'<circle cx="54" cy="{y + 6}" r="4.5" fill="{c[kind]}"/>')
        b.append(T(74, y + 10.5, f, 12.5, 'text', 600 if kind == 'amber' else 500, mono=True, c=c))
        b.append(T(622, y + 10.5, what, 12, 'muted', 400, 'end', c=c))
    b.append(T(18, 334, 'Files lists the five documents and designs; Comments holds their threads.', 12, 'dim', 500, c=c))
    b.append(card(c, 660, 0, 340, 346))
    b.append(T(678, 30, 'What you can read', 14, 'text', 650, c=c))
    leg = [('amber', 'One document per step'), ('blue', 'Agent records: read-only,'),
           (None, 'opened from the document-header chip'), ('violet', 'Evidence the checks kept'), ('lock', 'Interactive designs stay local')]
    for i, (k, t) in enumerate(leg):
        y = 56 + i * 30
        if k == 'lock':
            b.append(lock(c, 681, y - 7, 'muted'))
        elif k:
            b.append(f'<circle cx="686" cy="{y}" r="5" fill="{c[k]}"/>')
        b.append(T(700, y + 4.5, t, 12.5, 'text' if k else 'muted', 500, c=c))
    b.append(T(678, 230, 'The five documents read as plain', 12.5, 'muted', c=c))
    b.append(T(678, 250, 'Markdown on GitHub. They live in your', 12.5, 'muted', c=c))
    b.append(T(678, 270, 'repository and go into Git with', 12.5, 'muted', c=c))
    b.append(T(678, 290, 'the change.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'A task folder in docs/plans: five human documents, local interactive designs out of Git, evidence, and private agent details and logs. Files lists documents and designs; the document-header chip opens agent records read-only')


# ---------------------------------------------------------------- shared pieces of the App's anatomy
def ring(c: Theme, x: float, y: float, kind: str, r: float = 6) -> str:
    """Who acts: an amber ring for you, a blue open ring for agents, a filled dot when done."""
    if kind == 'you':
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c["amber"]}" stroke-width="2"/>'
    if kind == 'agent':
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c["blue"]}" stroke-width="2" '
                f'stroke-dasharray="{r * 5.2:.1f} {r * 1.2:.1f}" stroke-linecap="round"/>')
    if kind == 'dim':
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c["off"]}" stroke-width="2"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r - 0.5}" fill="{c["text"]}"/>'


def vmark(c: Theme, x: float, y: float) -> str:
    """A check made by agents: violet."""
    return (f'<path d="M{x - 6} {y} l4 4 l8 -9" fill="none" stroke="{c["violet"]}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def abtn(c: Theme, x: float, y: float, text: str, primary: bool = False, h: float = 26, size: float = 12) -> float:
    """Not a string: returns the width, so callers can lay buttons out. Use `abtn_svg` to draw."""
    return 18 + len(text) * (size * 0.52)


def abtn_svg(c: Theme, x: float, y: float, text: str, primary: bool = False, h: float = 26, size: float = 12,
             w: float | None = None) -> str:
    w = w if w is not None else abtn(c, x, y, text, primary, h, size)
    if primary:
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{c["blue"]}"/>'
                + T(x + w / 2, y + h / 2 + 4, text, size, 'onblue', 650, 'middle', c=c))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
            + T(x + w / 2, y + h / 2 + 4, text, size, 'text', 600, 'middle', c=c))


def buttons_right(c: Theme, right: float, y: float, labels: list, h: float = 26, size: float = 12) -> str:
    """Draw buttons right-aligned at `right`; a label may be ('text', True) for the primary one."""
    out, x = [], right
    for lab in reversed(labels):
        text, primary = (lab if isinstance(lab, tuple) else (lab, False))
        w = abtn(c, 0, 0, text, primary, h, size)
        x -= w
        out.append(abtn_svg(c, x, y, text, primary, h, size, w))
        x -= 8
    return ''.join(out)


def item(c: Theme, x: float, y: float, w: float, kind: str, what: str, answers: list, h: float = 56,
         state: str = 'you', note: str | None = None) -> str:
    """One item in Your turn: its kind, the thing itself, the answers of its family."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c["bg"]}" stroke="{c["cardline"]}"/>',
           ring(c, x + 18, y + 20, state),
           T(x + 34, y + 21, kind, 11.5, 'dim', 500, c=c),
           T(x + 34, y + 42, what, 13.5, 'text', 500, c=c)]
    if note:
        out.append(T(x + w - 16, y + 21, note, 11.5, 'dim', 500, 'end', c=c))
    out.append(buttons_right(c, x + w - 14, y + h / 2 - 13 + (6 if note else 0), answers))
    return ''.join(out)


def vline(c: Theme, x: float, y: float, w: float, facts: list, h: float = 34) -> str:
    """The violet line: what agents proved, never more than five facts."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{c["violetf"]}" stroke="{c["violet"]}" stroke-opacity="0.45"/>',
           T(x + 14, y + h / 2 + 4.5, 'Checked by agents', 12, 'violet', 700, c=c)]
    tx = x + 14 + 124
    for f in facts:
        out.append(T(tx, y + h / 2 + 4.5, f, 12, 'muted', 500, c=c))
        tx += 22 + len(f) * 6.1
    out.append(f'<path d="M{x + w - 24} {y + h / 2 - 2} l5 5 l5 -5" fill="none" stroke="{c["violet"]}" stroke-width="1.6"/>')
    return ''.join(out)


def stepline(c: Theme, x: float, y: float, w: float, kind: str, title: str, sub: str, buttons: list,
             h: float = 54) -> str:
    fill, stroke = {'you': ('amberf', 'amberl'), 'agent': ('bluef', 'blue'), 'done': ('card', 'cardline')}[kind]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" fill="{c[fill]}" stroke="{c[stroke]}" stroke-opacity="0.8"/>'
            + ring(c, x + 22, y + h / 2, kind, 7)
            + T(x + 42, y + 23, title, 14, 'text', 650, c=c)
            + T(x + 42, y + 41, sub, 12.5, 'muted', c=c)
            + buttons_right(c, x + w - 14, y + h / 2 - 14, buttons, h=28, size=12.5))


def section_label(c: Theme, x: float, y: float, title: str, count: str = '', col: str = 'text') -> str:
    out = T(x, y, title, 13, col, 650, c=c)
    if count:
        out += T(x + len(title) * 7.4 + 8, y, count, 12, 'dim', 500, c=c)
    return out


def tabs(c: Theme, x: float, y: float, here: int, counts: dict | None = None, done: int | None = None) -> str:
    """The step tabs: a done dot, the agent's open ring, your amber ring with its count."""
    counts = counts or {}
    out, sx = [], x
    for i, (s, _) in enumerate(STEPS):
        label = s + (f'  {counts[s]}' if s in counts else '')
        kind = 'done' if i < (done if done is not None else here) else ('you' if STEPS[i][1] == 'amber' and i == here else
                                                                       'agent' if i == here else 'dim')
        out.append(ring(c, sx + 5, y, kind, 5))
        out.append(f'<text x="{sx + 16}" y="{y + 4}" font-family="{SANS}" font-size="12.5" font-weight="{600 if i == here else 400}" '
                   f'fill="{c["text"] if i == here else c["dim"] if kind == "dim" else c["muted"]}">{escape(label)}</text>')
        sx += 16 + len(label) * 7.0 + 22
    return ''.join(out)


def sidebar(c: Theme, W: float, H: float, groups: list, selected: str | None = None) -> str:
    """The App's sidebar: search, Your turn / Running / Shipped, the foot with Feedback."""
    out = [f'<path d="M1 41 H221 V{H - 1} H17 a16 16 0 0 1 -16 -16 Z" fill="{c["card"]}"/>',
           f'<line x1="221" y1="41" x2="221" y2="{H - 1}" stroke="{c["cardline"]}"/>',
           T(20, 68, 'QualityLayer', 14, 'text', 700, c=c),
           f'<rect x="150" y="53" width="58" height="22" rx="6" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-opacity="0.6"/>',
           T(179, 68, '+ New', 11.5, 'text', 600, 'middle', c=c),
           f'<rect x="12" y="80" width="198" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>',
           T(24, 98, 'Search or jump to a task', 11.5, 'dim', c=c), T(198, 98, '⌘K', 10.5, 'dim', 500, 'end', mono=True, c=c)]
    y = 134
    for title, rows in groups:
        out.append(T(20, y, title, 11.5, 'amber' if title.startswith('Your turn') else 'muted', 650, c=c))
        y += 10
        for name, tail, kind in rows:
            if name == selected:
                out.append(f'<rect x="12" y="{y}" width="198" height="30" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            out.append(ring(c, 28, y + 15, kind, 4.5))
            out.append(T(40, y + 19, name, 12.5, 'text', 500, c=c))
            out.append(T(200, y + 19, tail, 10.5, 'amber' if kind == 'you' else 'dim', 500, 'end', mono=True, c=c))
            y += 32
        y += 14
    fy = H - 66
    out.append(f'<line x1="1" y1="{fy}" x2="221" y2="{fy}" stroke="{c["cardline"]}"/>')
    out.append(f'<circle cx="28" cy="{fy + 20}" r="11" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    out.append(T(28, fy + 24, 'MR', 9.5, 'muted', 650, 'middle', c=c))
    out.append(T(46, fy + 18, 'Max Ritter', 12, 'text', 600, c=c))
    out.append(T(46, fy + 33, 'Team licence', 10.5, 'dim', c=c))
    for i in range(3):
        out.append(f'<rect x="{14 + i * 34}" y="{fy + 40}" width="28" height="20" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
                   f'<circle cx="{28 + i * 34}" cy="{fy + 50}" r="3" fill="{c["dim"]}"/>')
    out.append(f'<rect x="120" y="{fy + 40}" width="90" height="20" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    out.append(T(165, fy + 54, 'Feedback', 11, 'text', 600, 'middle', c=c))
    return ''.join(out)


def head(c: Theme, x: float, y: float, w: float, title: str, chips: list) -> str:
    out = [T(x, y, title, 18, 'text', 650, c=c)]
    cx = x + len(title) * 9.6 + 14
    for ch in chips:
        pw = 16 + len(ch) * 6.3
        out.append(f'<rect x="{cx}" y="{y - 15}" width="{pw}" height="21" rx="10.5" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        out.append(T(cx + pw / 2, y - 1, ch, 11, 'muted', 500, 'middle', c=c))
        cx += pw + 6
    out.append(T(x + w, y - 2, 'Cost · $14.20     Share', 11.5, 'muted', 500, 'end', c=c))
    return ''.join(out)


# ---------------------------------------------------------------- the App as it is drawn now: one page per step
AMBER_FILL = '#f7b23b'


def spill(c: Theme, x: float, y: float, kind: str, head_: str, rest: str = '') -> tuple[str, float]:
    """A neutral named agent chip; its mark carries the live state."""
    text = 'Claude Code · ' + head_ + (f' · {rest}' if rest else '')
    w = 34 + len(text) * 6.2
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
           + ring(c, x + 14, y + 11, 'you' if kind == 'you' else 'agent', 4.5)
           + T(x + 25, y + 15, text, 11.5, 'text', 600, c=c))
    return out, w


def rside(c: Theme, x: float, y: float, w: float, h: float, tab: str) -> str:
    """The right sidebar: Files and Comments; designs are rows within Files."""
    out = [f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + h}" stroke="{c["cardline"]}"/>',
           f'<rect x="{x + 12}" y="{y + 12}" width="{w - 56}" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>']
    tab = 'files' if tab == 'designs' else tab
    half = (w - 60) / 2
    for i, t in enumerate(['Files', 'Comments']):
        bx = x + 14 + i * half
        if t.lower() == tab:
            out.append(f'<rect x="{bx}" y="{y + 14}" width="{half}" height="24" rx="6" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        out.append(T(bx + half / 2, y + 30, t, 10.5, 'text' if t.lower() == tab else 'muted', 600 if t.lower() == tab else 500, 'middle', c=c))
    out.append(f'<rect x="{x + w - 38}" y="{y + 14}" width="24" height="24" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
               f'<rect x="{x + w - 32}" y="{y + 20}" width="12" height="12" rx="2" fill="none" stroke="{c["dim"]}" stroke-width="1.3"/>')
    return ''.join(out)


def lock(c: Theme, x: float, y: float, col: str = 'text') -> str:
    return (f'<rect x="{x}" y="{y + 4}" width="10" height="8" rx="1.5" fill="none" stroke="{c[col]}" stroke-width="1.5"/>'
            f'<path d="M{x + 2} {y + 4} v-2.5 a3 3 0 0 1 6 0 v2.5" fill="none" stroke="{c[col]}" stroke-width="1.5"/>')


def mini_page(c: Theme, x: float, y: float, w: float, h: float) -> str:
    """A design drawn small: a page with a title and a table of rows."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{c["bg"]}" stroke="{c["cardline"]}"/>',
           f'<rect x="{x + w * 0.08}" y="{y + h * 0.12}" width="{w * 0.3}" height="{max(3, h * 0.07)}" rx="1.5" fill="{c["text"]}"/>']
    for i in range(4):
        ry = y + h * (0.32 + i * 0.15)
        out.append(f'<rect x="{x + w * 0.08}" y="{ry}" width="{w * 0.84}" height="{h * 0.1}" rx="1.5" fill="{c["card"]}"/>')
        out.append(f'<rect x="{x + w * 0.62}" y="{ry + h * 0.03}" width="{w * 0.16}" height="{h * 0.04}" rx="1" fill="{c["amber"] if i == 1 else c["dim"]}"/>')
    return ''.join(out)


# ---------------------------------------------------------------- the five steps
def flow(c):
    W, H = 1000, 280
    x0, cw = 130, 174
    cx = [x0 + i * cw + cw / 2 for i in range(5)]
    b = [f'<line x1="{cx[0]}" y1="62" x2="{cx[-1]}" y2="62" stroke="{c["line"]}" stroke-width="2"/>']
    for i, (n, col) in enumerate(STEPS):
        b.append(T(cx[i], 30, n, 16, 'text', 700, 'middle', c=c))
        b.append(diamond(c, cx[i], 62, 10) if n in GATES else f'<circle cx="{cx[i]}" cy="62" r="10" fill="{c[col]}"/>')
    you = ['Answer its questions', 'Answer, then approve', 'Copy one command', None, 'Settle what is left']
    agent = ['Reads the code, asks', 'Writes the Plan', 'Builds test first', 'Agents check it', 'Writes the PR text']
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


def slices(c):
    W, H = 1000, 292
    b = []
    for name, xa, xz, col in [('Implement', 0, 610, 'blue'), ('Verify', 640, 1000, 'violet')]:
        b.append(f'<rect x="{xa}" y="0" width="{xz - xa}" height="4" rx="2" fill="{c[col]}"/>')
        b.append(T(xa, 26, name, 15, col, 650, c=c))

    def sl(x, y, w, col, title, line2, col2, check):
        out = [card(c, x, y, w, 80, stroke=col, sw=1.6)]
        out.append(T(x + 14, y + 24, title, 13.5, 'text', 650, c=c))
        out.append(T(x + 14, y + 44, line2, 12, col2, 600 if col2 == 'amber' else 400, c=c))
        out.append(vmark(c, x + 20, y + 61))
        out.append(T(x + 32, y + 66, check, 11, 'blue', 500, mono=True, c=c))
        return ''.join(out)

    b.append(sl(0, 44, 190, 'blue', 'Slice 1 · Export', 'T1, T2, each test first', 'muted', 'check slice 1 · exit 0'))
    b.append(arrow(c, 192, 84, 214))
    b.append(sl(216, 44, 214, 'cardline', 'Slice 3 · Large reports', 'Risky: new mail service', 'amber', 'check slice 3 · exit 0'))
    b.append(arrow(c, 432, 84, 454))
    b.append(card(c, 456, 44, 154, 80, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(470, 68, 'Checkpoint', 13.5, 'text', 650, c=c))
    b.append(T(470, 88, 'Runs slice 3’s', 12, 'muted', c=c))
    b.append(T(470, 106, 'scenarios', 12, 'muted', c=c))
    b.append(sl(0, 144, 300, 'blue', 'Slice 2 · Filter the export', 'Side by side: shares no file with slice 1', 'muted', 'check slice 2 · exit 0'))
    b.append(f'<path d="M610 84 H625 V184 M300 184 H625" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(arrow(c, 625, 84, 644))
    b.append(arrow(c, 625, 184, 644))
    b.append(node(c, 646, 44, 170, 80, 'Polish', ['Leftover code,', 'missing tests, docs'], 'cardline'))
    b.append(node(c, 646, 144, 170, 80, 'Security review', ['Only when it crosses', 'a trust boundary'], 'cardline', dash=True))
    b.append(curve(c, 816, 84, 838, 134, 'muted'))
    b.append(curve(c, 816, 184, 838, 134, 'muted', True))
    b.append(node(c, 838, 94, 154, 80, 'Checking', ['Agents that did not', 'write the code'], 'violet', 'violetf'))
    b.append(T(W / 2, 258, 'Slices that share no files build side by side, and only a risky slice gets a checkpoint.', 13, 'muted', 400, 'middle', c=c))
    b.append(T(W / 2, 278, 'Then Polish and the security review run side by side, and agents check every point.', 13, 'muted', 400, 'middle', c=c))
    return svg(W, H, ''.join(b), 'Implement and Verify: slices built test first, side by side where they share no files, a checkpoint after a risky slice, then Polish and the security review side by side, then agents that did not write the code check every point')


def agents(c):
    W, H = 1000, 352
    b = []
    b.append(node(c, 0, 170, 160, 80, 'You', ['Answer, then approve', 'the Plan and change'], 'amber', 'amberf'))
    b.append(curve(c, 160, 210, 185, 210, 'amberl'))
    b.append(node(c, 185, 170, 190, 80, 'Your agent', ['Discuss and Plan,', 'Opus 5.5 recommended'], 'blue', 'bluef'))
    b.append(curve(c, 375, 210, 400, 210, 'blue'))
    b.append(f'<rect x="400" y="150" width="120" height="120" rx="12" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-width="2"/>')
    b.append(T(416, 180, 'The Plan', 15, 'text', 650, c=c))
    for i in range(4):
        b.append(f'<rect x="416" y="{196 + i * 15}" width="{[88, 72, 84, 56][i]}" height="6" rx="3" fill="{c["blue"]}" fill-opacity="0.35"/>')
    b.append(curve(c, 520, 210, 545, 210, 'blue'))
    b.append(node(c, 545, 170, 190, 80, 'Orchestrator', ['Started with one command,', 'Opus 5.5, writes no code'], 'blue', 'bluef'))
    right = [(0, 'Workers', ['Sonnet 5.5, each task', 'test first, fixes too'], 'blue'),
             (88, 'Polish and security', ['Side by side,', 'after the build'], 'violet'),
             (176, 'Checking', ['Opus 5.5. Agents that did', 'not write the code'], 'violet'),
             (264, 'Second opinion', ['The other coding agent,', 'on risky Plans'], 'violet')]
    for y, t, s, col in right:
        b.append(curve(c, 735, 210, 770, y + 39, col, dash=(t == 'Second opinion')))
        b.append(node(c, 770, y, 230, 78, t, s, 'cardline', dash=(t == 'Second opinion')))
        b.append(f'<circle cx="{980}" cy="{y + 22}" r="6" fill="{c[col]}"/>')
    b.append(T(474, 300, 'Every worker starts from the Plan,', 12, 'muted', c=c))
    b.append(T(474, 316, 'never from your chat', 12, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Who does what: you and your agent on Opus 5.5 discuss and write the Plan; the orchestrator you start with one command writes no code and hands each slice to workers on Sonnet 5.5; Polish and the security review run side by side; agents that did not write the code check it; a second opinion from the other coding agent reviews risky Plans by itself')


# ---------------------------------------------------------------- the App window
def task_example(c: Theme, step: int, sections: list, questions: list, working: str) -> str:
    """Current App model: two header rows, one focused card above the work, Files / Comments."""
    h = 118 + len(questions[0][2]) * 44 + 132 if questions else 144
    content_height = sum(41 if kind == 'heading' else 24 for kind, _ in sections) + (84 if step == 2 else 0)
    W, H = 1400, max(860, 138 + h + 32 + 65 + content_height + 62)
    b = [window(c, W, H, 'Settings cleanup · QualityLayer')]
    group = 'Your turn  1' if questions else 'Running  1'
    b.append(sidebar(c, W, H, [(group, [('Settings cleanup', STEPS[step][0], 'you' if questions else 'agent')]),
                               ('Shipped  6', [])], selected='Settings cleanup'))
    b.append(T(238, 67, 'Settings cleanup', 16, 'text', 650, c=c))
    b.append(tabs(c, 238, 104, step))
    p, _ = spill(c, 790, 48, 'you' if working == 'Waits for you' else 'agent', working)
    b.append(p)
    b.append(T(1368, 66, '…', 18, 'muted', 650, 'end', c=c))
    b.append(f'<line x1="222" y1="82" x2="{W}" y2="82" stroke="{c["cardline"]}"/>')
    x, y, w = 258, 138, 850
    if questions:
        kind, lines, choices = questions[0]
        b.append(card(c, x, y, w, h, stroke='amber', fill='bg'))
        b.append(T(x + 20, y + 29, 'Your turn', 17, 'text', 650, c=c))
        b.append(T(x + w - 20, y + 29, f'0 of {len(questions)} answered', 12, 'muted', 500, 'end', c=c))
        b.append(T(x + 20, y + 57, kind, 12, 'muted', 500, c=c))
        for k, line in enumerate(lines):
            b.append(T(x + 20, y + 83 + k * 19, line, 15, 'text', 600, c=c))
        for i, label in enumerate(choices):
            cy = y + 118 + i * 44
            b.append(f'<rect data-choice="{i + 1}" x="{x + 20}" y="{cy}" width="{w - 40}" height="36" rx="8" fill="{c["bg"]}" stroke="{c["blue"] if kind == "Question" and i == 0 else c["cardline"]}"/>')
            b.append(T(x + 34, cy + 23, str(i + 1), 12, 'muted', 500, c=c))
            b.append(T(x + 58, cy + 23, label, 13, 'text', 600, c=c))
            if kind == 'Question' and i == 0:
                b.append(T(x + w - 34, cy + 23, 'Recommended', 11.5, 'blue', 600, 'end', c=c))
        own_y = y + 118 + len(choices) * 44
        b.append(T(x + 20, own_y + 14, 'Your own answer', 12, 'muted', 500, c=c))
        b.append(f'<rect data-own-words="true" x="{x + 20}" y="{own_y + 26}" width="{w - 130}" height="38" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(x + 32, own_y + 50, 'Write what works for you…', 12.5, 'dim', c=c))
        b.append(abtn_svg(c, x + w - 96, own_y + 26, 'Send', True, 38, 12.5, 76))
        if kind == 'Question':
            b.append(T(x + 20, own_y + 96, 'Tell me more', 12, 'blue', 600, c=c))
            b.append(T(x + 148, own_y + 96, 'Skip for now', 12, 'blue', 600, c=c))
            b.append(T(x + w - 20, own_y + 96, 'Each answer reaches the agent immediately.', 12, 'muted', 400, 'end', c=c))
        else:
            b.append(T(x + 20, own_y + 96, 'Settle this point, then continue to the next open decision.', 12, 'muted', c=c))
            if step == 1:
                b.append(T(x + 20, own_y + 116, 'Answers do not approve the Plan.', 12, 'muted', c=c))
    else:
        h = 144
        b.append(card(c, x, y, w, h))
        b.append(T(x + 16, y + 29, "Agent’s turn", 17, 'text', 650, c=c))
        b.append(T(x + 16, y + 56, working, 12.5, 'text', 500, c=c))
        b.append(T(x + 16, y + 82, 'Open the live status for details.', 12, 'muted', c=c))
        b.append(T(x + 16, y + 111, 'You can comment while it works.', 12, 'muted', c=c))
    dx, dy = 258, y + h + 32
    b.append(T(dx, dy, f'{step + 1:02d}-{STEPS[step][0].lower()}.md  ▾', 11.5, 'muted', 500, mono=True, c=c))
    b.append(T(dx + w, dy, 'Read in full', 12, 'blue', 600, 'end', c=c))
    b.append(T(dx, dy + 36, 'Build' if step == 2 else STEPS[step][0], 23, 'text', 650, c=c))
    yy = dy + 65
    for kind, text in sections:
        if kind == 'heading':
            yy += 12
            b.append(T(dx, yy, text, 14, 'text', 650, c=c))
            yy += 29
        else:
            col = 'violet' if kind == 'proof' else 'text' if kind == 'agreed' else 'muted'
            b.append(T(dx, yy, text, 12.5, col, 500, c=c))
            yy += 24
    if step == 2:
        for i, label in enumerate(['▸ 11 helpers allocated', '▸ 14 helpers awaiting commit', '▸ 34 helpers finished']):
            b.append(T(dx, yy + 18 + i * 28, label, 12, 'muted', c=c))
    b.append(rside(c, 1140, 82, 260, H - 82, 'files'))
    b.append(T(1156, 148, 'Settings cleanup', 12, 'muted', 600, c=c))
    for i, label in enumerate(['01-discuss.md', '02-plan.md', '03-implement.md', '04-verify.md', '05-review.md']):
        b.append(T(1156, 184 + i * 32, label, 12, 'text' if i <= step else 'dim', 500, mono=True, c=c))
    b.append(T(1156, 368, 'Designs · 1', 12, 'muted', 600, c=c))
    b.append(T(1156, 398, 'Settings page', 12.5, 'text', 600, c=c))
    b.append(T(1156, 420, 'Only on this computer', 11.5, 'muted', c=c))
    b.append(T(dx, H - 24, 'Illustration · example task, people and results', 10.5, 'muted', c=c))
    return svg(W, H, ''.join(b), f'{STEPS[step][0]}: named agent status, one focused Your turn card above the work, visible own words and Send for questions, and Files / Comments with designs within Files')


def app(c):
    return plan_ill(c)


def app_marked(c: Theme) -> str:
    """The App illustration uses the current focused-card layout of the Plan."""
    return app(c)


def home_ill(c: Theme) -> str:
    W, H = 1100, 540
    b = [window(c, W, H, 'Home · QualityLayer')]
    b.append(sidebar(c, W, H, [('Your turn  1', [('Settings cleanup', 'Plan', 'you')]),
                               ('Running  1', [('Links', 'Verify', 'agent')]), ('Shipped  6', [])]))
    b.append(T(242, 76, 'Home', 22, 'text', 650, c=c))
    b.append(T(1076, 76, 'Notifications · 2', 12, 'blue', 600, 'end', c=c))
    b.append(T(242, 108, 'Discuss 1  ·  Plan 1  ·  Implement 0  ·  Verify 1  ·  Review 0', 12, 'muted', c=c))
    groups = [('Your turn', 'amber', 'amberf', 'Settings cleanup · 2 questions', 'Answer in any order; each answer reaches the agent at once.'),
              ('Agents at work', 'blue', 'bluef', 'Links · checking point 2', 'Open the live status for what is working, quiet or stopped.'),
              ('Shipped', 'cardline', 'card', 'CSV export · shipped today', '42 min · $4.20 estimated · open the result and proof')]
    for i, (title, col, fill, task, detail) in enumerate(groups):
        y = 140 + i * 120
        b.append(card(c, 238, y, 842, 102, stroke=col, fill=fill))
        b.append(T(258, y + 25, title, 12, 'muted', 650, c=c))
        b.append(T(258, y + 51, task, 16, 'text', 650, c=c))
        b.append(T(258, y + 78, detail, 12.5, 'muted', c=c))
    b.append(T(242, H - 20, 'Illustration · example tasks and costs', 10.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Home: Your turn, live agent work, shipped tasks with time and estimated cost, task counts in each step and the notification bell')


def plan_full(c: Theme) -> str:
    W, H = 1100, 530
    b = [window(c, W, H, 'Plan · QualityLayer')]
    b.append(T(18, 70, '← Exit full size', 12, 'blue', 600, c=c))
    b.append(T(216, 70, 'Settings cleanup · Plan', 16, 'text', 650, c=c))
    p, _ = spill(c, 758, 51, 'agent', 'Writing the Plan')
    b.append(p)
    b.append(T(18, 116, 'Outline', 12, 'muted', 650, c=c))
    for i, text in enumerate(['The problem', 'Done means', 'Interface', 'Decisions', 'Slices', 'Checks']):
        b.append(T(18, 148 + i * 29, text, 12.5, 'text', 500, c=c))
    b.append(T(210, 114, '02-plan.md  ▾', 11.5, 'muted', mono=True, c=c))
    b.append(T(374, 114, 'Path · Editor · More agent records', 11.5, 'blue', c=c))
    rows = [('01', 'The Plan'), ('02', ''), ('03', 'Done means'), ('04', '1 · Every setting names what it changes.'),
            ('05', '2 · A risky Plan gets a second opinion.'), ('06', ''), ('07', 'Engineering decisions'),
            ('08', 'Keep the retry limit visible beside each setting.'), ('09', ''), ('10', 'Slices and checks'),
            ('11', '1 · Clearer settings · types, tests and build.'), ('12', '2 · Links · end-to-end scenarios.')]
    for i, (n, text) in enumerate(rows):
        y = 158 + i * 26
        if n == '08':
            b.append(f'<rect x="202" y="{y - 17}" width="588" height="26" fill="{c["amberf"]}"/>')
            b.append(T(766, y, '+ 1', 11, 'amber', 650, c=c))
        b.append(T(210, y, n, 11, 'muted', mono=True, c=c))
        b.append(T(244, y, text, 12.5, 'text', 650 if n in ('01', '03', '07', '10') else 400, c=c))
    b.append(rside(c, 810, 86, 290, H - 86, 'comments'))
    b.append(T(826, 156, 'Line 8 · Anna', 12, 'text', 650, c=c))
    b.append(T(826, 185, 'Keep the retry limit visible.', 12.5, 'text', c=c))
    b.append(T(826, 220, 'Agent: changed on line 8.', 12, 'blue', c=c))
    b.append(T(210, H - 20, 'Illustration · example document and comment', 10.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'The full-size Plan: outline, document-header file chip, lines with a comment on line 8, named agent status, and Files / Comments')


def items_ill(c: Theme) -> str:
    W, H = 1000, 300
    fams = [('Decide', ['Agree', 'Change'], ['Engineering decision', 'Decided by the agent', 'Out of scope', 'Extra review', 'Done means']),
            ('Look', ['Looks right', 'Change (pin a spot)'], ['Mockup', 'A diagram', 'Look at the result']),
            ('Confirm', ['I confirm', 'Ask the agent to record it'], ['Only you can confirm']),
            ('Fix', ['Accept · Fix it', 'Fine · Ask why', 'Add · Skip it'], ['Found while checking', 'Decided while building', 'Add to the Plan']),
            ('Answer', ['In Your turn', 'Looks right · Suggest', 'a change · Reply'], ['The agent’s question', 'A teammate’s question'])]
    cw, gap = 188, 15
    out = []
    for i, (name, ans, kinds) in enumerate(fams):
        x = i * (cw + gap)
        out.append(card(c, x, 0, cw, H - 4, stroke='cardline'))
        out.append(f'<rect x="{x}" y="0" width="{cw}" height="4" rx="2" fill="{c["amber"]}"/>')
        out.append(T(x + 16, 34, name, 16, 'text', 700, c=c))
        out.append(T(x + 16, 62, 'Answers', 11, 'dim', 700, c=c))
        for k, a in enumerate(ans):
            if name == 'Answer':
                out.append(T(x + 16, 84 + k * 18, a, 12.5, 'text', 600, c=c))
            elif name == 'Fix':
                out.append(T(x + 16, 84 + k * 18, a, 12.5, 'text', 600, c=c))
            else:
                out.append(abtn_svg(c, x + 16, 72 + k * 32, a, False, 26, 11.5, cw - 32))
        ky = 168
        out.append(T(x + 16, ky, 'Kinds', 11, 'dim', 700, c=c))
        for k, t in enumerate(kinds):
            out.append(T(x + 16, ky + 22 + k * 20, t, 12.5, 'muted', c=c))
    return svg(W, H, ''.join(out), 'Five families of items, each with its own answers: Decide, Look, Confirm, Fix and Answer')


def decision_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = [card(c, 0, 0, 620, 296)]
    b.append(T(18, 28, 'Engineering decision · decision rule', 12, 'dim', 600, c=c))
    b.append(T(18, 52, 'Your words win; otherwise the Plan’s risk decides', 14.5, 'text', 650, c=c))
    b.append(f'<rect x="24" y="108" width="130" height="44" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(89, 135, 'Plan written', 13, 'text', 600, 'middle', c=c))
    b.append(arrow(c, 156, 130, 214))
    b.append(diamond(c, 244, 130, 33, 'amberf', 'amber'))
    b.append(T(244, 120, 'Risky or', 11.5, 'text', 600, 'middle', c=c))
    b.append(T(244, 134, 'trust', 11.5, 'text', 600, 'middle', c=c))
    b.append(T(244, 148, 'boundary?', 11.5, 'text', 600, 'middle', c=c))
    b.append(curve(c, 277, 130, 420, 86, 'blue'))
    b.append(curve(c, 244, 160, 420, 200, 'muted'))
    b.append(T(340, 98, 'yes', 12, 'blue', 600, 'middle', c=c))
    b.append(T(330, 202, 'no', 12, 'muted', 600, 'middle', c=c))
    b.append(f'<rect x="422" y="62" width="176" height="48" rx="9" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-width="1.8"/>')
    b.append(T(510, 91, 'Second opinion', 13, 'text', 600, 'middle', c=c))
    b.append(f'<rect x="422" y="178" width="176" height="48" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(510, 207, 'Build', 13, 'text', 600, 'middle', c=c))
    b.append(f'<rect x="188" y="244" width="240" height="38" rx="10" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.5"/>')
    b.append(f'<path d="M244 196 L244 244" stroke="{c["amberl"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')
    b.append(f'<circle cx="244" cy="196" r="5" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="1.8"/>')
    b.append(T(208, 268, 'A pinned comment', 12, 'amber', 600, c=c))
    b.append(card(c, 640, 0, 360, 296, stroke='amberl'))
    b.append(T(658, 28, 'Comment pinned on the diagram', 12, 'dim', 600, c=c))
    b.append(f'<circle cx="676" cy="62" r="13" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="1.5"/>')
    b.append(T(676, 66.5, 'A', 11.5, 'amber', 700, 'middle', c=c))
    b.append(T(698, 58, 'Anna', 13, 'text', 650, c=c))
    for i, t in enumerate(['What if the Plan marks a slice risky', 'only after the build starts?']):
        b.append(T(658, 94 + i * 19, t, 13, 'text', c=c))
    b.append(f'<line x1="658" y1="140" x2="982" y2="140" stroke="{c["cardline"]}"/>')
    b.append(f'<circle cx="676" cy="170" r="13" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-width="1.5"/>')
    b.append(T(676, 174.5, 'AI', 10.5, 'blue', 700, 'middle', c=c))
    b.append(T(698, 166, 'The agent', 13, 'text', 650, c=c))
    for i, t in enumerate(['Then the second opinion runs at Verify.', 'Changed in the Plan: the rule says so.']):
        b.append(T(658, 202 + i * 19, t, 13, 'text', c=c))
    b.append(abtn_svg(c, 658, 252, 'Reply'))
    b.append(abtn_svg(c, 712, 252, 'Resolve'))
    return svg(W, H, ''.join(b), 'An engineering decision drawn as a diagram: a pinned comment on the diagram opens a thread, and the agent answers in it and changes the Plan')


# ---------------------------------------------------------------- Discuss and Plan
def discuss_ill(c: Theme) -> str:
    return task_example(c, 0, [
        ('heading', 'The problem'), ('row', 'Settings should be easier to understand.'),
        ('heading', 'Done means'), ('agreed', '✓ 1 · Every setting names what it changes.'),
        ('row', '2 · A risky Plan gets an independent second opinion.'),
        ('heading', 'Decided with you'), ('agreed', 'Notifications stay on by default.'),
        ('row', 'Earlier answers stay in Decided with you, with Change.'),
    ], [
        ('Question', ['When should a second opinion run?'], ['Risky Plans', 'Every Plan']),
        ('Question', ['Should notifications start on?'], ['Yes', 'No', 'Tell me more']),
    ], 'Waits for you')


def diagnose_ill(c: Theme) -> str:
    W, H = 1000, 250
    b = []
    cols = [('When', 'blue'), ('Today', 'danger'), ('Expected', 'blue'), ('Must keep working', 'blue')]
    cw = 232
    for i, (t, col) in enumerate(cols):
        x = i * (cw + 24)
        b.append(card(c, x, 0, cw, 190))
        b.append(f'<rect x="{x}" y="0" width="{cw}" height="4" rx="2" fill="{c[col]}"/>')
        b.append(T(x + 16, 34, t, 15, 'text', 650, c=c))
    lines = [['Someone opens', '/reports?page=2'], ['The page shows 49 of', '50 rows. The last one', 'is missing.'],
             ['Every page shows all', 'of its rows.'], ['Page size stays 50.', 'The first page does', 'not change.']]
    for i, ls in enumerate(lines):
        x = i * (cw + 24)
        for k, t in enumerate(ls):
            b.append(T(x + 16, 66 + k * 20, t, 13, 'text' if i != 1 else 'danger', 500, mono=(i == 0 and k == 1), c=c))
    b.append(T(0, 220, 'The cause, found in the code before anything is planned: an off-by-one in the page query.', 13, 'muted', c=c))
    b.append(T(0, 240, 'Done means adds the checks the fix must pass, starting with a test that fails today.', 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'A bug in Discuss: when it happens, what happens today, what is expected, and what must keep working')


def approve_card(c: Theme, x: float, y: float, w: float, title: str, note: str, rows: list, foot: str, button: str) -> tuple[str, float]:
    """“Approve the Plan?” or “Approve the change?”: what was answered, what is open, and the one main button."""
    h = 34 + len(rows) * 32 + 46
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.4"/>',
           f'<path d="M{x + 1} {y + 11} a10 10 0 0 1 10 -10 H{x + w - 11} a10 10 0 0 1 10 10 V{y + 34} H{x + 1} Z" fill="{c["amberf"]}"/>',
           ring(c, x + 18, y + 17, 'you', 6), T(x + 34, y + 22, title, 13.5, 'text', 650, c=c),
           T(x + w - 16, y + 22, note, 11.5, 'muted', 500, 'end', c=c)]
    for i, (label, answer, open_) in enumerate(rows):
        ry = y + 34 + i * 32
        out.append(f'<line x1="{x}" y1="{ry}" x2="{x + w}" y2="{ry}" stroke="{c["cardline"]}"/>')
        out.append(ring(c, x + 20, ry + 16, 'you' if open_ else 'done', 5))
        out.append(T(x + 34, ry + 20.5, label, 12.5, 'text', 500, c=c))
        out.append(T(x + w - 16, ry + 20.5, answer, 12, 'amber' if open_ else 'muted', 600 if open_ else 500, 'end', c=c))
    fy = y + 34 + len(rows) * 32
    out.append(f'<line x1="{x}" y1="{fy}" x2="{x + w}" y2="{fy}" stroke="{c["cardline"]}"/>')
    out.append(T(x + 16, fy + 27, foot, 12, 'muted', c=c))
    bw = 30 + len(button) * 7
    out.append(abtn_svg(c, x + w - 14 - bw, fy + 9, button, True, 28, 12.5, bw))
    return ''.join(out), h


def plan_ill(c: Theme) -> str:
    return task_example(c, 1, [
        ('heading', 'Interface'), ('row', 'Read the full-size design and comment on a spot.'),
        ('heading', 'Engineering decisions'), ('agreed', '✓ The Plan determines what each agent builds.'),
        ('heading', 'Done means'), ('agreed', '✓ 1 · Every setting names what it changes.'),
        ('row', '2 · The changed point waits for your agreement.'),
        ('heading', 'Slices and checks'), ('row', '1 · Simplify the settings · types, tests and build.'),
        ('row', '2 · Keep every link working · end-to-end scenarios.'),
        ('proof', 'Plan review recorded · read the evidence for who checked it'),
    ], [
        ('Done means · changed point 2', ['Was: A review on every Plan.', 'Now: A review on risky Plans.'], ['Agree', 'Change']),
        ('Plan approval', ['Settle the open decisions first.', 'Answers do not approve the Plan.'], ['Approve the Plan']),
    ], 'Waits for you')


# ---------------------------------------------------------------- after the Plan is approved
def implement_start(c):
    W, H = 1000, 446
    b = [window(c, W, H, 'Settings cleanup · QualityLayer')]
    x0 = 40

    def segmented(x, y, options, on):
        """A row of options; the one that is on has the blue fill."""
        out, cx = [], x
        for opt in options:
            w = 22 + len(opt) * 6.6
            if opt == on:
                out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="26" rx="7" fill="{c["bluef"]}" stroke="{c["blue"]}"/>')
                out.append(T(cx + w / 2, y + 17, opt, 12, 'blue', 650, 'middle', c=c))
            else:
                out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="26" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
                out.append(T(cx + w / 2, y + 17, opt, 12, 'muted', 600, 'middle', c=c))
            cx += w + 8
        return ''.join(out)

    b.append(f'<rect x="{x0 - 16}" y="56" width="{W - 2 * x0 + 32}" height="34" rx="9" fill="{c["amberf"]}" stroke="{c["amberl"]}" stroke-opacity="0.8"/>')
    b.append(ring(c, x0 + 2, 73, 'you', 6))
    b.append(T(x0 + 18, 78, 'Start the build', 13.5, 'text', 650, c=c))
    b.append(T(x0 + 130, 78, 'Your Build defaults, ready. Change anything for this build, or copy the command.', 12.5, 'muted', c=c))
    b.append(T(x0, 124, 'Build with', 13, 'muted', 600, c=c))
    b.append(segmented(130, 106, ['Claude Code', 'Codex', 'Another agent'], 'Claude Code'))
    b.append(T(W - x0, 124, '✓ Recommended setup', 12, 'muted', 500, 'end', c=c))
    # the build as two nodes you set in place: the orchestrator hands slices to its workers
    b.append(node(c, x0, 146, 330, 92, 'Orchestrator', [], 'cardline'))
    b.append(pill(c, x0 + 16, 184, 'Opus 5.5  ▾', 'text', 100))
    b.append(T(x0 + 16, 226, 'Plans each slice, reads each report · writes no code', 12, 'dim', c=c))
    b.append(arrow(c, x0 + 332, 192, W - x0 - 332))
    b.append(T(W / 2, 182, '4 slices', 12, 'muted', 500, 'middle', mono=True, c=c))
    b.append(node(c, W - x0 - 330, 146, 330, 92, 'Workers', [], 'cardline'))
    b.append(pill(c, W - x0 - 314, 184, 'Sonnet 5.5  ▾', 'text', 112))
    b.append(T(W - x0 - 314, 226, 'Write the code, a slice each, test first', 12, 'dim', c=c))
    b.append(T(W / 2 - 150, 272, 'Effort for both', 13, 'muted', 600, 'end', c=c))
    b.append(segmented(W / 2 - 136, 254, ['Medium', 'High', 'Extra high'], 'High'))
    b.append(T(x0, 312, 'Goal · This session', 12.5, 'muted', 500, c=c))
    b.append(abtn_svg(c, W - x0 - 80, 296, 'Adjust ▾', False, 26, 12, 80))
    b.append(f'<rect x="{x0}" y="330" width="{W - 2 * x0}" height="96" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x0 + 16, 352, 'In the session that planned it, type these first, one at a time', 12, 'muted', c=c))
    for i, t in enumerate(['/clear', '/model opus', '/effort high']):
        b.append(pill(c, x0 + 16 + i * 116, 362, t, 'text', 104, mono=True))
    b.append(f'<rect x="{x0 + 10}" y="390" width="{W - 2 * x0 - 20}" height="30" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x0 + 24, 410, '/goal /ql implement settings-cleanup', 13, 'text', 600, mono=True, c=c))
    b.append(abtn_svg(c, W - x0 - 90, 392, 'Copy', True, 26, 12, 72))
    return svg(W, H, ''.join(b), 'Implement Start: Build with Claude Code, Codex or another agent; the orchestrator and its workers with their models, set from your Build defaults; one effort for both; and the command to copy, with the lines to type first in the session that planned the task')


def implement_ill(c: Theme) -> str:
    return task_example(c, 2, [
        ('heading', 'The build'), ('agreed', '✓ Slice 1 · Clearer settings · committed'),
        ('row', 'Slice 2 · Sign-in · waiting for your login'),
        ('row', 'Slice 3 · Links · building and checking'),
        ('heading', 'Decided while building'), ('row', 'Kept the current settings file · Ask why'),
        ('heading', 'Checks'), ('proof', 'Slice 1 · tests, types and lint passed'),
        ('row', 'Other slices keep building while your login waits.'),
    ], [
        ('Slice 2 · Only you can provide', ['Sign in to the test service.', 'Set the login in your environment.'], ['Done, it’s set']),
    ], 'Building slice 3')


def checkpoint_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = []
    top = [(0, 'Slice 1 built', 'cardline', 'bg'), (220, 'Its scenarios run', 'blue', 'bluef'), (440, 'Passed', 'violet', 'bg'),
           (660, 'Next slice', 'cardline', 'bg')]
    for x, t, col, fill in top:
        b.append(card(c, x, 20, 180, 56, stroke=col, fill=fill, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 90, 54, t, 14, 'text', 650, 'middle', c=c))
    for x in (0, 220, 440):
        b.append(arrow(c, x + 182, 48, x + 218))
    b.append(vmark(c, 474, 48))
    b.append(T(90, 98, 'Risky: new mail service', 12, 'amber', 600, 'middle', c=c))
    b.append(T(870, 44, 'Output of every run', 12, 'muted', c=c))
    b.append(T(870, 60, 'is kept', 12, 'muted', c=c))
    b.append(card(c, 220, 172, 180, 56, stroke='danger', fill='bg', sw=1.6))
    b.append(mark(c, 250, 200, False))
    b.append(T(318, 205, 'Failed', 14, 'text', 650, 'middle', c=c))
    b.append(arrow(c, 310, 78, 310, 170, 'danger'))
    b.append(f'<path d="M218 200 H150 V112" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M145 119 l5 -7 l5 7" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(T(0, 160, 'An agent fixes it,', 12, 'muted', c=c))
    b.append(T(0, 176, 'then it runs again', 12, 'muted', c=c))
    b.append(arrow(c, 402, 200, 470))
    b.append(T(436, 190, 'failed 4 times', 11.5, 'danger', 600, 'middle', c=c))
    b.append(card(c, 472, 152, 508, 120, stroke='cardline', fill='card'))
    b.append(T(490, 180, 'Recorded as open: the build goes on', 14, 'text', 650, c=c))
    b.append(T(490, 200, 'Each try used a different approach; their output is kept.', 12.5, 'muted', c=c))
    b.append(T(490, 222, 'The final review lists it, in one plain sentence.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'A checkpoint after a risky slice: its scenarios run on the real program; a failure goes to an agent to fix and runs again with a different approach; after four failed runs the checkpoint is recorded as open, the build goes on, and the final review lists it')


# ---------------------------------------------------------------- Verify
def status(c: Theme, x: float, y: float, state: str) -> str:
    if state == 'passed':
        return vmark(c, x, y)
    if state == 'running':
        return ring(c, x, y, 'agent', 5.5)
    if state == 'failed':
        return mark(c, x, y, False)
    if state == 'user':
        return ring(c, x, y, 'you', 5.5)
    return ring(c, x, y, 'dim', 5.5)


def verify_ill(c: Theme) -> str:
    return task_example(c, 3, [
        ('heading', 'Done means · 1'), ('row', 'Every setting names what it changes.'),
        ('proof', 'Passed · scenario 1 · open output and screenshot'),
        ('heading', 'Done means · 2'), ('row', 'A risky Plan gets a second opinion.'),
        ('row', 'Checking now · scenario 2 on the running program'),
        ('heading', 'Done means · 3'), ('row', 'Every link opens the right page.'),
        ('row', 'Waiting · scenarios 3 and 4'),
        ('heading', 'Project checks and agent reviews'), ('proof', 'Types, lint and tests passed · open the evidence'),
    ], [], 'Checking point 2')


def stopped_ill(c: Theme) -> str:
    W, H = 1000, 490
    b = [card(c, 0, 0, W, H - 28, stroke='amber', fill='bg')]
    b.append(T(24, 32, 'Your turn · after two fixing rounds', 12.5, 'muted', 500, c=c))
    b.append(T(24, 62, 'Verify sent the build back twice', 22, 'text', 650, c=c))
    b.append(T(24, 86, '4 update tests still fail. Each recorded round so far:', 13.5, 'muted', c=c))
    b.append(T(24, 117, 'Fixing work', 12, 'muted', 500, c=c))
    b.append(T(810, 117, 'Time', 12, 'muted', 500, 'end', c=c))
    b.append(T(976, 117, 'Cost', 12, 'muted', 500, 'end', c=c))
    rounds = [('Round 1 · fixed 3 failing tests', '48 min', '$11.40'),
              ('Round 2 · fixed the token retry', '2 h 39 min', '$19.05')]
    for i, (fixed, minutes, cost) in enumerate(rounds):
        y = 143 + i * 30
        b.append(T(24, y, fixed, 13.5, 'text', 500, c=c))
        b.append(T(810, y, minutes, 13, 'muted', 400, 'end', c=c))
        b.append(T(976, y, cost, 13, 'text', 500, 'end', c=c))
    b.append(T(24, 207, 'Still failing · 4 update tests', 13.5, 'danger', 500, c=c))
    opts = [('One more round', 'Fix and check once; another failure asks you again'),
            ('Review it as it is', 'Review lists the open tests'),
            ('Stop here', 'The work and its evidence stay')]
    for i, (label, hint) in enumerate(opts):
        y = 227 + i * 48
        b.append(f'<rect data-choice="{i + 1}" x="24" y="{y}" width="952" height="40" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(40, y + 26, str(i + 1), 12, 'muted', 500, c=c))
        b.append(T(64, y + 26, label, 13.5, 'text', 600, c=c))
        b.append(T(310, y + 26, hint, 12.5, 'muted', c=c))
    b.append(T(24, 391, 'Your own words', 12, 'muted', 500, c=c))
    b.append(f'<rect data-own-words="true" x="24" y="402" width="852" height="38" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(36, 427, 'Or tell the agent what to try…', 12.5, 'dim', c=c))
    b.append(abtn_svg(c, 892, 402, 'Send', True, 38, 12.5, 84))
    b.append(T(24, 484, 'Illustration · example fixing work, times and costs', 10.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'After the initial review and two recorded fixing rounds, checks still fail. You choose One more round, Review it as it is, or Stop here; each round shows its fixing work, time and cost.')


# ---------------------------------------------------------------- Review
def review_ill(c: Theme) -> str:
    return task_example(c, 4, [
        ('heading', 'What changed'), ('row', 'Settings are clearer and links keep their destination.'),
        ('heading', 'How to try it'), ('row', 'Open Settings, then follow a link to a task.'),
        ('heading', 'Done means · 1'), ('row', 'Every setting names what it changes.'),
        ('proof', 'Passed · scenario 1 · output and screenshot'),
        ('heading', 'Done means · 2'), ('row', 'A risky Plan gets a second opinion.'),
        ('proof', 'Passed · scenario 2 · recorded command'),
        ('heading', 'Done means · 3'), ('row', 'Every link opens the right page.'),
        ('proof', 'Passed · scenarios 3 and 4 · evidence available'),
    ], [
        ('Only you can confirm · point 1', ['Do the settings read clearly to you?'], ['I confirm', 'Change']),
        ('Final approval', ['After settling the open items:', 'approve and open a pull request.'], ['Approve only']),
    ], 'Waits for you')


def comments_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = [card(c, 0, 0, 640, 326)]
    b.append(item(c, 14, 14, 612, 'Found while checking', 'The App waits up to 3 s for your login shell', ['Fix it', 'Undo'], state='done'))
    b.append(item(c, 14, 76, 612, 'Only you can confirm', 'One live call to the trial service gave 7 days', ['✓ I confirm'], state='done'))
    a, _ = approve_card(c, 14, 150, 612, 'Approve the change?', '1 answer asks for a change', [],
                        'Your notes and comments go with it.', 'Send 1 change')
    b.append(a)
    b.append(T(20, 268, 'One answer asks for a change, so the main button reads', 12.5, 'muted', c=c))
    b.append(T(20, 286, 'Send 1 change. The agent fixes it and asks again.', 12.5, 'muted', c=c))
    b.append(card(c, 660, 0, 340, 326, stroke='cardline'))
    b.append(rside(c, 660, 0, 340, 326, 'comments').replace(f'<line x1="660" y1="0" x2="660" y2="326" stroke="{c["cardline"]}"/>', ''))
    groups = [('Open on Review · 2', 'Settings.tsx · the Links row', 'Yours · goes with Send 1 change', 'amber'),
              ('', 'Plan · “Workers” only in the App?', 'Anna, 2 h ago · Claude Code answered', 'blue'),
              ('Resolved · 3', 'Done means · point 4', 'Ben · resolved by you', 'dim')]
    for i, (g, t, s, col) in enumerate(groups):
        y = 54 + i * 86
        if g:
            b.append(T(676, y + 14, g, 11.5, 'muted', 600, c=c))
        b.append(f'<rect x="674" y="{y + 22}" width="312" height="54" rx="9" fill="{c["card"] if col != "dim" else c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(688, y + 44, t, 12.5, 'text', 500, c=c))
        b.append(T(688, y + 63, s, 11.5, col, 600, c=c))
    return svg(W, H, ''.join(b), 'One answer asks for a change, so the main button reads Send 1 change; the Comments tab of the right sidebar lists your comments, answered threads and your team’s')


def shipped_ill(c: Theme) -> str:
    W, H = 1000, 210
    b = [card(c, 0, 40, 200, 110, stroke='amber', fill='amberf', sw=1.6)]
    b.append(ring(c, 26, 76, 'done', 7))
    b.append(T(42, 81, 'Shipped', 15, 'text', 650, c=c))
    b.append(T(20, 108, 'Approved at 15:42', 12.5, 'muted', c=c))
    b.append(T(20, 128, 'Your final decision', 12.5, 'muted', c=c))
    b.append(arrow(c, 204, 95, 250))
    b.append(card(c, 252, 20, 300, 150))
    b.append(T(272, 50, 'The task keeps', 14, 'text', 650, c=c))
    for i, t in enumerate(['The pull request, if you opened one', 'What you decided', 'What it cost']):
        y = 72 + i * 28
        b.append(f'<circle cx="280" cy="{y}" r="3.5" fill="{c["violet"]}"/>')
        b.append(T(292, y + 4.5, t, 13, 'muted', c=c))
    b.append(T(272, 160, 'All in docs/plans, with the evidence', 12, 'dim', c=c))
    b.append(arrow(c, 556, 95, 600))
    b.append(f'<rect x="602" y="0" width="398" height="190" rx="14" fill="none" stroke="{c["line"]}" stroke-dasharray="6 5"/>')
    b.append(T(622, 26, 'Your own process', 12, 'dim', 700, c=c))
    for i, t in enumerate(['Pull request', 'Merge', 'Deploy']):
        x = 622 + i * 126
        b.append(card(c, x, 60, 106, 70, fill='bg'))
        b.append(T(x + 53, 100, t, 13.5, 'text', 600, 'middle', c=c))
        if i < 2:
            b.append(arrow(c, x + 108, 95, x + 124))
    b.append(T(622, 166, 'QualityLayer opens the pull request only when you choose to.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Shipped: the task keeps its documents, what you decided and what it cost; the pull request, merge and deploy stay in your own process')


def abandon_ill(c: Theme) -> str:
    W, H = 1000, 170
    b = []
    items = [('Stop the task', 'Stops the work', 'The documents stay in your repository', 'muted'),
             ('Archive', 'Off the App’s task list', 'Restore brings it back', 'muted'),
             ('Delete', 'Removes the plan folder', 'Asks first, then moves the files to the Trash', 'dim')]
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
    return svg(W, H, ''.join(b), 'Stop the task ends the work and keeps the documents; Archive hides a task; Delete removes its plan folder after asking')


# ---------------------------------------------------------------- the App around the steps
def band_ill(c: Theme) -> str:
    W, H = 1000, 250
    b = [card(c, 0, 0, 1000, 246)]
    b.append(T(18, 28, 'Claude Code', 12, 'dim', 600, c=c))
    rows = [('While it waits for you', 'amber', 'amberf', 'QL · Settings cleanup · Plan · waits for you in the App: Approve the Plan?', None),
            ('While it builds', 'blue', 'bluef', 'QL · Settings cleanup · Implement · slices 2 and 3 building', None),
            ('When a teammate asks', 'amber', 'amberf', 'QL · 2 questions for you · Anna, Ben', None)]
    for i, (label, col, fill, text, _) in enumerate(rows):
        y = 46 + i * 58
        b.append(T(18, y + 25, label, 12.5, 'muted', 500, c=c))
        b.append(f'<rect x="190" y="{y}" width="790" height="40" rx="6" fill="{c[fill]}"/>')
        b.append(f'<rect x="190" y="{y}" width="4" height="40" fill="{c[col]}"/>')
        b.append(T(208, y + 25, text, 12.5, 'text', 500, mono=True, c=c))
        if i == 1:
            b.append(f'<rect x="846" y="{y + 16}" width="120" height="8" rx="4" fill="{c["line"]}"/>')
            b.append(f'<rect x="846" y="{y + 16}" width="66" height="8" rx="4" fill="{c[col]}"/>')
    b.append(T(190, 230, '>', 14, 'muted', 600, mono=True, c=c))
    b.append(f'<rect x="206" y="218" width="8" height="16" fill="{c["muted"]}"/>')
    return svg(W, H, ''.join(b), 'The band above the Claude Code prompt: what waits for you in the App, how the build runs, or teammates’ questions for you')


def cost_ill(c: Theme) -> str:
    W, H = 1000, 452
    b = [card(c, 0, 0, W - 4, H - 4)]
    b.append(T(20, 34, '$47.25 so far', 20, 'text', 700, c=c))
    b.append(T(176, 34, 'Example · 2 h 30 min · estimated at list price, read on this computer', 12.5, 'muted', c=c))
    steps = [('Discuss', '27 min', '12M', '$5.65', 0.31, 'blue'), ('Plan', '35 min', '25M', '$8.57', 0.47, 'blue'),
             ('Implement', '44 min', '60M', '$18.22', 1.0, 'blue'), ('Verify', '40 min', '39M', '$14.81', 0.81, 'violet')]
    for k, (h, x) in enumerate([('Step', 20), ('time', 700), ('tokens', 790), ('cost', 960)]):
        b.append(T(x, 62, h, 11.5, 'dim', 600, 'end' if k else 'start', c=c))
    y = 74
    for n, tm, tk, usd, m, col in steps:
        b.append(f'<line x1="20" y1="{y}" x2="960" y2="{y}" stroke="{c["cardline"]}"/>')
        b.append(T(20, y + 24, n, 13.5, 'text', 650, c=c))
        b.append(f'<rect x="130" y="{y + 12}" width="{300 * m:.0f}" height="12" rx="4" fill="{c[col]}" fill-opacity="0.75"/>')
        b.append(T(700, y + 24, tm, 12.5, 'muted', 500, 'end', c=c))
        b.append(T(790, y + 24, tk, 12.5, 'muted', 500, 'end', c=c))
        b.append(T(960, y + 24, usd, 13, 'text', 650, 'end', c=c))
        y += 38
        if n == 'Verify':
            for hn, htm, htk, hu in [('Your session · Opus 5.5', '', '11M', '$4.14'), ('Polish · Sonnet 5.5', '13 min', '9M', '$2.75'),
                                     ('Checking · part 1 of 3 · Opus 5.5', '9 min', '8M', '$3.19'),
                                     ('Checking · part 2 of 3 · Opus 5.5', '5 min', '5M', '$2.13'),
                                     ('Project checks · 4 full runs', '12 min', '', '$0')]:
                b.append(T(40, y + 18, hn, 12.5, 'text', 500, c=c))
                b.append(T(700, y + 18, htm, 12, 'dim', 500, 'end', c=c))
                b.append(T(790, y + 18, htk or '–', 12, 'dim', 500, 'end', c=c))
                b.append(T(960, y + 18, hu, 12.5, 'muted', 600, 'end', c=c))
                y += 26
    b.append(f'<line x1="20" y1="{y + 6}" x2="960" y2="{y + 6}" stroke="{c["cardline"]}"/>')
    b.append(T(20, y + 30, 'Total', 13.5, 'text', 700, c=c))
    b.append(T(700, y + 30, '2 h 30', 12.5, 'text', 600, 'end', c=c))
    b.append(T(790, y + 30, '136M', 12.5, 'text', 600, 'end', c=c))
    b.append(T(960, y + 30, '$47.25', 13.5, 'text', 700, 'end', c=c))
    b.append(f'<rect x="20" y="{y + 44}" width="{W - 48}" height="34" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(34, y + 66, 'Pricing coverage', 12, 'text', 600, c=c))
    b.append(T(150, y + 66, 'Priced usage is estimated; unpriced models keep their tokens and show “no list price”.', 12, 'muted', 500, c=c))
    return svg(W, H, ''.join(b), 'Illustrative Cost panel: recorded time and tokens, estimates at list price for priced models, each step and helper named by its work. Unpriced models retain their tokens and show no list price; cost is read on this computer')


def attention_ill(c: Theme) -> str:
    W, H = 1000, 400
    b = []
    cols = [(560, 'The App'), (700, 'Slack'), (840, 'Claude Code band')]
    for x, t in cols:
        b.append(T(x, 20, t, 12.5, 'text', 650, 'middle', c=c))
    rows = [('A Plan or a review waits for you', 'you', (1, 0, 1)), ('A teammate asks you', 'you', (1, 1, 1)),
            ('A reminder (at most every 4 hours)', 'you', (1, 1, 0)), ('Your question is answered', 'you', (1, 1, 0)),
            ('Every answer you needed is in', 'you', (1, 1, 0)), ('A build finishes or stops', 'you', (1, 1, 1)),
            ('A task ships', 'you', (1, 0, 0)), ('An outside reviewer comments', 'you', (1, 0, 0)),
            ('Agent progress and checks', 'never', (0, 0, 0))]
    for i, (t, kind, hits) in enumerate(rows):
        y = 34 + i * 38
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{c["cardline"]}"/>')
        b.append(T(0, y + 24, t, 13, 'text' if kind != 'never' else 'dim', 500, c=c))
        for (x, _), on in zip(cols, hits):
            if on:
                b.append(f'<circle cx="{x}" cy="{y + 19}" r="6" fill="{c["blue"]}"/>')
            else:
                b.append(f'<line x1="{x - 6}" y1="{y + 19}" x2="{x + 6}" y2="{y + 19}" stroke="{c["off"]}" stroke-width="2"/>')
        if kind == 'never':
            b.append(T(700, y + 24, 'never', 12, 'dim', 600, 'middle', c=c))
    b.append(T(0, 392, 'A channel speaks only when a person can act. The band and the sidebar show progress quietly.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Who hears about what: the App, Slack and the Claude Code band speak only when a person can act, and agent progress and checks never notify')


def feedback_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = []
    for i, t in enumerate(['Feedback in the sidebar', 'Send feedback in ⌘K', 'Report this on an error']):
        y = 20 + i * 54
        b.append(f'<rect x="0" y="{y}" width="200" height="40" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(100, y + 25, t, 12.5, 'text', 500, 'middle', c=c))
        b.append(curve(c, 202, y + 20, 250, 118, 'line'))
    b.append(card(c, 252, 0, 330, 220))
    b.append(T(270, 28, 'Send feedback', 14, 'text', 650, c=c))
    b.append(pill(c, 270, 40, 'Something doesn’t work', 'blue', 160, fill='bluef', stroke='blue'))
    b.append(pill(c, 438, 40, 'An idea', 'muted', 70))
    b.append(f'<rect x="270" y="74" width="294" height="50" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(bars(c, 282, 88, [240, 170], 14, 6))
    b.append(T(270, 148, 'Screenshots: paste, drop or choose, up to 5', 12, 'muted', c=c))
    b.append(switch(c, 270, 160, True))
    b.append(T(306, 173, 'Include diagnostics', 12.5, 'text', 500, c=c))
    b.append(T(440, 173, 'Show what is sent', 12, 'blue', 600, c=c))
    b.append(T(270, 204, 'From Max Ritter · from your Team licence', 12, 'dim', 500, c=c))
    b.append(arrow(c, 584, 110, 650))
    b.append(node(c, 652, 60, 170, 100, 'qualitylayer.dev', ['Checks your licence', 'or trial, rate limits'], 'cardline'))
    b.append(arrow(c, 824, 110, 850))
    b.append(node(c, 852, 60, 148, 100, 'Private issue', ['One per report,', 'reference QL-128'], 'blue', 'bluef'))
    b.append(f'<rect x="252" y="244" width="748" height="64" rx="10" fill="{c["amberf"]}" stroke="{c["amberl"]}" stroke-opacity="0.7"/>')
    b.append(T(270, 270, 'Offline', 12, 'amber', 700, c=c))
    b.append(T(330, 270, 'The report is saved on this computer and sent by itself when you are back online.', 12.5, 'text', 500, c=c))
    b.append(T(270, 292, 'Diagnostics never include code, plan text, task titles, repository names or file paths.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Feedback: from the sidebar, the command box or an error, one sheet with your text, screenshots and diagnostics you can read first; it goes to a private issue, and offline it waits on your computer')


def agents_other_ill(c: Theme) -> str:
    W, H = 1000, 250
    b = []
    b.append(node(c, 0, 60, 250, 130, 'Another coding agent', ['Any agent that can run', 'shell commands'], 'cardline'))
    b.append(curve(c, 252, 100, 330, 60, 'line'))
    b.append(curve(c, 252, 150, 330, 190, 'line'))
    b.append(node(c, 332, 20, 300, 80, 'The command line', ['qualitylayer on the agent’s PATH', 'The App sets this up for you'], 'blue', 'bluef'))
    b.append(node(c, 332, 150, 300, 80, 'The skill text', ['Copy › For another agent', 'in the App, or the prompt it shows'], 'blue', 'bluef'))
    b.append(curve(c, 634, 60, 700, 120, 'blue'))
    b.append(curve(c, 634, 190, 700, 130, 'blue'))
    b.append(node(c, 702, 70, 298, 110, 'The same five steps', ['It asks for the next step and records', 'the checks. You decide in the App.'], 'amber', 'amberf'))
    return svg(W, H, ''.join(b), 'Connecting another coding agent: any agent that runs shell commands needs the qualitylayer command on its path and the skill text from Copy, For another agent; then it follows the same five steps and you decide in the App')


# ---------------------------------------------------------------- team
def team_agents(c):
    W, H = 1000, 250
    b = [card(c, 0, 0, 230, 200)]
    b.append(T(16, 28, 'Dana’s App', 12, 'dim', 600, c=c))
    b.append(T(16, 54, 'A question for you', 15, 'text', 650, c=c))
    b.append(abtn_svg(c, 16, 74, 'Draft with my agent', False, 28, 12.5, 170))
    b.append(T(16, 128, 'Their own Claude Code or Codex', 12.5, 'muted', c=c))
    b.append(T(16, 146, 'reads it. Another agent takes', 12.5, 'muted', c=c))
    b.append(T(16, 164, 'the prompt, as /ql answer.', 12.5, 'muted', c=c))
    b.append(T(16, 188, '/ql answer 7f3a', 12, 'blue', 500, mono=True, c=c))
    b.append(arrow(c, 232, 100, 258))
    b.append(node(c, 260, 0, 230, 200, 'Their agent', ['Reads the question and the Plan,', 'looks at their own code,', 'asks them what it needs'], 'blue', 'bluef'))
    b.append(arrow(c, 492, 100, 518))
    b.append(node(c, 520, 0, 230, 200, 'A draft, not sent yet', ['Nothing is sent', 'without their yes'], 'blue'))
    b.append(abtn_svg(c, 536, 112, 'Send the draft', True, 30, 12, 108))
    b.append(abtn_svg(c, 652, 112, 'Edit', False, 30, 12, 56))
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
    b.append(T(W / 2, 236, 'Their agent runs on their own computer. Codex uses $ql answer.', 13, 'muted', 400, 'middle', c=c))
    return svg(W, H, ''.join(b), 'A teammate answers with their own agent: it reads the question and the Plan, drafts an answer, sends it only after their yes, and your App shows it via that agent')


def team_timeline(c: Theme) -> str:
    W, H = 1000, 210
    b = []
    bands = [(0, 420, 'Discuss and Plan', 'amber', 'amberf'), (430, 680, 'Implement and Verify', 'blue', 'bluef'),
             (690, 1000, 'Review', 'amber', 'amberf')]
    for x1, x2, t, col, fill in bands:
        b.append(f'<rect x="{x1}" y="104" width="{x2 - x1}" height="44" rx="10" fill="{c[fill]}" stroke="{c[col]}" stroke-width="1.4"/>')
        b.append(T((x1 + x2) / 2, 131, t, 14, 'text', 650, 'middle', c=c))
    b.append(T(210, 176, 'Comments are cheap: nothing is built yet', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(555, 176, 'Your agent builds and checks', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(845, 176, 'Reviewed with its proof', 12.5, 'muted', 400, 'middle', c=c))
    callouts = [(40, 340, '1  Review the plan', 'Before any code is written', 'amber'),
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
    top = [(0, 'Checks passed', 'Every point, with evidence', 'violet'),
           (230, 'Team review', 'Why, how, and the proof', 'cardline'),
           (500, 'Threads', '2 of 3 approved · 2 open', 'amber'),
           (770, 'Approve', 'When every thread is settled', 'blue')]
    for x, t, s, col in top:
        b.append(card(c, x, 20, 220 if x < 770 else 230, 74, stroke=col, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 16, 50, t, 14.5, 'text', 650, c=c))
        b.append(T(x + 16, 72, s, 12, 'muted', c=c))
    for x1, x2 in ((222, 228), (452, 498), (722, 768)):
        b.append(arrow(c, x1, 57, x2))
    bottom = [(500, 'Back to your agent', '/ql review csv-export', 'blue', True), (230, 'Checked again', 'Only what the fix touched', 'violet', False)]
    for x, t, s, col, mono in bottom:
        b.append(card(c, x, 190, 220, 74, stroke=col, sw=1.6))
        b.append(T(x + 16, 220, t, 14.5, 'text', 650, c=c))
        b.append(T(x + 16, 242, s, 12, 'blue' if mono else 'muted', 500, mono=mono, c=c))
    b.append(arrow(c, 610, 96, 610, 188, 'amber'))
    b.append(T(620, 146, 'open threads', 12, 'amber', 600, c=c))
    b.append(arrow(c, 498, 227, 452))
    b.append(arrow(c, 340, 188, 340, 96, 'violet'))
    b.append(T(350, 146, 're-review', 12, 'violet', 600, c=c))
    b.append(T(500, 290, 'Each thread ends', 12.5, 'muted', 500, c=c))
    for i, t in enumerate(['fixed', 'answered', 'replanned']):
        b.append(pill(c, 610 + i * 92, 276, t, 'text', 82))
    return svg(W, H, ''.join(b), 'Change review: the team reviews the finished change; open threads go back to your agent, which settles each one and checks again what the fix touched before the re-review')


# ---------------------------------------------------------------- getting started
def firsttask_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    steps = [('Describe', 'the change'), ('Answer', 'its questions'), ('Approve', 'the Plan'), ('Start', 'Implement'),
             ('Agents build', 'and check'), ('Settle', 'what is left'), ('Approve', 'the change')]
    you = {0, 1, 2, 3, 5, 6}
    xs = [60 + i * 147 for i in range(len(steps))]
    b.append(f'<line x1="{xs[0]}" y1="70" x2="{xs[-1]}" y2="70" stroke="{c["line"]}" stroke-width="2"/>')
    for i, (t, s) in enumerate(steps):
        col = 'amber' if i in you else 'blue'
        b.append(f'<circle cx="{xs[i]}" cy="70" r="24" fill="{c["amberf" if i in you else "bluef"]}" stroke="{c[col]}" stroke-width="2"/>')
        b.append(T(xs[i], 76, str(i + 1), 16, col, 700, 'middle', c=c))
        b.append(T(xs[i], 124, t, 14, 'text', 650, 'middle', c=c))
        b.append(T(xs[i], 144, s, 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(xs[0] - 24, 22, 'You act at the amber steps; your agent does the rest', 12.5, 'muted', 500, c=c))
    return svg(W, H, ''.join(b), 'Your first task in seven steps: describe the change, answer its questions, approve the Plan, start Implement, agents build and check, settle what is left, approve the change')


def update_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    cards = [('Checks daily', ['Once a day, in', 'the background'], 'cardline', None),
             ('Downloads quietly', ['Checked against the', 'release signature'], 'cardline', None),
             ('A line in the sidebar', ['Update ready, with the', 'release notes one click away'], 'amber', 'amberf'),
             ('Restart and update', ['The App reopens on', 'the page you were on'], 'blue', 'bluef')]
    for i, (t, s, col, fill) in enumerate(cards):
        x = i * 256
        b.append(node(c, x, 0, 230, 96, t, s, col, fill))
        if i < 3:
            b.append(arrow(c, x + 232, 48, x + 254))
    b.append(T(0, 134, 'Agents keep working and keep calling the same command. On Windows the update waits', 13, 'muted', c=c))
    b.append(T(0, 154, 'for running commands. With the command line only, run', 13, 'muted', c=c))
    b.append(T(390, 154, 'qualitylayer update', 13, 'blue', 500, mono=True, c=c))
    return svg(W, H, ''.join(b), 'Updating the App: it checks daily and downloads in the background, a line in the sidebar says an update is ready, and Restart and update reopens the App on the same page')


def settings_ill(c: Theme) -> str:
    W, H = 1000, 560
    b = [card(c, 0, 0, 620, H - 4)]
    b.append(T(20, 30, 'Settings', 15, 'text', 650, c=c))
    tx = 20
    for i, t in enumerate(['Workflow', 'Licence', 'Team', 'About']):
        w = 22 + len(t) * 7
        b.append(T(tx + w / 2, 58, t, 12.5, 'text' if i == 0 else 'muted', 650 if i == 0 else 500, 'middle', c=c))
        if i == 0:
            b.append(f'<rect x="{tx}" y="64" width="{w}" height="2.5" rx="1" fill="{c["blue"]}"/>')
        tx += w + 6

    def defaults(y: float, title: str, sub: str, rows: list) -> str:
        out = [T(20, y, title, 13.5, 'text', 650, c=c), T(20 + len(title) * 7.6 + 10, y, sub, 11.5, 'muted', c=c)]
        ax = 20
        for i, t in enumerate(['Claude Code', 'Codex', 'Another agent']):
            out.append(T(ax, y + 26, t, 12, 'text' if i == 0 else 'muted', 600 if i == 0 else 500, c=c))
            if i == 0:
                out.append(pill(c, ax + 84, y + 12, 'Default', 'muted', 52))
                out.append(f'<rect x="{ax}" y="{y + 32}" width="136" height="2" rx="1" fill="{c["text"]}"/>')
            ax += 150 if i == 0 else 70
        out.append(T(600, y + 26, '✓ Recommended setup', 11.5, 'muted', 500, 'end', c=c))
        for i, (label, v) in enumerate(rows):
            ry = y + 40 + i * 34
            out.append(f'<line x1="20" y1="{ry}" x2="600" y2="{ry}" stroke="{c["cardline"]}"/>')
            out.append(T(20, ry + 22, label, 12.5, 'text', 500, c=c))
            out.append(f'<rect x="400" y="{ry + 4}" width="200" height="26" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            out.append(T(412, ry + 21, v, 12, 'text', 500, c=c))
            out.append(T(590, ry + 21, 'recommended', 10, 'dim', 500, 'end', c=c))
        return ''.join(out)

    b.append(defaults(96, 'Planning defaults', 'New task opens with these', [('Model', 'Opus 5.5'), ('Effort', 'High'), ('Start in', 'New session')]))
    b.append(defaults(256, 'Build defaults', 'Implement Start opens with these', [('Orchestrator', 'Opus 5.5'), ('Workers', 'Sonnet 5.5'),
                                                                                  ('Effort for both', 'High'), ('Start in', 'This session')]))
    b.append(T(20, 452, 'Independent review', 13.5, 'text', 650, c=c))
    b.append(T(170, 452, 'decides whether the change passes', 11.5, 'muted', c=c))
    for i, (w_, v) in enumerate([('In Claude Code', 'Opus 5.5'), ('In Codex', 'GPT-6.1 Sol')]):
        x = 20 + i * 300
        b.append(T(x, 482, w_, 12.5, 'text', 500, c=c))
        b.append(f'<rect x="{x + 130}" y="466" width="140" height="26" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(x + 142, 483, v, 12, 'text', 500, c=c))
    b.append(f'<line x1="20" y1="508" x2="600" y2="508" stroke="{c["cardline"]}"/>')
    b.append(T(20, 536, 'Second opinion · Notifications', 13, 'muted', 600, c=c))
    b.append(switch(c, 568, 523, True))
    b.append(card(c, 640, 0, 360, 336))
    b.append(T(660, 30, 'For one task', 15, 'text', 650, c=c))
    b.append(T(660, 50, 'Say it in words; your agent records it', 12.5, 'muted', c=c))
    chips = ['+security', '-security', '+checkpoint:all', '-checkpoint', '+second-opinion', '-second-opinion', '-ui-review']
    for i, ch in enumerate(chips):
        x = 660 + (i % 2) * 170
        y = 72 + (i // 2) * 34
        b.append(pill(c, x, y, ch, 'text', 160, mono=True))
    b.append(T(660, 230, '“Skip security” is recorded as', 12.5, 'muted', c=c))
    b.append(T(660, 250, '-security on this task.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Settings, Workflow: Planning defaults and Build defaults, each with a tab per agent, the independent review, the second opinion and Notifications, beside the tabs Licence, Team and About; and the changes you can ask for on one task in words')


def privacy_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = [card(c, 0, 0, 420, 296)]
    b.append(T(18, 30, 'Stays on your computer', 14, 'text', 650, c=c))
    for i, t in enumerate(['Your code and the diff', 'Every plan document', 'Build evidence and logs', 'The App and its cost view']):
        y = 52 + i * 32
        b.append(f'<path d="M{24} {y + 8} l4 4 l8 -9" fill="none" stroke="{c["muted"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(T(46, y + 13, t, 13, 'text', 500, c=c))
    b.append(T(18, 200, 'Your agent sends your code to its own provider,', 12, 'muted', c=c))
    b.append(T(18, 218, 'as it always does. QualityLayer does not change that.', 12, 'muted', c=c))
    b.append(card(c, 440, 0, 560, 100))
    b.append(T(458, 28, 'Daily licence check · qualitylayer.dev', 14, 'text', 650, c=c))
    b.append(T(458, 50, 'The licence and this machine\'s identity confirm access.', 12.5, 'muted', c=c))
    b.append(T(458, 68, 'Workflow texts and App updates also contact QualityLayer.', 12.5, 'muted', c=c))
    b.append(T(458, 89, 'No usage events are queued or sent.', 12, 'text', 500, c=c))
    b.append(card(c, 440, 108, 560, 84))
    b.append(T(458, 134, 'Team service · only when you share', 14, 'text', 650, c=c))
    b.append(T(458, 156, 'Title, Plan and comments, encrypted on your machine.', 12.5, 'muted', c=c))
    b.append(T(458, 176, 'Never your code, the diff or your logs.', 12.5, 'text', 600, c=c))
    b.append(card(c, 440, 200, 560, 96))
    b.append(T(458, 228, 'Feedback · only when you send it', 14, 'text', 650, c=c))
    b.append(T(458, 249, 'Your text, the screenshots you add and diagnostics you can read first,', 12.5, 'muted', c=c))
    b.append(T(458, 267, 'in a private issue. Never code, plan or document text, task titles,', 12.5, 'text', 600, c=c))
    b.append(T(458, 285, 'repository or branch names, or file paths.', 12.5, 'text', 600, c=c))
    return svg(W, H, ''.join(b), 'What stays on your computer, what the licence check sends, what sharing sends to the team service, and what a feedback report sends to a private issue')


def architecture(c):
    """How the parts fit: your agent, the command line, the Markdown files and the App on your computer; only
    encrypted plans, comments and asks leave it, for the team and for share links."""
    W, H = 1100, 380
    b = []
    # your computer: everything that reads or writes your plans
    b.append(f'<rect x="0" y="0" width="720" height="{H}" rx="16" fill="none" stroke="{c["cardline"]}" stroke-width="1.5" stroke-dasharray="6 5"/>')
    b.append(T(20, 30, 'Your computer', 13, 'muted', 650, c=c))
    b.append(node(c, 20, 126, 170, 96, 'Your agent', ['Claude Code, Codex', 'or any other agent'], 'blue', 'bluef'))
    b.append(arrow(c, 192, 174, 236))
    b.append(card(c, 238, 92, 236, 164, 'cardline'))
    b.append(T(256, 120, 'QualityLayer CLI', 15, 'text', 650, c=c))
    for i, cmd in enumerate(['qualitylayer next', 'qualitylayer question show', 'qualitylayer check slice', 'qualitylayer gate open']):
        b.append(T(256, 148 + i * 24, cmd, 12.5, 'blue', 500, mono=True, c=c))
    b.append(arrow(c, 356, 258, 356, 290))
    b.append(node(c, 238, 292, 236, 72, 'Markdown files', ['docs/plans/<task>/ in your repo'], 'cardline'))
    b.append(arrow(c, 476, 174, 518))
    b.append(node(c, 520, 126, 180, 96, 'QualityLayer App', ['Shows each step', 'and asks you'], 'blue', 'bluef'))
    b.append(f'<path d="M476 328 H610 V224" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M605 231 l5 -7 l5 7" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(T(488, 348, 'reads the same files', 12, 'muted', 500, c=c))
    # what leaves your computer: sealed with the team key, or with a key only the link carries
    b.append(arrow(c, 702, 174, 818, col='amber'))
    b.append(f'<rect x="720" y="186" width="96" height="22" rx="11" fill="{c["bg"]}" stroke="{c["amberl"]}"/>')
    b.append(f'<rect x="730" y="195" width="9" height="7" rx="1.5" fill="none" stroke="{c["amber"]}" stroke-width="1.5"/>'
             f'<path d="M732 195 v-2.5 a2.5 2.5 0 0 1 5 0 v2.5" fill="none" stroke="{c["amber"]}" stroke-width="1.5"/>')
    b.append(T(745, 201, 'encrypted', 11.5, 'amber', 600, c=c))
    b.append(node(c, 820, 110, 260, 124, 'QualityLayer Server', [], 'cardline'))
    b.append(T(836, 160, 'qualitylayer.dev', 12.5, 'blue', 500, mono=True, c=c))
    b.append(T(836, 186, 'Plans and comments arrive', 13, 'muted', c=c))
    b.append(T(836, 204, 'encrypted; it sees who and when', 13, 'muted', c=c))
    b.append(arrow(c, 900, 236, 900, 274, col='amber'))
    b.append(arrow(c, 1000, 236, 1000, 274, col='amber'))
    b.append(node(c, 820, 276, 125, 76, 'Your team', ['In their App'], 'amber', 'amberf'))
    b.append(node(c, 955, 276, 125, 76, 'Link guests', ['In the browser'], 'cardline', dash=True))
    return svg(W, H, ''.join(b), 'How QualityLayer fits together: on your computer, your agent runs the QualityLayer CLI, which keeps each task in Markdown files in your repository, and the QualityLayer App reads the same files; only when you share, plans and comments go to the QualityLayer Server at qualitylayer.dev, encrypted, for your team and for people with a share link')


# ---------------------------------------------------------------- designs
def designs_flow(c: Theme) -> str:
    """What a design is: you ask, your agent draws one page, the App shows it, you comment, it changes the same page."""
    W, H = 1000, 236
    steps = [('You', 'amber', 'amberf', 'Ask your agent', ['“Mock up the', 'settings page”']),
             ('Your agent', 'blue', 'bluef', 'Draws one page', ['One HTML file', 'in your project']),
             ('The App', 'cardline', 'card', 'Lists it', ['Inside Files,', 'with a New dot']),
             ('You', 'amber', 'amberf', 'Open it full size', ['Click a spot, say', 'what should change']),
             ('Your agent', 'blue', 'bluef', 'Changes it', ['Edits the same page', 'and says what changed']),
             ('The App', 'cardline', 'card', 'Shows the update', ['A quiet notice.', 'Always the latest'])]
    b = []
    for i, (who, col, fill, t, s) in enumerate(steps):
        x = i * 168
        b.append(card(c, x, 0, 156, 118, stroke=col, fill=fill if col != 'cardline' else 'card', sw=1.5 if col != 'cardline' else 1))
        b.append(T(x + 14, 24, who, 11.5, col if col != 'cardline' else 'muted', 650, c=c))
        b.append(T(x + 14, 50, t, 13.5, 'text', 650, c=c))
        for k, line in enumerate(s):
            b.append(T(x + 14, 74 + k * 18, line, 12, 'muted', c=c))
        if i < 5:
            b.append(arrow(c, x + 157, 59, x + 167))
    b.append(f'<path d="M{3 * 168 + 78} 120 V138 H{5 * 168 + 78} V120" fill="none" stroke="{c["muted"]}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    b.append(T(4 * 168 + 78, 156, 'and again, until it looks right', 12, 'muted', 500, 'middle', c=c))
    b.append(f'<rect x="0" y="180" width="996" height="50" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(lock(c, 18, 197))
    b.append(T(38, 210, 'Stays local.', 13, 'text', 650, c=c))
    b.append(T(136, 210, 'The interactive page and its comments stay on your computer. A share link can show a still picture.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Designs: ask your agent, open its page full size, comment on a spot and see its update; the interactive page stays local, and a share link can show a still picture')


def designs_tab(c: Theme) -> str:
    """A step shows its named preview; Files contains the documents and designs."""
    W, H = 1000, 400
    b = [card(c, 0, 0, 640, 396)]
    b.append(T(18, 32, 'The Plan · Interface', 12, 'dim', 600, c=c))
    b.append(f'<rect x="14" y="46" width="612" height="236" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(mini_page(c, 150, 64, 340, 180))
    b.append(pill(c, 26, 58, 'Preview', 'bg', 66, fill='text', stroke='text'))
    b.append(f'<line x1="14" y1="252" x2="626" y2="252" stroke="{c["cardline"]}"/>')
    b.append(T(30, 272, 'Settings page', 12.5, 'text', 600, c=c))
    b.append(T(130, 272, 'Updated just now · 2 comments', 12, 'dim', c=c))
    b.append(abtn_svg(c, 516, 258, 'Open full size', False, 24, 11.5, 100))
    b.append(item(c, 14, 300, 612, 'Look', 'Is this how Settings should read?', ['Looks right', 'Change'], h=52))
    b.append(T(18, 380, 'The Plan shows its named preview; Files lists the documents and designs.', 12, 'dim', 500, c=c))
    b.append(card(c, 660, 0, 340, 396))
    b.append(rside(c, 660, 0, 340, 396, 'designs').replace(f'<line x1="660" y1="0" x2="660" y2="396" stroke="{c["cardline"]}"/>', ''))
    b.append(f'<rect x="672" y="50" width="316" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(lock(c, 682, 57))
    b.append(T(700, 69, 'Only on this computer.', 12, 'text', 600, c=c))
    for i, name in enumerate(['01-discuss.md', '02-plan.md', '03-implement.md', '04-verify.md', '05-review.md']):
        b.append(T(680, 102 + i * 27, name, 12.5, 'text', 500, mono=True, c=c))
    rows = [('Designs · 1', [('Settings page', 'Every setting on one page', 'Updated just now · Shown in the Plan', True)])]
    y = 258
    for g, items_ in rows:
        b.append(T(674, y, g, 11.5, 'muted', 600, c=c))
        y += 10
        for name, purpose, when, new in items_:
            b.append(f'<rect x="672" y="{y}" width="316" height="62" rx="8" fill="{c["card"] if new else c["bg"]}" stroke="{c["cardline"] if new else c["bg"]}"/>')
            b.append(mini_page(c, 680, y + 9, 64, 44))
            b.append(T(756, y + 22, name, 12.5, 'text', 650, c=c))
            if new:
                b.append(f'<circle cx="{762 + len(name) * 7}" cy="{y + 18}" r="3.5" fill="{c["blue"]}"/>')
            b.append(T(756, y + 39, purpose, 11.5, 'muted', c=c))
            b.append(T(756, y + 55, when, 10.5, 'dim', c=c))
            y += 68
        y += 18
    b.append(T(674, 376, 'Shared Plans may include a labelled still picture.', 11.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'The Plan shows its named preview and question; Files / Comments is the sidebar, with designs within Files. Interactive designs and their comments stay local; an explicitly shared Plan can include a labelled still picture')


def design_open(c: Theme) -> str:
    """A design in the viewer: its toolbar, page, pinned comment and the agent's answer."""
    W, H = 1000, 470
    b = [window(c, W, H, 'Settings page · QualityLayer')]
    b.append(sidebar(c, W, H, [('Your turn  1', [('Settings cleanup', 'Plan', 'you')]), ('Running  0', []), ('Shipped  6', [])], selected='Settings cleanup'))
    x0 = 236
    b.append(f'<line x1="222" y1="84" x2="{W - 1}" y2="84" stroke="{c["cardline"]}"/>')
    b.append(T(x0, 67, '← Back to the Plan', 12, 'muted', 500, c=c))
    b.append(T(x0 + 130, 67, 'Settings page', 13.5, 'text', 650, c=c))
    b.append(T(x0 + 228, 67, 'Updated 2 min ago', 11.5, 'dim', c=c))
    p, pw = spill(c, x0 + 330, 87, 'you', 'Waits for you')
    b.append(p)
    bx = x0
    for t, on in [('Comment  C', True), ('−  Fit  +', False), ('Jump to ▾', False), ('⤢', False)]:
        w = 22 + len(t) * 6.6
        b.append(f'<rect x="{bx}" y="86" width="{w}" height="24" rx="6" fill="{c["bluef"] if on else c["bg"]}" stroke="{c["blue"] if on else c["cardline"]}"/>')
        b.append(T(bx + w / 2, 102, t, 11.5, 'blue' if on else 'text', 600, 'middle', c=c))
        bx += w + 6
    b.append(f'<rect x="222" y="120" width="{W - 223}" height="{H - 121}" fill="{c["card"]}"/>')
    px, py, pw_, ph = 300, 132, 520, 308
    b.append(f'<rect x="{px}" y="{py}" width="{pw_}" height="{ph}" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(px + 24, py + 36, 'Settings', 17, 'text', 650, c=c))
    for i, (label, value) in enumerate([('Model for planning', 'Opus 5.5'), ('Model for building', 'Sonnet 5.5'), ('Notifications', 'On'), ('Second opinion', 'Risky Plans')]):
        ry = py + 62 + i * 44
        b.append(f'<rect x="{px + 24}" y="{ry}" width="{pw_ - 48}" height="36" rx="6" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(T(px + 38, ry + 23, label, 12.5, 'text', 500, c=c))
        b.append(T(px + pw_ - 38, ry + 23, value, 12.5, 'muted', 500, 'end', c=c))
    # the comment on a spot, and the agent's answer
    b.append(f'<circle cx="{px + 196}" cy="{py + 64}" r="10" fill="{AMBER_FILL}" stroke="{c["bg"]}" stroke-width="2.5"/>')
    b.append(T(px + 196, py + 68, '1', 11, '#171717', 700, 'middle', c=c))
    cx_, cy_ = px + 210, py + 84
    b.append(f'<rect x="{cx_}" y="{cy_}" width="250" height="96" rx="9" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-opacity="0.6"/>')
    b.append(T(cx_ + 14, cy_ + 22, 'You · this spot', 12, 'text', 650, c=c))
    b.append(T(cx_ + 14, cy_ + 40, 'Say which model plans.', 12, 'text', c=c))
    b.append(f'<rect x="{cx_ + 10}" y="{cy_ + 50}" width="230" height="38" rx="6" fill="{c["card"]}"/>')
    b.append(ring(c, cx_ + 22, cy_ + 64, 'agent', 4))
    b.append(T(cx_ + 32, cy_ + 68, 'Claude Code: the row now says', 11.5, 'muted', c=c))
    b.append(T(cx_ + 32, cy_ + 82, '“Model for planning”.', 11.5, 'muted', c=c))
    b.append(f'<rect x="{W / 2 - 40}" y="{H - 44}" width="240" height="30" rx="8" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-opacity="0.6"/>')
    b.append(f'<circle cx="{W / 2 - 24}" cy="{H - 29}" r="3.5" fill="{c["blue"]}"/>')
    b.append(T(W / 2 - 14, H - 24.5, 'Settings page was updated', 12, 'text', 600, c=c))
    b.append(T(W / 2 + 186, H - 24.5, 'Open', 12, 'blue', 600, 'end', c=c))
    return svg(W, H, ''.join(b), 'A design in the viewer: Back to the Plan, its name and update time, named agent status, Comment, zoom, Jump to and full screen. A pinned comment keeps the agent’s answer beside the spot; a quiet notice reports an update')


DRAWINGS = [('architecture', architecture), ('flow', flow), ('slices', slices), ('agents', agents), ('app', app), ('app-marked', app_marked),
            ('home', home_ill), ('plan-full', plan_full),
            ('items', items_ill), ('decision', decision_ill),
            ('implement-start', implement_start), ('implement', implement_ill), ('checkpoint', checkpoint_ill),
            ('discuss', discuss_ill), ('diagnose', diagnose_ill), ('plan', plan_ill),
            ('verify', verify_ill), ('stopped', stopped_ill), ('review', review_ill), ('comments', comments_ill),
            ('shipped', shipped_ill), ('abandon', abandon_ill), ('band', band_ill), ('cost', cost_ill),
            ('attention', attention_ill), ('feedback', feedback_ill), ('agents-other', agents_other_ill),
            ('team', team), ('team-agents', team_agents), ('team-timeline', team_timeline), ('team-change', team_change),
            ('peers', peers), ('install', install_ill), ('firsttask', firsttask_ill), ('update', update_ill),
            ('move', move_ill), ('settings', settings_ill), ('files', files_ill), ('privacy', privacy_ill),
            ('designs', designs_flow), ('designs-tab', designs_tab), ('design-open', design_open)]
DRAWINGS += [(f'track-{n.lower()}', track(n)) for n, _ in STEPS]

os.makedirs(OUT, exist_ok=True)
for name, fn in DRAWINGS:
    for theme, c in THEMES.items():
        with open(os.path.join(OUT, f'{name}-{theme}.svg'), 'w') as f:
            # Full-size links open the SVG alone, without the article's themed background.
            f.write(fn(c).replace('<svg ', f'<svg style="background:{c["bg"]}" ', 1))
print('ok')
