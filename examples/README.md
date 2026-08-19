# Example data

`data/` 包含 C1–C24 的完整 UTF-8 JSON 示例，文件名与模板一一对应。

```powershell
python scripts/render.py `
  --chart C17 `
  --data examples/data/c17-market-candles.json `
  --output output/c17.html `
  --title "价格放量突破前高，短期趋势转强"
```

这些文件由 `scripts/export_examples.py` 从 `moxing/charts.py` 中受测试保护的默认数据生成。修改默认数据后重新运行脚本，并提交生成差异。

字段含义、数量限制与图表选择边界见 [`references/chart-contracts.md`](../references/chart-contracts.md)。
