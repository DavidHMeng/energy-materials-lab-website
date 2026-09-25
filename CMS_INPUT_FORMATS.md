# Pages CMS 输入格式与部署契约

更新：2026-09-25

这份文件记录当前 `.pages.yml` 的真实编辑契约。它不是要求维护者记忆 YAML；Pages CMS 会在界面上显示必填、选项和部分正则提示。提交前仍应按下面的格式填写，以便 `main` 上的 CI 能直接构建并发布。

## 先看结论

- 当前有 9 个可编辑模块、146 个字段（含嵌套对象字段），其中 67 个字段由 CMS 标记为必填。
- 目前发现并修复的本次失败原因不是“格式限制过严”，而是 Team 记录的 `slug` 被改成 `jianwen-liang`，文件仍叫 `mei-li.md`。英文页面按文件名生成，中文页面按 `slug` 生成，两个路由因此不一致。
- Team 的 `slug`、Team Role 的 `id`、DOI、日期和固定下拉选项属于结构性约束，不能安全地全部取消；取消会破坏文件名、双语路由、成员引用、引用注册表或日期逻辑。
- 已让成员生成器、语言切换和 alternate metadata 都按实际 `slug` 生成两种语言的同一路由；现有 CMS 文件即使保留旧文件名也可以安全修改 slug，生成站点检查按实际成员 slug 动态验证，不再硬编码 `mei-li`。
- 中文字段继续是主要编辑源；英文可留空，由可选英文生成流程处理。Publication 记录不进入翻译流程。

## 模块统计

| CMS 模块 | 编辑字段数 | 必填字段 | 主要限制 |
| --- | ---: | ---: | --- |
| Homepage Settings | 24 | 14 | slide 类型、图片、DOI、顺序、显示开关 |
| Highlights / News | 11 | 4 | category、日期、图片与 alt 配对 |
| Events | 16 | 4 | Academic/Group、日期、结束日期不能早于开始日期 |
| Research | 10 | 5 | Graphical Abstract、DOI 列表、顺序 |
| Publications | 7 | 1 | DOI 是唯一必填标识，出版物内容不翻译 |
| Team | 33 | 9 | slug、role、头像、中文核心字段、代表性 DOI |
| Team Role Labels | 5 | 3 | role ID、中文标签、顺序 |
| Opportunities | 14 | 7 | category、active override、日期、链接 |
| Site Settings | 26 | 20 | 图片、中文站点信息、受控 Typography 预设 |
| **合计** | **146** | **67** | 含对象和列表中的嵌套字段 |

## 必须遵守的格式

### 1. Team Member ID / slug

截图中的 `Member ID / slug` 是路由和文件名标识，不是普通显示名称。只允许小写 ASCII 字母、数字和连字符：

```text
正确：jianwen-liang、doctoral-researcher-08、visitor-2026
错误：Jianwen Liang、梁剑文、member_id、member/one
```

`slug` 控制公开路由；新建记录的文件名也会按 slug 创建。修改已有记录时不必手动改 Windows 文件名，站点生成器会统一两种语言的路由：

```text
slug: jianwen-liang
源记录：_members/mei-li.md（已有记录可保留旧文件名）
英文：/team/jianwen-liang/
中文：/zh/team/jianwen-liang/
```

不要把文件名当作显示名称；新记录由 CMS 的 `{slug}.md` 模板创建。当前 CI 会检查所有实际生成的中英文 profile 路由，避免两种语言树再次分叉。

### 2. Team Role ID 和下拉选项

`role` 必须是 `_data/team_roles.yaml` 中已经存在的 ID，同样只用小写字母、数字和连字符，例如 `pi`、`phd-students`、`visiting-students`。类别显示文字在 Team Role Labels 的 `label_zh` / `label_en` 中维护；不要把中文显示名称直接填入 `role`。

当前固定选项包括：

