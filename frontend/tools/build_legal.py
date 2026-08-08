#!/usr/bin/env python3
"""
Generate PinClip's policy pages.

Run from ./frontend, then run tools/normalize_pages.py to add the shared chrome:

    python3 tools/build_legal.py && python3 tools/normalize_pages.py
"""

from page_template import write_page, legal_main

SITE = "https://pinclip.vercel.app"
EMAIL = "orderbusinesspromotion@gmail.com"
UPDATED = "8 August 2026"

# ─────────────────────────────── Privacy Policy ───────────────────────────────

PRIVACY = """
<p>This Privacy Policy explains what information PinClip (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) collects when you
visit <a href="/">pinclip.vercel.app</a>, why we collect it, who we share it with, and the choices
you have. It applies to every page and tool on this website.</p>

<p>PinClip is operated by an independent two-person team. You can reach us at any time at
<a href="mailto:{email}">{email}</a>.</p>

<h2>1. The short version</h2>
<ul>
<li>You do not need an account, and we never ask for your name, address or payment details.</li>
<li>Pinterest links you paste are processed in memory to fetch the video and are not saved to a database.</li>
<li>We do not store the videos you download. Nothing is retained on our servers after your request finishes.</li>
<li>We show advertising from Google AdSense. Google may set cookies &mdash; you control this through our consent banner.</li>
<li>You can decline all non-essential cookies and still use every feature of the site.</li>
</ul>

<h2>2. Information we collect</h2>

<h3>2.1 Information you give us directly</h3>
<p>The only information you actively provide is the <strong>Pinterest URL</strong> you paste into the
downloader, and anything you choose to include if you email us. A pasted URL is sent to our
processing server, used to locate the corresponding public video file, and then discarded. It is
not written to any database and is not linked to you.</p>

<h3>2.2 Information collected automatically</h3>
<p>Like virtually every website, our servers write short-lived technical logs. These may include:</p>
<ul>
<li>your IP address (used for abuse prevention and rate limiting);</li>
<li>your browser type, version and operating system;</li>
<li>the page you requested and the date and time of the request;</li>
<li>the referring page, if any.</li>
</ul>
<p>These logs exist so we can diagnose errors, block abuse, and keep the service available. They are
not used to build a profile of you, are not sold, and are rotated and deleted automatically within
<strong>30 days</strong>.</p>

<h3>2.3 Information we do not collect</h3>
<p>We do not collect names, email addresses (unless you email us), postal addresses, phone numbers,
payment information, government identifiers, biometric data, precise geolocation, or any
special-category personal data.</p>

<h2>3. Cookies and similar technologies</h2>
<p>A cookie is a small text file a website stores in your browser. PinClip uses two categories:</p>
<ul>
<li><strong>Strictly necessary</strong> &mdash; a single local storage entry (<code>pinclip_consent</code>) that
remembers your cookie choice so we do not ask again on every page. This cannot be switched off,
because without it we could not honour your preference.</li>
<li><strong>Advertising</strong> &mdash; cookies set by Google and its partners to serve and measure ads.
These are only enabled after you press &ldquo;Accept all&rdquo; on our consent banner.</li>
</ul>
<p>Our <a href="/cookie-policy">Cookie Policy</a> lists each cookie in detail and explains how to change
your mind later.</p>

<h2>4. Advertising and third-party vendors</h2>
<p>PinClip is free to use and is funded entirely by advertising.</p>
<ul>
<li>Third-party vendors, <strong>including Google</strong>, use cookies to serve ads based on your prior
visits to this website or other websites.</li>
<li>Google's use of advertising cookies enables it and its partners to serve ads to you based on
your visit to our site and/or other sites on the Internet.</li>
<li>You may opt out of personalised advertising by visiting
<a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google Ads Settings</a>.</li>
<li>You can opt out of a third-party vendor's use of cookies for personalised advertising at
<a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info/choices</a>
or <a href="https://optout.networkadvertising.org/" rel="nofollow noopener" target="_blank">optout.networkadvertising.org</a>.</li>
</ul>
<p>We implement <strong>Google Consent Mode v2</strong>. Until you make a choice, ad storage, ad
personalisation, ad user data and analytics storage all default to <em>denied</em>. If you decline,
Google may still serve non-personalised ads, which do not rely on advertising cookies for
targeting.</p>
<p>Google's own handling of data is described in
<a href="https://policies.google.com/technologies/partner-sites" rel="nofollow noopener" target="_blank">How Google uses information from sites that use its services</a>.</p>

<h2>5. Where your data goes</h2>
<p>We use a small number of service providers to run the site. Each processes data only as needed to
deliver its function:</p>
<ul>
<li><strong>Vercel</strong> &mdash; static hosting and content delivery for the pages you are reading.</li>
<li><strong>Render</strong> &mdash; hosting for the extraction API that resolves Pinterest links.</li>
<li><strong>Google AdSense</strong> &mdash; advertising delivery and measurement.</li>
<li><strong>Google Fonts</strong> &mdash; web font delivery.</li>
</ul>
<p>These providers may process data outside your country, including in the United States. Where
personal data is transferred out of the EEA or UK, it is covered by the European Commission's
Standard Contractual Clauses or an equivalent safeguard. We do not sell, rent or trade personal
information to anyone.</p>

<h2>6. Legal bases for processing (EEA and UK visitors)</h2>
<ul>
<li><strong>Legitimate interests</strong> &mdash; delivering the service you requested, preventing abuse, and
keeping the site secure and available.</li>
<li><strong>Consent</strong> &mdash; advertising cookies and any personalised advertising. You give this through
the banner and may withdraw it at any time without affecting your use of the site.</li>
</ul>

<h2>7. Your rights</h2>
<p>Depending on where you live, you may have the right to access, correct, delete, restrict, or
object to our processing of your personal data, to data portability, and to withdraw consent. You
also have the right to lodge a complaint with your local data protection authority.</p>
<p>If you are a California resident, the CCPA/CPRA gives you the right to know what personal
information is collected, to request deletion, and to opt out of the &ldquo;sale&rdquo; or &ldquo;sharing&rdquo; of
personal information. <strong>We do not sell or share personal information as those terms are defined
under the CCPA.</strong></p>
<p>To exercise any right, email <a href="mailto:{email}">{email}</a>. We respond within 30 days. Because
we do not hold accounts, we may need you to describe your request precisely enough for us to locate
any relevant records.</p>

<h2>8. Data retention</h2>
<table>
<thead><tr><th>Data</th><th>Kept for</th></tr></thead>
<tbody>
<tr><td>Pinterest URLs you submit</td><td>Not stored &mdash; processed in memory only</td></tr>
<tr><td>Downloaded video files</td><td>Not stored &mdash; streamed to you and discarded</td></tr>
<tr><td>Server access logs</td><td>Up to 30 days, then deleted automatically</td></tr>
<tr><td>Consent preference</td><td>In your browser until you clear it (up to 12 months)</td></tr>
<tr><td>Emails you send us</td><td>Up to 24 months, so we can follow up on your enquiry</td></tr>
</tbody>
</table>

<h2>9. Children's privacy</h2>
<p>PinClip is not directed at children under 13 (or under 16 in the EEA and UK), and we do not
knowingly collect personal information from them. If you believe a child has provided us with
personal information, email <a href="mailto:{email}">{email}</a> and we will delete it.</p>

<h2>10. Security</h2>
<p>All traffic is served over HTTPS with HSTS enabled. We hold no user accounts and no password
database, which removes the most common category of breach risk entirely. No method of
transmission over the Internet is completely secure, so we cannot guarantee absolute security.</p>

<h2>11. Links to other sites</h2>
<p>Our pages link to Pinterest and to other third-party websites. We are not responsible for their
content or privacy practices, and we encourage you to read their policies.</p>

<h2>12. Changes to this policy</h2>
<p>We may update this policy to reflect changes to the service or to the law. Material changes will
be announced on this page with a revised &ldquo;last updated&rdquo; date. Continued use of the site after a
change means you accept the revised policy.</p>

<h2>13. Contact</h2>
<p>Questions, requests or complaints about this policy:
<a href="mailto:{email}">{email}</a>. We aim to reply within two business days.</p>
""".format(email=EMAIL)

