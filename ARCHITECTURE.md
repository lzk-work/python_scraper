# 架构说明 — 爬虫是怎么跑起来的

## 一句话总结

> 爬虫 = **伪装浏览器** + **发请求** + **解析数据** + **存下来**

跟你在 Vue 里调后端接口一模一样，只是反过来——你去调别人的接口。

---

## 整体流程图

```
你写的 Python 脚本
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  1. create_session()                                │
│     utils/session.py                                │
│                                                     │
│     做的事：                                         │
│     - 创建一个 requests.Session（相当于一个浏览器）   │
│     - 设置伪装 Headers（User-Agent、Accept 等）      │
│     - 配置重试机制（遇到 429/500 自动重试）          │
│     - 接入代理池（如果有的话）                       │
│                                                     │
│     类比：你打开浏览器，设置好 UA，准备上网           │
└─────────────────────┬───────────────────────────────┘
                      │ session 对象
                      ▼
┌─────────────────────────────────────────────────────┐
│  2. search_api(session, keyword, page)              │
│     ozon/ozon_search.py                             │
│                                                     │
│     做的事：                                         │
│     - 构造请求 URL + 参数（就像你在浏览器里搜索）    │
│     - session.get(url) 发请求（等同于 axios.get）   │
│     - 拿到 JSON 响应                                │
│     - 从 JSON 里提取你要的字段（标题、价格、评分）   │
│                                                     │
│     类比：你在 Vue 里调后端接口，拿到数据渲染        │
└─────────────────────┬───────────────────────────────┘
                      │ list[dict] 商品数据
                      ▼
┌─────────────────────────────────────────────────────┐
│  3. save_csv() / save_json()                        │
│     utils/storage.py                                │
│                                                     │
│     做的事：                                         │
│     - 把数据写入 CSV 文件（Excel 能打开）            │
│     - 或写入 JSON 文件（结构化，后续导入数据库）     │
│     - 自动创建 data/ 目录，自动生成文件名            │
│                                                     │
│     类比：后端把数据存进数据库                       │
└─────────────────────────────────────────────────────┘
```

---

## 模块职责对照表

就像你写 SpringBoot 项目会分 Controller / Service / Mapper 一样，爬虫也分层：

```
你的 SpringBoot 项目              这个爬虫项目
─────────────────────            ─────────────────────
Controller (接收请求)             ozon/ozon_search.py (构造请求)
Service (业务逻辑)               ozon/ozon_search.py (解析数据)
Mapper (数据库操作)              utils/storage.py (文件存储)
Utils (工具类)                   utils/ (整个工具包)
application.yml (配置)           utils/session.py (平台配置)
```

### utils/ — 工具包（你不需要改，直接用）

| 文件 | 干什么 | 什么时候用 | 类比 |
|------|--------|-----------|------|
| **session.py** | 创建 HTTP 客户端 | 每次爬取第一步 | 你打开浏览器 |
| **proxy.py** | 代理池管理 | 被封 IP 时 | 换个网络出口 |
| **rate.py** | 限速控制 | 批量爬取时 | 控制你点链接的速度 |
| **parser.py** | 数据清洗 | 解析出的价格有乱码时 | 数据格式化 |
| **storage.py** | 存 CSV/JSON | 爬完存数据 | 数据入库 |
| **logger.py** | 日志输出 | 看爬取进度 | console.log |

### ozon/ — 业务代码（你要改的）

| 文件 | 干什么 | 核心函数 |
|------|--------|---------|
| **ozon_search.py** | 按关键词搜索商品 | `search_api()` — 调 API 拿 JSON<br>`search_html()` — 解析网页（备用）<br>`run()` — 串起来：循环翻页 + 延时 + 去重 + 存储 |
| **ozon_product.py** | 拿单品详情 | `fetch_product()` — 请求单品页 → 解析<br>`run()` — 批量爬取 |

---

## 单次爬取的完整流程（以 Ozon 搜索为例）

```python
# 你执行: python -m ozon.ozon_search --keyword "蓝牙耳机" --pages 3

# 第 1 步: 创建 session（相当于打开浏览器）
session = create_session(platform="ozon")
#   → 内部做了:
#     - 随机选一个 User-Agent（伪装成 Chrome/Firefox）
#     - 设置 Accept-Language: ru-RU（Ozon 是俄罗斯网站）
#     - 配置重试: 遇到 429 自动等一会儿再试
#     - 如果传了 proxy，设置代理

# 第 2 步: 循环爬取每一页
for page in range(1, 4):  # 3 页
    # 2a. 限速等待（避免请求太快被封）
    limiter.wait()

    # 2b. 发请求（等同于你在浏览器里按回车搜索）
    resp = session.get(
        "https://www.ozon.ru/api/composer-api.bx/page/json/v2",
        params={"url": "/search/?text=蓝牙耳机&page=1"}
    )
    # → 服务器返回 JSON

    # 2c. 解析 JSON，提取商品信息
    data = resp.json()
    for item in data["data"]["widgets"]:
        product = {
            "name": "蓝牙耳机 Pro Max",
            "price": 2999.0,
            "rating": 4.8,
            ...
        }

    # 2d. 翻页前随机等 3~6 秒（模拟人的操作节奏）
    random_delay(3, 6)

# 第 3 步: 去重 + 存储
save_csv(unique_products)   # → data/ozon_蓝牙耳机_20260522_114500.csv
save_json(unique_products)  # → data/ozon_蓝牙耳机_20260522_114500.json
```

---

## 为什么要这么分层？

**现在：** 只爬 Ozon，数据量小，直连就行。

**以后：** 爬 Walmart、Amazon，用代理池批量爬，每天跑几千条。

分层之后，扩展只需要：

```
想加新平台？     → 新建 walmart/walmart_search.py，套同样模式
想用代理？       → 传一个 ProxyPool 进去，业务代码不用改
想批量限速？     → RateLimiter(qps=2)，一行搞定
想存数据库？     → 在 storage.py 加一个 save_mysql()，调用方不用改
```

不分层的话，改一个地方要动所有代码，迟早乱掉。

---

## 反爬与应对（速查）

```
你访问太快        →  rate.py: random_delay(3, 6)  随机等几秒
                   rate.py: RateLimiter(qps=2)    令牌桶精确限速

IP 被封          →  proxy.py: ProxyPool(...)      换代理 IP

User-Agent 被识别 →  session.py: 随机 UA 池        每次请求换一个

请求失败         →  session.py: Retry(3次)        自动重试

页面是 JS 渲染的  →  目前不需要，后续加 Selenium/Playwright
```

---

## 数据流向

```
Ozon 服务器
    │
    │ HTTP 响应（JSON / HTML）
    ▼
session.get() 拿到原始数据
    │
    │ _parse_api_item() / _parse_html()
    ▼
list[dict]  ← 干净的结构化数据
    │
    │ save_csv() / save_json()
    ▼
data/ozon_xxx.csv    ← 用 Excel 打开看
data/ozon_xxx.json   ← 后续导入数据库
```
