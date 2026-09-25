# Pages CMS 网站维护使用手册

适用仓库：`DavidHMeng/energy-materials-lab-website`  
默认分支：`main`  
Staging 预览：<https://davidhmeng.github.io/energy-materials-lab-website/>
正式域名：<https://jliang.eitech.edu.cn/>（VM 完成人工部署后）
CMS 入口：<https://app.pagescms.org/>

本手册对应当前仓库的真实配置，不是通用示例。2026-09-23 已完成一次
Pages CMS 编辑、GitHub 提交、CI、GitHub Pages 部署、中英文页面检查和测试内容
清理闭环。

## 1. 首次进入

1. 打开 <https://app.pagescms.org/>，选择 **Sign in with GitHub**。
2. 选择账户 `DavidHMeng`。
3. 打开项目 **energy-materials-lab-website**。
4. 确认右上或侧边栏显示分支 **main**。

Pages CMS 直接编辑 GitHub 仓库中的 Markdown/YAML 文件，没有独立内容数据库。
每次点击 **Save** 都会产生 `main` 上的 Git commit，并自动触发 CI、翻译/fallback
检查和 production 静态分支发布。Pages CMS 不迁移到 VM，日常维护方式不变。

## 2. 日常编辑和发布流程

### 2.1 编辑内容

1. 从左侧 **Content** 选择内容类型。
2. 打开现有记录，或在集合页面选择新建记录。
3. 日常维护以中文为准：标为“中文（必填）”的字段必须填写；English 字段可留空。
4. 图片必须填写中文替代文本（Alt）；英文 Alt 留空时可由翻译流程生成。
5. 检查日期、排序、显示开关和外部链接。
6. 点击 **Save**。

保存后的 Git commit 使用以下格式：

- 新建：`content: add <filename>`
- 修改：`content: update <filename>`
- 删除：`content: remove <filename>`
- 重命名：`content: rename <old> to <new>`

News、Events、Research、Team 和 Opportunities 都不设占位记录数量下限，也不要求
保留特定 slug、文件名或占位图片。占位记录可以直接删除、通过 `display`/`active`
隐藏，或逐字段替换为真实内容；删除记录后，翻译流程会清理对应的状态缓存。

仍然保留的必要校验包括：中文必填字段、唯一且安全的 ID/slug、已配置的 Team Role、
ISO 日期、有效 DOI 与跨记录引用、图片文件存在和图片中文 Alt。保留中的记录必须满足
这些结构要求；若要删除一张共享图片，应先替换或删除所有引用该图片的记录。Homepage
Introduction 和 Site Settings 是页面结构配置，不属于可整体删除的集合；首页仍需至少
一张可显示的轮播图，站点身份、Logo、Header image 和 Typography 仍需保持有效。

### 2.2 检查构建

保存后先等待 GitHub Actions 的 **Validate and build** 变为绿色。失败时不要发布；
打开失败运行，查看第一个红色步骤。常见原因是中文必填字段缺失、日期格式错误、图片
路径不存在、中文 Alt 缺失、DOI 未登记或内部链接无效。

Actions 页面：
<https://github.com/DavidHMeng/energy-materials-lab-website/actions>

### 2.3 发布 staging 与 production

`main` 更新后，`Publish production static branch` 会依次检查 Citation、
Translation/fallback、内容、production build、内部链接和 SEO 输出；全部通过后，才把
纯静态网站更新到 `server-deploy`。VM 定时器后续从该分支拉取并原子切换，因此 CMS
编辑者不应 SSH 到服务器改 HTML。

CI 通过后，在 Pages CMS 左侧 **Actions** 中选择 **Deploy website**，可手工更新
GitHub Pages staging。该按钮运行 `deploy-pages.yml`，使用 staging 配置重新构建并发布。

