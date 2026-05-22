# Ozon 数据爬取

## 概述

Python 爬取 Ozon 平台公开数据，用于市场分析和选品参考。

## 目标数据

| 字段 | 说明 |
|------|------|
| product_id | Ozon 商品 ID |
| name | 商品名称 |
| price | 当前价格（₽） |
| original_price | 原价 |
| discount | 折扣率 |
| rating | 评分 |
| review_count | 评论数 |
| seller | 卖家名称 |
| category | 分类 |
| url | 商品链接 |

## 技术栈

- **requests** — HTTP 请求
- **BeautifulSoup** — 页面解析
- **pandas** — 数据整理 & 导出
- **CSV/JSON** — 数据存储（后续可接 MySQL）

## 目录结构

```
Ozon数据爬取/
├── README.md
├── src/
│   ├── ozon_search.py    # 搜索关键词爬取
│   ├── ozon_product.py   # 单品详情爬取
│   └── utils.py          # 通用工具（headers、延时、重试）
├── data/                 # 爬取结果（gitignore）
└── docs/                 # 分析文档
```

## 使用方式

```bash
# 爬取搜索结果
python src/ozon_search.py --keyword "蓝牙耳机" --pages 5

# 爬取单品详情
python src/ozon_product.py --url "https://www.ozon.ru/product/..."
```

## 注意事项

- 遵守 robots.txt，控制请求频率
- 数据仅用于个人分析，不用于商业用途
- Ozon 有反爬机制，需代理支持（后续按需添加）