- Homepage Visual Type：`graphical-abstract` 或 `lab-photo`
- News Category：`Publication`、`Award`、`Member`、`Academic Achievement`、`Funding`、`Announcement`
- Event Type：`Academic` 或 `Group`
- Opportunity Active Override：`auto`、`force_show`、`force_hide`
- Site Typography：预设字体、字号和行高选项；不开放任意 CSS 值

这些值用于模板分支、排序或可访问性，不能改成自由文本。

### 3. DOI

Publication 的 `DOI` 必填；Research DOI list、Homepage related DOI、Team representative DOIs 为可选列表。以下形式均可：

```text
10.1021/jacs.5c22628
https://doi.org/10.1021/jacs.5c22628
DOI:10.1021/jacs.5c22628
DOI：10.1021/jacs.5c22628
```

系统会去除前缀、统一大小写并写入共享 citation registry。Publication 的标题、作者、期刊、年份等不会走中文→英文自动翻译。

### 4. 日期、数字和顺序

- 日期统一 `YYYY-MM-DD`，例如 `2026-09-25`。
- Event 的 `end_date` 不得早于 `date`；Opportunity 的 `closing_date` 不得早于 `opening_date`。
- `order`、`display_order` 和 slide order 使用数字；不要输入带单位或带文字的值。
- Homepage `autoplay_seconds` 推荐 5–8 秒（当前验证器允许的安全范围为 5–12）；首页数量限制使用正整数。

### 5. 图片、alt 和文本类型

- 图片从 Media library 的 `images/uploads` 选择，保存路径以 `/images/uploads/` 开头；不要把本地 Windows 路径粘到内容字段。
- Homepage、Research、Team、Site 的必需图片必须同时填写中文 alt；alt 是对图像内容的简短描述，不是文件名。
- Rich-text 的媒体插入目前有意关闭于 Publications 自定义备注、Events 描述、Team Education、Opportunities 内容。这样可避免编辑器写入无法被校验或部署的外部附件；需要图片时使用专门的 image 字段。
- Personal Note 是纯文本，不接受 HTML、表格或图片。

### 6. 中英文字段

中文字段是必填源；多数英文编辑字段为可选。英文为空时，Actions 可生成学术化英文；人工填写的官方英文优先且不会被覆盖。姓名、官方机构名和 Publication 记录不自动猜测或翻译。

## 当前验证结果

| 项目 | 结果 | 证据/说明 |
| --- | --- | --- |
| Homepage、News、Events、Research、Publications、Team、Opportunities、Site 的历史 CMS 编辑矩阵 | PASS | 见 `CMS_ACCEPTANCE_REPORT.md`；此前已验证保存、显示开关、顺序、图片选择和 CI |
| DOI 四种输入形式 | PASS | `scripts/test_cms_schema.py` 与 `scripts/test_cms_input_contract.py` |
| 当前 Team 成员修改后的主链构建 | PASS | 修复提交 `c42baf4` 后，`Validate and build` run `36136604546`、production static branch run `36136604861` 和 staging deploy run `36136792298` 均成功 |
| 全部字段的静态契约检查 | PASS | `scripts/test_cms_input_contract.py` 已纳入 CI，统计模块、嵌套字段、正则、下拉项、日期、图片和富文本边界；当前 `main` 的验证 run `36136604546` 成功 |
| 浏览器中新上传本地文件 | PARTIAL | 既有 Media 选择已验证；当前自动化浏览器对本地文件选择器曾返回 `Not allowed`，不影响已存在媒体文件的部署 |

## 提交后的正确路径

1. 在 Pages CMS 选择 `main`，编辑并保存。
2. Team 若修改 Member ID，应让 CMS entry/file 名称与 slug 一致；不要只改字段。
3. 等待 `Validate and build`、`Generate optional English`（如触发）和 `Publish production static branch` 完成。
4. 只有 `main` 才允许进入 `github-pages` 环境；QA/功能分支应使用 Build staging artifact。
5. Pages CMS 的 `Deploy website` 应在 `main` 上执行；若某次失败，先打开失败 job 的具体步骤，不要重复点击 Deploy。当前站点 staging 地址为：<https://davidhmeng.github.io/energy-materials-lab-website/>。
