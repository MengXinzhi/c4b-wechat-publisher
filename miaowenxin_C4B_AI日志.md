# AI 使用日志 — C4B 公众号文章生成技能

> C4B 挑战交付物（评审必读）｜ 作者：苗文馨 ｜ 记录时间：2026-10-04
> 本文如实记录与 AI（WorkBuddy Agent）协作完成 C4B 的全过程、每轮 prompt 的意图与产出、以及迭代中的失败与修复。

## Round 0 — 任务启动

**我的输入：**

> "E:\挑战合集\挑战_C4B 公众号文章生成技能_bp05rs_完整资料 帮我完成挑战，要下载的内容下载到D盘或者E盘"

**AI 做了什么：**
- 读取 CHALLENGE.md / rubric.json，确认交付物清单与评审维度（内容质量 25 分、AI 使用质量 20 分、复盘质量 20 分、产物完整性 15 分、传播设计 20 分）
- 建立四步任务计划：跑通 starter → skill-creator 定制 → 写文章转换 → 生成提交文件
- 解压 starter kit 到 `E:\挑战合集\C4B_作业\starter`

## Round 1 — Level 1：跑通 starter kit（理解阶段）

**AI 做了什么：**
- 通读 starter kit 全部 6 个文件，总结已有能力（md/docx 读取、标签过滤、inline CSS）与缺失能力清单
- 创建 Python venv，安装 markdown / beautifulsoup4 / python-docx / lxml
- 跑通 `convert_to_wechat.py examples/sample_article.md starter_output.html`，确认输出无 h1/div/script

**这一轮的价值：** 先理解再动手，明确"拿来什么"的边界。

## Round 2 — Level 2：按 skill-creator 流程定制（开发阶段）

**AI 做了什么：**
- 加载 skill-creator 技能，按其六步流程执行：理解用例 → 规划可复用资源 → `init_skill.py` 初始化骨架 → 编辑 → eval → `package_skill.py` 打包
- 从挑战"缺失能力清单"中选定 7 项新增能力（超过"至少 2 项"的要求）：多主题 / callout / 目录 / 元数据 / 页脚 / CJK 间距 / 批量转换
- 重写 `SKILL.md`（description 优化触发条件）、新增 `evals/` 用例与报告

**关键迭代记录（失败与修复）：**

1. **失败 1：callout 永远只渲染第一个。** eval 首轮输出显示 📘 框存在、🔧/⚠️/💡 框缺失。排查发现 Python-Markdown 把连续的 `>` 引用块合并进同一个 `<blockquote>`，而逻辑按"每个 blockquote 一个 callout"编写。
   **修复：** 改为逐 `<p>` 段落识别 emoji 标记并拆分为独立高亮框，blockquote 处理为 unwrap。复测四个框全部通过。
2. **失败 2：打包验证报错 "Description cannot contain angle brackets"。** SKILL.md 的 description 使用了 YAML 的 `>` 折叠标量，被验证器误判。
   **修复：** 改为单行引号描述，重新打包通过。
3. **失败 3（环境类）：** 本会话的 bash 环境缺失 coreutils（ls/mkdir 不可用），且 PowerShell 删除文件被环境拦截导致旧示例文件混入首个 zip。
   **修复：** 全部文件操作改用 Python 的 os/shutil 完成，清理后重新打包。

**最终打包结果：** `package_skill.py` 验证通过，生成 `miaowenxin-wechat-publisher.zip`（含 SKILL.md、scripts、references、evals 共 9 个文件）。

## Round 3 — Level 3：写作与转换（验证阶段）

**AI 做了什么：**
- 与我确认选题：以"本次 C4B 改造经历"为题（同时满足挑战"写你的技能说明/学习心得"的建议，可计入 C7 首篇产出）
- AI 起草《我用 AI 把一个 starter kit 改造成了公众号排版引擎》，含 frontmatter 元数据、4 种 callout、表格、代码场景
- 用定制技能转换：`--theme blue --toc`，生成 `miaowenxin_C4B_output.html`
- 校验输出：无 h1/div/script、含目录/文头/页脚/四色 callout/中英文间距

**我的角色（human-in-the-loop）：**
- 确认选题方向与新增能力优先级
- 审阅文章观点表述（"先交比不交强""eval 是安全网"）
- 最终发布动作由我在公众号后台完成（AI 无公众号账号权限）：粘贴 → 手机预览 → 群发，链接见《miaowenxin_C4B_文章链接.md》

## 使用的工具链

| 环节 | 工具 |
|------|------|
| 挑战解读 | WorkBuddy Agent（读文件/任务管理） |
| 技能开发 | skill-creator（init_skill.py → 编辑 → eval → package_skill.py） |
| 代码实现 | WorkBuddy Agent 生成 + 我审阅逻辑（尤其 callout 拆分与 CJK 正则） |
| 测试 | 自建 eval 用例 4 组（全功能/主题切换/间距开关/批量），见 eval_report.md |
| 文章写作 | AI 起草 + 我定稿 |

## 经验沉淀

1. **先跑通再改造**：Level 1 的 30 分钟理解，避免了 Level 2 推翻重写的浪费。
2. **eval 用例要覆盖"自以为没问题"的路径**：blockquote 合并 bug 正是用例设计逼出来的。
3. **元技能的元技能**：skill-creator 把"做技能"本身流程化，其价值在格式约束（description 规则、agent_created 标记）和验证脚本，而非模板文字。
