"""
爬虫模板 — 通用爬虫骨架

这是所有爬虫的基础模板，后面写沃尔玛、亚马逊爬虫都从这个改
"""
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import random
from datetime import datetime


class BaseScraper:
    """通用爬虫基类"""
    
    def __init__(self, platform_name):
        self.platform = platform_name
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """配置请求头（伪装浏览器）"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
    
    def fetch(self, url, params=None):
        """发送请求"""
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def parse(self, html):
        """解析 HTML（子类重写这个方法）"""
        raise NotImplementedError("子类必须实现 parse 方法")
    
    def save_csv(self, data, filename):
        """保存为 CSV"""
        if not data:
            return
        
        fieldnames = data[0].keys()
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"已保存 CSV: {filename}")
    
    def save_json(self, data, filename):
        """保存为 JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已保存 JSON: {filename}")
    
    def random_delay(self, min_sec=2, max_sec=5):
        """随机延时（避免被封）"""
        delay = random.uniform(min_sec, max_sec)
        print(f"等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    def run(self, *args, **kwargs):
        """主流程（子类重写这个方法）"""
        raise NotImplementedError("子类必须实现 run 方法")


# ============================================
# 示例：用模板写一个简单的爬虫
# ============================================

class ExampleScraper(BaseScraper):
    """示例爬虫：抓取 httpbin.org/html"""
    
    def __init__(self):
        super().__init__("example")
    
    def parse(self, html):
        """解析 HTML，提取标题和段落"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 提取标题
        title = soup.select_one("h1")
        title_text = title.text if title else "无标题"
        
        # 提取段落
        paragraphs = []
        for p in soup.select("p"):
            paragraphs.append(p.text.strip())
        
        return {
            "title": title_text,
            "paragraphs": paragraphs,
            "scraped_at": datetime.now().isoformat(),
        }
    
    def run(self, url):
        """执行爬取"""
        print(f"开始抓取: {url}")
        
        # 1. 发请求
        response = self.fetch(url)
        if not response:
            return None
        
        # 2. 解析
        data = self.parse(response.text)
        
        # 3. 输出
        print(f"\n抓取结果:")
        print(f"  标题: {data['title']}")
        print(f"  段落数: {len(data['paragraphs'])}")
        if data['paragraphs']:
            print(f"  第一段: {data['paragraphs'][0][:100]}...")
        
        return data


# ============================================
# 运行示例
# ============================================

if __name__ == "__main__":
    # 创建爬虫实例
    scraper = ExampleScraper()
    
    # 执行爬取
    result = scraper.run("https://httpbin.org/html")
    
    if result:
        # 保存结果
        scraper.save_json([result], "example_result.json")
    
    print("\n" + "="*50)
    print("模板说明")
    print("="*50)
    print("""
BaseScraper 提供了:
  1. fetch(url) → 发请求（带错误处理）
  2. parse(html) → 解析 HTML（子类重写）
  3. save_csv(data, filename) → 保存 CSV
  4. save_json(data, filename) → 保存 JSON
  5. random_delay() → 随机延时

使用方式:
  1. 继承 BaseScraper
  2. 重写 parse() 方法（定义如何解析 HTML）
  3. 重写 run() 方法（定义主流程）
  4. 调用 fetch()、parse()、save_xxx() 组合

后面写沃尔玛、亚马逊爬虫，都是这个套路。
""")
