#!/usr/bin/env python3
"""Genera los SVG animados del README de perfil (assets/*-dark.svg y *-light.svg).

Uso:  python3 scripts/build_assets.py
Para cambiar un proyecto, el stack o un contacto, editá las listas de abajo y volvé a correrlo.
Sin dependencias: solo la librería estándar.
"""
from __future__ import annotations

import base64
import math
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
PORTRAIT = OUT / "portrait.jpg"  # recorte 4:5 de la foto del portfolio
DISPLAY_FONT = Path("/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf")  # opcional: si no está, el nombre sale como texto

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": dict(bg="#111514", panel="#171c1a", line="#2b332f", ink="#e8ece8", muted="#9ea49f",
                 accent="#8fb39c", soft="#c5d4c8", ok="#5fbf87", warn="#d9a441", faint="#1f2623"),
    "light": dict(bg="#f6f5f0", panel="#ffffff", line="#d6d5cc", ink="#151a18", muted="#5d655f",
                  accent="#4f6f5c", soft="#6f8f7c", ok="#2f8f5b", warn="#a8741a", faint="#ebeae3"),
}

# ----------------------------------------------------------------------------- contenido

PROJECTS = [
    dict(id="miboliche", name="miBoliche", status="prod", label="Bosko Nightclub · desde julio de 2026", motif="eq",
         desc=["POS y pedidos por QR para boliches: carta digital, barra en vivo, caja",
               "y cobros. Cerca de 1.000 pedidos por noche en eventos pico."],
         chips=["Next.js", "SSE", "Postgres", "Mercado Pago"]),
    dict(id="arbos", name="ARBOS", status="prod", label="arbos.ar · tienda online", motif="spray",
         desc=["E-commerce de perfumes con catálogo, combos y bolsa, más un dashboard",
               "privado para stock, insumos, pedidos, ventas y gastos."],
         chips=["Next.js 16", "Supabase", "GSAP", "Playwright"]),
    dict(id="pedilo", name="Pedilo", status="dev", label="Delivery", motif="route",
         desc=["Delivery local para Bolívar: app del consumidor,",
               "panel del negocio con comandera en tiempo real",
               "y bot de pedidos por WhatsApp con IA."],
         chips=["Next.js 16", "Supabase", "Turborepo", "Docker"]),
    dict(id="ticketera", name="Ticketera QR", status="dev", label="Ticketing", motif="qr",
         desc=["Entradas para eventos: reserva atómica de stock,",
               "webhook de pagos idempotente, QR firmado con",
               "HMAC y check-in atómico en portería."],
         chips=["Next.js", "Supabase", "Mercado Pago", "Zod"]),
    dict(id="market", name="Pedilo Market", status="demo", label="Marketplace · demo", motif="bids",
         desc=["Marketplace por localidades con pujas en vivo.",
               "Demo web; el objetivo es una app nativa",
               "para Android y iOS."],
         chips=["Next.js 16", "React 19", "Tailwind v4"]),
    dict(id="inmo", name="Bolívar Inmo", status="dev", label="Portal inmobiliario", motif="pin",
         desc=["Portal inmobiliario de la ciudad: las propiedades",
               "de todas las inmobiliarias en un solo lugar,",
               "con mapa. Mobile primero."],
         chips=["Next.js 16", "MapLibre", "Base UI", "Supabase"]),
    dict(id="ventapro", name="VentaPro", status="dev", label="Punto de venta", motif="barcode",
         desc=["POS y gestión para kioscos y supermercados:",
               "corre local en la PC del comercio, con escaneo",
               "por cámara y consulta desde el celular."],
         chips=["React", "Vite", "TypeScript", "Supabase"]),
    dict(id="mora", name="Mora", status="demo", label="Gobierno · demo", motif="chart",
         desc=["SaaS de gestión de mora y cobranza municipal:",
               "panel de administración y portal del vecino,",
               "con datos sintéticos."],
         chips=["Next.js", "TypeScript", "SDD"]),
    dict(id="auditoria", name="Auditoría Actual Online", status="case", label="Responsible disclosure",
         motif="shield",
         desc=["Hallazgo en la superficie pública, contacto con la",
               "empresa y auditoría autorizada: 22 hallazgos,",
               "re-auditoría y plan de remediación."],
         chips=["API security", "OWASP", "Auth"]),
    dict(id="bridge-panel", name="Bridge Panel", status="tool", label="Herramienta interna", motif="calendar",
         desc=["Calendario interno del equipo: reuniones,",
               "deadlines y timeline por proyecto. PWA pensada",
               "para usarse con una mano desde el celular."],
         chips=["Vite", "React", "Motion", "Supabase"]),
]

