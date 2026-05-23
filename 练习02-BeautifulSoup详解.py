"""
爬虫基础练习02 — BeautifulSoup 详解

用一个完整的 HTML 示例，练习所有常用操作
"""
from bs4 import BeautifulSoup

# ============================================
# 用一个完整的 HTML 来练习
# ============================================

html = """
<!DOCTYPE html>
<html>
<head>
    <title>跨境电商商品列表</title>
</head>
<body>
    <div class="container">
        <h1>热门商品</h1>
        
        <div class="product-card" data-id="1001">
            <h2 class="title">蓝牙耳机 Pro</h2>
            <span class="price">299 ₽</span>
            <span class="original-price">399 ₽</span>
            <span class="rating">4.8</span>
            <span class="reviews">1256 条评价</span>
            <a href="/product/1001" class="link">查看详情</a>
        </div>
        
        <div class="product-card" data-id="1002">
            <h2 class="title">无线充电器</h2>
            <span class="price">149 ₽</span>
            <span class="original-price">199 ₽</span>
            <span class="rating">4.5</span>
            <span class="reviews">892 条评价</span>
            <a href="/product/1002" class="link">查看详情</a>
        </div>
        
        <div class="product-card" data-id="1003">
            <h2 class="title">手机壳 防摔</h2>
            <span class="price">49 ₽</span>
            <span class="original-price">79 ₽</span>
            <span class="rating">4.9</span>
            <span class="reviews">3421 条评价</span>
            <a href="/product/1003" class="link">查看详情</a>
        </div>
        
        <div class="pagination">
            <a href="?page=1" class="active">1</a>
            <a href="?page=2">2</a>
            <a href="?page=3">3</a>
        </div>
    </div>
</body>
</html>
"""

# ============================================
# 1. 基本解析
# ============================================

soup = BeautifulSoup(html, "html.parser")

print("="*50)
print("1. 基本解析")
print("="*50)

# 提取标题
title = soup.select_one("h1").text
print(f"页面标题: {title}")

# 提取所有商品卡片
cards = soup.select(".product-card")
print(f"找到 {len(cards)} 个商品")

# ============================================
# 2. 遍历商品，提取数据
# ============================================

print("\n" + "="*50)
print("2. 提取商品数据")
print("="*50)

products = []
for card in cards:
    # 提取各个字段
    name = card.select_one(".title").text
    price = card.select_one(".price").text
    original_price = card.select_one(".original-price").text
    rating = card.select_one(".rating").text
    reviews = card.select_one(".reviews").text
    link = card.select_one(".link").get("href")
    
    # 提取 data-id 属性
    product_id = card.get("data-id")
    
    # 组装成字典
    product = {
        "id": product_id,
        "name": name,
        "price": price,
        "original_price": original_price,
        "rating": rating,
        "reviews": reviews,
        "link": link,
    }
    products.append(product)
    
    # 打印
    print(f"\n商品 {product_id}:")
    print(f"  名称: {name}")
    print(f"  价格: {price} (原价: {original_price})")
    print(f"  评分: {rating} ({reviews})")
    print(f"  链接: {link}")

# ============================================
# 3. CSS 选择器详解
# ============================================

print("\n" + "="*50)
print("3. CSS 选择器速查")
print("="*50)

# 类选择器
print("\n类选择器 (找 class='title' 的元素):")
titles = soup.select(".title")
for t in titles:
    print(f"  - {t.text}")

# 标签选择器
print("\n标签选择器 (找所有 <span>):")
spans = soup.select("span")
print(f"  找到 {len(spans)} 个 <span>")

# 属性选择器
print("\n属性选择器 (找 data-id='1002' 的元素):")
card = soup.select_one("[data-id='1002']")
if card:
    print(f"  找到: {card.select_one('.title').text}")

# 子元素选择器
print("\n子元素选择器 (找 .product-card 下的 .price):")
prices = soup.select(".product-card .price")
for p in prices:
    print(f"  - {p.text}")

# 伪类选择器
print("\n伪类选择器 (找第一个商品):")
first = soup.select_one(".product-card:first-child")
if first:
    print(f"  第一个: {first.select_one('.title').text}")

# ============================================
# 4. 提取属性
# ============================================

print("\n" + "="*50)
print("4. 提取属性")
print("="*50)

# 提取 href 属性
links = soup.select(".product-card .link")
for link in links:
    href = link.get("href")  # 方法1: .get("属性名")
    text = link["href"]      # 方法2: ["属性名"]（如果属性不存在会报错）
    print(f"  链接: {href}")

# 提取 data-* 属性
cards = soup.select(".product-card")
for card in cards:
    product_id = card.get("data-id")  # data-* 属性用 .get()
    print(f"  商品ID: {product_id}")

# ============================================
# 5. 分页处理
# ============================================

print("\n" + "="*50)
print("5. 分页处理")
print("="*50)

pagination = soup.select(".pagination a")
print("分页链接:")
for page in pagination:
    href = page.get("href")
    text = page.text
    is_active = "active" in page.get("class", [])
    status = "← 当前页" if is_active else ""
    print(f"  第{text}页: {href} {status}")

# ============================================
# 6. 实战：组装成结构化数据
# ============================================

print("\n" + "="*50)
print("6. 最终输出（JSON格式）")
print("="*50)

import json
print(json.dumps(products, ensure_ascii=False, indent=2))

# ============================================
# 总结
# ============================================

print("\n" + "="*50)
print("总结：BeautifulSoup 常用操作")
print("="*50)
print("""
1. 解析 HTML:
   soup = BeautifulSoup(html, "html.parser")

2. 查找元素:
   soup.select("css选择器")  → 返回列表
   soup.select_one("css选择器")  → 返回第一个

3. 提取文本:
   element.text  → 获取文本内容

4. 提取属性:
   element.get("href")  → 获取属性值
   element["href"]  → 同上（不存在会报错）

5. CSS 选择器语法:
   .class  → 类选择器
   #id  → ID选择器
   tag  → 标签选择器
   tag.class  → 标签+类
   .parent .child  → 后代选择器
   [attr='value']  → 属性选择器
""")
