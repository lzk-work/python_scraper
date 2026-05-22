"""
爬虫通用工具包

模块划分:
  - session   : HTTP Session 管理（含代理支持）
  - proxy     : 代理池抽象（后续扩展）
  - rate      : 限速 & 延时策略
  - parser    : 数据清洗 & 解析工具
  - storage   : CSV / JSON 存储
  - logger    : 统一日志
"""

from .session import create_session
from .rate import random_delay, RateLimiter
from .proxy import ProxyPool
from .parser import clean_price, clean_int, safe_text
from .storage import save_csv, save_json
from .logger import logger

__all__ = [
    "create_session",
    "random_delay", "RateLimiter",
    "ProxyPool",
    "clean_price", "clean_int", "safe_text",
    "save_csv", "save_json",
    "logger",
]
