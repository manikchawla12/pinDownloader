import os
import re

header_html = """    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo -->
                <a href="/" class="flex items-center gap-2">
                    <img src="/favicon.png" alt="PinClip Logo" class="h-8 w-8 rounded">
                    <span class="font-bold text-xl tracking-tight text-dark">PinClip</span>
                </a>
                
                <!-- Desktop Nav -->
                <nav class="hidden md:flex space-x-8">
                    <a href="/" class="text-gray-600 hover:text-pinterest font-medium transition-colors">Home</a>
                    <a href="/blog" class="text-gray-600 hover:text-pinterest font-medium transition-colors">Blog</a>
                    <a href="/download-pinterest-video" class="text-gray-600 hover:text-pinterest font-medium transition-colors">Features</a>
                </nav>

                <!-- Mobile Menu Button -->
                <button id="mobileMenuBtn" class="md:hidden text-gray-600 hover:text-pinterest focus:outline-none">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
            </div>
        </div>

        <!-- Mobile Menu -->
        <div id="mobileMenu" class="md:hidden hidden bg-white border-t border-gray-100 shadow-lg absolute w-full left-0">
            <div class="px-4 py-3 space-y-2 pb-4">
                <a href="/" class="block text-base font-medium text-gray-700 hover:text-pinterest">Home</a>
                <a href="/blog" class="block text-base font-medium text-gray-700 hover:text-pinterest">Blog</a>
                <a href="/download-pinterest-video" class="block text-base font-medium text-gray-700 hover:text-pinterest">Features</a>
            </div>
        </div>
    </header>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var btn = document.getElementById('mobileMenuBtn');
            var menu = document.getElementById('mobileMenu');
            if (btn && menu) {
                btn.addEventListener('click', function() {
                    menu.classList.toggle('hidden');
                });
            }
        });
    </script>"""

footer_svg_pattern = r'<svg class="h-6 w-6 text-pinterest" fill="currentColor" viewBox="0 0 24 24">.*?</svg>'
footer_img_replacement = '<img src="/favicon.png" alt="PinClip Logo" class="h-6 w-6 rounded">'

def update_headers(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace <header> to </header>
                new_content = re.sub(r'<header.*?</header>', header_html, content, flags=re.DOTALL)
                
                # Replace footer SVG if present
                new_content = re.sub(footer_svg_pattern, footer_img_replacement, new_content, flags=re.DOTALL)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

update_headers('/Users/manikchawla/.gemini/antigravity/scratch/pinterest-downloader/frontend')
