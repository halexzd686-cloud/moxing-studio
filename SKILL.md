---
name: moxing-studio
description: 生成具有结构装配动画和静态降级能力的中文商业、金融与分析图表。输入比较、趋势、构成、电商经营、市场、风险、预测或统计数据，输出离线 HTML/SVG，并可导出 PNG、WebM、MP4 或 GIF；适用于 PPT、路演、经营分析、投研和网页数据故事。
---

# Moxing Studio v2

把数据组织成一页一个判断的 **Structural Interface / 结构接口**。图表的最终状态必须先成立，动画再通过定位、装配、接通和锁定解释关系。

## Workflow

1. 按数据形状、行业问题、标签长度和阅读速度选择 C1–C24。读取 [references/chart-contracts.md](references/chart-contracts.md) 获取契约、家族复用与选型边界。
   需要可复制输入时，从 `examples/data/` 选择对应 ID 的 JSON；这些示例由 `scripts/export_examples.py` 从受测试保护的默认数据生成。
2. 选择 `brief` 或 `editorial`。汇报默认 `brief`；文章、网页或需要解释证据时使用 `editorial`。需要动画时再选 `brief`、`standard` 或 `story` 时间轴，三者不是简单倍速。
3. 默认使用冷白画布。用户明确要求深色、发布展示或仪器感时使用 `dark`。
4. 标题写判断，不写图型名。单位、时间范围、口径和来源进入副标题或底行。
5. 用 `scripts/render.py` 生成独立 HTML；需要图片或视频时再调用导出脚本。
6. 按本文和相关参考文件自检后交付。

视觉或构图判断不明确时读取 [references/visual-charter.md](references/visual-charter.md)。修改动画、节奏或触发方式时读取 [references/motion-system.md](references/motion-system.md)。

## Render

```powershell
python scripts/render.py --chart C3 --data data.json --output chart.html `
  --title "增长在下半年加速，年末达到新高" `
  --subtitle "单位：万元 · 2025 年 1–12 月" `
  --footer "数据来源：内部经营系统 · 口径：含税收入"
```

默认把开源字体嵌入 HTML，适合独立交付。仓库内批量模板使用 `--linked-fonts` 避免重复体积。

## Export

```powershell
python scripts/export.py chart.html chart.png
node scripts/export-motion.mjs chart.html chart.webm standard
node scripts/export-motion.mjs chart.html chart.mp4 brief
```

首次录制可运行 `npx playwright install ffmpeg` 安装 Playwright 录制组件。MP4/GIF 转换还需要系统 `ffmpeg`；没有时交付 WebM。PNG 始终截取动画完成后的锁定状态。

## Non-negotiable rules

- 最终 SVG 几何在生成阶段完成。JavaScript只编排动画，不计算核心布局。
- 禁用 JavaScript 或启用减少动态效果时，直接显示完整锁定状态。
- 动画必须按 `ALIGN → DOCK → ROUTE → LOCK` 解释真实结构，不使用随机、弹跳、无限循环或装饰性粒子。
- 全图只有一个氧化橙红锁定结论。多系列最多四种低饱和功能色，并提供形状、填充或线型第二通道。
- 柱、条和长度编码必须从零开始。趋势图可使用清楚标注的非零范围，但不得暗示从基线起算的量级。
- 面积和半径编码使用平方根换算。不得使用 3D、装饰渐变、玻璃拟态、霓虹光晕、双 Y 轴或彩虹色。
- 标题至少 30px；轴与正文至少 14px；数据标签至少 16px；来源至少 12px。
- 点阵字体只用于编号、时间码、比例和状态，不用于长中文或正文。
- 保持离线可用，不加载在线字体、CDN 或外部图表库。

## Delivery check

- 两米外三秒内能找到结论。
- 十五秒内能找到至少一条支持证据。
- 灰度下仍能区分主次和系列。
- 动画结束后画面适合作为静态截图。
- 重播、暂停、明暗切换和减少动态效果正常。
- 长中文、空值、负值、相同值和极端值不产生重叠、裁切、`NaN` 或 `Infinity`。
- 数据、单位、时间、口径与来源静态可见。
