# data-scraper

跨境电商数据采集工具，支持多平台商品数据抓取。

> 📖 **架构说明**: [ARCHITECTURE.md](./ARCHITECTURE.md) — 整体流程、模块职责、数据流向

## 平台支持

| 平台 | 状态 | 说明 |
|------|------|------|
| Ozon | 📝 待开发 | 搜索 + 单品详情 |
| Walmart | 📝 待开发 | 搜索 + 单品详情 |
| Amazon | 📝 待开发 | 搜索 + 单品详情（反爬最强） |

## 项目结构

```
data-scraper/
├── utils/              # 通用工具包
│   ├── session.py      #   HTTP Session（含代理支持）
│   ├── proxy.py        #   代理池抽象
│   ├── rate.py         #   限速策略
│   ├── parser.py       #   数据清洗
│   ├── storage.py      #   存储（CSV / JSON）
│   └── logger.py       #   统一日志
├── ozon/               # Ozon 平台爬虫
├── walmart/            # Walmart 平台爬虫
├── amazon/             # Amazon 平台爬虫
├── data/               # 爬取结果（gitignore）
└── ARCHITECTURE.md     # 架构说明
```

## 使用

```bash
pip install -r requirements.txt

# 待开发
```