CONTACTS = [
    dict(id="portfolio", label="PORTFOLIO", value="matiasasin.is-a.dev"),
    dict(id="linkedin", label="LINKEDIN", value="in/matias-asin"),
    dict(id="email", label="EMAIL", value="matiasasin123@gmail.com"),
    dict(id="whatsapp", label="WHATSAPP", value="+54 9 11 7062-3866"),
]

STACK = [
    ("FRONTEND", ["Next.js", "React", "TypeScript", "Tailwind CSS", "Motion", "GSAP", "Vite", "Flutter", "PWA"]),
    ("BACKEND Y DATOS", ["Node.js", "Supabase", "PostgreSQL", "SQL", "Row Level Security", "Java · Spring", "Zod"]),
    ("PAGOS E INTEGRACIONES", ["Mercado Pago Checkout Pro", "Webhooks", "SSE", "Realtime", "WhatsApp Cloud API"]),
    ("TESTING E INFRA", ["Playwright", "Vitest", "GitHub Actions", "Docker", "Vercel", "Caddy", "Linux", "Turborepo"]),
    ("SEGURIDAD Y REDES", ["Auditoría de APIs", "OWASP Top 10", "Auth / RBAC", "TCP/IP · DNS", "Redes Wi-Fi"]),
    ("DISEÑO", ["Figma", "Penpot", "Photoshop", "Illustrator", "Identidad visual", "UI / UX", "Motion"]),
]

STEPS = ["Brief", "Spec", "Código", "Tests", "Producción", "Soporte"]
ROLES = ["Full Stack", "Frontend", "Diseño", "Data", "Pagos", "Seguridad"]
FEATURED = {"miboliche", "arbos"}

# ----------------------------------------------------------------------------- helpers

KEYFRAMES = """
@keyframes ping{0%{transform:scale(1);opacity:.7}80%,100%{transform:scale(2.8);opacity:0}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes flow{to{stroke-dashoffset:-24}}
@keyframes blink{50%{opacity:0}}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes bar{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}
@keyframes nudge{0%,100%{transform:translate(0,0)}50%{transform:translate(3px,-3px)}}
@keyframes scany{0%,100%{transform:translateY(0)}50%{transform:translateY(40px)}}
@keyframes scanx{0%,100%{transform:translateX(0)}50%{transform:translateX(78px)}}
@keyframes draw{0%{stroke-dashoffset:160}55%,100%{stroke-dashoffset:0}}
@keyframes spray{0%{transform:translate(0,0);opacity:0}15%{opacity:1}100%{transform:translate(34px,-14px);opacity:0}}
@keyframes rise{0%,15%{transform:scaleY(0)}45%,85%{transform:scaleY(1)}100%{transform:scaleY(0)}}
@keyframes cell{0%,100%{opacity:.18}50%{opacity:1}}
@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(-6px,5px)}}
@keyframes word{0%{opacity:0;transform:translateY(10px)}2.5%,14%{opacity:1;transform:none}16.6%,100%{opacity:0;transform:translateY(-10px)}}
@keyframes sheen{0%{transform:translateX(-140px)}60%,100%{transform:translateX(900px)}}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}
.float{animation:float 4s ease-in-out infinite}
.flow{stroke-dasharray:4 4;animation:flow 1.2s linear infinite}
.blink{animation:blink 1.1s steps(1) infinite}
.tw{animation:tw 3.6s ease-in-out infinite}
.bar{transform-box:fill-box;transform-origin:bottom;animation:bar 1.3s ease-in-out infinite}
.nudge{animation:nudge 2.2s ease-in-out infinite}
.scany{animation:scany 3s ease-in-out infinite}
.scanx{animation:scanx 3.2s ease-in-out infinite}
.draw{stroke-dasharray:160;animation:draw 4s ease-out infinite}
.spray{animation:spray 2.2s ease-out infinite}
.rise{transform-box:fill-box;transform-origin:bottom;animation:rise 4s ease-in-out infinite}
.cell{animation:cell 3s ease-in-out infinite}
.drift{animation:drift 14s ease-in-out infinite}
.word{opacity:0;animation:word 18s cubic-bezier(.16,1,.3,1) infinite}
.sheen{animation:sheen 7s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.45}}
@keyframes grow{0%{transform:scaleX(0)}25%,100%{transform:scaleX(1)}}
.wave{animation:wave 5s ease-in-out infinite}
.grow{transform-box:fill-box;transform-origin:left;animation:grow 8s cubic-bezier(.3,.7,.2,1) infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.word{opacity:0}.w0{opacity:1}}
"""


