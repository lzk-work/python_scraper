"""
限速 & 延时策略

当前: 固定范围随机延时
扩展: RateLimiter 令牌桶（用于批量爬取时控制整体速率）
"""
import time
import random
from .logger import logger


def random_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    """随机延时，避免被封"""
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"sleep {delay:.1f}s")
    time.sleep(delay)


class RateLimiter:
    """令牌桶限速器

    用于批量爬取时控制整体 QPS，避免短时间内请求过多。

    用法:
      limiter = RateLimiter(qps=2)  # 每秒最多 2 个请求

      for url in urls:
          limiter.wait()  # 如果太快会自动等待
          resp = session.get(url)
    """

    def __init__(self, qps: float = 1.0):
        """
        Args:
            qps: 每秒请求数上限
        """
        self._interval = 1.0 / qps if qps > 0 else 0
        self._last_time = 0.0

    def wait(self):
        """等待直到可以发起下一个请求"""
        if self._interval <= 0:
            return

        now = time.monotonic()
        elapsed = now - self._last_time
        if elapsed < self._interval:
            sleep_time = self._interval - elapsed
            logger.debug(f"rate limit: sleep {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self._last_time = time.monotonic()