重要：正式发布操作必须在 Pages CMS 的 `main` 分支上下文中执行。仓库的
`github-pages` 环境只允许 `main`，因此在 `codex/*` 或其他 QA/feature 分支点击
**Deploy website** 会在构建成功后被环境保护规则拒绝。这不是内容或图片错误。

如果正在检查尚未合并的分支，请使用 **Build staging artifact**；它会构建并校验
七天有效的可下载网站包，但不会覆盖公共 Pages。确认内容无误后，将分支合并到
`main`，再从 `main` 的 Actions 执行 **Deploy website**。

若 CMS 按钮暂未刷新，也可以在 GitHub Actions 中打开
**Deploy GitHub Pages (manual)**，选择 **Run workflow**，分支选 `main`。

staging 发布完成后检查：

- 英文首页：<https://davidhmeng.github.io/energy-materials-lab-website/>
- 中文首页：<https://davidhmeng.github.io/energy-materials-lab-website/zh/>
- 本次修改涉及的英文和中文页面。

GitHub Pages 可能缓存静态资源约十分钟。文字通常立即更新；样式或脚本若仍显示旧版，
等待缓存过期后再刷新，不要重复保存内容。

正式域名上线后，还应检查 `/version.json` 的 `source_commit` 是否对应本次 `main`
提交。正式站发生异常时，服务器管理员按 `DEPLOYMENT.md` 回切旧 release；内容编辑者
不要强制推送或直接修改 `server-deploy`。

## 3. 内容目录

| CMS 入口 | 维护内容 | 关键规则 |
| --- | --- | --- |
| Homepage Settings | 首页 Introduction 文字、轮播图、Highlights / Events 标题和数量 | 轮播图分 A/B 类型；科研图以 1.65:1 容器完整显示；可关联 DOI |
| Highlights / News | 动态、获奖、成员、论文、项目和公告 | 必填中英文标题/摘要/日期；空外链自动隐藏 |
| Events | 学术或课题组活动 | `Academic` 或 `Group`；结束日期不得早于开始日期 |
| Research | 研究方向 | 图文、中英文简介、DOI 列表、显示和顺序 |
| Publications | DOI 来源列表 | 可填裸 DOI 或 doi.org URL；系统统一规范化，不要手填作者、期刊或年份 |
| Team | 成员、圆形头像、简短介绍与个人页 | 支持 Profile Summary 与代表作 DOI；`slug` 稳定且唯一；离组成员关闭 `active` 或 `display` |
| Team Role Labels | 成员分类及其中英文标题 | 可维护博士后、访问学生等类别，也可新增未来类别 |
| Opportunities | 招聘与机会 | 使用日期窗口和 `active_override`；空类别自动隐藏 |
| Site Settings | 名称、学校、地址、邮箱、Logo、页头图和站点描述 | 替换占位内容时同时完成中英文信息 |
| Media | 上传站点图片 | 上传后在内容记录中选择，并填写双语 Alt |
| Actions | 构建、发布和 DOI 更新 | 先 CI，后发布；DOI 更新会创建 PR |

主导航固定为 `RESEARCH | PUBLICATIONS | TEAM | OPPORTUNITIES`。不要通过内容编辑
新增 Projects、Blog、Alumni、页脚导航或页脚语言链接。

## 4. 各模块操作要点

### Homepage Settings

- **Homepage Introduction** 位于 Highlights 上方，维护 Slogan、简介和轮播图片。
- 建议简介保持 1–2 段。页面已按文字约 43%、视觉约 57% 的节奏设计，不要在
  Introduction 中重复 Research 页的研究方向长文。
- 在 **Visual Slides** 中选择图片并填写双语 Alt；Caption 可留空。
- `Visual Type` 有两类：**A - Graphical Abstract** 与
  **B - Lab / Group Photo**。类型只用于维护和小标签，不会切换成不同页面结构。
- Graphical Abstract 会完整显示，不会自动裁切；上传前仍应去除大面积无效留白。
- 视觉容器约为 1.65:1，图片使用 `object-fit: contain`；不同原始比例允许出现少量
  上下或左右留白，不会为了铺满而裁掉文字、箭头或图例。