def svg(w: int, h: int, label: str, body: str) -> str:
    lab = escape(label, quote=True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{lab}"><title>{lab}</title><style>'
            f'text{{font-family:{SANS}}}.m{{font-family:{MONO}}}{KEYFRAMES}</style>{body}</svg>\n')


def mono_w(text: str, size: float) -> float:
    return len(text) * size * 0.6


def cham(x: float, y: float, w: float, h: float, c: float) -> str:
    """Rectángulo con dos esquinas en chaflán (arriba-izquierda y abajo-derecha), como el retrato del portfolio."""
    return f"M{x + c} {y}H{x + w}V{y + h - c}L{x + w - c} {y + h}H{x}V{y + c}Z"


def chip(x: float, y: float, text: str, t: dict, size: float = 10.5) -> tuple[str, float]:
    w = mono_w(text, size) + 16
    s = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="22" rx="2" fill="{t["faint"]}" stroke="{t["line"]}"/>'
         f'<text class="m" x="{x + 8:.1f}" y="{y + 15}" font-size="{size}" fill="{t["muted"]}">{escape(text)}</text>')
    return s, w


def text_path(text: str, size: float, x: float, y: float, fill: str, tracking: float = -0.02) -> str | None:
    """Convierte texto a contornos con la tipografía display, para que se vea igual en cualquier sistema."""
    try:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        from fontTools.ttLib import TTFont
        font = TTFont(DISPLAY_FONT)
    except Exception:
        return None
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
    k, cx, out = size / upm, x, ""
    for ch in text:
        g = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs)
        g.draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        out += pen.getCommands()
        cx += g.width * k + tracking * size
    return f'<path d="{out}" fill="{fill}"/>'


# ----------------------------------------------------------------------------- motifs (caja 96x56)

