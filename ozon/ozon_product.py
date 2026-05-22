"""
Ozon 单品详情爬取

流程:
  1. 给定商品 URL 或 ID，发请求拿到页面 HTML
  2. 优先从 JSON-LD（页面里的结构化数据）提取商品信息
  3. JSON-LD 没有就回退到 HTML 解析
  4. 批量模式：逐个请求，每请求一个随机延时

用法:
  python -m ozon.ozon_product --url "https://www.ozon.ru/product/xxx-123456789/"
  python -m ozon.ozon_product --ids "123456789,987654321"
"""
import argparse
import json
import re
from datetime import datetime
from typing import Optional

from utils import (
    create_session, random_delay, ProxyPool,
    save_csv, logger, clean_price, clean_int,
)

BASE_URL = "https://www.ozon.ru"

FIELDS = [
    "product_id", "name", "brand", "price", "original_price", "discount",
    "rating", "review_count", "seller", "category", "description",
    "specs", "url", "scraped_at",
]


def fetch_product(session, url_or_id: str) -> Optional[dict]:
    """获取单品详情"""
    if url_or_id.startswith("http"):
        url = url_or_id
    else:
        url = f"{BASE_URL}/product/{url_or_id}"

    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"请求失败: {url} → {e}")
        return None

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")

    # ── 从 JSON-LD 提取结构化数据 ──
    json_ld = None
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                data = data[0]
            if data.get("@type") == "Product":
                json_ld = data
                break
        except (json.JSONDecodeError, TypeError):
            continue

    if json_ld:
        return _parse_json_ld(json_ld, url)

    # ── 回退: HTML 解析 ──
    return _parse_html(soup, url)


def _parse_json_ld(data: dict, url: str) -> dict:
    """从 JSON-LD 解析"""
    offer = data.get("offers", {})
    if isinstance(offer, list):
        offer = offer[0] if offer else {}

    rating_data = data.get("aggregateRating", {})

    product_id = ""
    if "/product/" in url:
        parts = url.split("/product/")[1].split("/")[0]
        product_id = parts.split("-")[-1] if "-" in parts else parts

    return {
        "product_id": product_id,
        "name": data.get("name", ""),
        "brand": data.get("brand", {}).get("name", "")
        if isinstance(data.get("brand"), dict) else str(data.get("brand", "")),
        "price": clean_price(str(offer.get("price", ""))),
        "original_price": None,
        "discount": "",
        "rating": float(rating_data.get("ratingValue", 0)) or None,
        "review_count": clean_int(str(rating_data.get("reviewCount", ""))),
        "seller": offer.get("seller", {}).get("name", "")
        if isinstance(offer.get("seller"), dict) else "",
        "category": data.get("category", ""),
        "description": data.get("description", "")[:500],
        "specs": "",
        "url": url,
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
    }


def _parse_html(soup, url: str) -> dict:
    """从 HTML 解析（备用）"""
    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    price = None
    for sel in ['[data-widget="webPrice"] span', '[class*="Price"] span', '.pdp-info__price']:
        el = soup.select_one(sel)
        if el:
            price = clean_price(el.get_text())
            if price:
                break

    rating = None
    rating_el = soup.select_one('[class*="rating"]')
    if rating_el:
        m = re.search(r"(\d+[.,]?\d*)", rating_el.get_text())
        rating = float(m.group(1).replace(",", ".")) if m else None

    review_count = None
    review_el = soup.select_one('[class*="review"]')
    if review_el:
        review_count = clean_int(review_el.get_text())

    product_id = ""
    if "/product/" in url:
        parts = url.split("/product/")[1].split("/")[0]
        product_id = parts.split("-")[-1] if "-" in parts else parts

    return {
        "product_id": product_id,
        "name": title,
        "brand": "",
        "price": price,
        "original_price": None,
        "discount": "",
        "rating": rating,
        "review_count": review_count,
        "seller": "",
        "category": "",
        "description": "",
        "specs": "",
        "url": url,
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
    }


def run(urls: list[str], proxy_pool: Optional[ProxyPool] = None) -> list[dict]:
    """批量爬取单品"""
    session = create_session(platform="ozon", proxy_pool=proxy_pool)
    products = []

    for i, url in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {url}")
        product = fetch_product(session, url)
        if product:
            products.append(product)
        if i < len(urls):
            random_delay(3, 6)

    if products:
        save_csv(products, prefix="ozon_product")
    return products


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ozon 单品详情爬取")
    parser.add_argument("--url", "-u", help="单品 URL")
    parser.add_argument("--ids", help="商品 ID，逗号分隔")
    parser.add_argument("--proxy", help="代理地址")
    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(args.url)
    if args.ids:
        for pid in args.ids.split(","):
            urls.append(f"{BASE_URL}/product/{pid.strip()}")

    if not urls:
        parser.error("需要 --url 或 --ids 参数")

    pool = ProxyPool(args.proxy) if args.proxy else None
    results = run(urls, proxy_pool=pool)
    print(f"\n✅ 完成! 获取 {len(results)} 个商品详情")
