#!/usr/bin/env python3
"""
Minimal page skeleton writer.

Writes the <head> plus an empty <header>/<footer> pair; tools/normalize_pages.py
then fills in the canonical chrome, social meta and shared scripts. Keeping the
two steps separate means the nav only ever has to be edited in one place.
"""

import os

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{prefix}/assets/css/style.css">
    <link rel="icon" type="image/png" href="/favicon.png">
    <link rel="canonical" href="{canonical}">
{extra_head}</head>
<body class="bg-gray-50 text-gray-800 font-sans flex flex-col min-h-screen">
    <header></header>

{main}

    <footer></footer>
</body>
</html>
"""


def write_page(path, title, description, canonical, main, extra_head=""):
    depth = len(os.path.normpath(path).split(os.sep)) - 1
    prefix = "/".join([".."] * depth) if depth else "."
    html = TEMPLATE.format(
        title=title,
        description=description,
        canonical=canonical,
        main=main,
        prefix=prefix,
        extra_head=extra_head,
    )
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote %s" % path)


def legal_main(heading, updated, body):
    """Standard wrapper for a long-form legal / policy page."""
    return """    <main class="flex-grow py-12 px-4">
        <div class="max-w-4xl mx-auto">
            <nav aria-label="Breadcrumb" class="text-sm text-gray-500 mb-6">
                <a href="/" class="hover:text-pinterest">Home</a>
                <span class="mx-2" aria-hidden="true">/</span>
                <span class="text-gray-700">{heading}</span>
            </nav>
            <article class="bg-white p-8 md:p-12 rounded-2xl shadow-sm border border-gray-100">
                <h1 class="text-3xl md:text-4xl font-bold text-dark mb-2">{heading}</h1>
                <p class="text-sm text-gray-500 mb-8">Last updated: {updated}</p>
                <div class="prose prose-lg max-w-none">
{body}
                </div>
            </article>
        </div>
    </main>""".format(heading=heading, updated=updated, body=body)
