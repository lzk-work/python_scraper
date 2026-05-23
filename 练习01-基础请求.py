"""
爬虫基础练习 — requests + BeautifulSoup

目标：抓取一个简单的网页，提取标题和链接
"""
import requests
from bs4 import BeautifulSoup

# ============================================
# 第一步：发请求（就像浏览器访问网页）
# ============================================

# 用 requests 发 GET 请求
url = "https://httpbin.org/html"  # 一个专门用于测试的网站
response = requests.get(url)

# 看看响应
print(f"状态码: {response.status_code}")  # 200 表示成功
print(f"响应头: {response.headers['Content-Type']}")  # 内容类型
print(f"响应内容长度: {len(response.text)} 字符")

# ============================================
# 第二步：解析 HTML（用 BeautifulSoup）
# ============================================

# 把 HTML 字符串解析成树形结构
soup = BeautifulSoup(response.text, "html.parser")

# 提取标题
title = soup.select_one("h1")
if title:
    print(f"\n标题: {title.text}")

# 提取所有链接
links = soup.select("a")
print(f"\n找到 {len(links)} 个链接:")
for link in links[:5]:  # 只显示前5个
    href = link.get("href", "")
    text = link.text.strip()
    print(f"  - {text}: {href}")

# 提取所有段落
paragraphs = soup.select("p")
print(f"\n找到 {len(paragraphs)} 个段落:")
for i, p in enumerate(paragraphs[:3], 1):  # 只显示前3个
    text = p.text.strip()[:100]  # 截取前100个字符
    print(f"  {i}. {text}...")

# ============================================
# 第三步：实际应用 — 抓取 Hacker News 首页
# ============================================

print("\n" + "="*50)
print("实战：抓取 Hacker News 首页标题")
print("="*50)

try:
    # 发请求
    resp = requests.get("https://news.ycombinator.com/", timeout=10)
    resp.raise_for_status()  # 如果状态码不是 200，抛出异常
    
    # 解析
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 提取标题（class="titleline" 的链接）
    titles = soup.select(".titleline > a")
    
    print(f"\n前10条新闻:")
    for i, title in enumerate(titles[:10], 1):
        text = title.text.strip()
        href = title.get("href", "")
        print(f"{i:2d}. {text}")
        print(f"    → {href[:80]}...")
        
except Exception as e:
    print(f"请求失败: {e}")

# ============================================
# 练习要点总结
# ============================================

print("\n" + "="*50)
print("要点总结")
print("="*50)
print("""
1. requests.get(url) → 发请求，拿到响应
2. BeautifulSoup(html, "html.parser") → 解析 HTML
3. soup.select("css选择器") → 找多个元素
4. soup.select_one("css选择器") → 找一个元素
5. element.text → 提取文本
6. element.get("href") → 提取属性

类比前端：
- requests.get() ≈ fetch() 或 axios.get()
- BeautifulSoup ≈ DOM 解析器
- select() ≈ querySelectorAll()
- select_one() ≈ querySelector()
""")