# ─────────────────────────────── Cookie Policy ────────────────────────────────

COOKIES = """
<p>This Cookie Policy explains how PinClip uses cookies and browser storage, and how you can control
them. It should be read together with our <a href="/privacy-policy">Privacy Policy</a>.</p>

<h2>What cookies are</h2>
<p>Cookies are small text files placed on your device by a website. They are widely used to make
sites work, to remember preferences, and to measure and personalise advertising. Related
technologies such as <em>local storage</em> serve the same purpose and are covered by this policy.</p>

<h2>How we ask for your permission</h2>
<p>The first time you visit, a banner asks whether you accept advertising cookies. Until you choose,
PinClip runs with Google Consent Mode v2 defaults of <strong>denied</strong> for advertising and analytics
storage &mdash; meaning no advertising cookies are placed. If you decline, you keep full access to the
downloader and every article on the site.</p>

<h2>Cookies used on this site</h2>

<h3>Strictly necessary</h3>
<table>
<thead><tr><th>Name</th><th>Set by</th><th>Purpose</th><th>Duration</th></tr></thead>
<tbody>
<tr><td><code>pinclip_consent</code></td><td>PinClip (local storage)</td><td>Remembers whether you accepted or declined advertising cookies</td><td>Until cleared</td></tr>
</tbody>
</table>

<h3>Advertising &mdash; only after you accept</h3>
<table>
<thead><tr><th>Name</th><th>Set by</th><th>Purpose</th><th>Duration</th></tr></thead>
<tbody>
<tr><td><code>__gads</code>, <code>__gpi</code></td><td>Google</td><td>Ad delivery, frequency capping and measurement</td><td>Up to 13 months</td></tr>
<tr><td><code>IDE</code>, <code>test_cookie</code></td><td>Google DoubleClick</td><td>Measuring ad effectiveness and personalising ads</td><td>Up to 13 months</td></tr>
<tr><td><code>NID</code></td><td>Google</td><td>Stores advertising preferences</td><td>Up to 6 months</td></tr>
</tbody>
</table>
<p>Google may update the exact cookie names it uses. The authoritative, current list is published in
Google's <a href="https://business.safety.google/adscookies/" rel="nofollow noopener" target="_blank">advertising cookies reference</a>.</p>

<h2>Changing your mind</h2>
<p>To withdraw or change consent, clear this site's data in your browser &mdash; the banner will appear
again on your next visit:</p>
<ul>
<li><strong>Chrome</strong>: Settings &rarr; Privacy and security &rarr; Third-party cookies &rarr; See all site data and permissions.</li>
<li><strong>Safari</strong>: Settings &rarr; Privacy &rarr; Manage Website Data.</li>
<li><strong>Firefox</strong>: Settings &rarr; Privacy &amp; Security &rarr; Cookies and Site Data &rarr; Manage Data.</li>
<li><strong>Edge</strong>: Settings &rarr; Cookies and site permissions &rarr; Manage and delete cookies and site data.</li>
</ul>
<p>You can also opt out of personalised advertising globally at
<a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google Ads Settings</a>,
<a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info/choices</a>, or
<a href="https://optout.networkadvertising.org/" rel="nofollow noopener" target="_blank">optout.networkadvertising.org</a>.</p>

<h2>What happens if you block cookies</h2>
<p>Nothing on PinClip breaks. The downloader, the guides and the blog all work with cookies fully
disabled. You will simply see non-personalised advertising instead of personalised advertising.</p>

<h2>Contact</h2>
<p>Questions about this policy? Email <a href="mailto:{email}">{email}</a>.</p>
""".format(email=EMAIL)

