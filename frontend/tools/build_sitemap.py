#!/usr/bin/env python3
"""
Regenerate sitemap.xml from the pages that actually exist on disk.

The old sitemap was maintained by hand and had drifted: it listed a page that
had been removed and omitted several that existed. Run from ./frontend:

    python3 tools/build_sitemap.py
"""

import os
import re
import glob
import datetime

SITE = "https://pinclip.vercel.app"
EXCLUDE_DIRS = {"admin", "node_modules", "tools"}
EXCLUDE_FILES = {"404.html"}

# Anything not listed here falls back to 0.5 / monthly.
PRIORITY = {
    "/": ("1.0", "weekly"),
    "/pinterest-to-mp4": ("0.9", "monthly"),
    "/download-pinterest-reels": ("0.9", "monthly"),
    "/download-pinterest-video": ("0.9", "monthly"),
    "/blog": ("0.8", "weekly"),
    "/about-us": ("0.5", "yearly"),
    "/contact": ("0.5", "yearly"),
    "/privacy-policy": ("0.3", "yearly"),
    "/cookie-policy": ("0.3", "yearly"),
    "/terms-of-service": ("0.3", "yearly"),
    "/dmca": ("0.3", "yearly"),
    "/disclaimer": ("0.3", "yearly"),
}
BLOG_DEFAULT = ("0.7", "monthly")


def url_for(path):
    slug = os.path.normpath(path)
    if slug == "index.html":
        return "/"
    slug = slug[: -len(".html")]
    if slug.endswith("/index"):
        slug = slug[: -len("/index")]
    return "/" + slug


def is_indexable(path):
    with open(path, "r", encoding="utf-8") as fh:
        head = fh.read(4000)
    return not re.search(r'<meta name="robots"[^>]*content="[^"]*noindex', head)


def main():
    if not os.path.isfile("index.html"):
        raise SystemExit("Run this from the frontend/ directory.")

    entries = []
    for path in sorted(glob.glob("**/*.html", recursive=True)):
        parts = set(os.path.normpath(path).split(os.sep))
        if parts & EXCLUDE_DIRS or os.path.basename(path) in EXCLUDE_FILES:
            continue
        if not is_indexable(path):
            print("skipping noindex page: %s" % path)
            continue
        loc = url_for(path)
        priority, freq = PRIORITY.get(loc, BLOG_DEFAULT if loc.startswith("/blog/") else ("0.5", "monthly"))
        lastmod = datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
        entries.append((loc, lastmod, freq, priority))

    entries.sort(key=lambda e: (-float(e[3]), e[0]))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod, freq, priority in entries:
        full = SITE + "/" if loc == "/" else SITE + loc
        lines += [
            "  <url>",
            "    <loc>%s</loc>" % full,
            "    <lastmod>%s</lastmod>" % lastmod,
            "    <changefreq>%s</changefreq>" % freq,
            "    <priority>%s</priority>" % priority,
            "  </url>",
        ]
    lines.append("</urlset>")

    with open("sitemap.xml", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("sitemap.xml written with %d URLs" % len(entries))


if __name__ == "__main__":
    main()