- `Related DOI` 可选。可填裸 DOI 或 doi.org URL；系统登记后从 Citation 系统读取期刊与年份；
  不要把作者、题名、期刊或年份手工复制到轮播数据。
- `Display Order` 越小越靠前；`Display` 可临时隐藏图片而不删除记录。
- `Seconds per slide` 建议使用 5–8 秒，允许范围为 5–12 秒。轮播会在鼠标悬停、
  键盘操作和系统“减少动态效果”设置下暂停或停用自动播放。
- `News items on homepage` 和 `Event items on homepage` 只控制首页显示数量。
- News 和 Events 的完整记录仍在对应集合中维护。
- 首页结构固定为 Introduction、Highlights、Events；不要在 CMS 中复制 Research
  页的详细研究内容。

### Highlights / News

- Category 只能选：Publication、Award、Member、Academic Achievement、Funding、
  Announcement。
- `display` 关闭后，记录保留在仓库中但不在网站显示。
- 有图片时必须填写中文 Alt；English Alt 可留空并由翻译流程生成。
- 外部链接为空时，“Learn more / 了解更多”不会显示。

### Events

- Type 只能选 Academic 或 Group；Category 可填写更具体的 Seminar、Workshop 等。
- 首页显示摘要卡片，归档页还会显示 Description 和 Gallery。
- 单日活动可将 End date 留空；多日活动必须保证结束日期不早于开始日期。

### Research

- `Graphical Abstract` 使用统一比例的正式研究图。
- `DOI list` 每行只写 DOI，例如 `10.1002/adma.202102415`，不要复制书目信息。
- `Order` 越小越靠前；`display` 关闭后整条研究方向隐藏。

### Publications

1. 在 DOI 字段填写裸 DOI、完整 doi.org 地址或 `DOI:` / `DOI：` 前缀，例如
   `10.1002/adma.202102415` 或 `https://doi.org/10.1002/adma.202102415`。
2. 需要关联成员时，在 `member_ids` 填 Team 中对应的稳定 slug。
3. 保存后，GitHub 会自动规范化 DOI、去重并汇入中央 Citation Registry；也可打开
   **Actions → Synchronize DOI citations** 手动刷新。
4. 工作流从 DOI 获取书目信息；临时网络失败时保留缓存元数据，首次解析失败则显示
   `Publication metadata pending` 和 DOI 链接，不会让整站构建失败。
5. 检查 PR 中作者、标题、期刊、年份和 DOI 后再合并。
6. 合并并通过 CI 后，再执行 **Deploy website**。

Research 和 Team 都通过 DOI/成员 ID 引用同一出版物；不要在多个模块复制作者、
题名、期刊和年份。

### Team

- `Member ID / slug` 只能使用小写字母、数字和连字符，是双语个人页的稳定路由 ID。
  新建记录会按 slug 创建文件；已有记录即使文件仍保留旧名称，模板也会按 slug 生成
  英文和中文相同的个人页路由，因此可以安全修改。完整示例和所有模块的输入契约见
  [`CMS_INPUT_FORMATS.md`](CMS_INPUT_FORMATS.md)。
- `Role ID` 必须对应 **Team Role Labels** 中的 ID。常用分类已包含 PI、博士后、
  博士生、硕士生、本科生、访问学生、科研人员和行政人员。
- `active: true` 且 `display: true` 时成员才显示。
- 离组成员将 `active` 或 `display` 设为 false；不要创建 Alumni 页面。
- `Short research area EN / ZH` 显示在团队圆形头像下，建议控制为一句话；过长内容
  在列表页只显示两行，完整研究兴趣可填入 Research interests。
- `Personal Note EN / ZH` 对应个人页的 **Personal Note / 个人寄语**，可留空。
  只允许纯文本和换行，不要粘贴图片、表格、HTML 或富文本。
