"""
代理池抽象层

当前: 基础实现（直连 / 单代理）
扩展: 对接代理池服务（快代理、芝麻代理、自建代理池）

用法:
  # 直连（默认）
  pool = ProxyPool()

  # 单代理
  pool = ProxyPool("http://user:pass@proxy:8080")

  # 代理列表（轮询）
  pool = ProxyPool(["http://p1:8080", "http://p2:8080"])

  # 自定义 provider（对接代理池 API）
  pool = ProxyPool(provider=my_provider_func)
"""
import random
from typing import Optional, Callable
from .logger import logger


class ProxyPool:
    """代理池管理器

    支持模式:
      1. 无代理（直连）
      2. 单代理
      3. 代理列表（轮询/随机）
      4. 自定义 provider 函数（对接代理池 API）

    扩展点:
      - 实现 provider 函数对接第三方代理池 API
      - 继承此类重写 get_proxy() 实现更复杂的策略
    """

    def __init__(
        self,
        proxies: Optional[str | list[str]] = None,
        provider: Optional[Callable[[], Optional[str]]] = None,
        strategy: str = "round_robin",  # round_robin | random
    ):
        self._provider = provider
        self._strategy = strategy
        self._index = 0

        if proxies is None:
            self._proxies = []
        elif isinstance(proxies, str):
            self._proxies = [proxies]
        else:
            self._proxies = list(proxies)

    def get_proxy(self) -> Optional[dict]:
        """获取一个代理，返回 requests 格式的 proxies dict

        Returns:
            None (直连) 或 {"http": "...", "https": "..."}
        """
        # 优先使用自定义 provider
        if self._provider:
            proxy_url = self._provider()
            if proxy_url:
                return self._to_requests_proxies(proxy_url)
            logger.warning("provider 返回空，使用直连")
            return None

        # 无代理
        if not self._proxies:
            return None

        # 从列表中取
        proxy_url = self._pick()
        return self._to_requests_proxies(proxy_url)

    def _pick(self) -> str:
        """根据策略选取代理"""
        if self._strategy == "random":
            return random.choice(self._proxies)
        # round_robin
        proxy = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return proxy

    @staticmethod
    def _to_requests_proxies(proxy_url: str) -> dict:
        """转换为 requests.Session.proxies 格式"""
        return {
            "http": proxy_url,
            "https": proxy_url,
        }

    def __len__(self) -> int:
        return len(self._proxies)

    def __repr__(self) -> str:
        if self._provider:
            return "ProxyPool(provider=custom)"
        if not self._proxies:
            return "ProxyPool(direct)"
        return f"ProxyPool({len(self._proxies)} proxies, strategy={self._strategy})"


# ── 预置 Provider 示例（对接代理池 API）──────────────────

def kdl_provider(api_url: str) -> Callable[[], Optional[str]]:
    """快代理 / 芝麻代理等 API 获取代理的示例

    用法:
      pool = ProxyPool(provider=kdl_provider("https://api.kdl.com/get?num=1"))
    """
    import requests as _req

    def _fetch() -> Optional[str]:
        try:
            resp = _req.get(api_url, timeout=5)
            resp.raise_for_status()
            text = resp.text.strip()
            if text:
                # 通常返回 "ip:port" 格式
                return f"http://{text}"
        except Exception as e:
            logger.error(f"获取代理失败: {e}")
        return None

    return _fetch
