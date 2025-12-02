import scrapy
from scrapy_playwright.page import PageMethod
import json


class AdvancedSpider(scrapy.Spider):
    """
    高级示例：展示更多 Playwright 功能
    - 页面交互（点击、输入、滚动）
    - 截图
    - 执行 JavaScript
    - 处理动态内容
    """
    name = 'advanced'
    allowed_domains = ['quotes.toscrape.com']
    
    def start_requests(self):
        """生成初始请求"""
        yield scrapy.Request(
            url='http://quotes.toscrape.com/js/',
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # 等待元素出现
                    PageMethod("wait_for_selector", "div.quote"),
                    # 滚动到页面底部
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    # 等待一段时间（可选）
                    PageMethod("wait_for_timeout", 1000),
                ],
            }
        )
    
    async def parse(self, response):
        """
        解析页面
        使用 playwright_include_page=True 可以访问 Page 对象
        """
        page = response.meta["playwright_page"]
        
        # 示例1: 执行自定义 JavaScript
        quotes_count = await page.evaluate("document.querySelectorAll('div.quote').length")
        self.logger.info(f"找到 {quotes_count} 条名言")
        
        # 示例2: 截图（可选）
        # await page.screenshot(path="screenshot.png", full_page=True)
        
        # 示例3: 提取数据
        quotes = response.css('div.quote')
        for quote in quotes:
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
        
        # 示例4: 点击按钮或链接
        next_button = response.css('li.next a')
        if next_button:
            next_page_url = response.urljoin(next_button.attrib['href'])
            
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.quote"),
                    ],
                }
            )
        
        # 关闭页面
        await page.close()
    
    async def parse_with_interaction(self, response):
        """
        示例：与页面交互
        """
        page = response.meta["playwright_page"]
        
        # 点击按钮
        # await page.click('button.load-more')
        
        # 输入文本
        # await page.fill('input#search', 'search term')
        
        # 等待内容加载
        # await page.wait_for_selector('div.new-content')
        
        # 提取数据
        data = await page.evaluate("""
            () => {
                const quotes = [];
                document.querySelectorAll('div.quote').forEach(quote => {
                    quotes.push({
                        text: quote.querySelector('span.text').textContent,
                        author: quote.querySelector('small.author').textContent,
                        tags: Array.from(quote.querySelectorAll('a.tag')).map(t => t.textContent)
                    });
                });
                return quotes;
            }
        """)
        
        for item in data:
            yield item
        
        await page.close()

