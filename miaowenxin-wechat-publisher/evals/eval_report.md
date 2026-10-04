# Eval 用例与结果 — miaowenxin-wechat-publisher

## 测试方法

对同一份全功能测试文章（`evals/test_feature_article.md`）执行 4 组转换，检查输出 HTML。

## 用例列表

| # | 用例 | 命令 | 通过标准 |
|---|------|------|----------|
| E1 | 默认主题全功能 | `convert_to_wechat.py test_feature_article.md e1.html --toc` | 无脚本/style/div/h1 标签；callout 四色框存在；TOC 存在；元数据文头存在；页脚存在 |
| E2 | 主题切换 | `--theme blue` / `--theme warm` | h2 颜色分别为 #1a73e8 / #e65100 |
| E3 | 关闭中文间距 | `--no-cjk-space` | "English混排" 保持无空格 |
| E4 | 批量转换 | `--batch evals --outdir evals/batch_out` | 目录内全部 md 各生成一个 html |

## 结果（2026-10-04 实测）

- E1 ✅：无禁用标签；📘/🔧/⚠️/💡 四个 callout 均渲染为彩色高亮框；📑 目录块生成（2 个 h2 + 1 个 h3）；文头含标题/作者/日期/摘要；页脚含版权。
- E2 ✅：blue 与 warm 主题的 h2 内联色值正确。
- E3 ✅：加 `--no-cjk-space` 后英文与中文之间无插入空格；默认行为下已自动加空格。
- E4 ✅：batch 模式对目录内全部 md 逐一转换并输出 `_wechat.html`。
- 首轮 eval 发现并修复的 bug：callout 渲染位于 blockquote→p 转换之后导致永远不触发；已将渲染顺序调整为 sanitize 内部先识别 callout，再转换普通 blockquote，复测通过。
