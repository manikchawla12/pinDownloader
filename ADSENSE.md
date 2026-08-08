# AdSense readiness

Everything in this file describes the state of the repo after the compliance
pass. Read the "Before you resubmit" section first — the two items there matter
more than anything that was changed in code.

---

## Before you resubmit

### 1. Get a custom domain (most important)

The site currently lives on `pinclip.vercel.app`. A free platform subdomain is
the single biggest handicap in an AdSense application. Google can't verify that
you own it in the normal way, these subdomains carry the reputation of every
other project on the platform, and reviewers see a large volume of low-quality
applications from exactly this kind of URL.

Buy a domain (`pinclip.app`, `pinclip.io`, anything), point it at the Vercel
project, and apply with that. When you do:

```bash
# one edit, then regenerate everything that embeds the URL
# frontend/tools/normalize_pages.py  -> SITE_URL
# frontend/tools/build_legal.py      -> SITE
# frontend/tools/build_sitemap.py    -> SITE
# frontend/robots.txt                -> Sitemap: line

cd frontend
python3 tools/build_legal.py
python3 tools/normalize_pages.py
python3 tools/build_sitemap.py
npm run build:css
```

Canonical tags, OG URLs and the sitemap all regenerate from those constants.

Let the domain age a few weeks with the content live before applying, and get
Search Console verified and the sitemap submitted in the meantime.

### 2. Understand the category risk

Video downloader sites are a category Google scrutinises heavily, because they
can be used to redistribute other people's work. That is why the DMCA page, the
"only download what you have the right to download" language, and the
non-affiliation notices exist throughout the site — they are the difference
between a tool that looks like it facilitates infringement and one that
documents its limits. Don't remove them to save space.

An honest expectation: none of this guarantees approval. It removes the
concrete, fixable reasons for rejection.

### 3. Fill in the AdSense dashboard

- Verify site ownership with the `ads.txt` file (already at `/ads.txt`).
- Turn Auto Ads on rather than hand-placing units — there are no `<ins>` slots
  in the markup, so nothing renders until you do.
- Set the EEA/UK consent message to "off" in AdSense; this site implements its
  own Consent Mode v2 banner and two consent UIs will conflict.

---

## What was fixed

### Rendering (this was almost certainly costing you the review)

The compiled `assets/css/style.css` was stale and the Tailwind config never
scanned `blog/`. Roughly 25 utility classes used in the markup were missing
from the stylesheet, including `md:grid-cols-2` and `lg:grid-cols-3` — the
feature and article grids were not laying out in columns at all.

Worse, every long-form page used `prose prose-lg`, but
`@tailwindcss/typography` was not installed and `plugins` was empty. All those
classes were no-ops, so every article on the site rendered as an unspaced wall
of text. A reviewer opening the homepage saw a broken page.

- installed `@tailwindcss/typography` and configured it
- added `blog/**` and `admin/**` to the Tailwind content globs
- added `npm run build` so Vercel rebuilds CSS on deploy
- rebuilt `style.css` (15 KB → 39 KB)

### Policy compliance

- **`/ads.txt`** — was 404. Now present with the publisher ID.
- **Consent** — Google Consent Mode v2 defaults (`denied` for ad storage, ad
  user data, ad personalisation and analytics) are set inline in `<head>`
  *before* the AdSense tag on every page, plus an accept/decline banner
  (`assets/js/consent.js`). Required for EEA/UK traffic.
- **Privacy Policy** — rewritten from 4 short paragraphs to a full policy:
  Google third-party vendor and DART cookie disclosure, the three required
  opt-out links, GDPR legal bases, CCPA statement, a data retention table,
  children's privacy, and sub-processors.
- **Cookie Policy** — new page, itemising every cookie with duration.
- **Terms of Service** — expanded from 165 to ~870 words with acceptable use,
  IP, warranty disclaimer, liability cap and governing law.
- **Disclaimer** — expanded, plus explicit non-affiliation with Pinterest.
- **DMCA & Copyright Policy** — new page with the full §512(c)(3) notice
  procedure, response SLAs, counter-notice process and repeat-infringer policy.
  This is the page that most distinguishes a compliant downloader site.

### Content and structure

- **Removed `/pinterest-video-downloader`** — it duplicated the homepage almost
  exactly (same tool, same intent, near-identical title). Five same-intent
  pages targeting one keyword is the textbook definition of doorway pages.
  301-redirected to `/` in `vercel.json`; all 19 internal links repointed.
- **Repurposed `/download-pinterest-video`** into a genuinely distinct
  desktop-focused guide (Windows/macOS/Linux/ChromeOS file locations,
  browser-specific behaviour, library organisation, desktop troubleshooting).
- **Unique FAQ sections + `FAQPage` schema** on `/pinterest-to-mp4` and
  `/download-pinterest-reels`, so each tool page answers questions the others
  don't.
- **Blog posts** got `BlogPosting` + `BreadcrumbList` JSON-LD, article
  published/modified meta, visible breadcrumbs and `<time>` elements.
- **Header and footer are now identical on all 18 pages**, generated from one
  definition in `tools/normalize_pages.py`. Several pages previously had
  truncated navigation and no links to the legal pages.
- **Contact page** got a real form (validates, then opens a pre-filled email —
  no third-party form service or data collection involved).
- **Custom 404 page** instead of Vercel's default.

### Technical

- `robots.txt` disallows `/admin`, explicitly allows the AdSense crawlers.
- `sitemap.xml` is now generated from disk (`tools/build_sitemap.py`). The old
  hand-maintained one listed a deleted page and omitted `/disclaimer`.
- Removed the `noindex` that was on `/disclaimer`.
- OG + Twitter Card meta everywhere, with a generated 1200×630 share image.
- `vercel.json`: 301 redirects, `X-Robots-Tag: noindex` on `/admin`,
  HSTS, Referrer-Policy, Permissions-Policy, asset caching. Dropped the
  deprecated `X-XSS-Protection`; `X-Frame-Options` relaxed `DENY` → `SAMEORIGIN`.
- `app.js`: the result thumbnail fell back to `via.placeholder.com`, which no
  longer resolves — replaced with an inline SVG. Raw yt-dlp errors
  (`ERROR: [Pinterest] 123: Unable to download JSON metadata: HTTP Error 404`)
  were being shown to visitors verbatim; they're now mapped to plain-language
  messages. Added a 60s timeout, client-side URL validation, and support for
  non-`.com` Pinterest domains (`in.pinterest.com`, `pinterest.co.uk`).
- Accessibility: skip links, `<main id="main">`, labelled form inputs,
  `aria-expanded` on the menu button, `role="alert"` on errors,
  `aria-hidden` on decorative icons.

---

## Regenerating the site

```bash
cd frontend
npm install
python3 tools/build_legal.py       # policy pages
python3 tools/normalize_pages.py   # shared head/header/footer on every page
python3 tools/build_sitemap.py     # sitemap from disk
npm run build:css                  # Tailwind
```

`normalize_pages.py` is idempotent — run it after editing any page. Edit the
nav in one place (`NAV`, `HEADER`, `FOOTER` in that file) and re-run.

## Still worth doing

- Add original images or diagrams to the blog posts; they currently hotlink
  generic Unsplash stock, which reads as filler.
- The tool depends on a Render free-tier backend that sleeps. A reviewer who
  hits a cold start may conclude the tool doesn't work. Consider a paid
  instance, or at minimum verify the service is warm before applying.
- Two of the five blog posts are ~550 words. Bringing them to 1,000+ would help.
