#!/usr/bin/env python3
"""
Normalize the shared <head> / <body> boilerplate across every public HTML page.

Idempotent: safe to re-run after editing any page. Run from ./frontend:

    python3 tools/normalize_pages.py

What it guarantees on every public page:
  * Google Consent Mode v2 defaults set BEFORE the AdSense tag loads
  * the AdSense tag itself
  * a meta description, canonical, robots, author and theme-color tag
  * Open Graph + Twitter Card tags
  * an accessible "skip to content" link and <main id="main">
  * the cookie consent banner script

Replaces the old add_adsense.py, which hardcoded an absolute path.
"""

import os
import re
import sys
import glob

SITE_URL = "https://pinclip.vercel.app"  # <- change here if you move to a custom domain
ADSENSE_CLIENT = "ca-pub-7120148790304596"
OG_IMAGE = SITE_URL + "/assets/og-image.png"

# Pages that must never be indexed or carry ads.
EXCLUDE_DIRS = {"admin", "node_modules", "tools"}

# Fallback descriptions for pages that lack one.
DESCRIPTIONS = {
    "privacy-policy.html": (
        "PinClip's privacy policy: what data we collect, how cookies and Google AdSense "
        "are used, your GDPR and CCPA rights, and how to contact us."
    ),
    "terms-of-service.html": (
        "The terms and conditions that govern your use of PinClip's free Pinterest video "
        "downloader, including acceptable use and copyright obligations."
    ),
    "disclaimer.html": (
        "PinClip's disclaimer: we do not host or store any videos, and users are "
        "responsible for respecting copyright when downloading Pinterest content."
    ),
}

CONSENT_SNIPPET = """    <!-- Google Consent Mode v2 — must run before any Google tag -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      (function(){
        var stored = null;
        try { stored = localStorage.getItem('pinclip_consent'); } catch (e) {}
        var state = stored === 'granted' ? 'granted' : 'denied';
        gtag('consent', 'default', {
          ad_storage: state,
          ad_user_data: state,
          ad_personalization: state,
          analytics_storage: state,
          functionality_storage: 'granted',
          security_storage: 'granted',
          wait_for_update: 500
        });
      })();
    </script>
"""

ADSENSE_SNIPPET = (
    '    <!-- Google AdSense -->\n'
    '    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
    '?client=%s" crossorigin="anonymous"></script>\n' % ADSENSE_CLIENT
)

SKIP_LINK = '    <a href="#main" class="skip-link">Skip to main content</a>\n'
CONSENT_SCRIPT_TAG = '    <script src="%s/assets/js/consent.js" defer></script>\n'
SITE_SCRIPT_TAG = '    <script src="%s/assets/js/site.js" defer></script>\n'

# Canonical navigation. Every page gets exactly this header and footer so the
# site reads as one coherent product rather than a pile of landing pages.
NAV = [
    ("/", "Home"),
    ("/pinterest-to-mp4", "MP4 Converter"),
    ("/download-pinterest-reels", "Reels"),
    ("/blog", "Blog"),
    ("/about-us", "About"),
]

HEADER = """    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <a href="/" class="flex items-center gap-2" aria-label="PinClip home">
                    <img src="/favicon.png" alt="" width="32" height="32" class="h-8 w-8 rounded">
                    <span class="font-bold text-xl tracking-tight text-dark">PinClip</span>
                </a>
                <nav class="hidden md:flex space-x-7" aria-label="Main navigation">
%(desktop)s
                </nav>
                <button id="mobileMenuBtn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu" class="md:hidden text-gray-600 hover:text-pinterest focus:outline-none focus:ring-2 focus:ring-pinterest rounded">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
            </div>
        </div>
        <div id="mobileMenu" class="md:hidden hidden bg-white border-t border-gray-100 shadow-lg absolute w-full left-0">
            <nav class="px-4 py-3 space-y-2 pb-4" aria-label="Mobile navigation">
%(mobile)s
            </nav>
        </div>
    </header>"""

