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


# ---------------------------------------------------------------- 1 routes
def routes(c):
    W, H = 1000, 372
    cols = [('Frame', 'plan'), ('Research', 'plan'), ('Design', 'plan'), ('Outline', 'plan'),
            ('Handoff', 'build'), ('Build', 'build'), ('Checkpoint', 'build'), ('Simplify', 'build'), ('Verify', 'check'),
            ('Review', 'ok')]
    x0, cw = 186, 81
    cx = [x0 + i * cw + cw / 2 for i in range(len(cols))]
    groups = [('Plan', 'Before any code', 0, 4, 'violet'), ('Build', 'Tested as it goes', 4, 8, 'blue'),
              ('Check', 'Independent', 8, 9, 'teal'), ('Ship', 'Your call', 9, 10, 'amber')]
    b = []
    for name, sub, a, z, col in groups:
        xa, xz = x0 + a * cw + 4, x0 + z * cw - 4
        b.append(f'<rect x="{xa}" y="8" width="{xz - xa}" height="4" rx="2" fill="{c[col]}"/>')
        b.append(T(xa, 34, name, 15, col, 650, c=c))
        b.append(T(xa, 52, sub, 12, 'muted', c=c))
    for i, (n, _) in enumerate(cols):
        b.append(T(cx[i], 86, n, 12, 'muted', 500, 'middle', c=c))
    you = {'Frame', 'Research', 'Design', 'Outline', 'Handoff', 'Review', 'Diagnose'}
    rows = [
        ('Feature', 'The full plan', {}),
        ('Bug', 'Cause first', {'Research': 'Diagnose', 'Design': None}),
        ('Quick change', 'A rename, a setting', {'Frame': None, 'Research': None, 'Design': None, 'Outline': None,
                                                  'Handoff': None, 'Checkpoint': None, 'Simplify': None, 'Build': 'Change'}),
    ]
    y = 140
    for name, sub, mods in rows:
        b.append(T(24, y - 2, name, 15, 'text', 650, c=c))
        b.append(T(24, y + 16, sub, 12, 'muted', c=c))
        on = [i for i, (n, _) in enumerate(cols) if mods.get(n, n) is not None]
        b.append(f'<line x1="{cx[0]}" y1="{y}" x2="{cx[-1]}" y2="{y}" stroke="{c["off"]}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>')
        b.append(f'<line x1="{cx[on[0]]}" y1="{y}" x2="{cx[on[-1]]}" y2="{y}" stroke="{c["line"]}" stroke-width="2"/>')
        for i, (n, _) in enumerate(cols):
            label = mods.get(n, n)
            if label is None:
                b.append(f'<circle cx="{cx[i]}" cy="{y}" r="4" fill="{c["bg"]}" stroke="{c["off"]}" stroke-width="2"/>')
                continue
            if label in you:
                b.append(f'<rect x="{cx[i] - 9}" y="{y - 9}" width="18" height="18" rx="3" transform="rotate(45 {cx[i]} {y})" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="2"/>')
            else:
                b.append(f'<circle cx="{cx[i]}" cy="{y}" r="9" fill="{c["blue"]}"/>')
            if label != n:
                b.append(T(cx[i], y + 30, label, 12, 'text', 600, 'middle', c=c))
        y += 82
    ly = H - 16
    b.append(f'<rect x="{x0 + 4 - 7}" y="{ly - 12}" width="14" height="14" rx="2" transform="rotate(45 {x0 + 4} {ly - 5})" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="2"/>')
    b.append(T(x0 + 20, ly, 'You review and approve', 13, 'muted', c=c))
    b.append(f'<circle cx="{x0 + 214}" cy="{ly - 5}" r="7" fill="{c["blue"]}"/>')
    b.append(T(x0 + 228, ly, 'The agent works on its own', 13, 'muted', c=c))
    b.append(f'<circle cx="{x0 + 442}" cy="{ly - 5}" r="4" fill="{c["bg"]}" stroke="{c["off"]}" stroke-width="2"/>')
    b.append(T(x0 + 454, ly, 'Skipped on this route', 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Three routes through QualityLayer: Feature, Bug and Quick change, from planning to your approval')


# ---------------------------------------------------------------- 2 slices
def slices(c):
    W, H = 1000, 430
    layers = ['Screen', 'API', 'Logic', 'Database']
    top, lh = 96, 52
    b = []
    for i, l in enumerate(layers):
        y = top + i * lh
        b.append(f'<line x1="130" y1="{y + lh / 2}" x2="{W - 24}" y2="{y + lh / 2}" stroke="{c["line"]}" stroke-width="1" stroke-dasharray="3 5"/>')
        b.append(T(24, y + lh / 2 + 5, l, 13, 'muted', 500, c=c))
    sl = [('s1', 'Slice 1', 'Export one report'), ('s2', 'Slice 2', 'Filter what is exported'),
          ('s3', 'Slice 3', 'Large reports in the background')]
    sx, sw, gap = 132, 200, 26
    for k, (col, name, what) in enumerate(sl):
        x = sx + k * (sw + gap)
        b.append(T(x, 30, name, 15, col, 650, c=c))
        b.append(T(x, 50, what, 13, 'muted', c=c))
        b.append(f'<rect x="{x}" y="64" width="{sw}" height="24" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<circle cx="{x + 14}" cy="76" r="5" fill="none" stroke="{c["danger"]}" stroke-width="2"/>')
        b.append(T(x + 26, 81, 'A failing test first', 12, 'text', 500, c=c))
        bx = x + 18
        b.append(f'<rect x="{bx}" y="{top + 4}" width="{sw - 36}" height="{lh * 4 - 8}" rx="12" fill="{c[col]}" fill-opacity="0.14" stroke="{c[col]}" stroke-width="2"/>')
        for i in range(4):
            yy = top + i * lh + lh / 2
            b.append(f'<circle cx="{bx + (sw - 36) / 2}" cy="{yy}" r="5" fill="{c[col]}"/>')
        b.append(f'<line x1="{bx + (sw - 36) / 2}" y1="{top + lh / 2}" x2="{bx + (sw - 36) / 2}" y2="{top + 3.5 * lh}" stroke="{c[col]}" stroke-width="2"/>')
        cy = top + lh * 4 + 18
        b.append(f'<rect x="{x}" y="{cy}" width="{sw}" height="86" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<path d="M{x + 14} {cy + 22} l5 5 l9 -10" fill="none" stroke="{c["ok"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(T(x + 36, cy + 27, 'Runs end to end', 14, 'text', 650, c=c))
        for ev, ex, ew in [('Tests', 12, 50), ('Logs', 68, 44), ('Screenshot', 118, 70)]:
            b.append(f'<rect x="{x + ex}" y="{cy + 44}" width="{ew}" height="26" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(x + ex + ew / 2, cy + 61, ev, 11, 'muted', 500, 'middle', c=c))
        ax = x + sw + 5
        b.append(f'<path d="M{ax} {cy + 43} h{gap - 10}" stroke="{c["muted"]}" stroke-width="1.6"/>')
        b.append(f'<path d="M{ax + gap - 14} {cy + 38} l6 5 l-6 5" fill="none" stroke="{c["muted"]}" stroke-width="1.6"/>')
    # Simplify: one pass over the whole change at the end of the build
    x, w = sx + 3 * (sw + gap), W - 24 - (sx + 3 * (sw + gap))
    b.append(T(x, 30, 'Simplify', 15, 'teal', 650, c=c))
    b.append(T(x, 50, 'The whole change, once', 13, 'muted', c=c))
    b.append(f'<rect x="{x}" y="64" width="{w}" height="24" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x + 14, 81, 'A fresh helper', 12, 'text', 500, c=c))
    b.append(f'<rect x="{x + 10}" y="{top + 4}" width="{w - 20}" height="{lh * 4 - 8}" rx="12" fill="{c["teal"]}" fill-opacity="0.07" stroke="{c["teal"]}" stroke-width="2"/>')
    for i in range(4):
        yy = top + i * lh + lh / 2
        mx = x + w / 2
        b.append(f'<circle cx="{mx}" cy="{yy}" r="9" fill="{c["bg"]}" stroke="{c["teal"]}" stroke-width="1.6"/>')
        b.append(f'<path d="M{mx - 4} {yy} h8" stroke="{c["teal"]}" stroke-width="2" stroke-linecap="round"/>')
    cy = top + lh * 4 + 18
    b.append(f'<rect x="{x}" y="{cy}" width="{w}" height="86" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(f'<path d="M{x + 14} {cy + 22} l5 5 l9 -10" fill="none" stroke="{c["ok"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(T(x + 36, cy + 27, 'Same behaviour', 14, 'text', 650, c=c))
    for ev, ex, ew in [('Merge', 10, 46), ('Reuse', 60, 44), ('Remove', 108, 52)]:
        b.append(f'<rect x="{x + ex}" y="{cy + 44}" width="{ew}" height="26" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(x + ex + ew / 2, cy + 61, ev, 11, 'muted', 500, 'middle', c=c))
    b.append(T(W / 2, H - 4, 'Each slice works on its own before the next starts. Then one pass makes the whole change simpler, and verification checks nothing broke.', 13, 'muted', 400, 'middle', c=c))
    return svg(W, H, ''.join(b), 'A feature built in three vertical slices, each tested end to end with kept evidence, then simplified as a whole while its behaviour stays the same')


# ---------------------------------------------------------------- 3 agents
def node(c, x, y, w, h, title, sub, col, fill=None, icon=None):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c[fill] if fill else c["card"]}" stroke="{c[col] if col != "cardline" else c["cardline"]}" stroke-width="{2 if col != "cardline" else 1}"/>']
    out.append(T(x + 16, y + 28, title, 15, 'text', 650, c=c))
    for i, s in enumerate(sub if isinstance(sub, list) else [sub]):
        out.append(T(x + 16, y + 48 + i * 18, s, 13, 'muted', c=c))
    return ''.join(out)


def curve(c, x1, y1, x2, y2, col='line', dash=False, w=2):
    mx = (x1 + x2) / 2
    d = ' stroke-dasharray="4 5"' if dash else ''
    return f'<path d="M{x1} {y1} C{mx} {y1} {mx} {y2} {x2} {y2}" fill="none" stroke="{c[col]}" stroke-width="{w}"{d}/>'


def agents(c):
    W, H = 1000, 482
    b = []
    py, ph = 174, 120
    # left: you and your agent
    b.append(curve(c, 196, 234, 236, 234, 'amberl'))
    b.append(node(c, 24, 194, 172, 80, 'You', 'Approve every step', 'amber', 'amberf'))
    b.append(node(c, 236, 194, 190, 80, 'Your agent', ['Plans it with you,', 'your best model'], 'blue', 'bluef'))
    b.append(curve(c, 426, 234, 470, 234, 'blue'))
    # the plan
    b.append(f'<rect x="470" y="{py}" width="150" height="{ph}" rx="12" fill="{c["violetf"]}" stroke="{c["violet"]}" stroke-width="2"/>')
    b.append(T(486, py + 30, 'Plan documents', 15, 'text', 650, c=c))
    for i in range(4):
        b.append(f'<rect x="486" y="{py + 46 + i * 15}" width="{[104, 88, 112, 70][i]}" height="6" rx="3" fill="{c["violet"]}" fill-opacity="0.35"/>')
    b.append(T(545, py + ph + 26, 'Every helper starts from these,', 12, 'muted', 400, 'middle', c=c))
    b.append(T(545, py + ph + 43, 'never from your chat', 12, 'muted', 400, 'middle', c=c))
    # right: helpers
    right = [
        (8, 'Research helpers', 'Read the code before the plan', 'teal'),
        (100, 'Slice builders', 'Smaller, cheaper models, in parallel', 'blue'),
        (192, 'Testers', 'Run the program end to end', 'blue'),
        (284, 'Simplify', 'Makes the finished change simpler', 'teal'),
        (376, 'Independent check', 'An AI that did not write the code', 'teal'),
    ]
    for y, t, s, col in right:
        b.append(curve(c, 620, py + ph / 2, 690, y + 38, col))
        b.append(node(c, 690, y, 286, 76, t, s, 'cardline'))
        if t == 'Slice builders':
            for k, sc in enumerate(['s1', 's2', 's3']):
                b.append(f'<rect x="{690 + 286 - 76 + k * 16}" y="{y + 16}" width="12" height="12" rx="3" fill="{c[sc]}"/>')
        else:
            b.append(f'<circle cx="{690 + 286 - 20}" cy="{y + 22}" r="6" fill="{c[col]}"/>')
    # second AI under the plan, reviewing
    b.append(curve(c, 545, py + ph + 56, 545, 404, 'violet', True))
    b.append(f'<rect x="420" y="404" width="250" height="68" rx="12" fill="{c["card"]}" stroke="{c["violet"]}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(T(436, 430, 'Second AI', 15, 'text', 650, c=c))
    b.append(T(436, 450, 'Another vendor reviews the', 13, 'muted', c=c))
    b.append(T(436, 466, 'design and the finished change', 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Who does what: you and your agent write the plan; helper agents research, build, test and check from it; an AI from another vendor reviews')


# ---------------------------------------------------------------- 4 team
def team(c):
    W, H = 1000, 306
    b = []
    b.append(node(c, 24, 120, 190, 90, 'Shared plan', ['Design, outline', 'and progress'], 'violet', 'violetf'))
    people = [(20, 'Ben', 'Approved', 'ok'), (120, 'Anna', 'Asked for changes', 'amber'), (220, 'Sam, by link', 'Comment', 'muted')]
    for y, who, what, col in people:
        b.append(curve(c, 214, 165, 290, y + 40, 'line'))
        b.append(f'<rect x="290" y="{y}" width="250" height="80" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<circle cx="320" cy="{y + 40}" r="16" fill="{c["bg"]}" stroke="{c["line"]}" stroke-width="1.5"/>')
        b.append(T(320, y + 45, who[0], 13, 'text', 650, 'middle', c=c))
        b.append(T(346, y + 34, who, 14, 'text', 650, c=c))
        b.append(T(346, y + 54, what, 13, col, 500, c=c))
        b.append(curve(c, 540, y + 40, 610, 165, 'line'))
    b.append(node(c, 610, 120, 190, 90, 'Your agent', ['Answers every comment,', 'updates the plan'], 'blue', 'bluef'))
    b.append(curve(c, 800, 165, 830, 165, 'amberl'))
    b.append(node(c, 830, 120, 146, 90, 'You decide', ['Feedback is', 'advice'], 'amber', 'amberf'))
    return svg(W, H, ''.join(b), 'Team review of a plan: teammates and outside reviewers comment, your agent answers, you decide')


# ---------------------------------------------------------------- 5 peers
def peers(c):
    W, H = 1000, 270
    b = []
    pos = {'a': (60, 40, 'Claude Code', 'Building the export', 'blue'), 'b': (60, 190, 'Claude Code', 'Fixing a flaky test', 'blue'),
           'c': (700, 40, 'Codex', 'Reviewing the design', 'violet'), 'd': (700, 190, 'Codex', 'Idle', 'violet')}
    links = [('a', 'c', 'Asks for a review'), ('b', 'd', 'Hands over a task'), ('a', 'b', 'Talks a problem through')]
    for f, t, lab in links:
        x1, y1 = pos[f][0] + 240, pos[f][1] + 36
        x2, y2 = pos[t][0], pos[t][1] + 36
        if f == 'a' and t == 'b':
            b.append(f'<path d="M{pos[f][0] + 120} {pos[f][1] + 72} V{pos[t][1]}" stroke="{c["line"]}" stroke-width="2"/>')
            b.append(f'<rect x="{pos[f][0] + 40}" y="{(pos[f][1] + 72 + pos[t][1]) / 2 - 13}" width="160" height="26" rx="13" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(pos[f][0] + 120, (pos[f][1] + 72 + pos[t][1]) / 2 + 4, lab, 12, 'muted', 500, 'middle', c=c))
            continue
        b.append(f'<path d="M{x1} {y1} H{x2}" stroke="{c["line"]}" stroke-width="2"/>')
        b.append(f'<path d="M{x2 - 8} {y1 - 5} l8 5 l-8 5" fill="none" stroke="{c["line"]}" stroke-width="2"/>')
        b.append(f'<rect x="{(x1 + x2) / 2 - 80}" y="{y1 - 13}" width="160" height="26" rx="13" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T((x1 + x2) / 2, y1 + 4, lab, 12, 'muted', 500, 'middle', c=c))
    for k, (x, y, name, what, col) in pos.items():
        b.append(f'<rect x="{x}" y="{y}" width="240" height="72" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<circle cx="{x + 22}" cy="{y + 25}" r="6" fill="{c[col]}"/>')
        b.append(T(x + 38, y + 30, name, 15, 'text', 650, c=c))
        b.append(T(x + 22, y + 52, what, 13, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Claude Code and Codex sessions on one computer messaging each other')


# ---------------------------------------------------------------- 6 cockpit: a design under review
def bars(c, x, y, widths, gap=14, h=6, col='line'):
    return ''.join(f'<rect x="{x}" y="{y + i * gap}" width="{w}" height="{h}" rx="3" fill="{c[col]}"/>' for i, w in enumerate(widths))


def window(c, W, H):
    return (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{c["bg"]}" stroke="{c["cardline"]}" stroke-width="1.5"/>'
            f'<path d="M1 17 a16 16 0 0 1 16 -16 H{W - 17} a16 16 0 0 1 16 16 V40 H1 Z" fill="{c["card"]}"/>'
            f'<line x1="1" y1="40" x2="{W - 1}" y2="40" stroke="{c["cardline"]}"/>'
            + ''.join(f'<circle cx="{22 + i * 18}" cy="21" r="5" fill="{c["line"]}"/>' for i in range(3))
            + T(W / 2, 26, 'localhost · QualityLayer Cockpit', 12, 'dim', 500, 'middle', mono=True, c=c))


def cockpit(c):
    W, H = 1000, 600
    b = [window(c, W, H)]
    # sidebar
    b.append(f'<path d="M1 41 H221 V{H - 1} H17 a16 16 0 0 1 -16 -16 Z" fill="{c["card"]}"/>')
    b.append(f'<line x1="221" y1="41" x2="221" y2="{H - 1}" stroke="{c["cardline"]}"/>')
    b.append(T(24, 72, 'QualityLayer', 15, 'text', 700, c=c))
    b.append(T(24, 108, 'Needs you', 12, 'amber', 650, c=c))
    tasks = [('Queue migration', 'Design', True), ('Webhooks', 'Build 5/11', False), ('Invoice totals', 'Handoff', False),
             ('Export API', 'Review', False)]
    for i, (n, st, sel) in enumerate(tasks):
        y = 124 + i * 34
        if sel:
            b.append(f'<rect x="12" y="{y}" width="198" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(f'<circle cx="28" cy="{y + 14}" r="4.5" fill="none" stroke="{c["blue"]}" stroke-width="2"/>')
        b.append(T(40, y + 18, n, 12.5, 'text', 500, c=c))
        b.append(T(200, y + 18, st, 10.5, 'dim', 400, 'end', mono=True, c=c))
    b.append(T(24, 290, 'In progress', 12, 'muted', 650, c=c))
    for i in range(2):
        y = 304 + i * 34
        b.append(f'<circle cx="28" cy="{y + 14}" r="4.5" fill="none" stroke="{c["dim"]}" stroke-width="2" stroke-dasharray="3 3"/>')
        b.append(bars(c, 40, y + 11, [[110, 92][i]]))
    # header and stage track
    x0 = 250
    b.append(T(x0, 78, 'Queue migration', 20, 'text', 650, c=c))
    stages = ['Frame', 'Research', 'Design', 'Outline', 'Handoff', 'Build', 'Verify', 'Review']
    sx = x0
    for i, s in enumerate(stages):
        done, cur = i < 2, i == 2
        col = c['text'] if done else c['amber'] if cur else c['dim']
        if done:
            b.append(f'<circle cx="{sx + 5}" cy="{106}" r="5" fill="{c["text"]}"/>')
        else:
            b.append(f'<circle cx="{sx + 5}" cy="{106}" r="5" fill="none" stroke="{col}" stroke-width="2"/>')
        b.append(f'<text x="{sx + 16}" y="110" font-family="{SANS}" font-size="12.5" font-weight="{600 if cur else 400}" fill="{col}">{s}</text>')
        sx += 16 + len(s) * 7.2 + 18
    # review bar
    by = 128
    b.append(f'<rect x="222" y="{by}" width="{W - 223}" height="64" fill="{c["amberf"]}"/>')
    b.append(f'<rect x="222" y="{by}" width="4" height="64" fill="{c["amber"]}"/>')
    b.append(T(x0, by + 28, 'Your review · the design', 14, 'text', 650, c=c))
    b.append(T(x0, by + 48, 'Comment on any passage, then decide.', 12.5, 'muted', c=c))
    b.append(f'<rect x="{W - 290}" y="{by + 16}" width="148" height="34" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(W - 216, by + 38, 'Request changes', 13, 'text', 600, 'middle', c=c))
    b.append(f'<rect x="{W - 130}" y="{by + 16}" width="100" height="34" rx="8" fill="{c["blue"]}"/>')
    b.append(T(W - 80, by + 38, 'Approve', 13, '#ffffff', 650, 'middle', c=c))
    # system design card
    cy = 218
    b.append(f'<rect x="{x0}" y="{cy}" width="410" height="350" rx="12" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    b.append(T(x0 + 18, cy + 30, 'System design', 14, 'text', 650, c=c))
    def box(x, y, w, label, col, fill):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="9" fill="{c[fill]}" stroke="{c[col]}" stroke-width="1.8"/>'
                + T(x + w / 2, y + 27, label, 13, 'text', 600, 'middle', c=c))
    b.append(box(x0 + 22, cy + 140, 96, 'Jobs', 'cardline', 'bg'))
    b.append(box(x0 + 160, cy + 140, 104, 'Adapter', 'violet', 'violetf'))
    b.append(box(x0 + 300, cy + 76, 92, 'New queue', 'blue', 'bluef'))
    b.append(box(x0 + 300, cy + 204, 92, 'Legacy', 'cardline', 'bg'))
    b.append(f'<path d="M{x0 + 118} {cy + 162} H{x0 + 160}" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(curve(c, x0 + 264, cy + 162, x0 + 300, cy + 98, 'blue'))
    b.append(curve(c, x0 + 264, cy + 162, x0 + 300, cy + 226, 'line', True))
    # a comment pinned on the adapter
    b.append(f'<rect x="{x0 + 100}" y="{cy + 262}" width="230" height="58" rx="10" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.5"/>')
    b.append(f'<path d="M{x0 + 205} {cy + 262} l7 -10 l7 10" fill="{c["bg"]}" stroke="{c["amberl"]}" stroke-width="1.5"/>')
    b.append(f'<rect x="{x0 + 204}" y="{cy + 261}" width="16" height="3" fill="{c["bg"]}"/>')
    b.append(f'<circle cx="{x0 + 124}" cy="{cy + 291}" r="12" fill="{c["amberf"]}" stroke="{c["amber"]}" stroke-width="1.5"/>')
    b.append(T(x0 + 124, cy + 295, 'A', 11, 'amber', 700, 'middle', c=c))
    b.append(T(x0 + 144, cy + 286, 'Anna', 12, 'text', 650, c=c))
    b.append(T(x0 + 144, cy + 304, 'Keep the retry test green', 12, 'muted', c=c))
    # mockup card
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
    return svg(W, H, ''.join(b), 'The Cockpit: a design under review with a system diagram, a teammate comment and a clickable mockup')


# ---------------------------------------------------------------- 7 cockpit: handoff
def handoff(c):
    W, H = 1000, 470
    b = [window(c, W, H)]
    x0 = 40
    b.append(T(x0, 84, 'Start the build', 18, 'text', 650, c=c))
    b.append(T(x0, 106, '3 slices · 11 tasks · planning stops here on purpose', 13, 'muted', c=c))
    # agent switch
    b.append(T(x0, 152, 'Build with', 13, 'muted', 600, c=c))
    seg = [('Claude Code', True), ('Codex', False), ('Other agent', False)]
    sx = x0 + 84
    b.append(f'<rect x="{sx}" y="{130}" width="314" height="36" rx="9" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
    for i, (s, on) in enumerate(seg):
        w = [112, 84, 110][i]
        if on:
            b.append(f'<rect x="{sx + 4}" y="134" width="{w}" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(sx + 4 + w / 2, 152, s, 13, 'text' if on else 'muted', 600 if on else 500, 'middle', c=c))
        sx += w + 2
    # recommendation
    ry = 186
    b.append(f'<rect x="{x0}" y="{ry}" width="{W - 2 * x0}" height="62" rx="12" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-width="1.5"/>')
    b.append(T(x0 + 18, ry + 26, 'Recommended', 12, 'blue', 650, c=c))
    b.append(T(x0 + 18, ry + 47, 'This session, cleared · your best model coordinates', 14, 'text', 600, c=c))
    b.append(T(W - x0 - 18, ry + 37, 'Helpers on smaller models build the slices', 12.5, 'muted', 400, 'end', c=c))
    # steps
    chips = ['/clear', '/model']
    y = 280
    for n in (1, 2, 3):
        b.append(f'<circle cx="{x0 + 14}" cy="{y + 14}" r="13" fill="none" stroke="{c["cardline"]}" stroke-width="1.5"/>')
        b.append(T(x0 + 14, y + 19, str(n), 12, 'muted', 650, 'middle', c=c))
        if n == 1:
            b.append(T(x0 + 40, y + 19, 'Start a clean session', 14, 'text', 600, c=c))
            cx = x0 + 220
            for ch in chips:
                w = 22 + len(ch) * 8
                b.append(f'<rect x="{cx}" y="{y + 1}" width="{w}" height="28" rx="7" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
                b.append(T(cx + w / 2, y + 20, ch, 12, 'text', 500, 'middle', mono=True, c=c))
                cx += w + 10
        elif n == 2:
            b.append(T(x0 + 40, y + 19, 'Paste the build prompt', 14, 'text', 600, c=c))
            px, pw = x0 + 220, W - x0 - (x0 + 220)
            b.append(f'<rect x="{px}" y="{y - 4}" width="{pw}" height="76" rx="10" fill="{c["card"]}" stroke="{c["cardline"]}"/>')
            b.append(bars(c, px + 18, y + 14, [300, 220], 16, 7))
            b.append(f'<rect x="{px + pw - 130}" y="{y + 30}" width="114" height="30" rx="7" fill="{c["blue"]}"/>')
            b.append(T(px + pw - 73, y + 50, 'Copy prompt', 13, '#ffffff', 650, 'middle', c=c))
            y += 46
        else:
            b.append(T(x0 + 40, y + 19, 'Watch it here: it stops for you at Review, or earlier only for a decision that is yours', 14, 'text', 600, c=c))
        y += 56
    return svg(W, H, ''.join(b), 'The Cockpit handoff: choose the agent that builds, a recommended setup, launch steps and the build prompt')


# ---------------------------------------------------------------- 8 the steps of the Feature route, for page tracks
STEPS = [('Frame', 'violet'), ('Research', 'violet'), ('Design', 'violet'), ('Outline', 'violet'),
         ('Handoff', 'blue'), ('Build', 'blue'), ('Checkpoint', 'blue'), ('Simplify', 'blue'),
         ('Verify', 'teal'), ('Review', 'amber'), ('Shipped', 'amber')]


# ---------------------------------------------------------------- 9 step illustrations
def card(c: Theme, x: float, y: float, w: float, h: float, stroke: str = 'cardline', fill: str = 'card',
         dash: bool = False, sw: float = 1) -> str:
    d = ' stroke-dasharray="5 4"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{c[fill]}" stroke="{c[stroke]}" stroke-width="{sw}"{d}/>'


def arrow(c: Theme, x1: float, y1: float, x2: float, y2: float | None = None, col: str = 'muted', dash: bool = False) -> str:
    y2 = y1 if y2 is None else y2
    d = ' stroke-dasharray="4 4"' if dash else ''
    if y1 == y2:
        head = f'<path d="M{x2 - 7} {y2 - 5} l7 5 l-7 5" fill="none" stroke="{c[col]}" stroke-width="1.8"/>'
    else:
        s = 1 if y2 > y1 else -1
        head = f'<path d="M{x2 - 5} {y2 - 7 * s} l5 {7 * s} l5 {-7 * s}" fill="none" stroke="{c[col]}" stroke-width="1.8"/>'
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c[col]}" stroke-width="1.8"{d}/>' + head


def mark(c: Theme, x: float, y: float, ok: bool = True) -> str:
    if ok:
        return f'<path d="M{x - 6} {y} l4 4 l8 -9" fill="none" stroke="{c["ok"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    return (f'<path d="M{x - 5} {y - 5} l10 10 M{x + 5} {y - 5} l-10 10" stroke="{c["danger"]}" stroke-width="2.4" '
            f'stroke-linecap="round"/>')


def pill(c: Theme, x: float, y: float, text: str, col: str = 'muted', w: float | None = None, mono: bool = False) -> str:
    w = w if w is not None else 18 + len(text) * (7.4 if mono else 6.6)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{c["bg"]}" stroke="{c["cardline"]}"/>'
            + T(x + w / 2, y + 15, text, 11.5, col, 600, 'middle', mono, c=c))


def doc_head(c: Theme, x: float, y: float, w: float, file: str, who: str) -> str:
    return (f'<line x1="{x}" y1="{y + 34}" x2="{x + w}" y2="{y + 34}" stroke="{c["cardline"]}"/>'
            + T(x + 16, y + 22, file, 12, 'muted', 500, mono=True, c=c) + T(x + w - 16, y + 22, who, 12, 'dim', 600, 'end', c=c))


def frame_ill(c: Theme) -> str:
    W, H = 1000, 330
    b = [card(c, 0, 0, 600, 326), doc_head(c, 0, 0, 600, '00-frame.md', 'For you')]
    b.append(T(20, 66, 'Add a CSV export to the reports page', 17, 'text', 700, c=c))
    b.append(T(20, 96, 'PROBLEM', 11, 'dim', 700, c=c))
    b.append(T(20, 116, 'Support copies report tables by hand to send them to customers.', 13.5, 'muted', c=c))
    b.append(T(20, 150, 'DONE MEANS', 11, 'dim', 700, c=c))
    for i, t in enumerate(['An Export button on every report', 'The file opens in a spreadsheet with the same columns',
                           'A large report arrives by email within five minutes']):
        y = 164 + i * 50
        b.append(card(c, 20, y, 560, 40, fill='bg'))
        b.append(f'<circle cx="42" cy="{y + 20}" r="11" fill="{c["violetf"]}" stroke="{c["violet"]}" stroke-width="1.5"/>')
        b.append(T(42, y + 24.5, str(i + 1), 12, 'violet', 700, 'middle', c=c))
        b.append(T(64, y + 25, t, 13.5, 'text', 500, c=c))
    b.append(card(c, 630, 0, 370, 326))
    b.append(T(650, 30, 'Decided with you', 14, 'text', 650, c=c))
    b.append(f'<rect x="650" y="48" width="250" height="40" rx="10" fill="{c["bluef"]}" stroke="{c["blue"]}" stroke-opacity="0.5"/>')
    b.append(T(664, 73, 'Which reports need the export?', 13, 'text', c=c))
    b.append(f'<rect x="730" y="98" width="250" height="40" rx="10" fill="{c["amberf"]}" stroke="{c["amberl"]}"/>')
    b.append(T(744, 123, 'All of them, with their filters', 13, 'text', c=c))
    b.append(T(650, 176, 'Research questions', 14, 'text', 650, c=c))
    for i, t in enumerate(['How is a report built today?', 'What happens to a report that runs long?']):
        y = 192 + i * 34
        b.append(f'<circle cx="660" cy="{y + 11}" r="3.5" fill="{c["teal"]}"/>')
        b.append(T(674, y + 15.5, t, 13, 'muted', c=c))
    b.append(f'<rect x="650" y="274" width="330" height="36" rx="8" fill="{c["blue"]}"/>')
    b.append(T(815, 297, 'Approve the frame', 13.5, '#ffffff', 650, 'middle', c=c))
    return svg(W, H, ''.join(b), 'A frame: the problem, three numbered Done means, the questions decided with you, and the research questions')


def research_ill(c: Theme) -> str:
    W, H = 1000, 320
    b = [card(c, 0, 0, 1000, 316), doc_head(c, 0, 0, 1000, '01-research.md', 'For you')]
    b.append(T(20, 64, 'How a report reaches the page today', 15, 'text', 650, c=c))
    parts = [('Reports page', 'cardline'), ('Report API', 'cardline'), ('Query builder', 'teal'), ('Database', 'cardline')]
    for i, (p, col) in enumerate(parts):
        x = 20 + i * 118
        b.append(card(c, x, 84, 100, 44, stroke=col, fill='tealf' if col == 'teal' else 'bg', sw=1.6 if col == 'teal' else 1))
        b.append(T(x + 50, 111, p, 12, 'text', 600, 'middle', c=c))
        if i < 3:
            b.append(arrow(c, x + 102, 106, x + 116))
    b.append(T(20, 160, 'One query builder serves every report; the export can reuse it.', 13, 'muted', c=c))
    b.append(f'<line x1="500" y1="50" x2="500" y2="296" stroke="{c["cardline"]}"/>')
    b.append(T(524, 64, 'Findings', 15, 'text', 650, c=c))
    rows = [('Every report goes through one query builder', 'api/reports/query.ts:41'),
            ('A report that runs over 30 s times out today', 'api/reports/run.ts:88'),
            ('Nothing exports a report yet', 'web/reports/page.tsx')]
    for i, (t, ref) in enumerate(rows):
        y = 82 + i * 70
        b.append(card(c, 524, y, 456, 58, fill='bg'))
        b.append(f'<circle cx="542" cy="{y + 20}" r="3.5" fill="{c["teal"]}"/>')
        b.append(T(554, y + 24, t, 13, 'text', 500, c=c))
        b.append(T(554, y + 44, ref, 11.5, 'blue', 500, mono=True, c=c))
    b.append(f'<rect x="20" y="196" width="460" height="100" rx="10" fill="{c["bg"]}" stroke="{c["cardline"]}" stroke-dasharray="4 4"/>')
    b.append(T(36, 222, 'For the agent', 12, 'dim', 700, c=c))
    b.append(bars(c, 36, 236, [380, 320, 350, 260], 12, 5))
    return svg(W, H, ''.join(b), 'Research: a picture of the parts involved, and findings that each point to the code')


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
    return svg(W, H, ''.join(b), 'Diagnosis: how to reproduce the bug, its root cause in the code, and the behaviour the fix must have')


def checkpoint_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = []
    top = [(0, 'Slice 2 built', 'cardline', 'bg'), (220, 'Running', 'blue', 'bluef'), (440, 'Passed', 'ok', 'bg'),
           (660, 'Next slice', 'cardline', 'bg')]
    for x, t, col, fill in top:
        b.append(card(c, x, 20, 180, 56, stroke=col, fill=fill, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 90, 54, t, 14, 'text', 650, 'middle', c=c))
    for x in (0, 220, 440):
        b.append(arrow(c, x + 182, 48, x + 218))
    b.append(mark(c, 474, 48))
    b.append(T(870, 54, 'Tests, logs and a', 12, 'muted', c=c))
    b.append(T(870, 70, 'screenshot are kept', 12, 'muted', c=c))
    b.append(card(c, 220, 172, 180, 56, stroke='danger', fill='bg', sw=1.6))
    b.append(mark(c, 250, 200, False))
    b.append(T(318, 205, 'Failed', 14, 'text', 650, 'middle', c=c))
    b.append(arrow(c, 310, 78, 310, 170, 'danger'))
    b.append(f'<path d="M218 200 H150 V78" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M145 85 l5 -7 l5 7" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(T(84, 150, 'Fixed at the', 12, 'muted', 400, 'middle', c=c))
    b.append(T(84, 166, 'source, run again', 12, 'muted', 400, 'middle', c=c))
    b.append(arrow(c, 402, 200, 470))
    b.append(T(436, 190, '3 runs', 11.5, 'danger', 600, 'middle', c=c))
    b.append(card(c, 472, 152, 508, 96, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(490, 180, 'Stopped: the build waits for you', 14, 'text', 650, c=c))
    for i, (t, w) in enumerate([('Continue', 96), ('Pivot', 72), ('Abandon', 92)]):
        x = 490 + sum([96, 72, 92][:i]) + i * 10
        b.append(pill(c, x, 204, t, 'text', w))
    return svg(W, H, ''.join(b), 'A checkpoint: after a slice the scenarios run; a pass goes on, a failure is fixed and run again, and three failures stop for you')


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
    groups = [('Automated checks', [('Tests', 'PASS'), ('Lint and types', 'PASS'), ('Build', 'PASS')]),
              ('Done means', [('1  Export button', 'PASS'), ('2  Opens in a spreadsheet', 'PASS'), ('3  Email within 5 min', 'PASS')]),
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
    return svg(W, H, ''.join(b), 'The Verify tab: rounds on the left, then automated checks, Done means and scenarios, each with PASS and its evidence')


def approve_ill(c: Theme) -> str:
    W, H = 1000, 350
    b = []
    tiles = [('11', 'tasks built'), ('3', 'checks passed'), ('Round 2', 'verified'), ('1', 'plan change')]
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
    b.append(T(508, 120, 'The change', 14, 'text', 650, c=c))
    for i, (f, add, rm) in enumerate([('api/reports/export.ts', 84, 0), ('api/reports/query.ts', 6, 4),
                                       ('web/reports/ExportButton.tsx', 41, 0), ('tests/export.test.ts', 120, 0)]):
        y = 138 + i * 34
        b.append(T(508, y + 16, f, 12, 'text', 500, mono=True, c=c))
        b.append(T(900, y + 16, f'+{add}', 12, 'ok', 600, 'end', mono=True, c=c))
        b.append(T(944, y + 16, f'-{rm}', 12, 'danger', 600, 'end', mono=True, c=c))
        b.append(f'<rect x="954" y="{y + 6}" width="28" height="10" rx="2" fill="{c["ok"]}" fill-opacity="0.6"/>')
    b.append(f'<rect x="0" y="300" width="1000" height="46" rx="12" fill="{c["amberf"]}"/>')
    b.append(T(18, 328, 'Your review · the finished change', 14, 'text', 650, c=c))
    b.append(f'<rect x="640" y="307" width="160" height="32" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(720, 328, 'Request changes', 13, 'text', 600, 'middle', c=c))
    b.append(f'<rect x="812" y="307" width="176" height="32" rx="8" fill="{c["blue"]}"/>')
    b.append(T(900, 328, 'Approve and ship', 13, '#ffffff', 650, 'middle', c=c))
    return svg(W, H, ''.join(b), 'The Review stage: what was built and checked, steps to try it, the files changed, and the final decision')


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
    b.append(T(622, 166, 'Your agent can open the pull request, with your OK.', 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Shipped: the task keeps its documents and evidence; the pull request, merge and deploy stay in your own process')


def quick_ill(c: Theme) -> str:
    W, H = 1000, 230
    b = []
    flow = [('Your request', 'Rename --out to --output', 'cardline', 'bg'), ('A failing test', 'The new name is checked', 'danger', 'bg'),
            ('The change', 'Smallest fix that passes', 'blue', 'bluef'), ('Verify', 'Run it, keep evidence', 'teal', 'tealf'),
            ('You approve', 'The final decision', 'amber', 'amberf')]
    for i, (t, s, col, fill) in enumerate(flow):
        x = i * 204
        b.append(card(c, x, 10, 184, 80, stroke=col, fill=fill, sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 16, 42, t, 14.5, 'text', 650, c=c))
        b.append(T(x + 16, 66, s, 12, 'muted', c=c))
        if i < 4:
            b.append(arrow(c, x + 186, 50, x + 202))
    b.append(f'<path d="M500 92 V150 H560" fill="none" stroke="{c["muted"]}" stroke-width="1.8" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M553 145 l7 5 l-7 5" fill="none" stroke="{c["muted"]}" stroke-width="1.8"/>')
    b.append(T(490, 128, 'Turns out bigger', 12, 'muted', 500, 'end', c=c))
    b.append(card(c, 562, 120, 300, 64, stroke='violet', fill='violetf', sw=1.6))
    b.append(T(580, 148, 'Feature route', 14.5, 'text', 650, c=c))
    b.append(T(580, 170, 'Starts again at Frame, with a plan', 12, 'muted', c=c))
    return svg(W, H, ''.join(b), 'A quick change: a failing test, the change, a check and your approval; a bigger task moves to the Feature route')


def stopped_ill(c: Theme) -> str:
    W, H = 1000, 220
    b = []
    for i in range(3):
        x = i * 128
        b.append(card(c, x, 70, 112, 60, stroke='danger', fill='bg', sw=1.4))
        b.append(mark(c, x + 24, 100, False))
        b.append(T(x + 40, 105, f'Round {i + 1}', 13, 'text', 600, c=c))
    b.append(arrow(c, 372, 100, 410))
    b.append(card(c, 412, 60, 190, 80, stroke='amber', fill='amberf', sw=1.6))
    b.append(T(430, 94, 'Stopped', 15, 'text', 650, c=c))
    b.append(T(430, 116, 'The choice is yours', 12.5, 'muted', c=c))
    opts = [('Continue', 'Keep the approach, try again'), ('Pivot', 'Agree on a new approach'), ('Abandon', 'Stop, keep the documents')]
    for i, (t, s) in enumerate(opts):
        y = i * 74
        b.append(curve(c, 602, 100, 650, y + 30, 'line'))
        b.append(card(c, 650, y, 350, 60))
        b.append(T(668, y + 26, t, 14, 'text', 650, c=c))
        b.append(T(668, y + 46, s, 12.5, 'muted', c=c))
    return svg(W, H, ''.join(b), 'Stopped verification: three failed rounds, then you choose to continue, pivot or abandon')


def abandon_ill(c: Theme) -> str:
    W, H = 1000, 170
    b = []
    items = [('Abandon', 'Stops the work', 'The documents stay in your repository', 'danger'),
             ('Archive', 'Off the Cockpit list', 'Restore brings it back', 'muted'),
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


def track_group(first: str, last: str, label: str):
    """The Feature route with one group of steps highlighted, for a page that covers several steps."""
    def draw(c: Theme) -> str:
        W, H = 1000, 112
        x0, step = 54, 89.2
        names = [n for n, _ in STEPS]
        a, z = names.index(first), names.index(last)
        xs = [x0 + i * step for i in range(len(STEPS))]
        col = STEPS[a][1]
        b = [T(0, 16, 'Feature route', 12, 'muted', 600, c=c)]
        b.append(f'<rect x="{xs[a] - 30}" y="30" width="{xs[z] - xs[a] + 60}" height="76" rx="14" fill="{c[col]}" fill-opacity="0.09" stroke="{c[col]}" stroke-opacity="0.5"/>')
        b.append(T((xs[a] + xs[z]) / 2, 22, label, 12.5, col, 700, 'middle', c=c))
        b.append(f'<line x1="{xs[0]}" y1="52" x2="{xs[-1]}" y2="52" stroke="{c["line"]}" stroke-width="2"/>')
        for i, (n, _) in enumerate(STEPS):
            inside = a <= i <= z
            dash = ' stroke-dasharray="3 2.5"' if n == 'Simplify' else ''
            if inside:
                b.append(f'<circle cx="{xs[i]}" cy="52" r="8" fill="{c["bg"]}" stroke="{c[col]}" stroke-width="2.5"{dash}/>')
            else:
                b.append(f'<circle cx="{xs[i]}" cy="52" r="5" fill="{c["bg"]}" stroke="{c["line"]}" stroke-width="2"{dash}/>')
            b.append(T(xs[i], 86, n, 12.5 if inside else 12, 'text' if inside else 'muted', 650 if inside else 500, 'middle', c=c))
        return svg(W, H, ''.join(b), f'The Feature route with {label} highlighted: {first} to {last}')
    return draw


def install_ill(c: Theme) -> str:
    W, H = 1000, 200
    b = []
    steps = [('1  Install', 'One command in your terminal', 'curl … install.sh | bash', 'cardline'),
             ('2  Start a task', 'In any repository, in your agent', '/ql add a CSV export', 'blue'),
             ('3  Review in the Cockpit', 'It opens in your browser', 'localhost', 'amber')]
    for i, (t, s, code, col) in enumerate(steps):
        x = i * 340
        b.append(card(c, x, 10, 310, 170, stroke=col, fill='card', sw=1.6 if col != 'cardline' else 1))
        b.append(T(x + 20, 46, t, 16, 'text', 700, c=c))
        b.append(T(x + 20, 72, s, 13, 'muted', c=c))
        b.append(f'<rect x="{x + 20}" y="96" width="270" height="40" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(x + 34, 121, code, 13, 'text', 500, mono=True, c=c))
        if i < 2:
            b.append(arrow(c, x + 314, 95, x + 336))
    b.append(T(20, 160, 'Claude Code and Codex are set up for you', 12, 'dim', 500, c=c))
    b.append(T(360, 160, '$ql in Codex', 12, 'dim', 500, c=c))
    b.append(T(700, 160, 'Approve, or comment and ask for changes', 12, 'dim', 500, c=c))
    return svg(W, H, ''.join(b), 'Install with one command, start a task with /ql, and review it in the Cockpit')


def firsttask_ill(c: Theme) -> str:
    W, H = 1000, 190
    b = []
    steps = [('Describe', 'the change'), ('Approve', 'the frame'), ('Approve', 'research, design'), ('Approve', 'the outline'),
             ('Hand off', 'the build'), ('Follow', 'the build'), ('Approve', 'the change')]
    xs = [60 + i * 147 for i in range(len(steps))]
    b.append(f'<line x1="{xs[0]}" y1="70" x2="{xs[-1]}" y2="70" stroke="{c["line"]}" stroke-width="2"/>')
    for i, (t, s) in enumerate(steps):
        you = t in ('Approve', 'Describe', 'Hand off')
        col = 'amber' if you else 'blue'
        b.append(f'<circle cx="{xs[i]}" cy="70" r="24" fill="{c["amberf" if you else "bluef"]}" stroke="{c[col]}" stroke-width="2"/>')
        b.append(T(xs[i], 76, str(i + 1), 16, col, 700, 'middle', c=c))
        b.append(T(xs[i], 124, t, 14, 'text', 650, 'middle', c=c))
        b.append(T(xs[i], 144, s, 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(xs[0] - 24, 22, 'You act at the amber steps; your agent does the rest', 12.5, 'muted', 500, c=c))
    return svg(W, H, ''.join(b), 'Your first task in seven steps: describe, approve the frame, the research and design, the outline, hand off, follow the build, approve the change')


def settings_ill(c: Theme) -> str:
    W, H = 1000, 360
    b = [card(c, 0, 0, 600, 356)]
    b.append(T(20, 30, 'Subagents', 15, 'text', 650, c=c))
    b.append(T(20, 50, 'Fresh helpers, one job each', 12.5, 'muted', c=c))
    b.append(T(250, 80, 'In Claude Code', 11.5, 'dim', 700, c=c))
    b.append(T(420, 80, 'In Codex', 11.5, 'dim', 700, c=c))
    rows = [('Research', 'Sonnet 5.5', 'GPT-6.1 Sol'), ('Outline cold read', 'Sonnet 5.5', 'GPT-6.1 Sol'),
            ('Slice builds', 'Sonnet 5.5', 'GPT-6.1 Sol'), ('Build checkpoints', 'Sonnet 5.5', 'GPT-6.1 Sol'),
            ('Simplify', 'Sonnet 5.5', 'GPT-6.1 Sol'), ('Verify judge', 'Sonnet 5.5', 'Off')]
    for i, (job, cc, cx) in enumerate(rows):
        y = 92 + i * 42
        b.append(f'<line x1="20" y1="{y}" x2="580" y2="{y}" stroke="{c["cardline"]}"/>')
        b.append(T(20, y + 26, job, 13, 'text', 500, c=c))
        for x, v in ((250, cc), (420, cx)):
            off = v == 'Off'
            b.append(f'<rect x="{x}" y="{y + 8}" width="150" height="28" rx="7" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(T(x + 12, y + 27, v, 12.5, 'muted' if off else 'text', 500, c=c))
            b.append(f'<path d="M{x + 132} {y + 19} l4 4 l4 -4" fill="none" stroke="{c["muted"]}" stroke-width="1.5"/>')
    b.append(card(c, 620, 0, 380, 236))
    b.append(T(640, 30, 'Second opinion', 15, 'text', 650, c=c))
    b.append(T(640, 50, 'The other vendor reviews', 12.5, 'muted', c=c))
    for i, (pt, who) in enumerate([('Design', 'Codex reviews Claude Code'), ('Verify', 'Claude Code reviews Codex')]):
        y = 74 + i * 76
        b.append(card(c, 640, y, 340, 64, fill='bg'))
        b.append(T(656, y + 26, pt, 13.5, 'text', 650, c=c))
        b.append(T(656, y + 46, who, 12, 'muted', c=c))
        b.append(f'<rect x="{940}" y="{y + 22}" width="28" height="18" rx="9" fill="{c["blue"]}"/>')
        b.append(f'<circle cx="959" cy="{y + 31}" r="6" fill="#ffffff"/>')
    b.append(card(c, 620, 256, 380, 100))
    b.append(T(640, 286, 'Notifications', 15, 'text', 650, c=c))
    b.append(T(640, 308, 'When something waits for you', 12.5, 'muted', c=c))
    b.append(f'<rect x="940" y="276" width="28" height="18" rx="9" fill="{c["blue"]}"/>')
    b.append(f'<circle cx="959" cy="285" r="6" fill="#ffffff"/>')
    return svg(W, H, ''.join(b), 'Settings: a model for each helper job in Claude Code and Codex, the second opinion, and notifications')



os.makedirs(OUT, exist_ok=True)
ROUTE_OFF = {
    'feature': set(),
    'bug': {'Design'},
    'quick': {'Frame', 'Research', 'Design', 'Outline', 'Handoff', 'Checkpoint', 'Simplify'},
}
ROUTE_NAME = {'bug': {'Research': 'Diagnose'}, 'quick': {'Build': 'Change'}}
ROUTE_LABEL = {'feature': 'Feature route', 'bug': 'Bug route', 'quick': 'Quick change route'}


def track(here: str, route: str = 'feature', stopped: bool = False):
    """The route on one line, with the page's own step highlighted."""
    def draw(c: Theme) -> str:
        W, H = 1000, 112
        x0, step = 54, 89.2
        xs = [x0 + i * step for i in range(len(STEPS))]
        off, names = ROUTE_OFF[route], ROUTE_NAME.get(route, {})
        cur = [n for n, _ in STEPS].index(here)
        b = [T(0, 16, ROUTE_LABEL[route], 12, 'muted', 600, c=c)]
        on = [i for i, (n, _) in enumerate(STEPS) if n not in off]
        b.append(f'<line x1="{xs[0]}" y1="52" x2="{xs[-1]}" y2="52" stroke="{c["off"]}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>')
        b.append(f'<line x1="{xs[on[0]]}" y1="52" x2="{xs[on[-1]]}" y2="52" stroke="{c["line"]}" stroke-width="2"/>')
        b.append(f'<line x1="{xs[on[0]]}" y1="52" x2="{xs[cur]}" y2="52" stroke="{c["blue"]}" stroke-width="2.5"/>')
        for i, (n, col) in enumerate(STEPS):
            x, label = xs[i], names.get(n, n)
            dash = ' stroke-dasharray="3 2.5"' if n == 'Simplify' else ''
            if n in off:
                b.append(f'<circle cx="{x}" cy="52" r="4" fill="{c["bg"]}" stroke="{c["off"]}" stroke-width="2"/>')
                b.append(T(x, 86, label, 12, 'dim', 400, 'middle', c=c))
            elif i == cur:
                ring = c['danger'] if stopped else c[col]
                b.append(f'<circle cx="{x}" cy="52" r="15" fill="{ring}" fill-opacity="0.16"/>')
                b.append(f'<circle cx="{x}" cy="52" r="9" fill="{ring}"/>')
                b.append(T(x, 86, label, 13, 'text', 700, 'middle', c=c))
                b.append(T(x, 104, 'Stopped' if stopped else 'This page', 11, 'danger' if stopped else col, 600, 'middle', c=c))
            elif i < cur:
                b.append(f'<circle cx="{x}" cy="52" r="6" fill="{c["blue"]}"/>')
                b.append(T(x, 86, label, 12, 'muted', 500, 'middle', c=c))
            else:
                b.append(f'<circle cx="{x}" cy="52" r="6" fill="{c["bg"]}" stroke="{c["line"]}" stroke-width="2"{dash}/>')
                b.append(T(x, 86, label, 12, 'muted', 500, 'middle', c=c))
        return svg(W, H, ''.join(b), f'{ROUTE_LABEL[route]}: {names.get(here, here)} highlighted')
    return draw


def num(c: Theme, x: float, y: float, n: int) -> str:
    return (f'<circle cx="{x}" cy="{y}" r="12" fill="{c["blue"]}" stroke="{c["bg"]}" stroke-width="2.5"/>'
            + T(x, y + 4.5, str(n), 12.5, '#ffffff', 700, 'middle', c=c))


def cockpit_marked(c: Theme) -> str:
    """The Cockpit drawing with numbered markers for the parts the Cockpit page explains."""
    marks = [(200, 108, 1), (236, 106, 2), (700, 144, 3), (652, 222, 4), (586, 478, 5), (968, 230, 6)]
    base = cockpit(c)
    return base.replace('</svg>', ''.join(num(c, x, y, n) for x, y, n in marks) + '</svg>')


def outline_ill(c: Theme) -> str:
    W, H = 1000, 270
    b = [card(c, 0, 0, 640, 266)]
    b.append(T(18, 30, 'Outline', 15, 'text', 650, c=c))
    slices = [('s1', 'Slice 1 · Export one report', ['T1', 'T2', 'T3'], 'Scenario 1: export a report'),
              ('s2', 'Slice 2 · Filter what is exported', ['T4', 'T5'], None),
              ('s3', 'Slice 3 · Large reports by email', ['T6', 'T7', 'T8'], 'Scenario 2: 200,000 rows by email')]
    y = 48
    for col, title, tasks, cp in slices:
        b.append(f'<rect x="18" y="{y}" width="4" height="44" rx="2" fill="{c[col]}"/>')
        b.append(T(32, y + 15, title, 13, 'text', 650, c=c))
        for k, t in enumerate(tasks):
            x = 32 + k * 112
            b.append(f'<rect x="{x}" y="{y + 22}" width="104" height="22" rx="6" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
            b.append(f'<circle cx="{x + 12}" cy="{y + 33}" r="4" fill="none" stroke="{c["danger"]}" stroke-width="1.6"/>')
            b.append(T(x + 22, y + 37.5, f'{t} · test first', 11, 'muted', 500, c=c))
        if cp:
            b.append(f'<rect x="{390}" y="{y + 22}" width="230" height="22" rx="11" fill="{c["tealf"]}" stroke="{c["teal"]}"/>')
            b.append(mark(c, 404, y + 32))
            b.append(T(416, y + 37.5, cp, 11, 'text', 600, c=c))
        y += 70
    b.append(card(c, 660, 0, 340, 112, stroke='amber', fill='amberf', sw=1.5))
    b.append(T(678, 30, 'Before the build', 14, 'text', 650, c=c))
    b.append(T(678, 56, 'Connect the mail service · granted', 12.5, 'text', 500, c=c))
    b.append(T(678, 86, 'Then the build runs on its own.', 12.5, 'muted', c=c))
    b.append(card(c, 660, 128, 340, 138))
    b.append(T(678, 156, 'Checked end to end', 14, 'text', 650, c=c))
    for i, t in enumerate(['Export a report, open it', 'Export with filters', '200,000 rows arrive by email']):
        yy = 170 + i * 30
        b.append(mark(c, 688, yy + 6))
        b.append(T(704, yy + 11, t, 12.5, 'text', 500, c=c))
    return svg(W, H, ''.join(b), 'An outline: slices of test-first tasks, end-to-end checks after marked slices, and what you settle before the build')


def build_ill(c: Theme) -> str:
    W, H = 1000, 320
    b = [card(c, 0, 0, 1000, 44, stroke='blue', fill='bluef', sw=1.4)]
    b.append(f'<circle cx="22" cy="22" r="5" fill="{c["blue"]}"/>')
    b.append(T(36, 27, 'Now: T5 · writing the failing test', 13, 'text', 600, c=c))
    b.append(T(980, 27, 'reported 1 min ago', 12, 'muted', 400, 'end', c=c))
    rows = [('s1', 'Slice 1', ['T1', 'T2', 'T3'], 3), ('s2', 'Slice 2', ['T4', 'T5'], 1)]
    y = 62
    for col, name, tasks, done in rows:
        b.append(T(0, y + 18, name, 13, col, 650, c=c))
        for k, t in enumerate(tasks):
            x = 80 + k * 120
            b.append(f'<rect x="{x}" y="{y}" width="110" height="28" rx="7" fill="{c["bg"]}" stroke="{c[col] if k < done else c["cardline"]}"/>')
            if k < done:
                b.append(mark(c, x + 16, y + 14))
            else:
                b.append(f'<circle cx="{x + 16}" cy="{y + 14}" r="5" fill="none" stroke="{c["blue"]}" stroke-width="2" stroke-dasharray="3 2"/>')
            b.append(T(x + 30, y + 18.5, t, 12, 'text', 600, c=c))
        y += 44
    b.append(f'<rect x="460" y="62" width="250" height="28" rx="14" fill="{c["tealf"]}" stroke="{c["teal"]}"/>')
    b.append(mark(c, 476, 76))
    b.append(T(490, 80.5, 'Checkpoint 1 passed on run 2', 12, 'text', 600, c=c))
    b.append(card(c, 0, 160, 1000, 156))
    b.append(T(18, 188, 'T3 · Write the CSV file · notes', 14, 'text', 650, c=c))
    notes = [('tactical', 'The query returns rows lazily; the writer streams them', 'muted'),
             ('found by checkpoint 1', 'The header row was missing; fixed at the source', 'teal'),
             ('agreed', 'CSV only, no Excel export — your words, recorded', 'amber')]
    for i, (tag, t, col) in enumerate(notes):
        yy = 204 + i * 36
        w = 18 + len(tag) * 6.9
        b.append(f'<rect x="18" y="{yy}" width="{w}" height="24" rx="6" fill="{c["bg"]}" stroke="{c[col] if col != "muted" else c["cardline"]}"/>')
        b.append(T(18 + w / 2, yy + 16.5, tag, 11.5, col if col != 'muted' else 'muted', 600, 'middle', mono=True, c=c))
        b.append(T(30 + w, yy + 16.5, t, 13, 'text', 400, c=c))
    return svg(W, H, ''.join(b), 'The Build tab: what the agent does now, slices with ticked tasks, a passed checkpoint, and the notes on a task')


def simplify_ill(c: Theme) -> str:
    W, H = 1000, 300
    b = []
    b.append(card(c, 0, 0, 400, 230))
    b.append(T(18, 30, 'Before', 14, 'text', 650, c=c))
    for i, y in enumerate((46, 106)):
        b.append(f'<rect x="18" y="{y}" width="230" height="50" rx="8" fill="{c["amberf"]}" stroke="{c["amberl"]}"/>')
        b.append(T(30, y + 20, ['writeCsvReport()', 'writeCsvExport()'][i], 12, 'text', 600, mono=True, c=c))
        b.append(bars(c, 30, y + 30, [180, 150], 9, 4))
    b.append(T(258, 92, 'near-copies', 12, 'amber', 600, c=c))
    b.append(f'<rect x="18" y="166" width="230" height="44" rx="8" fill="{c["bg"]}" stroke="{c["danger"]}" stroke-dasharray="4 3"/>')
    b.append(T(30, 193, 'exportWrapper()', 12, 'muted', 500, mono=True, c=c))
    b.append(T(258, 193, 'only passes through', 12, 'danger', 600, c=c))
    b.append(arrow(c, 404, 115, 470, col='teal'))
    b.append(T(437, 104, 'Simplify', 12, 'teal', 700, 'middle', c=c))
    b.append(card(c, 472, 0, 528, 230, stroke='teal', sw=1.5))
    b.append(T(490, 30, 'After', 14, 'text', 650, c=c))
    b.append(f'<rect x="490" y="46" width="250" height="50" rx="8" fill="{c["tealf"]}" stroke="{c["teal"]}"/>')
    b.append(T(502, 66, 'writeCsv(rows, columns)', 12, 'text', 600, mono=True, c=c))
    b.append(bars(c, 502, 76, [190], 9, 4))
    b.append(T(490, 124, 'One pass over the whole change:', 12.5, 'muted', c=c))
    for i, t in enumerate(['merge the two writers', 'reuse formatDate()', 'remove the pass-through wrapper']):
        yy = 140 + i * 26
        b.append(f'<circle cx="498" cy="{yy + 8}" r="3.5" fill="{c["teal"]}"/>')
        b.append(T(510, yy + 12.5, t, 12.5, 'text', 500, mono=i == 1, c=c))
        b.append(T(980, yy + 12.5, 'commit', 11, 'dim', 600, 'end', mono=True, c=c))
    b.append(card(c, 0, 248, 1000, 48, fill='bg'))
    b.append(mark(c, 22, 272))
    b.append(T(38, 277, 'Same behaviour: every test and scenario still passes. A simplification that broke something is undone.', 13, 'text', 500, c=c))
    return svg(W, H, ''.join(b), 'Simplify: two near-copies merged, existing code reused, a wrapper removed, one commit each, with the same behaviour')


def secondop_ill(c: Theme) -> str:
    W, H = 1000, 230
    b = [card(c, 0, 70, 180, 80, stroke='violet', fill='violetf', sw=1.5)]
    b.append(T(18, 104, 'Design is up', 14, 'text', 650, c=c))
    b.append(T(18, 124, 'for your review', 12.5, 'muted', c=c))
    b.append(curve(c, 180, 110, 230, 40, 'amberl'))
    b.append(curve(c, 180, 110, 230, 180, 'violet', True))
    b.append(card(c, 230, 10, 320, 64, stroke='amber', fill='amberf', sw=1.4))
    b.append(T(248, 38, 'You', 14, 'text', 650, c=c))
    b.append(T(248, 58, 'Read, try the mockup, comment', 12.5, 'muted', c=c))
    b.append(card(c, 230, 146, 320, 64, stroke='violet', dash=True, sw=1.4))
    b.append(T(248, 174, 'The other vendor’s AI', 14, 'text', 650, c=c))
    b.append(T(248, 194, 'Reviews frame, research, design', 12.5, 'muted', c=c))
    b.append(curve(c, 550, 42, 600, 110, 'amberl'))
    b.append(curve(c, 550, 178, 600, 110, 'violet', True))
    b.append(card(c, 600, 70, 200, 80, stroke='blue', fill='bluef', sw=1.5))
    b.append(T(618, 104, 'Your agent', 14, 'text', 650, c=c))
    b.append(T(618, 124, 'Answers every finding', 12.5, 'muted', c=c))
    b.append(arrow(c, 802, 110, 836))
    b.append(f'<rect x="838" y="88" width="160" height="44" rx="9" fill="{c["blue"]}"/>')
    b.append(T(918, 115, 'Approve unlocks', 13.5, '#ffffff', 650, 'middle', c=c))
    return svg(W, H, ''.join(b), 'The second opinion: while you review the design, the other vendor’s AI reviews it too; your agent answers its findings, then Approve unlocks')


def files_ill(c: Theme) -> str:
    W, H = 1000, 420
    b = [card(c, 0, 0, 640, 416)]
    b.append(T(18, 30, 'docs/plans/2026-10-01-csv-export/', 13.5, 'text', 700, mono=True, c=c))
    rows = [('README.md', 'The task: its route, step and status', 'dim'),
            ('00-frame.md · 00-frame-details.md', 'Frame', 'pair'),
            ('01-research.md · 01-research-details.md', 'Research (or 01-diagnosis)', 'pair'),
            ('02-design.md · 02-design-details.md', 'Design', 'pair'),
            ('artifacts/', 'Mockups and diagrams', 'amber'),
            ('03-outline-overview.md · 03-outline.md', 'Outline', 'pair'),
            ('04-build.md · 04-build-details.md', 'The build record and its notes', 'blue'),
            ('reviews/', 'Second-opinion findings', 'violet'),
            ('evidence/', 'Test output, logs, screenshots', 'teal'),
            ('pr-description.md', 'The approved pull request text', 'dim')]
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
    b.append(card(c, 660, 0, 340, 416))
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
    return svg(W, H, ''.join(b), 'A task folder in docs/plans: a short and a detailed document per planning step, mockups, the build record, reviews, evidence and the pull request text')


def privacy_ill(c: Theme) -> str:
    W, H = 1000, 280
    b = [card(c, 0, 0, 420, 276, stroke='ok', sw=1.5)]
    b.append(T(18, 30, 'Stays on your computer', 14, 'text', 650, c=c))
    for i, t in enumerate(['Your code and the diff', 'Every plan document', 'Build evidence and logs', 'The Cockpit itself']):
        y = 52 + i * 32
        b.append(mark(c, 30, y + 8))
        b.append(T(46, y + 13, t, 13, 'text', 500, c=c))
    b.append(T(18, 196, 'Your agent sends your code to its own provider,', 12, 'muted', c=c))
    b.append(T(18, 214, 'as it always does. QualityLayer does not change that.', 12, 'muted', c=c))
    b.append(card(c, 440, 0, 560, 126))
    b.append(T(458, 30, 'QualityLayer service', 14, 'text', 650, c=c))
    b.append(T(458, 54, 'A daily licence check, with five anonymous events:', 12.5, 'muted', c=c))
    b.append(T(458, 74, 'task started, step entered, check result, task shipped, step name.', 12.5, 'muted', c=c))
    b.append(T(458, 104, 'qualitylayer telemetry off  ·  DO_NOT_TRACK=1', 12, 'blue', 500, mono=True, c=c))
    b.append(card(c, 440, 146, 560, 130, stroke='violet', sw=1.4))
    b.append(T(458, 176, 'Team service · only when you share', 14, 'text', 650, c=c))
    b.append(T(458, 200, 'The plan a reviewer reads, its title and step, and comments.', 12.5, 'muted', c=c))
    b.append(T(458, 222, 'Only your team, or whoever has your link, can read it.', 12.5, 'muted', c=c))
    b.append(T(458, 252, 'Never your code, the diff or your logs.', 12.5, 'text', 600, c=c))
    return svg(W, H, ''.join(b), 'What stays on your computer, what the licence check sends, and what sharing sends to the team service')


def team_timeline(c: Theme) -> str:
    W, H = 1000, 210
    b = []
    bands = [(0, 420, 'Plan', 'violet', 'violetf'), (430, 680, 'Build', 'blue', 'bluef'), (690, 1000, 'Check and ship', 'teal', 'tealf')]
    for x1, x2, t, col, fill in bands:
        b.append(f'<rect x="{x1}" y="104" width="{x2 - x1}" height="44" rx="10" fill="{c[fill]}" stroke="{c[col]}" stroke-width="1.4"/>')
        b.append(T((x1 + x2) / 2, 131, t, 14, 'text', 650, 'middle', c=c))
    b.append(T(210, 176, 'Comments are cheap: nothing is built yet', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(555, 176, 'Your agent builds and checks', 12.5, 'muted', 400, 'middle', c=c))
    b.append(T(845, 176, 'Reviewed like a pull request', 12.5, 'muted', 400, 'middle', c=c))
    callouts = [(40, 340, '1  Review the plan', 'Before any code is written', 'violet'),
                (650, 350, '2  Review the change', 'After the build, with its proof', 'teal')]
    for x, w, t, s, col in callouts:
        b.append(card(c, x, 0, w, 62, stroke=col, sw=1.6))
        b.append(T(x + 16, 26, t, 15, 'text', 700, c=c))
        b.append(T(x + 16, 47, s, 12.5, 'muted', c=c))
        b.append(f'<path d="M{x + w / 2} 62 V100" stroke="{c[col]}" stroke-width="1.8"/>')
        b.append(f'<path d="M{x + w / 2 - 5} 94 l5 7 l5 -7" fill="none" stroke="{c[col]}" stroke-width="1.8"/>')
    return svg(W, H, ''.join(b), 'Two moments for your team: review the plan before any code, and review the finished change after the build')


def team_plan(c: Theme) -> str:
    W, H = 1000, 360
    b = [T(0, 16, 'Your Cockpit', 13, 'muted', 700, c=c), T(520, 16, 'Your teammate’s Cockpit', 13, 'muted', 700, c=c)]
    b.append(card(c, 0, 28, 480, 328))
    b.append(T(18, 58, 'Share · CSV export', 14, 'text', 650, c=c))
    for i, (t, s) in enumerate([('Your team', 'They read, comment and approve'), ('People outside your team', 'A link for 14 days, no account')]):
        y = 74 + i * 58
        b.append(card(c, 18, y, 444, 48, fill='bg'))
        b.append(T(32, y + 21, t, 13, 'text', 600, c=c))
        b.append(T(32, y + 38, s, 11.5, 'muted', c=c))
        b.append(f'<rect x="{410}" y="{y + 15}" width="34" height="18" rx="9" fill="{c["blue"]}"/>')
        b.append(f'<circle cx="435" cy="{y + 24}" r="6.5" fill="#ffffff"/>')
    b.append(T(18, 214, 'From your team', 13, 'text', 650, c=c))
    comments = [('B', 'Ben approved', 'The adapter is the right seam', 'ok'),
                ('A', 'Anna asked for changes', 'Keep the retry test green', 'amber')]
    for i, (av, who, q, col) in enumerate(comments):
        y = 226 + i * 54
        b.append(f'<circle cx="34" cy="{y + 20}" r="13" fill="{c["bg"]}" stroke="{c[col]}" stroke-width="1.5"/>')
        b.append(T(34, y + 24.5, av, 12, col, 700, 'middle', c=c))
        b.append(T(56, y + 16, who, 12.5, col, 600, c=c))
        b.append(T(56, y + 34, q, 12.5, 'text', c=c))
        b.append(T(462, y + 24, 'reached your agent', 11, 'dim', 500, 'end', c=c))
    b.append(card(c, 520, 28, 480, 328))
    b.append(T(538, 58, 'Team', 13, 'muted', 700, c=c))
    tasks = [('CSV export', 'Design', 'Waits for your review', 'amber'), ('Webhook signing', 'Outline', 'Waits for Chen', 'muted'),
             ('Rate-limit tiers', 'Build 4/9', 'Building now', 'blue')]
    for i, (t, st, s, col) in enumerate(tasks):
        y = 70 + i * 40
        if i == 0:
            b.append(f'<rect x="530" y="{y - 4}" width="460" height="34" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
        b.append(T(546, y + 17, t, 12.5, 'text', 600, c=c))
        b.append(T(700, y + 17, st, 11.5, 'muted', 500, mono=True, c=c))
        b.append(T(980, y + 17, s, 12, col, 600, 'end', c=c))
    b.append(f'<rect x="538" y="196" width="444" height="92" rx="9" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(552, 218, '02-design.md · selected passage', 11.5, 'dim', 600, mono=True, c=c))
    b.append(f'<rect x="552" y="228" width="300" height="10" rx="3" fill="{c["amberf"]}" stroke="{c["amberl"]}"/>')
    b.append(T(552, 270, 'Can support see which client a job ran on?', 12.5, 'text', c=c))
    b.append(f'<rect x="538" y="300" width="200" height="34" rx="8" fill="{c["bg"]}" stroke="{c["cardline"]}"/>')
    b.append(T(638, 322, 'Ask for changes', 13, 'text', 600, 'middle', c=c))
    b.append(f'<rect x="750" y="300" width="232" height="34" rx="8" fill="{c["blue"]}"/>')
    b.append(T(866, 322, 'Approve', 13, '#ffffff', 650, 'middle', c=c))
    return svg(W, H, ''.join(b), 'Plan review on both sides: you share the task and see your team’s comments; your teammate finds it under Team, comments on a passage and approves or asks for changes')


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


DRAWINGS = [('routes', routes), ('slices', slices), ('agents', agents), ('team', team), ('peers', peers),
            ('cockpit', cockpit), ('handoff', handoff), ('frame', frame_ill), ('research', research_ill),
            ('diagnose', diagnose_ill), ('checkpoint', checkpoint_ill), ('verify', verify_ill), ('approve', approve_ill),
            ('shipped', shipped_ill), ('quick', quick_ill), ('stopped', stopped_ill), ('abandon', abandon_ill),
            ('install', install_ill), ('firsttask', firsttask_ill), ('settings', settings_ill),
            ('track-plan', track_group('Frame', 'Outline', 'Plan')),
            ('track-build', track_group('Handoff', 'Simplify', 'Build')),
            ('track-check', track_group('Verify', 'Shipped', 'Check and ship')),
            ('cockpit-marked', cockpit_marked), ('outline', outline_ill), ('build', build_ill), ('simplify', simplify_ill),
            ('secondop', secondop_ill), ('files', files_ill), ('privacy', privacy_ill),
            ('team-timeline', team_timeline), ('team-plan', team_plan), ('team-change', team_change),
            ('track-frame', track('Frame')), ('track-research', track('Research')),
            ('track-diagnose', track('Research', 'bug')), ('track-design', track('Design')),
            ('track-outline', track('Outline')), ('track-handoff', track('Handoff')), ('track-slices', track('Build')),
            ('track-checkpoint', track('Checkpoint')), ('track-simplify', track('Simplify')),
            ('track-verify', track('Verify')), ('track-approve', track('Review')), ('track-shipped', track('Shipped')),
            ('track-stopped', track('Verify', stopped=True))]
for name, fn in DRAWINGS:
    for theme, c in THEMES.items():
        with open(os.path.join(OUT, f'{name}-{theme}.svg'), 'w') as f:
            f.write(fn(c))
print('ok')
