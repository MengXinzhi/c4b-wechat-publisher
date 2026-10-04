# 拿来说明 — 从 starter kit 拿了什么、改了什么、为什么

> C4B 挑战交付物 ｜ 作者：苗文馨 ｜ 2026-10-04

## 一、拿了什么（拿来主义基座）

| 拿来的文件 | 内容 | 处置 |
|-----------|------|------|
| `SKILL.md` | 技能主指令、微信限制规则表、发布流程 | 重写（保留限制规则和发布流程框架） |
| `scripts/convert_to_wechat.py` | 转换主脚本：md/docx 读取、sanitize、inline CSS、主流程 | 保留骨架，深度扩展 |
| `references/wechat_styles.md` | 样式参考值 | 重写为主题化版本 |
| `references/wechat_restrictions.md` | 微信 HTML 限制权威参考 | 原样保留（信息仍然准确） |
| `examples/sample_article.md` | 示例文章 | 替换为自写功能测试文章（evals/） |

具体保留的函数级能力：

- `read_markdown()` / `read_docx()` — 输入读取（小幅扩展：md 增加 frontmatter 解析、docx 增加元数据返回）
- `sanitize()` 的 h1→h2、div→p、script/style/iframe 删除、strong/em→span、code 处理逻辑 — 原样继承
- `apply_styles()` 的"已有 style 不覆盖"策略 — 原样继承（callout/代码块依赖此行为）
- `clean_attributes()` 的 class/id 清理与非白名单标签 unwrap — 原样继承
- 自动安装依赖机制 — 原样继承
- `ALLOWED_TAGS` / `ALLOWED_CSS` 白名单 — 仅小幅扩充（section/hr/divider 相关）

## 二、改了什么（7 项新增能力）

| # | 能力 | 实现位置 | 为什么改 |
|---|------|---------|---------|
| 1 | 多主题系统 | `THEMES` 字典 + `build_styles()` | 不同文章气质不同：技术教程配 blue、生活随笔配 warm；starter 只有一套灰 |
| 2 | Callout 高亮框 | `CALLOUTS` + `render_callouts()` | 知识点/注意/实践框是公众号干货文的核心排版元素 |
| 3 | 自动目录 | `build_toc()` | 长文导航刚需；因微信禁 id 锚点，目录做成纯文本内嵌块 |
| 4 | 文章元数据 | `parse_frontmatter()` + `build_header()` | 标题/作者/日期/摘要渲染成文头卡片，发布时不用手动敲 |
| 5 | 页脚版权 | `build_footer()` | 原创声明是实际发布必需，每次手打容易忘 |
| 6 | 中文排版优化 | `add_cjk_spaces()` | 中英文/数字间自动加空格是"专业感"的分水岭；代码内容除外 |
| 7 | 批量转换 | `batch_convert()` | 有存量文章时逐篇转换太痛苦 |

结构性修改：

- 样式系统从"一个写死的 `STYLES` 字典"重构为"`THEMES` 主题字典 → `build_styles(theme)` 动态生成"，h2 增加主题色左边框，正文行高 1.75→1.8、加 0.5px 字距
- CLI 从 2 个位置参数升级为 argparse 全参数化
- 输出字体栈加入 `PingFang SC / Microsoft YaHei`，正文宽度 600→600px 保持、内边距微调

## 三、为什么这样改（决策依据）

1. **改样式不改架构**：sanitize 主流程被 starter 验证过，推翻重写风险大、收益小；所以新增能力全部以"前置/后置处理函数"挂进流水线。
2. **callout 放在 sanitize 内部、blockquote 转换之前**：eval 第一轮发现 Python-Markdown 会把连续 `>` 块合并为一个 `<blockquote>`，按块识别会漏掉 3/4 的框；改为逐 `<p>` 识别 + unwrap，修复后复测通过。
3. **目录不用锚点**：微信剥离 `id`，任何锚点跳转都是无效功；纯文本目录块才是可存活的方案。
4. **CJK 间距只处理文本节点且跳过代码样式**：用 BeautifulSoup 遍历 text node，靠 style 是否含 code/monospace 判断跳过，保证代码块语义不变。

## 四、遗留的改进方向（诚实清单）

- LaTeX 公式 → PNG base64（参考 wechat-math-html）尚未实现
- 本地图片 base64 内嵌尚未实现
- callout 内部的 Markdown 加粗/链接不会二次渲染（按纯文本处理）
- 更宽表格的移动端适配仍需手动拆列
