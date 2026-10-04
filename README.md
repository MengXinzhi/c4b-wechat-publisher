# C4B 公众号文章生成技能 — 提交包

本仓库是 C4B「公众号文章生成技能」挑战的提交包（学生：苗文馨 / 2024106220247）。

## 挑战任务
拿到 C4B starter kit，用 skill-creator 把它改造成自己的公众号文章生成技能，并用它发布一篇真实的公众号文章。

## 目录结构
- `miaowenxin-wechat-publisher/` —— 做成的技能包（SKILL.md + scripts + references + evals）
  - `scripts/convert_to_wechat.py` —— 主转换脚本（Markdown/Word → 公众号内联样式 HTML）
  - `references/wechat_restrictions.md`、`wechat_styles.md` —— 公众号排版限制与主题样式
  - `evals/` —— 4 个评测用例与评测报告
- `miaowenxin_C4B_文章源文件.md` —— 待发布的文章源文（Markdown）
- `miaowenxin_C4B_output.html` —— 技能生成的公众号排版 HTML
- `miaowenxin_C4B_文章链接.md` —— 文章链接与阅读数据（待发布后回填）
- `miaowenxin_C4B_教学说明.md` —— 技能使用教学
- `miaowenxin_C4B_拿来说明.md` —— 相对 starter kit 的能力增量说明
- `miaowenxin_C4B_AI日志.md` —— skill-creator 完整使用日志（含失败与修复）

## 技能相对 starter kit 的增量
多主题 / callout 提示框 / 自动目录 / 元数据块 / 页脚版权 / CJK 中英文间距 / 批量转换。

## 状态
文章尚未发布，`miaowenxin_C4B_文章链接.md` 中的链接为占位符，待发布后回填。
