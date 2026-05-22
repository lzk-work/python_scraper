"""
Ozon 爬虫通用工具
"""
import time
import random
import logging
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── Headers ──────────────────────────────────────────────

def get_headers() -> dict:
    """随机 User-Agent + 必要请求头"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }


# ── Session ──────────────────────────────────────────────

def create_session(retries: int = 3, backoff: float = 0.5):
    """创建带重试机制的 requests session"""
    import requests
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(get_headers())
    return session


# ── Rate Limiting ────────────────────────────────────────

def random_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """随机延时，避免被封"""
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Sleeping {delay:.1f}s")
    time.sleep(delay)


# ── Data Helpers ─────────────────────────────────────────

def clean_price(text: str) -> Optional[float]:
    """清洗价格文本 → float (₽)
    示例: "1 299 ₽" → 1299.0, "1 299,99 ₽" → 1299.99
    """
    if not text:
        return None
    import re
    # 去掉货币符号和空格，逗号换成点
    cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def clean_int(text: str) -> Optional[int]:
    """清洗文本 → int
    示例: "1 234 отзыва" → 1234
    """
    if not text:
        return None
    import re
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else None


def safe_text(element) -> str:
    """安全提取元素文本"""
    if element is None:
        return ""
    return element.get_text(strip=True)
