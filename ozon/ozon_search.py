"""
Ozon 搜索结果爬取

支持两种模式：
  1. API 模式（默认）— 调用 Ozon 内部 API，返回 JSON，速度快
  2. HTML 模式（备用）— 解析网页，适用于 API 变更时

用法:
  python -m ozon.ozon_search --keyword "蓝牙耳机" --pages 3
  python -m ozon.ozon_search --keyword "无线耳机" --mode html --pages 2
"""
import argparse
import json
import re
from datetime import datetime
from typing import Optional

from utils import (
    create_session, random_delay, RateLimiter, ProxyPool,
    save_csv, save_json, logger,
    clean_price, clean_int, safe_text,
)

# ── 常量 ─────────────────────────────────────────────────

BASE_URL = "https://www.ozon.ru"
SEARCH_API = "https://www.ozon.ru/api/composer-api.bx/page/json/v2"

FIELDS = [
    "product_id", "name", "price", "original_price", "discount",
    "rating", "review_count", "seller", "category", "url",
    "scraped_at",
]


# ── API 模式 ─────────────────────────────────────────────

def search_api(session, keyword: str, page: int = 1) -> list[dict]:
    """通过 Ozon 内部 API 获取搜索结果"""
    params = {
        "url": f"/search/?text={keyword}&from_search=true&page={page}",
        "layout_container": "SearchMegapagination",
        "layout_page_index": page,
    }
    try:
        resp = session.get(SEARCH_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"API 请求失败 (page={page}): {e}")
        return []

    products = []
    widgets = data.get("data", {}).get("widgets", [])

    for widget in widgets:
        if widget.get("widgetName") != "SearchResults":
            continue
        items = widget.get("data", {}).get("items", [])
        for item in items:
            main_state = item.get("mainState", [])
            product = _parse_api_item(item, main_state)
            if product:
                products.append(product)
        break

    logger.info(f"API page={page}: 获取 {len(products)} 条")
    return products


