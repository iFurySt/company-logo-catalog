# Company Logo Catalog

维护证券代码 → 公司 → Logo URL 的映射。普通股、Units、权证和优先股可以共用
发行公司的头像，避免每个代码都需要单独找到图片。

- `data/companies/`：每家公司一份 JSON，包含核实日期、证据和图片来源。
- `catalog.json`：生成后的完整目录，包含精确代码／别名索引。
- `verified`：已核对图片身份；`candidate`：待核实；`unavailable`：来源缺失。
- 查询脚本只返回 `verified` 图片，不自动猜测代码后缀或公司官网。

```sh
python3 scripts/catalog.py resolve 'US:AACOW'
python3 scripts/catalog.py validate
python3 scripts/catalog.py build
python3 -m unittest discover -s tests
```

首批优先处理 AIFi 中缺失的权证、Units、优先股头像。目录不是全市场图库，后续通过
PR 逐步补充。原始代码和整理的元数据采用 MIT；外部 Logo 的使用条件独立保留。

贡献说明：[CONTRIBUTING.md](CONTRIBUTING.md)。