# ──────────────────────────────── Terms of Service ────────────────────────────

TERMS = """
<p>These Terms of Service (&ldquo;Terms&rdquo;) govern your access to and use of PinClip at
<a href="/">pinclip.vercel.app</a> (the &ldquo;Service&rdquo;). By using the Service you agree to these Terms.
If you do not agree, please do not use the Service.</p>

<h2>1. What PinClip is</h2>
<p>PinClip is a free, browser-based utility that takes a publicly accessible Pinterest URL, locates
the underlying video file, and returns it to you as an MP4. It is a technical conduit. We are an
independent project and are <strong>not affiliated with, endorsed by, or sponsored by Pinterest, Inc.</strong>
&ldquo;Pinterest&rdquo;, &ldquo;Idea Pin&rdquo; and related marks belong to Pinterest, Inc.</p>

<h2>2. Eligibility</h2>
<p>You must be at least 13 years old (16 in the EEA and UK) to use the Service. By using it you
confirm that you meet this requirement and that you have the legal capacity to accept these Terms.</p>

<h2>3. Your responsibilities</h2>
<p>You are solely responsible for the content you choose to download and for what you do with it.
You agree that you will:</p>
<ul>
<li>only download content you own, content you have permission to download, or content whose use is
otherwise permitted by law in your jurisdiction (for example, a personal-use or fair-dealing exception);</li>
<li>not republish, redistribute, sell, sublicense or monetise downloaded content without the rights
holder's permission;</li>
<li>not present someone else's work as your own;</li>
<li>respect Pinterest's own Terms of Service and any restrictions a creator has placed on their work;</li>
<li>comply with all applicable laws, including copyright law.</li>
</ul>

<h2>4. Acceptable use</h2>
<p>You must not:</p>
<ul>
<li>use automated systems, scrapers or scripts to submit requests at volume;</li>
<li>attempt to circumvent rate limits, access controls, or any security measure;</li>
<li>use the Service to access private, restricted or non-public content;</li>
<li>interfere with, overload, or disrupt the Service or the infrastructure it runs on;</li>
<li>reverse engineer, decompile, or resell the Service;</li>
<li>use the Service for any unlawful, infringing, deceptive or harmful purpose.</li>
</ul>
<p>We apply rate limits and may block IP addresses that abuse the Service.</p>

<h2>5. Intellectual property</h2>
<p>The PinClip name, site design, written guides and source code are our property or are used under
licence, and are protected by copyright and trademark law. Nothing in these Terms transfers those
rights to you.</p>
<p>We claim <strong>no ownership whatsoever</strong> over the videos processed through the Service. All rights
in that content remain with the original creators and rights holders.</p>

<h2>6. Copyright complaints</h2>
<p>We respect intellectual property rights and respond to valid notices. If you believe the Service
has been used to infringe your copyright, please follow the procedure in our
<a href="/dmca">DMCA &amp; Copyright Policy</a>.</p>

<h2>7. Availability and changes</h2>
<p>The Service is provided free of charge and on a best-effort basis. We may modify, suspend or
discontinue any part of it at any time without notice. Because PinClip depends on how Pinterest
delivers its content, some links may stop working without warning, and we do not guarantee that any
particular video can be downloaded.</p>

<h2>8. Advertising</h2>
<p>The Service is funded by third-party advertising, primarily Google AdSense. Advertisements are
not endorsements. Any dealings you have with an advertiser are solely between you and them, and we
are not responsible for their products, services or content.</p>

<h2>9. Disclaimer of warranties</h2>
<p>THE SERVICE IS PROVIDED &ldquo;AS IS&rdquo; AND &ldquo;AS AVAILABLE&rdquo;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING WITHOUT LIMITATION THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE, AND NON-INFRINGEMENT. We do not warrant that the Service will be uninterrupted,
timely, secure, error-free, or that any specific result will be obtained from using it.</p>

<h2>10. Limitation of liability</h2>
<p>To the maximum extent permitted by law, PinClip and its operators shall not be liable for any
indirect, incidental, special, consequential or punitive damages, or for any loss of profits, data,
goodwill or other intangible losses, arising out of or relating to your use of or inability to use
the Service &mdash; including any claim arising from content you downloaded. Our total aggregate
liability for any claim relating to the Service shall not exceed <strong>USD 50</strong>.</p>
<p>Nothing in these Terms excludes or limits liability that cannot lawfully be excluded or limited,
including liability for death or personal injury caused by negligence, or for fraud.</p>

<h2>11. Indemnity</h2>
<p>You agree to indemnify and hold harmless PinClip and its operators from any claim, demand, loss or
expense (including reasonable legal fees) arising from your use of the Service, your breach of these
Terms, or your infringement of any third party's rights.</p>

<h2>12. Termination</h2>
<p>We may restrict or terminate your access to the Service at any time, without notice, if we
reasonably believe you have breached these Terms. Sections 5, 9, 10, 11 and 13 survive termination.</p>

<h2>13. Governing law</h2>
<p>These Terms are governed by the laws of India, without regard to conflict-of-laws principles.
Where you are a consumer, you retain the benefit of any mandatory protections of the law of your
country of residence.</p>

<h2>14. Changes to these Terms</h2>
<p>We may revise these Terms from time to time. The &ldquo;last updated&rdquo; date at the top of this page
reflects the current version. Continuing to use the Service after a change means you accept the
revised Terms.</p>

<h2>15. Contact</h2>
<p>Questions about these Terms: <a href="mailto:{email}">{email}</a>.</p>
""".format(email=EMAIL)

