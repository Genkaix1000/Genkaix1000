#!/usr/bin/env python3
"""Genera assets/activity-{dark,light}.svg con datos reales de GitHub y los inserta en el README.

Lo corre el workflow .github/workflows/stats.yml. Necesita GITHUB_TOKEN en el entorno.
Con el token por defecto del workflow solo se ven contribuciones y repos públicos; para incluir
los privados, creá un token personal (scopes: read:user, repo) y guardalo como secret STATS_TOKEN.

Prueba local sin red:  python3 scripts/stats.py --mock
"""
from __future__ import annotations

import datetime as dt
import json
import os
import random
import sys
import urllib.request
from html import escape
from pathlib import Path

from build_assets import OUT, THEMES, cham, mono_w, svg

LOGIN = os.environ.get("STATS_LOGIN", "Genkaix1000")
README = OUT.parent / "README.md"
START, END = "<!--STATS:START-->", "<!--STATS:END-->"

QUERY = """query($login:String!){user(login:$login){
 repositories(first:100,ownerAffiliations:OWNER,isFork:false){totalCount nodes{languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 contributionsCollection{totalCommitContributions totalPullRequestContributions
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch() -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise SystemExit(f"GitHub API: {payload['errors']}")
    return payload["data"]["user"]


def mock() -> dict:
    rnd = random.Random(3)
    start = dt.date(2025, 11, 23)
    days = [{"date": str(start + dt.timedelta(d)), "contributionCount": max(0, int(rnd.gauss(3, 5)))} for d in range(371)]
    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, 371, 7)]
    langs = [("TypeScript", 900), ("PLpgSQL", 160), ("Lua", 120), ("CSS", 90), ("Dart", 60), ("JavaScript", 40), ("HTML", 20)]
    return {"repositories": {"totalCount": 24, "nodes": [{"languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in langs]}}]},
            "contributionsCollection": {"totalCommitContributions": 1432, "totalPullRequestContributions": 87,
                                        "contributionCalendar": {"totalContributions": sum(d["contributionCount"] for d in days), "weeks": weeks}}}


def streaks(days: list[dict]) -> tuple[int, int]:
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] else 0
        best = max(best, cur)
    tail = days[:-1] if days and not days[-1]["contributionCount"] else days  # hoy todavía puede sumar
    current = 0
    for d in reversed(tail):
        if not d["contributionCount"]:
            break
        current += 1
    return current, best


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def card(user: dict, t: dict) -> str:
    W = 840
    cc = user["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"][-53:]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, best = streaks(days)
    stats = [("CONTRIBUCIONES · 12 MESES", fmt(cc["contributionCalendar"]["totalContributions"])),
             ("COMMITS", fmt(cc["totalCommitContributions"])),
             ("PULL REQUESTS", fmt(cc["totalPullRequestContributions"])),
             ("RACHA ACTUAL", f"{current} d"), ("RACHA MÁS LARGA", f"{best} d"),
             ("REPOS", fmt(user["repositories"]["totalCount"]))]
    body = f'<path d="CHAM" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    xs = [28, 262, 372, 508, 624, 760]
    for x, (label, value) in zip(xs, stats):
        body += (f'<text x="{x}" y="50" font-size="26" font-weight="800" fill="{t["ink"]}">{value}</text>'
                 f'<text x="{x}" y="70" font-size="9.5" font-weight="600" letter-spacing="1" fill="{t["muted"]}">{label}</text>')
    # heatmap
    counts = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]
    x0, y0, step = (W - len(weeks) * 14) // 2 + 1, 96, 14
    for wi, w in enumerate(weeks):
        cells = ""
        for d in w["contributionDays"]:
            n = d["contributionCount"]
            di = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            if n == 0:
                cells += f'<rect x="{x0 + wi * step}" y="{y0 + di * step}" width="11" height="11" rx="2" fill="{t["faint"]}"/>'
            else:
                op = (0.35, 0.55, 0.78, 1)[sum(n > v for v in q)]
                cells += f'<rect x="{x0 + wi * step}" y="{y0 + di * step}" width="11" height="11" rx="2" fill="{t["accent"]}" opacity="{op}"/>'
        body += f'<g class="wave" style="animation-delay:{-(len(weeks) - wi) * 0.09:.2f}s">{cells}</g>'
    # lenguajes
    sizes: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    y = y0 + 7 * step + 26
    body += f'<text x="28" y="{y}" font-size="9.5" font-weight="600" letter-spacing="1" fill="{t["muted"]}">LENGUAJES EN MIS REPOS</text>'
    y += 12
    x, bar_w, segs, legend, lx = 28.0, W - 56, "", "", 28.0
    for i, (name, size) in enumerate(top):
        w = bar_w * size / total
        op = max(0.22, 1 - i * 0.16)
        segs += f'<rect x="{x:.1f}" y="{y}" width="{max(w - 2, 1):.1f}" height="10" rx="3" fill="{t["accent"]}" opacity="{op:.2f}"/>'
        x += w
        text = f"{name} {100 * size / total:.0f}%"
        legend += (f'<rect x="{lx:.1f}" y="{y + 23}" width="9" height="9" rx="2" fill="{t["accent"]}" opacity="{op:.2f}"/>'
                   f'<text class="m" x="{lx + 15:.1f}" y="{y + 31}" font-size="10.5" fill="{t["ink"]}">{escape(text)}</text>')
        lx += mono_w(text, 10.5) + 34
    body += f'<g class="grow">{segs}</g>{legend}'
    H = y + 50
    label = "Actividad en GitHub: " + ", ".join(f"{l.lower()} {v}" for l, v in stats)
    return svg(W, H, label, body.replace("CHAM", cham(.5, .5, W - 1, H - 1, 16)))


def main() -> None:
    user = mock() if "--mock" in sys.argv else fetch()
    for name, t in THEMES.items():
        (OUT / f"activity-{name}.svg").write_text(card(user, t), encoding="utf-8")
    if "--mock" in sys.argv:
        return
    block = (f"{START}\n## Actividad\n\n"
             '<picture><source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg"/>'
             '<source media="(prefers-color-scheme: light)" srcset="assets/activity-light.svg"/>'
             '<img src="assets/activity-light.svg" width="100%" alt="Actividad en GitHub: contribuciones del último año, rachas y lenguajes"/></picture>\n\n'
             "<sub>Datos reales de GitHub, actualizados una vez por día por un workflow de este repo.</sub>\n"
             f"{END}")
    text = README.read_text(encoding="utf-8")
    a, b = text.index(START), text.index(END) + len(END)
    README.write_text(text[:a] + block + text[b:], encoding="utf-8")


if __name__ == "__main__":
    main()