def motif(kind: str, t: dict) -> str:
    a, m, l = t["accent"], t["muted"], t["line"]
    rnd = random.Random(kind)
    if kind == "eq":
        return "".join(
            f'<rect class="bar" style="animation-delay:{-i * 0.19:.2f}s" x="{6 + i * 12}" y="6" width="6" height="44" rx="3" fill="{a}"/>'
            for i in range(8))
    if kind == "spray":
        bottle = (f'<rect x="10" y="22" width="26" height="30" rx="5" fill="none" stroke="{a}" stroke-width="1.6"/>'
                  f'<rect x="18" y="12" width="10" height="10" rx="2" fill="{a}"/>'
                  f'<path d="M14 36h18" stroke="{l}" stroke-width="1.4"/>')
        dots = "".join(
            f'<circle class="spray" style="animation-delay:{-i * 0.44:.2f}s" cx="{36 + (i % 2) * 4}" cy="{15 + (i % 3) * 4}" r="{1.6 + (i % 2) * 0.8}" fill="{a}"/>'
            for i in range(5))
        return bottle + dots
    if kind == "route":
        path = "M8 46 C 26 46, 26 14, 48 14 S 70 40, 88 22"
        return (f'<path d="{path}" fill="none" stroke="{m}" stroke-width="1.6" class="flow"/>'
                f'<circle cx="8" cy="46" r="3.5" fill="{l}" stroke="{m}"/>'
                f'<circle class="ping" cx="88" cy="22" r="4" fill="{a}"/><circle cx="88" cy="22" r="4" fill="{a}"/>'
                f'<circle r="3.2" fill="{t["ink"]}"><animateMotion dur="3.6s" repeatCount="indefinite" path="{path}"/></circle>')
    if kind == "qr":
        cells = ""
        for r in range(6):
            for c in range(6):
                corner = (r < 2 and c < 2) or (r < 2 and c > 3) or (r > 3 and c < 2)
                if corner or rnd.random() < 0.5:
                    cells += f'<rect x="{24 + c * 8}" y="{4 + r * 8}" width="6" height="6" rx="1" fill="{a if corner else m}"/>'
        return cells + f'<rect class="scany" x="18" y="5" width="60" height="2" rx="1" fill="{t["ink"]}"/>'
    if kind == "bids":
        hs = [14, 22, 30, 40, 48]
        bars = "".join(
            f'<rect class="rise" style="animation-delay:{i * 0.22:.2f}s" x="{10 + i * 16}" y="{52 - h}" width="10" height="{h}" rx="2" fill="{a if i == 4 else m}"/>'
            for i, h in enumerate(hs))
        return bars + f'<path d="M4 53h88" stroke="{l}" stroke-width="1.4"/>'
    if kind == "pin":
        grid = "".join(f'<path d="M{8 + i * 20} 6v46" stroke="{l}"/>' for i in range(5))
        grid += "".join(f'<path d="M4 {12 + i * 16}h88" stroke="{l}"/>' for i in range(3))
        return (grid + f'<path d="M14 44 L40 30 L62 40 L86 18" fill="none" stroke="{m}" stroke-width="1.4" class="flow"/>'
                f'<circle class="ping" cx="50" cy="42" r="4" fill="{a}"/>'
                f'<g class="float"><path d="M50 42 C 40 28, 40 16, 50 16 S 60 28, 50 42Z" fill="{a}"/>'
                f'<circle cx="50" cy="25" r="3.4" fill="{t["panel"]}"/></g>')
    if kind == "barcode":
        x, out = 8, ""
        while x < 86:
            w = rnd.choice([1.5, 1.5, 3, 4.5])
            out += f'<rect x="{x:.1f}" y="8" width="{w}" height="40" fill="{m}"/>'
            x += w + rnd.choice([2, 3, 4])
        return out + f'<rect class="scanx" x="6" y="4" width="2.5" height="48" rx="1" fill="{a}"/>'
    if kind == "chart":
        return (f'<path d="M6 52h86M6 52V6" stroke="{l}" stroke-width="1.4" fill="none"/>'
                f'<path class="draw" d="M8 44 L24 38 L38 42 L54 26 L68 30 L88 10" fill="none" stroke="{a}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<circle class="ping" cx="88" cy="10" r="3.5" fill="{a}"/><circle cx="88" cy="10" r="3.5" fill="{a}"/>')
    if kind == "shield":
        return (f'<circle class="ping" cx="48" cy="28" r="12" fill="none" stroke="{a}" stroke-width="1.5"/>'
                f'<circle class="ping" style="animation-delay:-1.2s" cx="48" cy="28" r="12" fill="none" stroke="{a}" stroke-width="1.5"/>'
                f'<path d="M48 6 L66 13 V28 C66 40 58 48 48 52 C38 48 30 40 30 28 V13Z" fill="{t["panel"]}" stroke="{a}" stroke-width="1.8"/>'
                f'<path d="M40 28 l6 6 l11 -12" fill="none" stroke="{a}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "calendar":
        out = f'<rect x="12" y="4" width="72" height="48" rx="6" fill="none" stroke="{l}" stroke-width="1.4"/><path d="M12 15h72" stroke="{l}" stroke-width="1.4"/>'
        hot = {(0, 2), (1, 4), (2, 1), (1, 0), (2, 5)}
        for r in range(3):
            for c in range(6):
                if (r, c) in hot:
                    out += f'<rect class="cell" style="animation-delay:{-(r * 6 + c) * 0.37:.2f}s" x="{18 + c * 10.5:.1f}" y="{20 + r * 10}" width="7" height="7" rx="2" fill="{a}"/>'
                else:
                    out += f'<rect x="{18 + c * 10.5:.1f}" y="{20 + r * 10}" width="7" height="7" rx="2" fill="{t["faint"]}" stroke="{l}" stroke-width=".6"/>'
        return out
    raise ValueError(kind)


# ----------------------------------------------------------------------------- piezas

def project_card(p: dict, t: dict) -> str:
    big = p["id"] in FEATURED
    W, H = (840, 204) if big else (412, 196)
    body = f'<path d="{cham(.5, .5, W - 1, H - 1, 16)}" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    body += (f'<text x="{28 if big else 22}" y="{42 if big else 36}" font-size="10.5" font-weight="600" '
             f'letter-spacing="1.3" fill="{t["accent"]}">{escape(p["label"].upper())}</text>')
    if big:
        body += f'<g transform="translate(606,42) scale(2.05)">{motif(p["motif"], t)}</g>'
        body += f'<text x="28" y="88" font-size="32" font-weight="800" letter-spacing="-.6" fill="{t["ink"]}">{escape(p["name"])}</text>'
        x0, y0, fs, lh, cy = 28, 114, 14, 20, 162
    else:
        body += f'<g transform="translate(296,14)">{motif(p["motif"], t)}</g>'
        body += f'<text x="22" y="80" font-size="21" font-weight="700" letter-spacing="-.2" fill="{t["ink"]}">{escape(p["name"])}</text>'
        x0, y0, fs, lh, cy = 22, 103, 12.5, 18, 156
    for i, line in enumerate(p["desc"]):
        body += f'<text x="{x0}" y="{y0 + i * lh}" font-size="{fs}" fill="{t["muted"]}">{escape(line)}</text>'
    x = float(x0)
    for ch in p["chips"]:
        s, w = chip(x, cy, ch, t, 10)
        body += s
        x += w + 6
    assert x < W - 14, (p["id"], x)
    label = f'{p["name"]} ({p["label"]}): {" ".join(p["desc"])} Stack: {", ".join(p["chips"])}.'
    return svg(W, H, label, body)


