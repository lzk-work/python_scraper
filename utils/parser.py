"""
数据清洗 & 解析工具

支持多币种价格、评论数提取等常见爬虫数据清洗场景。
"""
import re
from typing import Optional


def clean_price(text: str) -> Optional[float]:
    """清洗价格文本 → float

    支持格式:
      - "1 299 ₽" → 1299.0 (卢布)
      - "$1,299.99" → 1299.99 (美元)
      - "1.299,99 €" → 1299.99 (欧元)
      - "¥199.00" → 199.0 (人民币/日元)
    """
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.\s]", "", text).strip()
    cleaned = cleaned.replace(" ", "")
    if not cleaned:
        return None

    # 同时有逗号和句号，判断哪个是小数分隔符
    if "," in cleaned and "." in cleaned:
        if cleaned.rindex(",") > cleaned.rindex("."):
            # 1.299,99 → 1299.99
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # 1,299.99 → 1299.99
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:
            # 199,99 → 199.99
            cleaned = cleaned.replace(",", ".")
        else:
            # 1,299 → 1299
            cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
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
    """安全提取 BeautifulSoup 元素文本，避免 None 报错"""
    if element is None:
        return ""
    return element.get_text(strip=True)