# ────────────────────────────────── Disclaimer ────────────────────────────────

DISCLAIMER = """
<p>Please read this disclaimer carefully before using PinClip. It sets out the limits of what this
website does and where your responsibilities begin.</p>

<h2>1. No affiliation with Pinterest</h2>
<p>PinClip is an independent project. We are <strong>not affiliated with, authorised by, endorsed by, or
in any way officially connected to Pinterest, Inc.</strong> The name &ldquo;Pinterest&rdquo;, the Pinterest logo,
&ldquo;Idea Pin&rdquo; and all related marks are trademarks of Pinterest, Inc. We use them only descriptively,
to explain what our tool does.</p>

<h2>2. We do not host or store any content</h2>
<p>PinClip stores no video files. When you submit a link, our server resolves the publicly accessible
media URL that Pinterest's own content delivery network already serves, streams the file to your
browser, and discards it. There is no media library, no archive, and no catalogue of downloaded
content on our systems.</p>

<h2>3. Copyright rests with the original creators</h2>
<p>Every video accessible through this tool belongs to the person or organisation that created it.
PinClip claims no ownership over any of it and grants you no rights to it. A technical ability to
download a file is not a licence to use it.</p>

<h2>4. Your responsibility</h2>
<p>You alone are responsible for how you use this tool and what you do with anything you download.
Before downloading, satisfy yourself that doing so is lawful where you live. As a general rule:</p>
<ul>
<li><strong>Usually fine:</strong> saving a video you created yourself; saving a public video for genuinely
private, personal, offline viewing where your local law permits it.</li>
<li><strong>Usually not fine:</strong> re-uploading someone's video to another platform; using it in an
advertisement, product or monetised channel; removing attribution and passing the work off as your
own; redistributing it at scale.</li>
</ul>
<p>Copyright law varies significantly between countries. Nothing here is a substitute for advice from
a qualified lawyer in your jurisdiction.</p>

<h2>5. No legal advice</h2>
<p>The content on this website, including our guides and articles, is provided for general
information only. It does not constitute legal advice and should not be relied on as such.</p>

<h2>6. No warranty</h2>
<p>This service is offered free of charge and on an &ldquo;as is&rdquo; basis. We make no promise that it will
be available, that any particular link will work, or that a downloaded file will be of any
particular quality. Pinterest may change how it delivers video at any time, which can break the tool
without notice.</p>

<h2>7. Limitation of liability</h2>
<p>To the fullest extent permitted by law, PinClip and its operators accept no liability for any
loss or damage arising from your use of this website, including any claim of copyright infringement
resulting from content you chose to download. Full terms are set out in our
<a href="/terms-of-service">Terms of Service</a>.</p>

<h2>8. Rights holders</h2>
<p>If you own content that you believe is being accessed improperly through this tool, we want to
hear from you and we act on valid notices. Please see our
<a href="/dmca">DMCA &amp; Copyright Policy</a> or email
<a href="mailto:{email}">{email}</a> directly.</p>

<h2>9. External links and advertising</h2>
<p>This site contains links to third-party websites and displays third-party advertising. We do not
control that content and are not responsible for it. The presence of an advertisement is not an
endorsement.</p>
""".format(email=EMAIL)