def contact_button(cdata: dict, t: dict) -> str:
    W, H = 412, 66
    body = (f'<path d="{cham(.5, .5, W - 1, H - 1, 12)}" fill="{t["panel"]}" stroke="{t["line"]}"/>'
            f'<text x="22" y="27" font-size="10" font-weight="600" letter-spacing="1.3" fill="{t["muted"]}">{cdata["label"]}</text>'
            f'<text x="22" y="48" font-size="15" font-weight="600" fill="{t["ink"]}">{escape(cdata["value"])}</text>'
            f'<g class="nudge"><path d="M{W - 44} 40 L{W - 30} 26 M{W - 40} 26 H{W - 30} V36" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linecap="square"/></g>')
    return svg(W, H, f'{cdata["label"].title()}: {cdata["value"]}', body)


def hero(t: dict) -> str:
    W, H = 840, 330
    rnd = random.Random(11)
    px, py, pw, ph = 590, 35, 208, 260  # retrato 4:5
    body = (f'<defs><clipPath id="hc"><path d="{cham(1, 1, W - 2, H - 2, 22)}"/></clipPath>'
            f'<clipPath id="pc"><path d="{cham(px, py, pw, ph, 24)}"/></clipPath>'
            f'<clipPath id="wipe"><rect x="{px}" y="{py}" width="0" height="{ph}">'
            f'<animate attributeName="width" dur="11s" repeatCount="indefinite" calcMode="spline" '
            f'values="0;0;{pw};{pw};0;0" keyTimes="0;.3;.44;.72;.86;1" '
            f'keySplines="0 0 1 1;.16 1 .3 1;0 0 1 1;.16 1 .3 1;0 0 1 1"/></rect></clipPath>'
            f'<filter id="bw"><feColorMatrix type="saturate" values="0"/>'
            f'<feComponentTransfer><feFuncR type="linear" slope="1.1" intercept="-.05"/><feFuncG type="linear" slope="1.1" intercept="-.05"/>'
            f'<feFuncB type="linear" slope="1.1" intercept="-.05"/></feComponentTransfer></filter></defs>')
    body += f'<path d="{cham(.5, .5, W - 1, H - 1, 22)}" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    # constelación, por detrás del retrato
    pts = []
    while len(pts) < 20:
        x, y = rnd.uniform(430, 824), rnd.uniform(22, 308)
        inside = px - 6 < x < px + pw + 6 and py - 6 < y < py + ph + 6
        if not inside and all(math.hypot(x - qx, y - qy) > 40 for qx, qy in pts):
            pts.append((x, y))
    lines = stars = ""
    for i, (x, y) in enumerate(pts):
        near = sorted((math.hypot(x - qx, y - qy), j) for j, (qx, qy) in enumerate(pts) if j != i)[:2]
        for d, j in near:
            if j > i and d < 170:
                qx, qy = pts[j]
                lines += f'<path d="M{x:.0f} {y:.0f}L{qx:.0f} {qy:.0f}" stroke="{t["line"]}" stroke-width="1.2"/>'
        big = i % 4 == 0
        stars += (f'<circle class="tw" style="animation-delay:{-i * 0.41:.2f}s" cx="{x:.0f}" cy="{y:.0f}" '
                  f'r="{3.4 if big else 2.1}" fill="{t["accent"] if big else t["muted"]}"/>')
    body += f'<g clip-path="url(#hc)"><g class="drift">{lines}{stars}</g></g>'
    # retrato: gris como en el sitio, con un barrido que revela el color
    if PORTRAIT.exists():
        b64 = base64.b64encode(PORTRAIT.read_bytes()).decode()
        img = f'x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMid slice"'
        body += (f'<g clip-path="url(#pc)"><image id="ph" {img} href="data:image/jpeg;base64,{b64}" filter="url(#bw)"/>'
                 f'<g clip-path="url(#wipe)"><image {img} href="data:image/jpeg;base64,{b64}"/></g></g>')
    body += f'<path d="{cham(px, py, pw, ph, 24)}" fill="none" stroke="{t["line"]}"/>'
    # marcas de corte de imprenta en las esquinas del retrato
    marks = ""
    for i, (cx, cy, sx, sy) in enumerate([(px + pw, py, 1, -1), (px, py + ph, -1, 1)]):
        marks += (f'<path class="tw" style="animation-delay:{-i * 1.8:.1f}s" d="M{cx + sx * 8} {cy}h{sx * 14}M{cx} {cy + sy * 8}v{sy * 14}" '
                  f'stroke="{t["accent"]}" stroke-width="1.4"/>')
    body += marks
    # texto
    name = text_path("Matías Asin", 60, 40, 108, t["ink"])
    body += name or f'<text x="42" y="108" font-size="58" font-weight="800" letter-spacing="-1.6" fill="{t["ink"]}">Matías Asin</text>'
    body += f'<text x="44" y="148" font-size="18" fill="{t["muted"]}">Software Engineer</text>'
    n = len(ROLES)
    for i, r in enumerate(ROLES):
        body += (f'<text class="word w{i}" style="animation-delay:{i * 18 / n:.1f}s" x="44" y="184" '
                 f'font-size="25" font-weight="700" letter-spacing="-.3" fill="{t["accent"]}">{escape(r)}</text>')
    body += f'<text x="44" y="238" font-size="17" fill="{t["ink"]}">Sistemas claros para problemas que no lo son.</text>'
    body += f'<text x="44" y="262" font-size="13.5" fill="{t["muted"]}">Producto de punta a punta, con frontend y diseño cuidados al detalle.</text>'
    body += f'<text x="44" y="296" font-size="11" font-weight="600" letter-spacing="1.3" fill="{t["muted"]}">BOLÍVAR, BUENOS AIRES · ARGENTINA</text>'
    return svg(W, H, "Matías Asin, Software Engineer: full stack, frontend y diseño. Bolívar, Buenos Aires, Argentina. "
                     "Sistemas claros para problemas que no lo son.", body)