- `Profile Summary ZH` 是个人页顶部的学术背景简介，建议说明学术背景、当前方向与
  专业兴趣，不要重复下方 Education；English 可留空或手工覆盖。
- `Representative Publication DOIs` 每行填写一个已经在 Publications 登记的 DOI，
  通常选择 3–6 篇。也可直接粘贴 doi.org URL；保存后会自动规范化、登记并复用统一
  Citation 组件，不手填书目信息；留空时整节隐藏。
- 个人页不显示 Biography、Phone 或 Office；联系方式以 Email 为主。
- Email、Address、Google Scholar、ORCID、ResearchGate、个人网站和 GitHub 为空时
  会自动隐藏，不会留下空图标或空白行。
- `Affiliation EN / ZH` 显示在个人页姓名和身份下方；`Address EN / ZH` 显示在左侧
  联系信息栏。两者都可以留空。
- ORCID 字段只填写 ORCID 标识，不要添加重复的展示文字。
- Team 不要求保留任何占位成员或固定人数。删除、隐藏或替换成员不会因布局测试而阻断
  CI；多人布局与末行居中由独立回归测试和浏览器验收负责。

### Team Role Labels

- 修改 `Display Label EN / ZH` 即可调整 Team 页分类标题，不必改模板。
- 新增分类时先建立唯一的 `Role ID`（小写字母、数字、连字符），再在成员记录中填写
  同一个 ID。例如 `visiting-scholars`。
- `Display category` 关闭后分类标题不显示；属于该分类的成员记录仍保留。
- 不要新建 Alumni 分类；离组成员继续使用 `active` 或 `display` 隐藏。

### Opportunities

- `auto`：按 Opening Date 和 Closing Date 自动判断。
- `force_show`：忽略日期，强制显示。
- `force_hide`：忽略日期，强制隐藏。
- `display: false` 是最高优先级的隐藏开关。
- 日期采用 `YYYY-MM-DD`；链接中文标签必填，英文标签可留空并自动生成。

### Site Settings 与 Media

- 先在 **Media** 上传图片，再回到内容记录选择图片。
- 建议使用 SVG（Logo/示意图）、WebP（照片）或优化后的 PNG/JPEG。
- Logo 优先使用 SVG 或带 alpha 通道的透明 PNG；避免 JPG、截图和导出时自带白色/
  灰色画布的文件。CMS 保留原始文件格式，不会把透明 Logo 自动转换为 JPEG。
- 文件名使用小写英文、数字和连字符，避免空格及中文文件名。
- Header image、Lab logo、School logo 和站点联系信息都是全站字段，保存前应由
  负责人确认。

### Site Settings → Typography

Typography 只提供经过验证的 preset，不提供任意字体名称、像素值、颜色或 HTML
style。这样可以在调整层级的同时保护手机端排版和中英文一致性。

- **Heading Font**：Default、Sans Modern、Sans Academic、Serif Editorial。
- **Body Font**：Default、Sans、Serif。
- **Lab Name Size**：控制 Homepage 实验室名称。
- **Navigation Size**：控制四个固定主导航项。
- **Page Title Size**：控制页面主标题。
- **Section Title Size**：控制 Team 分类及模块标题。
- **Body Text Size**：控制正文基础字号。
- **Caption Size**：控制图片说明和辅助文字。
- **Line Height**：Compact、Default、Relaxed。

字号类字段均选择 Small、Default 或 Large。Large 在桌面端放大，但前端会通过
`clamp()` 自动限制手机端尺寸；维护人员不需要也不能填写 `37px`、`1.473em` 等
自由值。修改后先保存并等待 CI，通过后再运行 **Build staging artifact** 检查中英
文、手机端和 Light/Dark，确认无误后再执行生产部署。

## 5. 四个 Actions 按钮

- **Generate pending English**：为英文空白或原先自动生成的字段生成学术网站英文；
  永不覆盖人工英文。

