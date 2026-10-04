#!/usr/bin/env python3
"""
miaowenxin-wechat-publisher — 公众号文章生成技能（C4B 定制版）

基于 C4B starter kit（wechat-publisher）改造，新增能力：
  1. 多主题系统（default / blue / warm / minimal）
  2. Callout 高亮框（📘知识点 / 🔧实践 / ⚠️注意 / 💡提示）
  3. 自动目录（--toc）
  4. 文章元数据（YAML frontmatter: title/author/date/abstract）
  5. 页脚版权声明（自动追加）
  6. 中文排版优化（中英文/数字之间自动加空格）
  7. 批量转换（--batch）

Usage:
    python convert_to_wechat.py input.md output.html
    python convert_to_wechat.py input.md output.html --theme blue --toc
    python convert_to_wechat.py input.md output.html --author 苗文馨
    python convert_to_wechat.py --batch ./articles --outdir ./output --theme warm

Then: open output.html in browser → Ctrl+A → Ctrl+C → paste into WeChat editor.
"""

import sys
import os
import re
import argparse
from pathlib import Path

# --- Auto-install dependencies ---
def install_dependencies():
    missing = []
    try:
        import markdown
    except ImportError:
        missing.append("markdown")
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        from docx import Document
    except ImportError:
        missing.append("python-docx")
    try:
        import lxml
    except ImportError:
        missing.append("lxml")

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *missing,
            "--break-system-packages", "-q"
        ])
        print("Done!\n")

install_dependencies()

import markdown
from bs4 import BeautifulSoup
from docx import Document

# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_TAGS = {
    'p', 'h2', 'h3', 'ul', 'ol', 'li', 'span', 'img', 'a',
    'table', 'tr', 'th', 'td', 'br', 'section', 'hr',
}

ALLOWED_CSS = {
    'color', 'background-color', 'font-size', 'font-weight',
    'line-height', 'text-align', 'font-style', 'margin',
    'padding', 'border', 'border-left', 'border-bottom',
    'border-top', 'border-collapse', 'text-decoration',
    'letter-spacing', 'max-width', 'width',
}

# --- NEW CAPABILITY 1: Multi-theme system ---
# Each theme overrides the accent colors of the base layout.
THEMES = {
    'default': {
        'name': '经典灰（Default）',
        'h2_color': '#333333', 'h3_color': '#333333',
        'accent': '#888888',
        'bq_border': '#dddddd', 'bq_bg': '#f9f9f9', 'bq_color': '#666666',
        'code_inline_color': '#d73a49',
        'link': '#0366d6',
    },
    'blue': {
        'name': '科技蓝（Blue）',
        'h2_color': '#1a73e8', 'h3_color': '#1a73e8',
        'accent': '#1a73e8',
        'bq_border': '#1a73e8', 'bq_bg': '#f0f7ff', 'bq_color': '#4a5568',
        'code_inline_color': '#c7254e',
        'link': '#1a73e8',
    },
    'warm': {
        'name': '暖橙（Warm）',
        'h2_color': '#e65100', 'h3_color': '#e65100',
        'accent': '#ff9800',
        'bq_border': '#ff9800', 'bq_bg': '#fff8e1', 'bq_color': '#6d4c41',
        'code_inline_color': '#bf360c',
        'link': '#e65100',
    },
    'minimal': {
        'name': '极简（Minimal）',
        'h2_color': '#333333', 'h3_color': '#555555',
        'accent': '#999999',
        'bq_border': '#999999', 'bq_bg': '#fafafa', 'bq_color': '#555555',
        'code_inline_color': '#333333',
        'link': '#333333',
    },
}


