# Ozon 数据爬取

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

## 使用

```bash
# 搜索结果
python -m ozon.ozon_search --keyword "蓝牙耳机" --pages 5

# 单品详情
python -m ozon.ozon_product --url "https://www.ozon.ru/product/xxx-123456789/"
python -m ozon.ozon_product --ids "123456789,987654321"

# 使用代理
python -m ozon.ozon_search --keyword "耳机" --proxy "http://user:pass@proxy:8080"
```

## Python 调用

```python
from ozon import search, fetch_products

# 搜索
result = search("蓝牙耳机", pages=3, mode="api")
print(result)  # {"total": 45, "csv": "...", "json": "..."}

# 单品
products = fetch_products(["https://www.ozon.ru/product/xxx-123456789/"])
```

## 技术栈

- **requests** — HTTP 请求
- **BeautifulSoup** — HTML 解析（备用模式）
- **CSV/JSON** — 数据存储

## 注意事项

- 遵守 robots.txt，控制请求频率
- 数据仅用于个人分析，不用于商业用途
- Ozon 有反爬机制，批量爬取需代理支持