def _parse_api_item(item: dict, main_state: list) -> Optional[dict]:
    """解析 API 返回的单个商品"""
    try:
        title = ""
        price = None
        original_price = None
        rating = None
        review_count = None
        seller = ""

        for state in main_state:
            atom = state.get("atom", {})
            atom_type = state.get("type", "")

            if atom_type == "textAtom":
                text = atom.get("textAtom", {}).get("text", "")
                if atom.get("textAtom", {}).get("textStyle") == "title":
                    title = text

            elif atom_type == "priceAtom":
                price_data = atom.get("priceAtom", {})
                price = clean_price(price_data.get("price", ""))
                original_price = clean_price(price_data.get("oldPrice", ""))

            elif atom_type == "ratingAtom":
                rating_data = atom.get("ratingAtom", {})
                rating = rating_data.get("rating")
                review_count = rating_data.get("reviewCount")

        # 提取 seller
        for state in main_state:
            atom = state.get("atom", {})
            if "seller" in str(atom).lower():
                seller_name = atom.get("textAtom", {}).get("text", "")
                if seller_name:
                    seller = seller_name
                    break

        # 提取分类
        category = ""
        breadcrumb = item.get("breadcrumb", {})
        if breadcrumb:
            items = breadcrumb.get("items", [])
            category = " > ".join([b.get("text", "") for b in items])

        # product_id
        action = item.get("action", {})
        url = action.get("link", "")
        product_id = ""
        if "/product/" in url:
            parts = url.split("/product/")[1].split("/")[0]
            product_id = parts.split("-")[-1] if "-" in parts else parts

        if not title:
            return None

        return {
            "product_id": product_id,
            "name": title,
            "price": price,
            "original_price": original_price,
            "discount": f"{round((1 - price / original_price) * 100)}%"
            if price and original_price and original_price > price else "",
            "rating": rating,
            "review_count": review_count,
            "seller": seller,
            "category": category,
            "url": f"{BASE_URL}{url}" if url.startswith("/") else url,
            "scraped_at": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as e:
        logger.warning(f"解析商品失败: {e}")
        return None


# ── HTML 模式（备用）────────────────────────────────────

def search_html(session, keyword: str, page: int = 1) -> list[dict]:
    """通过 HTML 解析搜索结果（备用方案）"""
    from bs4 import BeautifulSoup

    url = f"{BASE_URL}/search/"
    params = {"text": keyword, "from_search": "true", "page": page}

    try:
        resp = session.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"HTML 请求失败 (page={page}): {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    products = []

    cards = soup.select('[data-index]')
    if not cards:
        cards = soup.select('.widget-search-result-container .tile-root')

    for card in cards:
        try:
            title_el = card.select_one('span[class*="tsBody"]') or card.select_one('a span')
            title = safe_text(title_el)
            if not title:
                continue

            price_el = card.select_one('span[class*="price"]') or card.select_one('[class*="Price"]')
            price = clean_price(safe_text(price_el))

            rating_el = card.select_one('[class*="rating"]')
            rating = None
            if rating_el:
                m = re.search(r"(\d+[.,]?\d*)", safe_text(rating_el))
                rating = float(m.group(1).replace(",", ".")) if m else None

            review_el = card.select_one('[class*="review"]')
            review_count = clean_int(safe_text(review_el))

            link_el = card.select_one('a[href*="/product/"]')
            url = link_el["href"] if link_el else ""
            product_id = ""
            if "/product/" in url:
                parts = url.split("/product/")[1].split("/")[0]
                product_id = parts.split("-")[-1] if "-" in parts else parts

            products.append({
                "product_id": product_id,
                "name": title,
                "price": price,
                "original_price": None,
                "discount": "",
                "rating": rating,
                "review_count": review_count,
                "seller": "",
                "category": "",
                "url": f"{BASE_URL}{url}" if url.startswith("/") else url,
                "scraped_at": datetime.now().isoformat(timespec="seconds"),
            })
        except Exception as e:
            logger.warning(f"解析卡片失败: {e}")
            continue

    logger.info(f"HTML page={page}: 获取 {len(products)} 条")
    return products


# ── 主流程 ───────────────────────────────────────────────

def run(
    keyword: str,
    pages: int = 3,
    mode: str = "api",
    proxy_pool: Optional[ProxyPool] = None,
    qps: float = 0.5,
) -> dict:
    """执行爬取

    Args:
        keyword: 搜索关键词
        pages: 爬取页数
        mode: api 或 html
        proxy_pool: 代理池，None 则直连
        qps: 每秒请求数上限（默认 0.5，即每 2 秒一个请求）
    """
    session = create_session(platform="ozon", proxy_pool=proxy_pool)
    limiter = RateLimiter(qps=qps)
    all_products = []

    logger.info(f"开始爬取: keyword='{keyword}', pages={pages}, mode={mode}")

    for page in range(1, pages + 1):
        limiter.wait()

        if mode == "api":
            products = search_api(session, keyword, page)
        else:
            products = search_html(session, keyword, page)

        all_products.extend(products)

        if page < pages:
            random_delay(3, 6)

    # 去重
    seen = set()
    unique = []
    for p in all_products:
        pid = p.get("product_id") or p.get("name")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)

    logger.info(f"总计: {len(unique)} 条（去重前 {len(all_products)} 条）")

    csv_file = save_csv(unique, prefix=f"ozon_{keyword}")
    json_file = save_json(unique, prefix=f"ozon_{keyword}")

    return {"total": len(unique), "csv": csv_file, "json": json_file}


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ozon 搜索结果爬取")
    parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    parser.add_argument("--pages", "-p", type=int, default=3, help="爬取页数 (默认 3)")
    parser.add_argument("--mode", "-m", choices=["api", "html"], default="api",
                        help="爬取模式: api (默认) 或 html")
    parser.add_argument("--proxy", help="代理地址，如 http://user:pass@host:port")
    parser.add_argument("--qps", type=float, default=0.5, help="每秒请求数上限 (默认 0.5)")
    args = parser.parse_args()

    pool = ProxyPool(args.proxy) if args.proxy else None
    result = run(args.keyword, args.pages, args.mode, proxy_pool=pool, qps=args.qps)

    print(f"\n✅ 完成! 共 {result['total']} 条")
    print(f"   CSV: {result['csv']}")
    print(f"   JSON: {result['json']}")
