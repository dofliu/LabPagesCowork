#!/usr/bin/env python3
import os
import re

nav_items = [
    ("index.html", "首頁"),
    ("blog.html", "研究日誌"),
    ("projects.html", "研究與工具"),
    ("repos.html", "程式碼庫"),
    ("publications.html", "著作發表"),
    ("lab.html", "成員介紹"),
    ("about.html", "關於"),
    ("contact.html", "聯絡"),
    ("privacy.html", "隱私權"),
    ("https://infocard.doflab.cc/", "AI Graphic Studio")
]

def generate_nav(active_file):
    html = '            <ul class="nav-links">\n'
    for href, label in nav_items:
        active_class = ' class="active"' if href == active_file else ''
        if href == "https://infocard.doflab.cc/":
            html += f'                <li><a href="{href}" target="_blank" class="highlight-link">AI Graphic Studio <i class="fas fa-external-link-alt"></i></a></li>\n'
        else:
            html += f'                <li><a href="{href}"{active_class}>{label}</a></li>\n'
    html += '            </ul>'
    return html

files_to_update = ["index.html", "blog.html", "projects.html", "repos.html", "publications.html", "lab.html", "about.html", "contact.html", "privacy.html"]

nav_pattern = re.compile(r'<ul class="nav-links">.*?</ul>', re.DOTALL)

for filename in files_to_update:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_nav = generate_nav(filename)
        updated_content = nav_pattern.sub(new_nav, content)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"Updated {filename}")
