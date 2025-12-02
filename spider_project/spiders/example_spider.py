import scrapy
from scrapy_playwright.page import PageMethod


class ExampleSpider(scrapy.Spider):
    """
    使用 Scrapy + Playwright 的爬虫示例
    
    这个示例展示了如何使用 Playwright 处理 JavaScript 渲染的页面
    """
    name = 'example'
    allowed_domains = ['quotes.toscrape.com']
    
    def start_requests(self):
        """
        生成初始请求
        使用 playwright=True 启用 Playwright 下载处理器
        """
        urls = [
            'http://quotes.toscrape.com/js/',
        ]
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    # 可选: 等待页面加载完成
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.quote"),
                    ],
                    # 可选: 设置视口大小
                    "playwright_include_page": True,
                }
            )
    
    async def parse(self, response):
        """
        解析页面内容
        注意: 当使用 playwright_include_page=True 时，这是一个异步方法
        """
        # 提取所有名言
        quotes = response.css('div.quote')
        
        for quote in quotes:
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
        
        # 查找下一页链接
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.quote"),
                    ],
                }
            )