def build_styles(theme):
    """Build the inline style map from a theme dict."""
    t = THEMES.get(theme, THEMES['default'])
    return {
        'h2': (
            'font-size: 21px; font-weight: bold; line-height: 1.6; '
            f'color: {t["h2_color"]}; margin: 24px 0 12px 0; '
            f'border-left: 4px solid {t["accent"]}; padding-left: 10px;'
        ),
        'h3': (
            'font-size: 17px; font-weight: bold; line-height: 1.6; '
            f'color: {t["h3_color"]}; margin: 18px 0 8px 0;'
        ),
        'p': (
            'font-size: 16px; line-height: 1.8; color: #333; '
            'margin: 12px 0; letter-spacing: 0.5px;'
        ),
        'li': (
            'font-size: 16px; line-height: 1.8; color: #333; '
            'margin: 6px 0;'
        ),
        'code_inline': (
            'background-color: #f5f5f5; '
            f'color: {t["code_inline_color"]}; font-size: 14px; '
            'padding: 2px 5px; border-radius: 0;'
        ),
        'code_block': (
            'background-color: #f6f8fa; color: #24292e; font-size: 14px; '
            'line-height: 1.7; padding: 14px 16px; margin: 12px 0; '
            'white-space: pre-wrap; word-break: break-all;'
        ),
        'blockquote': (
            f'background-color: {t["bq_bg"]}; color: {t["bq_color"]}; '
            'padding: 12px 15px; margin: 12px 0; '
            f'border-left: 4px solid {t["bq_border"]};'
        ),
        'table': 'border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;',
        'th': (
            f'background-color: {t["bq_bg"]}; color: #24292e; font-weight: bold; '
            'padding: 8px 10px; text-align: left; border: 1px solid #e0e0e0;'
        ),
        'td': 'padding: 8px 10px; border: 1px solid #e0e0e0; color: #333;',
        'a': f'color: {t["link"]}; text-decoration: none; border-bottom: 1px solid {t["link"]};',
        'img': 'max-width: 100%; border-radius: 4px; display: block; margin: 12px auto;',
        'hr': (
            'border: none; border-top: 1px dashed #cccccc; '
            'margin: 24px 0; width: 100%;'
        ),
        'meta_line': (
            'font-size: 14px; color: #888; text-align: center; '
            'margin: 8px 0 16px 0;'
        ),
        'abstract': (
            f'background-color: {t["bq_bg"]}; color: {t["bq_color"]}; '
            'font-size: 14px; padding: 12px 15px; margin: 0 0 16px 0; '
            f'border-left: 4px solid {t["bq_border"]};'
        ),
        'toc': (
            f'background-color: {t["bq_bg"]}; padding: 14px 18px; '
            'margin: 0 0 20px 0; '
            f'border-left: 4px solid {t["bq_border"]};'
        ),
        'toc_item': (
            'font-size: 15px; line-height: 2.0; color: #333; margin: 0;'
        ),
        'footer': (
            'font-size: 13px; color: #999; text-align: center; '
            'margin: 28px 0 0 0; padding-top: 14px; '
            'border-top: 1px solid #e5e5e5;'
        ),
    }, t


# Callout types: markdown blockquote first line starts with these markers
CALLOUTS = {
    '📘': {'label': '知识点', 'border': '#1a73e8', 'bg': '#f0f7ff', 'color': '#1a4d8f'},
    '🔧': {'label': '实践',   'border': '#2e7d32', 'bg': '#f1f8e9', 'color': '#2e5d32'},
    '⚠️': {'label': '注意',   'border': '#e65100', 'bg': '#fff3e0', 'color': '#a34a00'},
    '💡': {'label': '提示',   'border': '#f9a825', 'bg': '#fffde7', 'color': '#7a5c00'},
}


# ============================================================
# INPUT READERS
# ============================================================

def parse_frontmatter(content):
    """Extract simple YAML frontmatter (title/author/date/abstract)."""
    meta = {}
    if content.startswith('---'):
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                if ':' in line:
                    key, _, val = line.partition(':')
                    meta[key.strip()] = val.strip().strip('"\'')
            content = content[m.end():]
    return meta, content


def read_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    meta, content = parse_frontmatter(content)
    html = markdown.markdown(content, extensions=[
        'extra', 'fenced_code', 'sane_lists', 'toc',
    ])
    return html, meta


def read_docx(filepath):
    doc = Document(filepath)
    parts = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = para.style.name if para.style else ''
        if style_name.startswith('Heading'):
            level = style_name.replace('Heading ', '')
            tag = 'h2' if level in ('1', '2') else 'h3'
            parts.append(f'<{tag}>{text}</{tag}>')
        else:
            p_html = '<p>'
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold and run.italic:
                    p_html += f'<span style="font-weight:bold;font-style:italic;">{t}</span>'
                elif run.bold:
                    p_html += f'<span style="font-weight:bold;">{t}</span>'
                elif run.italic:
                    p_html += f'<span style="font-style:italic;">{t}</span>'
                else:
                    p_html += t
            p_html += '</p>'
            parts.append(p_html)
    return '\n'.join(parts), {}