def process(t: dict) -> str:
    W, H = 840, 112
    body = f'<path d="{cham(.5, .5, W - 1, H - 1, 16)}" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    xs = [70 + i * 140 for i in range(len(STEPS))]
    y = 46
    body += f'<path class="flow" d="M{xs[0]} {y}H{xs[-1]}" stroke="{t["muted"]}" stroke-width="1.6" fill="none"/>'
    body += (f'<rect width="8" height="8" y="{y - 4}" fill="{t["accent"]}"><animate attributeName="x" values="{xs[0] - 4};{xs[-1] - 4}" '
             f'dur="6s" repeatCount="indefinite"/></rect>')
    for i, (x, s) in enumerate(zip(xs, STEPS)):
        col = t["accent"] if i == len(STEPS) - 2 else t["line"]
        body += f'<rect x="{x - 14}" y="{y - 14}" width="28" height="28" rx="2" fill="{t["panel"]}" stroke="{col}" stroke-width="1.6"/>'
        body += f'<text class="m" x="{x}" y="{y + 4}" font-size="10.5" text-anchor="middle" fill="{t["muted"]}">{i + 1:02d}</text>'
        body += f'<text x="{x}" y="{y + 42}" font-size="13" font-weight="600" text-anchor="middle" fill="{t["ink"]}">{escape(s)}</text>'
    return svg(W, H, "Cómo trabajo: " + " → ".join(STEPS), body)


