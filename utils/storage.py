"""
数据存储工具

当前: CSV / JSON 文件存储
扩展: 可添加 MySQL / MongoDB / Elasticsearch 等
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from .logger import logger

# 默认数据目录（项目根下的 data/）
DATA_DIR = Path(__file__).parent.parent / "data"


def save_csv(
    data: list[dict],
    filename: Optional[str] = None,
    prefix: str = "data",
    fields: Optional[list[str]] = None,
    data_dir: Optional[Path] = None,
) -> str:
    """保存到 CSV

    Args:
        data: 要保存的数据
        filename: 指定文件名，None 则自动生成
        prefix: 文件名前缀（自动生成时使用）
        fields: CSV 字段列表，None 则取第一条数据的 keys
        data_dir: 数据目录，None 则用默认目录

    Returns:
        保存的文件路径
    """
    out_dir = data_dir or DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"

    filepath = out_dir / filename

    if not fields:
        fields = list(data[0].keys()) if data else []

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    logger.info(f"已保存 CSV: {filepath} ({len(data)} 条)")
    return str(filepath)


def save_json(
    data: list[dict],
    filename: Optional[str] = None,
    prefix: str = "data",
    data_dir: Optional[Path] = None,
) -> str:
    """保存到 JSON

    Args:
        data: 要保存的数据
        filename: 指定文件名，None 则自动生成
        prefix: 文件名前缀（自动生成时使用）
        data_dir: 数据目录，None 则用默认目录

    Returns:
        保存的文件路径
    """
    out_dir = data_dir or DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"

    filepath = out_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"已保存 JSON: {filepath} ({len(data)} 条)")
    return str(filepath)
