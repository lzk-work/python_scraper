"""Ozon 平台爬虫"""
from .ozon_search import run as search
from .ozon_product import run as fetch_products

__all__ = ["search", "fetch_products"]