# ============================================================
# NEW CAPABILITY 6: Chinese typography (CJK-Latin spacing)
# ============================================================

CJK_RE_LEFT = re.compile(r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])([A-Za-z0-9@$`])')
CJK_RE_RIGHT = re.compile(r'([A-Za-z0-9@$`%])([\u4e00-\u9fff])')


def add_cjk_spaces(soup):
    """Add spaces between CJK and Latin/digit characters in text nodes."""
    for text_node in soup.find_all(string=True):
        parent = text_node.parent
        if parent is None:
            continue
        # Skip code content (styling signals code spans/blocks)
        style = parent.get('style', '') if hasattr(parent, 'get') else ''
        if 'code' in style or 'monospace' in style:
            continue
        s = str(text_node)
        new = CJK_RE_LEFT.sub(r'\1 \2', s)
        new = CJK_RE_RIGHT.sub(r'\1 \2', new)
        if new != s:
            text_node.replace_with(new)
    return soup


# ============================================================
# NEW CAPABILITY 2: Callout boxes
# ============================================================

def render_callouts(soup):
    """Convert paragraphs starting with a callout emoji into highlight boxes.

    Note: Python-Markdown merges consecutive `>` blocks (even separated by
    blank lines) into ONE blockquote containing multiple <p>. So markers are
    detected per <p> inside each blockquote, then the blockquote is unwrapped.
    """
    for bq in soup.find_all('blockquote'):
        has_box = False
        for child in list(bq.children):
            if getattr(child, 'name', None) == 'p':
                text = child.get_text(' ', strip=True)
            elif isinstance(child, str) and child.strip():
                text = child.strip()
            else:
                continue
            marker = next((e for e in CALLOUTS if text.startswith(e)), None)
            if not marker:
                continue
            conf = CALLOUTS[marker]
            body = text[len(marker):].strip()
            # Remove a leading "知识点：" style label from the body if duplicated
            label_re = re.compile(r'^\*?' + re.escape(conf['label']) + r'\*?[：:]\s*')
            body = label_re.sub('', body)
            box = soup.new_tag('p')
            label_span = soup.new_tag('span')
            label_span.string = f'{marker} {conf["label"]}'
            label_span['style'] = f'font-weight: bold; color: {conf["color"]};'
            box.append(label_span)
            box.append(soup.new_tag('br'))
            body_span = soup.new_tag('span')
            body_span.string = body
            box.append(body_span)
            box['style'] = (
                f'background-color: {conf["bg"]}; color: {conf["color"]}; '
                'padding: 12px 15px; margin: 14px 0; '
                f'border-left: 4px solid {conf["border"]};'
            )
            child.replace_with(box)
            has_box = True
        if has_box:
            bq.unwrap()
    return soup


# ============================================================
# SANITIZER (inherited from starter kit, with theme support)
# ============================================================