FOOTER = """    <footer class="bg-dark text-white py-12 mt-auto">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 grid md:grid-cols-4 gap-8">
            <div>
                <div class="flex items-center gap-2 mb-4">
                    <img src="/favicon.png" alt="" width="24" height="24" class="h-6 w-6 rounded">
                    <span class="font-bold text-lg tracking-tight">PinClip</span>
                </div>
                <p class="text-gray-400 text-sm mb-4">PinClip is a free online tool that saves public Pinterest videos as standard MP4 files. Built and maintained by an independent two-person team since 2026.</p>
                <p class="text-gray-400 text-sm">Email: <a href="mailto:orderbusinesspromotion@gmail.com" class="hover:text-pinterest transition-colors">orderbusinesspromotion@gmail.com</a></p>
            </div>
            <div>
                <h2 class="font-bold mb-4 text-base">Tools</h2>
                <ul class="space-y-2 text-sm text-gray-400">
                    <li><a href="/" class="hover:text-pinterest transition-colors">Pinterest Video Downloader</a></li>
                    <li><a href="/pinterest-to-mp4" class="hover:text-pinterest transition-colors">Pinterest to MP4 Converter</a></li>
                    <li><a href="/download-pinterest-reels" class="hover:text-pinterest transition-colors">Reels &amp; Idea Pin Downloader</a></li>
                    <li><a href="/download-pinterest-video" class="hover:text-pinterest transition-colors">Desktop (PC &amp; Mac) Guide</a></li>
                    <li><a href="/limitations" class="hover:text-pinterest transition-colors">What it cannot do</a></li>
                    <li><a href="/blog" class="hover:text-pinterest transition-colors">Blog &amp; Guides</a></li>
                </ul>
            </div>
            <div>
                <h2 class="font-bold mb-4 text-base">Legal</h2>
                <ul class="space-y-2 text-sm text-gray-400">
                    <li><a href="/privacy-policy" class="hover:text-pinterest transition-colors">Privacy Policy</a></li>
                    <li><a href="/cookie-policy" class="hover:text-pinterest transition-colors">Cookie Policy</a></li>
                    <li><a href="/terms-of-service" class="hover:text-pinterest transition-colors">Terms of Service</a></li>
                    <li><a href="/dmca" class="hover:text-pinterest transition-colors">DMCA &amp; Copyright</a></li>
                    <li><a href="/disclaimer" class="hover:text-pinterest transition-colors">Disclaimer</a></li>
                </ul>
            </div>
            <div>
                <h2 class="font-bold mb-4 text-base">Company</h2>
                <ul class="space-y-2 text-sm text-gray-400">
                    <li><a href="/about-us" class="hover:text-pinterest transition-colors">About Us</a></li>
                    <li><a href="/contact" class="hover:text-pinterest transition-colors">Contact</a></li>
                </ul>
            </div>
        </div>
        <div class="max-w-6xl mx-auto px-4 mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
            <p>&copy; 2026 PinClip. All rights reserved.</p>
            <p class="text-xs mt-3 max-w-3xl mx-auto">PinClip is an independent tool and is not affiliated with, endorsed by, or sponsored by Pinterest, Inc. &quot;Pinterest&quot; is a trademark of Pinterest, Inc. We do not host, store or upload any video files. Please only download content you own or have permission to use &mdash; see our <a href="/dmca" class="hover:text-pinterest underline">DMCA policy</a> and <a href="/disclaimer" class="hover:text-pinterest underline">disclaimer</a>.</p>
        </div>
    </footer>"""


def build_header():
    desktop, mobile = [], []
    for href, label in NAV:
        desktop.append(
            '                    <a href="%s" data-nav class="text-gray-600 hover:text-pinterest '
            'font-medium transition-colors">%s</a>' % (href, label)
        )
        mobile.append(
            '                <a href="%s" data-nav class="block text-base font-medium '
            'text-gray-700 hover:text-pinterest">%s</a>' % (href, label)
        )
    return HEADER % {"desktop": "\n".join(desktop), "mobile": "\n".join(mobile)}


def public_pages():
    """Every indexable HTML page, relative to the frontend root."""
    pages = []
    for path in glob.glob("**/*.html", recursive=True):
        parts = set(os.path.normpath(path).split(os.sep))
        if parts & EXCLUDE_DIRS:
            continue
        pages.append(path)
    return sorted(pages)


def depth_prefix(path):
    """Relative path back to the frontend root ('' or '..')."""
    depth = len(os.path.normpath(path).split(os.sep)) - 1
    return "/".join([".."] * depth) if depth else "."


def get(pattern, html, group=1, flags=re.S):
    m = re.search(pattern, html, flags)
    return m.group(group).strip() if m else None


def canonical_for(path, html):
    existing = get(r'<link rel="canonical" href="([^"]+)"', html)
    if existing:
        return existing
    slug = os.path.normpath(path)
    if slug == "index.html":
        return SITE_URL + "/"
    slug = slug[: -len(".html")]
    if slug.endswith("/index"):
        slug = slug[: -len("/index")]
    return "%s/%s" % (SITE_URL, slug)


def unescape_title(title):
    return (
        title.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )


