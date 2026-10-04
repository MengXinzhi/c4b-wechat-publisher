---
name: miaowenxin-wechat-publisher
description: "Convert Markdown or Word documents into WeChat Official Account (微信公众号) compatible HTML with themed styling, callout highlight boxes, auto table of contents, article metadata header, copyright footer, and CJK-Latin spacing optimization. This skill should be used when the user says '转换成公众号', '公众号文章', '微信公众号格式', 'make WeChat article', 'generate WeChat HTML', or provides a .md/.docx file and asks to format it for WeChat publishing, or asks to batch-convert a folder of articles for WeChat. Based on the C4B wechat-publisher starter kit, customized by 苗文馨 (miaowenxin)."
agent_created: true
---

# miaowenxin-wechat-publisher — Markdown/Word → 公众号 HTML（C4B 定制版）

## Purpose

Convert a Markdown (.md) or Word (.docx) document into copy-paste-ready HTML
for WeChat Official Account publishing. Based on the C4B starter kit
(`wechat-publisher`), this version adds: multi-theme styling, callout
highlight boxes, auto table of contents, article metadata header, copyright
footer, Chinese typography optimization, and batch conversion.

## Quick Start

```bash
python scripts/convert_to_wechat.py input.md output.html
python scripts/convert_to_wechat.py input.md output.html --theme blue --toc
python scripts/convert_to_wechat.py --batch ./articles --outdir ./output --theme warm
```

Then: open `output.html` in browser → Ctrl+A → Ctrl+C → paste into WeChat
editor (mp.weixin.qq.com) → preview on phone → publish.

## New Capabilities (vs starter kit)

| Capability | How To Use |
|-----------|-----------|
| 🎨 Multi-theme | `--theme default|blue|warm|minimal` — accent colors for headings, quotes, links |
| 📦 Callout boxes | In Markdown, write a blockquote whose paragraph starts with `📘`(知识点) / `🔧`(实践) / `⚠️`(注意) / `💡`(提示), e.g. `> 📘 知识点：inline CSS 是唯一选择` |
| 📑 Auto TOC | `--toc` — builds an embedded "本文目录" block from h2/h3 (no anchors; WeChat strips `id`) |
| 🏷️ Metadata header | YAML frontmatter at the top of the .md: `title`, `author`, `date`, `abstract` → rendered as a styled header card |
| 📄 Copyright footer | Auto-appended from frontmatter author/date; override with `--footer-text "..."` |
| 🀄 CJK-Latin spacing | Auto-inserts spaces between Chinese and Latin/digits in text; disable with `--no-cjk-space`; never applied inside code |
| ⚡ Batch mode | `--batch <dir> --outdir <dir>` converts every .md/.docx in the folder |

## Workflow

1. Read the input file (`.md` with optional YAML frontmatter, `.docx`, or `.html`).
2. Choose a theme with the user or pick one matching the article tone
   (tech tutorial → `blue`; lifestyle → `warm`; long structured article → `--toc`).
3. Run the converter with appropriate flags.
4. Open the output HTML in a browser and verify: headings, callouts, TOC,
   header/footer render correctly; no `<script>`/`<style>`/`<div>`/`<h1>` tags.
5. Hand over the publish steps: browser → Ctrl+A/Ctrl+C → WeChat editor → paste.

## Inherited from Starter Kit (unchanged behavior)

- Markdown via `python-markdown` (extra, fenced_code, sane_lists, toc)
- Word via `python-docx` (headings, bold/italic runs)
- Sanitization: `<h1>`→`<h2>`, `<div>`→`<p>`, script/style/iframe removed,
  class/id stripped, strong/em → styled spans, code blocks → styled `<p>`
- Inline-CSS-only output per WeChat rules — see `references/wechat_restrictions.md`
- Style values and theme palette — see `references/wechat_styles.md`

## Dependencies

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

The script auto-installs missing packages on first run.

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Consecutive callout blockquotes | Python-Markdown merges them into one `<blockquote>`; the converter detects markers per `<p>` and splits boxes correctly |
| Frontmatter title == first heading | The duplicated heading is removed automatically |
| External image URLs | Kept as-is; remind the user to re-upload via WeChat media library |
| Very long article | Works; WeChat limit is ~20,000 Chinese characters |
| Non-UTF-8 files | UTF-8 expected; convert with an editor first |

## Known Limitations

- Math formulas (LaTeX → PNG base64) are NOT implemented yet
- Local images are not embedded as base64 yet
- Callout body is rendered as plain text (markdown inside callouts is not re-parsed)
