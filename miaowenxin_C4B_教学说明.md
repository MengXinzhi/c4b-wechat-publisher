# miaowenxin-wechat-publisher 教学说明

> C4B 挑战交付物 ｜ 作者：苗文馨 ｜ 2026-10-04

## 一、这是什么

一个把 Markdown / Word 文档转换为「公众号可直接粘贴」HTML 的技能包。
在 C4B starter kit 基础上新增 7 项能力：多主题、callout 高亮框、自动目录、
文章元数据文头、页脚版权、中英文自动间距、批量转换。

## 二、安装

### 方式 A：作为 WorkBuddy 技能（推荐）

把技能包解压或复制到用户技能目录：

```
C:\Users\<用户名>\.workbuddy\skills\miaowenxin-wechat-publisher\
```

重启 WorkBuddy 后，对话中说「帮我把这篇文章转换成公众号格式」即可触发。

### 方式 B：仅用命令行脚本

```bash
# 1. 解压 miaowenxin-wechat-publisher.zip
# 2. 安装依赖（脚本首次运行也会自动安装）
pip install markdown beautifulsoup4 python-docx lxml

# 3. 转换
python scripts/convert_to_wechat.py 文章.md 输出.html
```

## 三、使用

### 基础转换

```bash
python scripts/convert_to_wechat.py input.md output.html
```

### 常用参数

| 参数 | 作用 |
|------|------|
| `--theme default\|blue\|warm\|minimal` | 切换配色主题 |
| `--toc` | 自动生成"本文目录" |
| `--author 名字` | 覆盖页脚/文头的作者名 |
| `--footer-text "文本"` | 自定义页脚（覆盖默认版权） |
| `--no-cjk-space` | 关闭中英文自动加空格 |
| `--batch 目录 --outdir 目录` | 批量转换整个目录 |

### Callout 高亮框写法（Markdown 源文件中）

```markdown
> 📘 知识点：微信只接受 inline CSS。
> 🔧 实践：先跑通最小用例再迭代。
> ⚠️ 注意：h1 和 div 会被公众号剥离。
> 💡 提示：发布前用手机预览。
```

### 文章元数据写法（Markdown 文件顶部）

```markdown
---
title: 文章标题
author: 你的名字
date: 2026-10-04
abstract: 一句话摘要，会显示在文头卡片里。
---
```

## 四、发布流程（SOP）

1. 用 Markdown 写好文章（含 frontmatter、callout）
2. 运行转换命令生成 `output.html`
3. 浏览器打开预览，确认排版满意
4. 在页面中 Ctrl+A 全选 → Ctrl+C 复制
5. 打开 mp.weixin.qq.com → 新建图文 → Ctrl+V 粘贴
6. 检查图片（外链图片需在公众号媒体库重新上传）
7. 手机预览 → 群发发布

## 五、常见问题

| 问题 | 解决 |
|------|------|
| 粘贴后样式丢失 | 检查源 HTML 是否被二次编辑引入了 class/style 标签，重新转换 |
| 图片消失 | 外链图片需上传公众号素材库；SVG 不支持，改用 PNG |
| 中英文没空格 | 确认没有加 `--no-cjk-space` |
| 想改主题颜色 | 编辑 `scripts/convert_to_wechat.py` 里的 `THEMES` 字典 |
