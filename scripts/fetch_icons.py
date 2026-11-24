#!/usr/bin/env python3
"""Baja los íconos del stack desde simple-icons (jsDelivr) y los guarda en assets/icons.json.

Necesita red, así que lo corre el workflow. Si un ícono no existe, se omite y la baldosa muestra iniciales.
"""
from __future__ import annotations

import json
import re
import urllib.request

from build_assets import ICONS_CACHE, STACK

URL = "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg"


def main() -> None:
    icons = {}
    try:
        icons = json.loads(ICONS_CACHE.read_text(encoding="utf-8"))
    except Exception:
        pass
    for _, items in STACK:
        for name, slug, _ in items:
            try:
                req = urllib.request.Request(URL.format(slug=slug), headers={"User-Agent": "profile-readme"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    m = re.search(r'<path[^>]*\sd="([^"]+)"', r.read().decode("utf-8"))
                if m:
                    icons[slug] = m.group(1)
                else:
                    print(f"sin path: {name} ({slug})")
            except Exception as e:  # ícono inexistente o sin red: queda el que hubiera, o las iniciales
                print(f"no se pudo bajar {name} ({slug}): {e}")
    ICONS_CACHE.write_text(json.dumps(icons, indent=0, sort_keys=True), encoding="utf-8")
    print(f"{len(icons)} íconos en {ICONS_CACHE}")


if __name__ == "__main__":
    main()
