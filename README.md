# python_scraper

跨境电商数据采集工具，支持多平台商品数据抓取。

## 平台支持

| 平台 | 状态 | 说明 |
|------|------|------|
| Ozon | 🚧 开发中 | 商品搜索 + 详情 |
| Walmart | 📝 待开发 | 商品搜索 + 详情 |
| Amazon | 📝 待开发 | 商品搜索 + 详情（反爬最强） |

## 项目结构

```
python_scraper/
├── utils.py          # 通用工具（请求、存储、日志）
├── ozon/             # Ozon 平台爬虫
├── walmart/          # Walmart 平台爬虫
└── amazon/           # Amazon 平台爬虫
```

## 环境

- Python 3.x
- requests
- beautifulsoup4

## 使用

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 Ozon 爬虫
python ozon/search.py
```
