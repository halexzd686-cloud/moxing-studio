# Moxing Studio v2

Moxing Studio 把中文商业数据生成具有结构装配动画的离线 HTML/SVG 图表。它不是一组 PPT 主题，而是一套统一的 **Structural Interface / 结构接口**：数据先对齐基准、装配构件、接通关系，最后锁定结论。

## Visual language

- 建筑秩序主导，东方当代气质来自比例、留白和中文排版。
- 基准脊线、榫接接口、证据铭牌和氧化橙锁定标记构成统一签名。
- 冷白工程纸为默认，配套深色仪器面板。
- 动画遵循 `ALIGN → DOCK → ROUTE → LOCK`。
- 无 JavaScript 或减少动态效果时，直接显示完整静态终态。

## Charts

| ID | Name | Use |
|---|---|---|
| C1 | Structural Rank | 少量类目比较 |
| C2 | Ranked Rail | 排名、长类目名 |
| C3 | Signal Trend | 时间趋势 |
| C4 | Composition Field | 占比构成 |
| C5 | Composition Bands | 构成随时间/类目变化 |
| C6 | Ledger Steps | 增减分解 |
| C7 | Milestone Lanes | 项目排期 |
| C8 | Stage Channel | 阶段转化 |
| C9 | Metric Lockup | 单个 KPI |
| C10 | Decision Interface | 2–4 个 KPI 对比 |

## Generate

生成默认模板和动画画廊：

```powershell
python scripts/build_templates.py
python scripts/build_gallery.py
```

从 JSON 生成可独立发送的单文件 HTML：

```powershell
python scripts/render.py --chart C3 --data data.json --output chart.html `
  --title "增长在下半年加速，年末达到新高" `
  --subtitle "单位：万元 · 2025 年 1–12 月" `
  --footer "数据来源：内部经营系统 · 口径：含税收入"
```

打开 [templates/gallery.html](templates/gallery.html) 查看十种动画图表。

## Export

```powershell
python scripts/export.py chart.html chart.png
node scripts/export-motion.mjs chart.html chart.webm standard
```

视频脚本支持 WebM；首次使用可运行 `npx playwright install ffmpeg` 安装录制组件。系统安装 `ffmpeg` 后还可输出 MP4/GIF。静态导出固定为 `2560×1440`。

## Validation

```powershell
python scripts/test_boundaries.py
node scripts/validate.mjs .
```

浏览器验收覆盖：浅/深模式、动画播放、禁用 JavaScript、减少动态效果、外部请求、字体加载、页面溢出和锁定状态截图。

## Fonts and licensing

仓库包含经过 GB2312 常用字符压缩的 Noto Sans SC、Noto Serif SC 和 Doto WOFF2，用于离线渲染。字体遵循各自的 SIL Open Font License，许可证位于 `assets/fonts/`。

项目代码使用 [MIT License](LICENSE)。v1 完整版本保存在 Git 标签 `v1.0`，主分支不重复维护旧模板和旧主题。