def attr(value):
    """Escape a string for use inside a double-quoted HTML attribute."""
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def normalize(path):
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()
    original = html
    name = os.path.basename(path)

    # ---- description -------------------------------------------------
    if not re.search(r'<meta name="description"', html):
        desc = DESCRIPTIONS.get(name)
        if desc:
            html = html.replace(
                "</title>",
                '</title>\n    <meta name="description" content="%s">' % desc,
                1,
            )

    title = unescape_title(get(r"<title>(.*?)</title>", html) or "PinClip")
    description = get(r'<meta name="description" content="([^"]*)"', html) or ""
    canonical = canonical_for(path, html)
    is_article = os.path.normpath(path).startswith("blog" + os.sep) and name != "index.html"

    # ---- consent mode, before the AdSense tag -------------------------
    if "gtag('consent', 'default'" not in html and 'gtag("consent"' not in html:
        if ADSENSE_CLIENT in html:
            # insert immediately before the AdSense comment/script
            html = re.sub(
                r'([ \t]*(?:<!-- Google AdSense -->\s*)?<script async src="https://pagead2\.googlesyndication\.com)',
                CONSENT_SNIPPET + r"\1",
                html,
                count=1,
            )
        else:
            html = html.replace("</head>", CONSENT_SNIPPET + "</head>", 1)

    # ---- AdSense tag ---------------------------------------------------
    if ADSENSE_CLIENT not in html:
        html = html.replace("</head>", ADSENSE_SNIPPET + "</head>", 1)

    # ---- canonical -----------------------------------------------------
    if not re.search(r'<link rel="canonical"', html):
        html = html.replace(
            "</head>", '    <link rel="canonical" href="%s">\n</head>' % canonical, 1
        )

    # ---- social + misc meta -------------------------------------------
    if not re.search(r'<meta property="og:', html):
        safe_title = attr(title)
        safe_desc = attr(description)
        meta = [
            "    <!-- Social sharing -->",
            '    <meta property="og:type" content="%s">' % ("article" if is_article else "website"),
            '    <meta property="og:site_name" content="PinClip">',
            '    <meta property="og:title" content="%s">' % safe_title,
            '    <meta property="og:description" content="%s">' % safe_desc,
            '    <meta property="og:url" content="%s">' % canonical,
            '    <meta property="og:image" content="%s">' % OG_IMAGE,
            '    <meta property="og:image:width" content="1200">',
            '    <meta property="og:image:height" content="630">',
            '    <meta property="og:locale" content="en_US">',
            '    <meta name="twitter:card" content="summary_large_image">',
            '    <meta name="twitter:title" content="%s">' % safe_title,
            '    <meta name="twitter:description" content="%s">' % safe_desc,
            '    <meta name="twitter:image" content="%s">' % OG_IMAGE,
        ]
        html = html.replace("</head>", "\n".join(meta) + "\n</head>", 1)

    if not re.search(r'<meta name="robots"', html):
        html = html.replace(
            "</head>",
            '    <meta name="robots" content="index, follow, max-image-preview:large">\n</head>',
            1,
        )
    if not re.search(r'<meta name="author"', html):
        html = html.replace(
            "</head>",
            '    <meta name="author" content="PinClip">\n'
            '    <meta name="theme-color" content="#E60023">\n</head>',
            1,
        )

    # ---- skip link + main landmark ------------------------------------
    if 'class="skip-link"' not in html:
        html = re.sub(r"(<body[^>]*>\n?)", r"\1" + SKIP_LINK, html, count=1)
    if "<main" in html and not re.search(r'<main[^>]*id="main"', html):
        html = html.replace("<main", '<main id="main"', 1)

    # ---- canonical header / footer ------------------------------------
    if "<header" in html:
        html = re.sub(r"[ \t]*<header\b.*?</header>", build_header(), html, count=1, flags=re.S)
    if "<footer" in html:
        html = re.sub(r"[ \t]*<footer\b.*?</footer>", FOOTER, html, count=1, flags=re.S)

    # The nav behaviour lives in site.js now; drop the per-page inline copies.
    html = re.sub(
        r"[ \t]*<script>\s*document\.addEventListener\((['\"])DOMContentLoaded\1\s*,"
        r"\s*function\s*\(\)\s*\{[^<]*?mobileMenu[^<]*?\}\s*\);?\s*</script>\n?",
        "",
        html,
        flags=re.S,
    )

    # ---- shared scripts -------------------------------------------------
    prefix = depth_prefix(path)
    if "assets/js/site.js" not in html:
        html = html.replace("</body>", (SITE_SCRIPT_TAG % prefix) + "</body>", 1)
    if "assets/js/consent.js" not in html:
        html = html.replace("</body>", (CONSENT_SCRIPT_TAG % prefix) + "</body>", 1)

    if html != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return True
    return False


def main():
    if not os.path.isfile("index.html"):
        sys.exit("Run this from the frontend/ directory.")
    changed = [p for p in public_pages() if normalize(p)]
    for p in changed:
        print("updated %s" % p)
    print("\n%d of %d pages updated." % (len(changed), len(public_pages())))


if __name__ == "__main__":
    main()
