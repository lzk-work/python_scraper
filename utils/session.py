"""
HTTP Session 管理

功能:
  - 带重试机制的 requests.Session
  - 平台自适应 Headers（Accept-Language 等）
  - 代理池集成
  - UA 轮换
"""
import random
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .proxy import ProxyPool
from .logger import logger

# ── User-Agent 池 ────────────────────────────────────────

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

# ── 平台配置 ─────────────────────────────────────────────

PLATFORM_CONFIG = {
    "ozon": {
        "lang": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "base_url": "https://www.ozon.ru",
    },
    "walmart": {
        "lang": "en-US,en;q=0.9",
        "base_url": "https://www.walmart.com",
    },
    "amazon": {
        "lang": "en-US,en;q=0.9",
        "base_url": "https://www.amazon.com",
    },
}


def create_session(
    platform: str = "ozon",
    retries: int = 3,
    backoff: float = 0.5,
    proxy_pool: Optional[ProxyPool] = None,
) -> requests.Session:
    """创建带重试机制的 requests Session

    Args:
        platform: 平台名（ozon / walmart / amazon），决定 Headers
        retries: 重试次数
        backoff: 重试退避因子
        proxy_pool: 代理池实例，None 则直连

    Returns:
        配置好的 requests.Session
    """
    session = requests.Session()

    # 重试策略
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Headers
    config = PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG["ozon"])
    session.headers.update({
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": config["lang"],
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    })

    # 代理
    if proxy_pool:
        proxies = proxy_pool.get_proxy()
        if proxies:
            session.proxies.update(proxies)
            logger.debug(f"使用代理: {proxies}")

    return session


def rotate_ua(session: requests.Session):
    """轮换 User-Agent（用于长任务中途切换）"""
    session.headers["User-Agent"] = random.choice(_USER_AGENTS)
