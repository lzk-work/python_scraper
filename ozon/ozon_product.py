"""
Ozon 单品详情爬取

用法:
  python ozon_product.py --url "https://www.ozon.ru/product/xxx-123456789/"
  python ozon_product.py --ids "123456789,987654321"
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import create_session, random_delay, logger, clean_price, clean_int

BASE_URL = "https://www.ozon.ru"
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FIELDS = [
    "product_id", "name", "brand", "price", "original_price", "discount",
    "rating", "review_count", "seller", "category", "description",
    "specs", "url", "scraped_at",
]


def fetch_product(session, url_or_id: str) -> dict | None:
    """获取单品详情"""
    # 构造 URL
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

    # ── 回退: 从 HTML 解析 ──
    return _parse_html(soup, url)


def _parse_json_ld(data: dict, url: str) -> dict:
    """从 JSON-LD 解析"""
    offer = data.get("offers", {})
    if isinstance(offer, list):
        offer = offer[0] if offer else {}

    rating_data = data.get("aggregateRating", {})

    # product_id 从 URL 提取
    product_id = ""
    if "/product/" in url:
        parts = url.split("/product/")[1].split("/")[0]
        product_id = parts.split("-")[-1] if "-" in parts else parts

    return {
        "product_id": product_id,
        "name": data.get("name", ""),
        "brand": data.get("brand", {}).get("name", "") if isinstance(data.get("brand"), dict) else str(data.get("brand", "")),
        "price": clean_price(str(offer.get("price", ""))),
        "original_price": None,
        "discount": "",
        "rating": float(rating_data.get("ratingValue", 0)) or None,
        "review_count": clean_int(str(rating_data.get("reviewCount", ""))),
        "seller": offer.get("seller", {}).get("name", "") if isinstance(offer.get("seller"), dict) else "",
        "category": data.get("category", ""),
        "description": data.get("description", "")[:500],
        "specs": "",
        "url": url,
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
    }


def _parse_html(soup, url: str) -> dict:
    """从 HTML 解析（备用）"""
    # 标题
    title_el = soup.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    # 价格 — 尝试多种选择器
    price = None
    for sel in ['[data-widget="webPrice"] span', '[class*="Price"] span', '.pdp-info__price']:
        el = soup.select_one(sel)
        if el:
            price = clean_price(el.get_text())
            if price:
                break

    # 评分
    rating = None
    rating_el = soup.select_one('[class*="rating"]')
    if rating_el:
        m = re.search(r"(\d+[.,]?\d*)", rating_el.get_text())
        rating = float(m.group(1).replace(",", ".")) if m else None

    # 评论数
    review_count = None
    review_el = soup.select_one('[class*="review"]')
    if review_el:
        review_count = clean_int(review_el.get_text())

    # product_id
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


def save_csv(products: list[dict], prefix: str = "product") -> str:
    """保存到 CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = DATA_DIR / f"ozon_{prefix}_{timestamp}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(products)
    logger.info(f"已保存: {filename} ({len(products)} 条)")
    return str(filename)


def run(urls: list[str]):
    """批量爬取单品"""
    session = create_session()
    products = []

    for i, url in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {url}")
        product = fetch_product(session, url)
        if product:
            products.append(product)
        if i < len(urls):
            random_delay(3, 6)

    if products:
        save_csv(products)
    return products


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ozon 单品详情爬取")
    parser.add_argument("--url", "-u", help="单品 URL")
    parser.add_argument("--ids", help="商品 ID，逗号分隔")
    args = parser.parse_args()

    urls = []
    if args.url:
        urls.append(args.url)
    if args.ids:
        for pid in args.ids.split(","):
            urls.append(f"{BASE_URL}/product/{pid.strip()}")

    if not urls:
        parser.error("需要 --url 或 --ids 参数")

    results = run(urls)
    print(f"\n✅ 完成! 获取 {len(results)} 个商品详情")