# ───────────────────────────────────── DMCA ───────────────────────────────────

DMCA = """
<p>PinClip respects the intellectual property rights of others and expects its users to do the same.
This page explains how rights holders can report infringement and how we respond.</p>

<h2>Our position</h2>
<p>PinClip is a technical conduit. It resolves publicly accessible media URLs from Pinterest's own
content delivery network and passes the file through to the person who requested it. <strong>We do not
host, store, cache, index or archive any video.</strong> Because nothing is stored on our servers, there
is generally no file for us to take down &mdash; the content remains where its creator uploaded it, on
Pinterest.</p>
<p>That said, we take reports seriously. Where a rights holder identifies a genuine problem, we will
act: we can block specific URLs, boards or accounts from being processed by our tool, and we
terminate access for users who repeatedly misuse the service.</p>

<h2>Filing a notice of alleged infringement</h2>
<p>If you are a copyright owner, or authorised to act on behalf of one, and you believe our service
has been used to infringe your copyright, send a written notice to
<a href="mailto:{email}">{email}</a> with the subject line <strong>&ldquo;DMCA Notice&rdquo;</strong>.</p>
<p>To be effective under 17 U.S.C. &sect; 512(c)(3), your notice must include all of the following:</p>
<ol>
<li>A physical or electronic signature of the copyright owner, or a person authorised to act on
their behalf.</li>
<li>Identification of the copyrighted work claimed to have been infringed &mdash; or, if multiple works
are covered by a single notice, a representative list.</li>
<li>Identification of the material claimed to be infringing, with information reasonably sufficient
for us to locate it (the specific Pinterest pin URL, please).</li>
<li>Your contact information: full name, mailing address, telephone number and email address.</li>
<li>A statement that you have a good-faith belief that the disputed use is not authorised by the
copyright owner, its agent, or the law.</li>
<li>A statement that the information in the notice is accurate, and &mdash; <strong>under penalty of
perjury</strong> &mdash; that you are the copyright owner or are authorised to act on their behalf.</li>
</ol>
<p>Incomplete notices may be invalid. Please note that under 17 U.S.C. &sect; 512(f), knowingly
misrepresenting that material is infringing can make you liable for damages, including costs and
legal fees.</p>

<h2>What happens next</h2>
<ol>
<li>We acknowledge receipt of your notice, normally within <strong>2 business days</strong>.</li>
<li>We review it, usually completing the review within <strong>10 business days</strong>.</li>
<li>If the notice is valid, we add the identified URLs, boards or accounts to a processing blocklist
so our tool will refuse them, and we confirm this to you in writing.</li>
<li>Where the material is hosted on Pinterest itself, we will also point you to Pinterest's own
copyright reporting process, since only Pinterest can remove the source file.</li>
</ol>

<h2>Counter-notice</h2>
<p>If you believe your material was blocked in error or as a result of misidentification, you may
send a counter-notice to the same address with the subject line
<strong>&ldquo;DMCA Counter-Notice&rdquo;</strong>. It must include your signature, identification of the material and
its location before it was blocked, a statement under penalty of perjury that you have a good-faith
belief the material was blocked as a result of mistake or misidentification, your name, address and
telephone number, and a statement consenting to the jurisdiction of the appropriate court.</p>

<h2>Repeat infringers</h2>
<p>In line with 17 U.S.C. &sect; 512(i), we operate a repeat-infringer policy. Users who repeatedly use
the service to infringe copyright will have their access permanently terminated.</p>

<h2>Reporting other problems</h2>
<p>For trademark concerns, privacy complaints, or content that should not be accessible for any other
reason, email <a href="mailto:{email}">{email}</a> with the relevant details. You do not need to file a
formal DMCA notice for these.</p>

<h2>Designated contact</h2>
<p>Copyright Agent, PinClip<br>
Email: <a href="mailto:{email}">{email}</a><br>
Response time: within 2 business days</p>
""".format(email=EMAIL)


