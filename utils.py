"""
爬虫通用工具 - 适用于 Ozon / Walmart / Amazon 等多平台
"""
import time
import random
import re
import logging
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── User-Agent 池 ────────────────────────────────────────

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

# ── 平台语言配置 ──────────────────────────────────────────

PLATFORM_LANG = {
    "ozon": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "walmart": "en-US,en;q=0.9",
    "amazon": "en-US,en;q=0.9",
}


# ── Session ──────────────────────────────────────────────

def create_session(platform: str = "walmart", retries: int = 3, backoff: float = 0.5) -> requests.Session:
    """创建带重试机制的 requests session
    
    Args:
        platform: 平台名，决定 Accept-Language
        retries: 重试次数
        backoff: 重试退避因子
    """
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

    lang = PLATFORM_LANG.get(platform, "en-US,en;q=0.9")
    session.headers.update({
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": lang,
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    })
    return session


# ── Rate Limiting ────────────────────────────────────────

def random_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """随机延时，避免被封"""
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Sleeping {delay:.1f}s")
    time.sleep(delay)


# ── 数据清洗 ─────────────────────────────────────────────

def clean_price(text: str) -> Optional[float]:
    """清洗价格文本 → float
    支持格式:
      - "1 299 ₽" → 1299.0 (卢布)
      - "$1,299.99" → 1299.99 (美元)
      - "1.299,99 €" → 1299.99 (欧元)
    """
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.\s]", "", text).strip()
    cleaned = cleaned.replace(" ", "")
    if "," in cleaned and "." in cleaned:
        if cleaned.rindex(",") > cleaned.rindex("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def clean_int(text: str) -> Optional[int]:
    """清洗文本 → int
    示例: "1 234 отзыва" → 1234, "1,234 reviews" → 1234
    """
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else None


def safe_text(element) -> str:
    """安全提取 BeautifulSoup 元素文本"""
    if element is None:
        return ""
    return element.get_text(strip=True)
