# 爬虫学习 Day 2 总结

> 日期：2026-05-23
> 目标：requests + BeautifulSoup 基础

## 今日完成

### 1. 环境准备
- Python 3.12.3 已安装
- requests 2.31.0 已安装
- beautifulsoup4 + lxml 已安装

### 2. 学习内容

#### requests 基础
```python
import requests

# 发 GET 请求
resp = requests.get(url, params=params, headers=headers)

# 查看响应
resp.status_code  # 状态码
resp.text         # 响应文本
resp.json()       # 解析 JSON
resp.headers      # 响应头
```

#### BeautifulSoup 基础
```python
from bs4 import BeautifulSoup

# 解析 HTML
soup = BeautifulSoup(html, "html.parser")

# 查找元素
soup.select("css选择器")      # 找多个
soup.select_one("css选择器")  # 找一个

# 提取数据
element.text          # 文本
element.get("href")   # 属性
```

#### CSS 选择器速查
- `.class` → 类选择器
- `#id` → ID选择器
- `tag` → 标签选择器
- `.parent .child` → 后代选择器
- `[attr='value']` → 属性选择器

### 3. 练习文件

| 文件 | 内容 |
|------|------|
| 练习01-基础请求.py | requests 发请求 + BeautifulSoup 解析 |
| 练习02-BeautifulSoup详解.py | 详细示例：提取商品数据、CSS选择器、属性提取 |
| 练习03-爬虫模板.py | 通用爬虫模板（BaseScraper 类） |

### 4. 核心理解

**爬虫 = 4 步**
1. 构造请求（URL + 参数 + Headers）
2. 发请求（requests.get）
3. 解析响应（BeautifulSoup 解析 HTML）
4. 存数据（CSV/JSON）

**类比前端**
- requests.get() ≈ fetch() / axios.get()
- BeautifulSoup ≈ DOM 解析器
- select() ≈ querySelectorAll()
- select_one() ≈ querySelector()

## 明日计划（5/24）

- 用浏览器 DevTools 观察沃尔玛网站的请求
- 用同样的套路写沃尔玛爬虫
- 目标：能抓到沃尔玛商品数据

## 学习心得

（待填写）
