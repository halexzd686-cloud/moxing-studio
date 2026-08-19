# Moxing Studio — 项目交接文档

> 更新时间：2026-08-19  
> 版本：v1.0 发布候选版  
> 状态：Phase 3 验收完成；Phase 4 本地发布完成，待 GitHub 重新认证后推送

## 一、项目概览

Moxing Studio 是面向职场汇报场景的单页图表 Skill：输入数据，输出 `1280×720` 定尺、可直接投屏或导出 PNG 的单文件 HTML 图表。

- 10 个图型 × 6 套主题，共 60 种组合。
- 图表主体为内联静态 SVG，无外部依赖和运行时布局计算。
- JavaScript 仅增强 tooltip；禁用 JavaScript 后图表仍完整可见。
- 中文字体使用系统降级栈，不依赖网络字体。

## 二、已完成

### Phase 1 — 全链路

- [x] 六套主题令牌：`tokens/themes.js`
- [x] Skill 规则与选型决策树：`SKILL.md`
- [x] 10 个静态 SVG 模板生成器：`scripts/build_templates.py`
- [x] 60 卡片验收画廊生成器：`scripts/build_gallery.py`
- [x] PNG 导出：`scripts/export.py`

### Phase 2 — 10 个图型

| 编号 | 图型 | 模板 | 状态 |
|---|---|---|---|
| C1 | 柱状图 | `templates/c01-bar.html` | 通过 |
| C2 | 条形图 | `templates/c02-hbar.html` | 通过 |
| C3 | 折线图 | `templates/c03-line.html` | 通过 |
| C4 | 环形图 | `templates/c04-donut.html` | 通过 |
| C5 | 堆叠柱 | `templates/c05-stacked.html` | 通过 |
| C6 | 瀑布图 | `templates/c06-waterfall.html` | 通过 |
| C7 | 甘特图 | `templates/c07-gantt.html` | 通过 |
| C8 | 漏斗图 | `templates/c08-funnel.html` | 通过 |
| C9 | 指标卡 | `templates/c09-kpi.html` | 通过 |
| C10 | 对比卡 | `templates/c10-compare.html` | 通过 |

C7 已正式统一为甘特图，`SKILL.md`、构建脚本、模板和画廊口径一致。C10 标题已改为结论型标题“华东营收领先，华南同比下滑”。

### Phase 3 — 验收

- [x] 构建脚本可重复执行，生成 10 个模板与 60 卡片画廊。
- [x] 六套主题完成自动切换、对比度与目视检查。
- [x] 六套 C10 主题样张已生成到 `docs/previews/`。
- [x] 10 个模板启用 JavaScript时正常渲染。
- [x] 10 个模板禁用 JavaScript 时正常渲染。
- [x] 控制台零错误，零外部请求。
- [x] 固定画布、静态 SVG、无 canvas 等结构检查通过。
- [x] 64 个边界数据生成用例通过：单点、多点、空数据、空值、负数、全相同、超长中文和亿级数字。
- [x] PNG 导出实测通过，输出尺寸为 `2560×1440`。

自动验收结果：`docs/previews/qa-report.json`，状态为 `passed`。

### Phase 4 — 发布材料

- [x] `README.md`
- [x] `LICENSE`（MIT）
- [x] 六套主题预览图
- [x] 2560×1440 C10 导出样张
- [x] 初始化本地 Git 仓库，默认分支为 `main`
- [x] 创建首个发布提交与 `v1.0` tag
- [x] 配置远端 `https://github.com/halexzd686-cloud/moxing-studio.git`
- [ ] 推送主分支与标签（当前 GitHub CLI 登录令牌已失效，需重新认证）

## 三、本轮新增的健壮性处理

`scripts/build_templates.py` 现在统一处理有限实数与空值：

- C1/C2：支持正负数和零线；无有效数据时显示静态空状态。
- C3：Y 轴始终包含零点，支持负值；数据长度不一致或存在空值时显示空状态，避免误连线。
- C4/C8：过滤不符合占比／漏斗契约的非正值。
- C5：空值按缺失段处理为 0，负值不进入堆叠。
- C6：过滤无效增减项。
- C7：过滤无效日期，进度约束在 0–100。
- C9/C10：无有效 KPI 时显示空状态，同比／环比缺失时显示破折号。

## 四、构建与验收命令

```powershell
python scripts/build_templates.py
python scripts/build_gallery.py
python scripts/test_boundaries.py
python scripts/export.py templates/c10-compare.html output.png
```

浏览器验收：

```powershell
node scripts/validate.mjs .
```

若 Playwright 或浏览器不在默认位置，设置：

```powershell
$env:MOXING_PLAYWRIGHT_PATH = '<playwright 包目录>'
$env:MOXING_BROWSER_EXECUTABLE = '<chrome.exe 或 msedge.exe>'
node scripts/validate.mjs .
```

## 五、文件结构

```text
moxing-studio/
├── SKILL.md
├── README.md
├── LICENSE
├── HANDOFF.md
├── tokens/
│   └── themes.js
├── templates/
│   ├── c01-bar.html ... c10-compare.html
│   └── gallery.html
├── scripts/
│   ├── build_templates.py
│   ├── build_gallery.py
│   ├── export.py
│   ├── test_boundaries.py
│   └── validate.mjs
└── docs/
    └── previews/
        ├── paper.png / ink.png / boardroom.png
        ├── tech.png / mori.png / dawn.png
        ├── c10-compare@2x.png
        └── qa-report.json
```

## 六、剩余发布条件

本地仓库、`main` 分支、发布提交、`v1.0` 标签和 `origin` 均已准备完成。当前唯一阻塞是 GitHub CLI 中 `halexzd686-cloud` 账号的登录令牌已经失效。

重新执行 `gh auth login -h github.com` 完成登录后，运行：

```powershell
git push -u origin main
git push origin v1.0
```

推送过程不使用 `--force`，不会主动覆盖远端历史。
