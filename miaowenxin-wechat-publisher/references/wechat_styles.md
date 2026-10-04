# miaowenxin-wechat-publisher — Style Reference (C4B 定制版)

Inline CSS values for WeChat Official Account articles, organized by theme.
All styles are applied inline (`style="..."`) — WeChat strips everything else.

## Typography (all themes share these dimensions)

### H2 (section heading, themed accent + left bar)
```
font-size: 21px; font-weight: bold; line-height: 1.6;
margin: 24px 0 12px 0; border-left: 4px solid {accent}; padding-left: 10px;
```

### H3
```
font-size: 17px; font-weight: bold; line-height: 1.6; margin: 18px 0 8px 0;
```

### Body
```
font-size: 16px; line-height: 1.8; color: #333; margin: 12px 0; letter-spacing: 0.5px;
```

## Theme Palette

| Token | default | blue | warm | minimal |
|-------|---------|------|------|---------|
| h2 / h3 color | #333333 | #1a73e8 | #e65100 | #333333 / #555555 |
| accent (left bar) | #888888 | #1a73e8 | #ff9800 | #999999 |
| blockquote border / bg | #dddddd / #f9f9f9 | #1a73e8 / #f0f7ff | #ff9800 / #fff8e1 | #999999 / #fafafa |
| inline code color | #d73a49 | #c7254e | #bf360c | #333333 |
| link | #0366d6 | #1a73e8 | #e65100 | #333333 |

## Callout Boxes (theme-independent)

| Marker | Label | Border | Background | Text |
|--------|-------|--------|-----------|------|
| 📘 | 知识点 | #1a73e8 | #f0f7ff | #1a4d8f |
| 🔧 | 实践 | #2e7d32 | #f1f8e9 | #2e5d32 |
| ⚠️ | 注意 | #e65100 | #fff3e0 | #a34a00 |
| 💡 | 提示 | #f9a825 | #fffde7 | #7a5c00 |

Box pattern:
```
background-color: {bg}; color: {color}; padding: 12px 15px;
margin: 14px 0; border-left: 4px solid {border};
```
First line: bold label `<span style="font-weight:bold;color:{color};">📘 知识点</span><br>`.

## Structural Elements

### Header card (from frontmatter)
- Title: `font-size: 22px; font-weight: bold; text-align: center;`
- Meta line: `font-size: 14px; color: #888; text-align: center;`
- Abstract: blockquote pattern + `📌 摘要：` prefix

### TOC block (`--toc`)
- Container: themed blockquote background, `border-left: 4px solid {bq_border}`
- h2 items: `▍` prefix, 15px; h3 items: `·` prefix, 14px, indented 16px
- No anchor links — WeChat strips `id` attributes

### Footer
```
font-size: 13px; color: #999; text-align: center; margin: 28px 0 0 0;
padding-top: 14px; border-top: 1px solid #e5e5e5;
```
Default text: `© {year} {author} ｜ 原创文章，转载请联系授权`

### Divider (`---` in Markdown)
Rendered as centered `· · ·` with `letter-spacing: 8px; color: #bbbbbb;`
(no `<hr>` — WeChat strips it)

## Mobile Considerations

- Minimum body text: 16px (smaller is unreadable on phones)
- Max width: articles display at ~375px on most phones
- Line height: 1.8 for Chinese readability
- Color: avoid pure black (#000); #333 is softer on eyes
- Images: always `max-width: 100%`
- Code blocks: `white-space: pre-wrap; word-break: break-all;` to avoid
  horizontal overflow on narrow screens
