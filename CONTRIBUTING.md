# Contributing to Moxing Studio

感谢你帮助改进 Moxing Studio。提交前请先确认改动解决的是数据表达或可用性问题，而不只是增加一种装饰外观。

## Development setup

```powershell
python -m pip install -r requirements-dev.txt
npm install
npx playwright install chromium
python scripts/export_examples.py
```

## Required checks

```powershell
python scripts/validate_skill.py
python scripts/test_boundaries.py
node scripts/validate.mjs .
```

## Chart admission bar

新增公开图表 ID 必须同时满足：

- 对应现实行业中重复出现的决策问题。
- 现有 C1–C24 无法在不误导的前提下表达该问题。
- 优先复用九个共享渲染家族；纯视觉变化实现为 preset。
- 具备有效、空值、相同值、极端值和非法数据测试。
- 支持 `brief / standard / story`、无 JavaScript、减少动态和明暗模式。
- 标题、单位、时间范围、口径和来源在锁定状态中可见。

## Pull requests

Pull Request 请说明：用户问题、选择的图表契约、拒绝的替代方案、验证命令和视觉证据。不要提交临时导出目录、浏览器缓存或大体积视频；演示视频应作为 Release 附件。