def stack(t: dict) -> str:
    W = 840
    x0, right = 214, W - 20
    y = 24
    rows = ""
    for gi, (label, items) in enumerate(STACK):
        rows += f'<text x="26" y="{y + 15}" font-size="10.5" font-weight="600" letter-spacing="1.3" fill="{t["accent"]}">{escape(label)}</text>'
        x = x0
        for it in items:
            w = mono_w(it, 11) + 16
            if x + w > right:
                x, y = x0, y + 28
            s, w = chip(x, y, it, t, 11)
            rows += s
            x += w + 6
        y += 28
        if gi < len(STACK) - 1:
            rows += f'<path d="M26 {y + 3}H{W - 26}" stroke="{t["line"]}"/>'
            y += 14
    H = y + 16
    clip = f'<clipPath id="c"><path d="{cham(1, 1, W - 2, H - 2, 16)}"/></clipPath>'
    sheen = (f'<g clip-path="url(#c)"><rect class="sheen" x="0" y="0" width="120" height="{H}" fill="{t["accent"]}" '
             f'opacity=".07" transform="skewX(-18)"/></g>')
    body = f'{clip}<path d="{cham(.5, .5, W - 1, H - 1, 16)}" fill="{t["bg"]}" stroke="{t["line"]}"/>{rows}{sheen}'
    label = "Stack: " + "; ".join(f"{g.title()}: {', '.join(i)}" for g, i in STACK)
    return svg(W, H, label, body)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        files = {"hero": hero(t), "process": process(t), "stack": stack(t)}
        files.update({f"project-{p['id']}": project_card(p, t) for p in PROJECTS})
        files.update({f"contact-{c['id']}": contact_button(c, t) for c in CONTACTS})
        for stem, content in files.items():
            (OUT / f"{stem}-{name}.svg").write_text(content, encoding="utf-8")
    print(f"{len(list(OUT.glob('*.svg')))} SVG en {OUT}")


if __name__ == "__main__":
    main()