def sanitize(html, STYLES):
    soup = BeautifulSoup(html, 'lxml')

    for tag_name in ('script', 'style', 'iframe'):
        for el in soup.find_all(tag_name):
            el.decompose()

    for h1 in soup.find_all('h1'):
        h1.name = 'h2'

    for div in soup.find_all('div'):
        div.name = 'p'

    # <pre><code> → styled <p>, preserving line breaks
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        code_text = code.get_text() if code else pre.get_text()
        p = soup.new_tag('p')
        p.string = code_text
        p['style'] = STYLES['code_block']
        pre.replace_with(p)

    for code in soup.find_all('code'):
        span = soup.new_tag('span')
        span.string = code.get_text()
        span['style'] = STYLES['code_inline']
        code.replace_with(span)

    # Callout boxes FIRST (they consume emoji-marked paragraphs),
    # then plain blockquotes → styled <p>
    soup = render_callouts(soup)
    for bq in soup.find_all('blockquote'):
        if any('border-left' in (p.get('style') or '') for p in bq.find_all('p')):
            for p in bq.find_all('p'):
                if not p.get('style'):
                    p['style'] = STYLES['blockquote']
            bq.unwrap()
            continue
        p = soup.new_tag('p')
        p = soup.new_tag('p')
        p.string = bq.get_text('\n', strip=True)
        p['style'] = STYLES['blockquote']
        bq.replace_with(p)

    for tag in soup.find_all(['strong', 'b']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-weight: bold;'
        tag.replace_with(span)

    for tag in soup.find_all(['em', 'i']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-style: italic;'
        tag.replace_with(span)

    # <hr> → themed divider
    for hr in soup.find_all('hr'):
        p = soup.new_tag('p')
        p.string = '· · ·'
        p['style'] = 'text-align: center; color: #bbbbbb; margin: 20px 0; letter-spacing: 8px;'
        hr.replace_with(p)

    return soup


def apply_styles(soup, STYLES):
    style_map = {
        'h2': STYLES['h2'], 'h3': STYLES['h3'], 'p': STYLES['p'],
        'li': STYLES['li'], 'table': STYLES['table'],
        'th': STYLES['th'], 'td': STYLES['td'], 'a': STYLES['a'],
        'img': STYLES['img'],
    }
    for tag_name, style in style_map.items():
        for el in soup.find_all(tag_name):
            existing = el.get('style', '')
            if existing:
                continue
            el['style'] = style
    return soup


def clean_attributes(soup):
    for tag in soup.find_all(True):
        for attr in ('class', 'id', 'onclick', 'role', 'lang'):
            if attr in tag.attrs:
                del tag.attrs[attr]
        if tag.name not in ALLOWED_TAGS and tag.name not in ('html', 'head', 'body', '[document]'):
            tag.unwrap()
    return soup


# ============================================================
# NEW CAPABILITY 4 & 5: Metadata header & footer
# ============================================================

def build_header(meta, STYLES, fallback_title=None):
    """Build a styled article header card from frontmatter metadata."""
    if not meta:
        return None
    parts = []
    title = meta.get('title') or fallback_title
    if title:
        parts.append(f'<p style="font-size: 22px; font-weight: bold; color: #333; '
                     f'text-align: center; margin: 8px 0 4px 0;">{title}</p>')
    meta_bits = []
    if meta.get('author'):
        meta_bits.append(f'作者 / {meta["author"]}')
    if meta.get('date'):
        meta_bits.append(meta['date'])
    if meta_bits:
        parts.append(f'<p style="{STYLES["meta_line"]}">{" ｜ ".join(meta_bits)}</p>')
    if meta.get('abstract'):
        parts.append(f'<p style="{STYLES["abstract"]}">📌 摘要：{meta["abstract"]}</p>')
    if not parts:
        return None
    return '\n'.join(parts)


def build_footer(meta, STYLES, footer_text=None):
    if footer_text:
        return f'<p style="{STYLES["footer"]}">{footer_text}</p>'
    author = (meta or {}).get('author', '')
    year = (meta or {}).get('date', '')[:4] or '2026'
    text = f'© {year} {author} ｜ 原创文章，转载请联系授权'.replace('© 2026  ｜', '© 2026')
    if not author:
        text = f'© {year} 原创文章，转载请联系授权'
    return f'<p style="{STYLES["footer"]}">{text}</p>'


# ============================================================
# NEW CAPABILITY 3: Auto table of contents
# ============================================================

def build_toc(soup, STYLES):
    """Generate an embedded TOC from h2/h3 (no anchors — WeChat strips id)."""
    headings = []
    for h in soup.find_all(['h2', 'h3']):
        text = h.get_text(strip=True)
        if text:
            headings.append((h.name, text))
    if len(headings) < 2:
        return None
    items = []
    for level, text in headings:
        if level == 'h2':
            items.append(f'<p style="{STYLES["toc_item"]}">▍{text}</p>')
        else:
            items.append(f'<p style="font-size: 14px; line-height: 1.9; '
                         f'color: #666; margin: 0 0 0 16px;">· {text}</p>')
    inner = '\n'.join(items)
    title_p = (f'<p style="font-size: 15px; font-weight: bold; color: #333; '
               f'margin: 0 0 6px 0;">📑 本文目录</p>')
    return f'<p style="{STYLES["toc"]}">{title_p}{inner}</p>'


# ============================================================
# MAIN CONVERTER
# ============================================================

def convert(input_path, output_path, theme='default', toc=False,
            author=None, footer_text=None, cjk_space=True):
    path = Path(input_path)
    if not path.exists():
        print(f"❌ Error: File '{input_path}' not found.")
        return False

    ext = path.suffix.lower()
    print(f"📖 Reading {path.name} ({ext})...")
    if ext == '.md':
        html, meta = read_markdown(input_path)
    elif ext == '.docx':
        html, meta = read_docx(input_path)
    elif ext in ('.html', '.htm'):
        with open(input_path, 'r', encoding='utf-8') as f:
            html = f.read()
        meta = {}
    else:
        print(f"❌ Unsupported format: {ext} (supported: .md, .docx, .html)")
        return False

    if author:
        meta['author'] = author

    STYLES, theme_conf = build_styles(theme)
    print(f"🎨 Theme: {theme_conf['name']}")

    soup = sanitize(html, STYLES)
    print("📦 Callout boxes rendered.")

    # Remove a duplicated leading h1/h2 title if frontmatter supplies one
    if meta.get('title'):
        first_h = soup.find(['h1', 'h2'])
        if first_h and first_h.get_text(strip=True) == meta['title']:
            first_h.decompose()

    if cjk_space:
        soup = add_cjk_spaces(soup)
        print("🀄 CJK-Latin spacing applied.")

    soup = apply_styles(soup, STYLES)
    soup = clean_attributes(soup)

    body = soup.find('body')
    content = '\n'.join(str(c) for c in body.children if str(c).strip()) if body else str(soup)

    header = build_header(meta, STYLES, fallback_title=path.stem)
    toc_html = build_toc(soup, STYLES) if toc else None
    if toc and toc_html:
        print("📑 TOC generated.")
    footer = build_footer(meta, STYLES, footer_text)

    assembled = '\n'.join(x for x in (header, toc_html, content, footer) if x)

    output_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WeChat Article Preview — {theme} theme</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 24px 20px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Roboto, sans-serif; background-color: #ffffff;">
{assembled}
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Done! {output_path} ({size_kb:.1f} KB)")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_path} in a browser to preview")
    print(f"   2. Ctrl+A → Ctrl+C (select all, copy)")
    print(f"   3. Go to mp.weixin.qq.com → 新建图文 → Ctrl+V")
    print(f"   4. Preview on phone → publish!")
    return True


def batch_convert(input_dir, outdir, **kwargs):
    """NEW CAPABILITY 7: batch conversion of a whole directory."""
    in_dir, out_dir = Path(input_dir), Path(outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [p for p in sorted(in_dir.iterdir())
             if p.suffix.lower() in ('.md', '.docx') and not p.name.startswith('~')]
    if not files:
        print(f"❌ No .md/.docx files found in {input_dir}")
        return False
    print(f"📦 Batch mode: {len(files)} file(s) found.\n")
    ok = 0
    for p in files:
        out_path = out_dir / (p.stem + '_wechat.html')
        print(f"--- [{ok+1}/{len(files)}] {p.name} ---")
        if convert(str(p), str(out_path), **kwargs):
            ok += 1
        print()
    print(f"✅ Batch finished: {ok}/{len(files)} converted → {out_dir}")
    return ok == len(files)


def main():
    parser = argparse.ArgumentParser(
        description='miaowenxin-wechat-publisher — Markdown/Word → 公众号 HTML（C4B 定制版）')
    parser.add_argument('input', nargs='?', help='input .md / .docx / .html')
    parser.add_argument('output', nargs='?', help='output .html')
    parser.add_argument('--theme', default='default',
                        choices=list(THEMES.keys()),
                        help='color theme (default: default)')
    parser.add_argument('--toc', action='store_true', help='generate embedded table of contents')
    parser.add_argument('--author', help='override author name for footer/header')
    parser.add_argument('--footer-text', help='custom footer text (overrides default copyright)')
    parser.add_argument('--no-cjk-space', action='store_true',
                        help='disable CJK-Latin auto spacing')
    parser.add_argument('--batch', metavar='DIR',
                        help='batch-convert all .md/.docx in DIR')
    parser.add_argument('--outdir', default='./wechat_output',
                        help='output directory for --batch mode')
    args = parser.parse_args()

    kw = dict(theme=args.theme, toc=args.toc, author=args.author,
              footer_text=args.footer_text, cjk_space=not args.no_cjk_space)

    if args.batch:
        sys.exit(0 if batch_convert(args.batch, args.outdir, **kw) else 1)

    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if convert(args.input, args.output, **kw) else 1)


if __name__ == '__main__':
    main()