PAGES = [
    ("privacy-policy.html", "Privacy Policy | PinClip",
     "How PinClip handles your data: no accounts, no stored videos, 30-day log retention, "
     "Google AdSense cookie disclosure, and your GDPR and CCPA rights.",
     "Privacy Policy", PRIVACY),
    ("cookie-policy.html", "Cookie Policy | PinClip",
     "Every cookie PinClip and its advertising partners use, why they exist, how long they last, "
     "and how to withdraw your consent at any time.",
     "Cookie Policy", COOKIES),
    ("terms-of-service.html", "Terms of Service | PinClip",
     "The terms governing your use of PinClip's free Pinterest video downloader: acceptable use, "
     "copyright obligations, warranties and limitation of liability.",
     "Terms of Service", TERMS),
    ("disclaimer.html", "Disclaimer | PinClip",
     "PinClip is not affiliated with Pinterest and hosts no video files. Read what that means for "
     "you and where your responsibility as a user begins.",
     "Disclaimer", DISCLAIMER),
    ("dmca.html", "DMCA &amp; Copyright Policy | PinClip",
     "How copyright owners can report infringement to PinClip, what our notice-and-blocklist "
     "process involves, and how to file a counter-notice.",
     "DMCA &amp; Copyright Policy", DMCA),
]


def main():
    for filename, title, description, heading, body in PAGES:
        slug = filename[: -len(".html")]
        write_page(
            filename,
            title,
            description,
            "%s/%s" % (SITE, slug),
            legal_main(heading, UPDATED, body),
        )


if __name__ == "__main__":
    main()
