# python_scraper

跨境电商数据采集工具，支持多平台商品数据抓取。

> 📖 **新手必读**: [ARCHITECTURE.md](./ARCHITECTURE.md) — 整体流程、模块职责、数据流向，图文讲解
> 📖 **爬虫基础**: [01-基础理论.md](./01-基础理论.md) — HTTP 基础、requests/BeautifulSoup 用法、反爬原理

## 平台支持

| 平台 | 状态 | 说明 |
|------|------|------|
| Ozon | 🚧 开发中 | 搜索 + 单品详情 |
| Walmart | 📝 待开发 | 搜索 + 单品详情 |
| Amazon | 📝 待开发 | 搜索 + 单品详情（反爬最强） |

## 项目结构

```
python_scraper/
├── utils/              # 通用工具包
│   ├── session.py      #   HTTP Session（含代理支持）
│   ├── proxy.py        #   代理池抽象（直连 / 单代理 / 代理列表 / 自定义 provider）
│   ├── rate.py         #   限速策略（随机延时 + 令牌桶）
│   ├── parser.py       #   数据清洗（价格、评论数等）
│   ├── storage.py      #   存储（CSV / JSON）
│   └── logger.py       #   统一日志
├── ozon/               # Ozon 平台爬虫
│   ├── ozon_search.py  #   搜索结果爬取
│   └── ozon_product.py #   单品详情爬取
├── walmart/            # Walmart（待开发）
├── amazon/             # Amazon（待开发）
└── data/               # 爬取结果（gitignore）
```

## 使用

```bash
# 安装依赖
pip install -r requirements.txt

# Ozon 搜索
python -m ozon.ozon_search --keyword "蓝牙耳机" --pages 3

# Ozon 单品
python -m ozon.ozon_product --url "https://www.ozon.ru/product/xxx-123456789/"

# 使用代理
python -m ozon.ozon_search --keyword "耳机" --proxy "http://user:pass@proxy:8080"

# Python 调用
from ozon import search, fetch_products
result = search("蓝牙耳机", pages=3)
products = fetch_products(["https://www.ozon.ru/product/xxx-123456789/"])
```

## 扩展

### 接入代理池

```python
from utils import ProxyPool, create_session

# 方式 1: 代理列表（轮询）
pool = ProxyPool(["http://p1:8080", "http://p2:8080"], strategy="round_robin")

# 方式 2: 对接代理池 API
from utils.proxy import kdl_provider
pool = ProxyPool(provider=kdl_provider("https://api.kdl.com/get?num=1"))

# 传入 session
session = create_session(platform="ozon", proxy_pool=pool)
```

### 批量爬取限速

```python
from utils import RateLimiter

limiter = RateLimiter(qps=2)  # 每秒最多 2 个请求
for url in urls:
    limiter.wait()
    resp = session.get(url)
```
