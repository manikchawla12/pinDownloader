import os

adsense_code = """    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7120148790304596" crossorigin="anonymous"></script>
</head>"""

def add_adsense(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prevent duplicate injection
                if 'client=ca-pub-7120148790304596' not in content:
                    new_content = content.replace("</head>", adsense_code)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                else:
                    print(f"Skipping {file}, AdSense already present.")

add_adsense('/Users/manikchawla/.gemini/antigravity/scratch/pinterest-downloader/frontend')