- **Deploy website**：生产构建并发布 GitHub Pages。
- **Build staging artifact**：构建并验证七天可下载的 `_site` 产物，不公开发布。
- **Synchronize DOI citations**：规范化并收集全站 DOI，解析元数据并在有变化时更新中央 Registry。

按钮默认显示确认对话框。生产发布前应先确认内容 commit 对应的 CI 已通过。

## 6. 双语内容工作流

1. 平时只填写中文即可；中文是必填内容源。
2. English 字段可留空。配置翻译服务后，保存会触发独立的英文生成工作流。
   Pages CMS 可能会直接省略空白 English 键，而不是保存为空字符串；当前脚本同时支持
   “空字符串”和“键不存在”两种情况，无需为触发翻译手工输入空格或占位符。
3. 人工填写或修改过的英文优先级最高，自动流程永不覆盖。
4. 中文修改时：自动生成的英文会重新生成；人工英文会保留并在后台状态中标记为
   `needs-review`，提醒后续人工核对。
5. 官方学校、学院、课题组、人名、职位、项目和地址英文建议人工填写；系统不会猜测
   人名拼音或官方机构名称。
6. Publications 中的题名、作者、期刊、年份、卷期页码、DOI、Citation 及自定义记录
   全部排除在翻译流程之外。
7. 翻译服务暂时失败时，英文路由会显示对应中文源内容并在构建日志中提示，不会出现
   空白模块，也不会让网站构建或部署中断。
8. 本项目不维护术语表；固定风格为简洁、自然、克制的学术机构网站英文，不使用夸张
   营销表达，也不增加中文原文没有的信息。

自动生成需要仓库管理员在 GitHub 设置唯一机密项 `TRANSLATION_API_KEY`，并设置
`TRANSLATION_MODEL` 变量。密钥只能存放在 GitHub Actions Secrets，不能写入 CMS、
YAML、JavaScript、聊天截图或 Git 历史。未配置时其余编辑、CI、staging 和部署照常工作。
此时 **Generate pending English** 会成功完成检测与完整网站构建，并将字段记录为
`pending`，但不会伪造英文；英文页面临时显示对应中文内容。按钮显示绿色只表示链路与
构建正常，不表示已经调用了翻译模型。

## 7. 出错与回退

### Save 后 CI 失败

1. 不要运行 Deploy website。
2. 打开失败的 Actions 运行，查看第一个失败步骤。
3. 回到 Pages CMS 修正字段并再次保存。
4. 新提交通过后再发布。

### 内容保存错误

优先在 Pages CMS 恢复原字段并再次保存，这会留下清晰的修正历史。若文件已损坏或
CMS 无法打开，由维护者在 GitHub 提交历史中对单个 commit 执行 revert。不要使用
强制推送或 `git reset --hard` 清除共享历史。

### 网站仍是旧内容

依次确认：

1. Pages CMS 已显示保存完成；
2. GitHub 仓库出现新的 `content:` commit；
3. Validate and build 已通过；
4. staging 问题：Deploy GitHub Pages 已成功；production 问题：Publish production
   static branch 已成功且 VM 定时同步已运行；
5. 打开的 URL 包含 `/energy-materials-lab-website/`；
6. 等待短时 CDN/浏览器缓存后刷新。

## 8. 已验证的闭环证据

- CMS 测试提交：[`2c85add`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/2c85addf9cc163132b0090fcd0b05d7d4b98e861)
- 测试提交 CI：[`35822457262`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822457262)
- 测试部署：[`35822539380`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822539380)
- 清理提交：[`4205075`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/4205075dea98e9f9943c8561de0278b1b9ca8c73)
- 清理提交 CI：[`35822706745`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822706745)
- 清理部署：[`35822768415`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822768415)

测试中英文标题曾分别显示 `[CMS validation]` 与 `【CMS 验证】`，随后已恢复原值；
英文和中文公开页面均确认不再包含测试标记。
