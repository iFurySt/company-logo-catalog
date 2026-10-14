# 公司 Logo Catalog

维护证券、发行人和公司图片来源，支持普通股、权证、单位、优先股等共用发行人图片。

## 当前覆盖

以 **2026-10-14 Nasdaq Trader 官方快照**为准，收录全部 **7,481 个非测试、非 ETF 证券**。

| 图片来源状态 | 证券数 |
| --- | ---: |
| 已核实公司图片 | 29 |
| 股票代码对应的供应商图片，尚未逐一核实身份 | 6,486 |
| 根据目录公司名称提出的共用图片候选，尚未逐一核实发行人 | 562 |
| 已检查图片字节的 GitHub 来源，尚未逐一核实身份 | 14 |
| 其他供应商 SVG，尚未逐一核实身份 | 48 |
| 本轮尚未找到可用来源 | 342 |

这是证券数量，不是公司数量，也不是“全部图片身份已核实”。已核实目录包含
18 家公司、35 个证券、41 个精确代码／别名，其中 16 家有核实过的公司图片。

[覆盖统计](coverage.json) · [完整供应商目录](catalog-provider.json) ·
[缺图清单](missing-logos.csv) · [核实记录](docs/full-directory-review.md)

## 查询

```sh
# 默认只返回已核实图片
python3 scripts/catalog.py resolve 'US:AACOW'

# 显式允许未逐一核实的供应商图片、名称分组候选和已检查的仓库图片
python3 scripts/catalog.py resolve 'US:AA' --allow-provider
```

`catalog.json` 是已核实公司目录，保留现有 AIFi 读取格式。
`catalog-provider.json` 是全量证券／来源数据，包含校验和、尺寸、可用性和核实等级；
消费者需要显式支持这个不同的数据格式。没有把未核实条目自动变成已核实 Logo。

本轮核对了 Ares、Averin、Wintrust 的品牌来源，并补充 ACCV、ADBT、ADIG、ADRX 的官网图片。
Apogee 的通用蓝色 A 图片被确认与官网品牌不符，已拒用并加入正确的盾牌标志。

## 维护

Python 3.12+、Node 24+，无需额外依赖或 API Key。

```sh
python3 scripts/catalog.py validate
python3 scripts/catalog.py build --check
python3 -m unittest discover -s tests
node --test tests/test_probe.mjs
```

[维护命令](docs/full-directory-maintenance.md) 支持限速、续跑、异常重试和离线生成检查。
全部图片仍未补齐，342 个缺来源条目和其余图片身份核实需要继续维护。

原创代码及维护的元数据采用 MIT。链接中的第三方图片仍受原权利人及供应商条款约束，
本仓库不包含第三方图片包。
