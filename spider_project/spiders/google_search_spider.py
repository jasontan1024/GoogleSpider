import scrapy
from scrapy_playwright.page import PageMethod
from spider_project.items import GoogleSearchItem
from urllib.parse import quote_plus
import os
from datetime import datetime


class GoogleSearchSpider(scrapy.Spider):
    """
    谷歌搜索结果爬虫
    
    使用 Playwright 处理 JavaScript 渲染的搜索结果页面
    收集标题、URL 和描述信息
    """
    name = 'google_search'
    allowed_domains = ['google.com', 'www.google.com']
    
    # 从环境变量获取搜索关键词，默认为 'python scrapy'
    search_query = os.getenv('SEARCH_QUERY', 'python scrapy')
    max_pages = int(os.getenv('MAX_PAGES', '3'))  # 最多爬取页数
    
    def start_requests(self):
        """生成初始搜索请求"""
        # 构建谷歌搜索 URL
        search_url = f"https://www.google.com/search?q={quote_plus(self.search_query)}&hl=en"
        
        self.logger.info(f"开始搜索: {self.search_query}")
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # 等待搜索结果加载
                    PageMethod("wait_for_selector", "div.g", timeout=10000),
                    # 等待页面完全加载
                    PageMethod("wait_for_load_state", "networkidle"),
                ],
            },
            dont_filter=True
        )
    
    async def parse(self, response):
        """解析搜索结果页面"""
        page = response.meta.get("playwright_page")
        page_number = response.meta.get("page_number", 1)
        
        try:
            # 等待搜索结果容器加载
            await page.wait_for_selector("div.g", timeout=10000)
            
            # 滚动页面以确保所有内容加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            
            # 提取搜索结果
            results = response.css('div.g')
            extracted_count = 0
            
            if not results:
                # 如果没有找到结果，尝试使用 JavaScript 提取
                self.logger.warning("使用 CSS 选择器未找到结果，尝试使用 JavaScript 提取")
                results_data = await page.evaluate("""
                    () => {
                        const results = [];
                        const elements = document.querySelectorAll('div.g');
                        elements.forEach(el => {
                            const titleEl = el.querySelector('h3');
                            const linkEl = el.querySelector('a[href]');
                            const descEl = el.querySelector('div.VwiC3b, div.s, span.st');
                            
                            if (titleEl && linkEl) {
                                results.push({
                                    title: titleEl.textContent.trim(),
                                    url: linkEl.getAttribute('href'),
                                    description: descEl ? descEl.textContent.trim() : ''
                                });
                            }
                        });
                        return results;
                    }
                """)
                
                for result in results_data:
                    item = GoogleSearchItem()
                    item['title'] = result.get('title', '')
                    item['url'] = result.get('url', '')
                    item['description'] = result.get('description', '')
                    item['search_query'] = self.search_query
                    item['page_number'] = page_number
                    item['crawled_at'] = datetime.now().isoformat()
                    yield item
                    extracted_count += 1
            else:
                # 使用 CSS 选择器提取
                for result in results:
                    item = GoogleSearchItem()
                    
                    # 提取标题
                    title = result.css('h3::text').get()
                    if not title:
                        title = result.css('h3 span::text').get()
                    
                    # 提取 URL
                    url = result.css('a[href]::attr(href)').get()
                    if url and url.startswith('/url?q='):
                        # 处理谷歌的 URL 重定向
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        url = parsed.get('q', [url])[0]
                    
                    # 提取描述
                    description = result.css('div.VwiC3b::text, div.s span.st::text, span.st::text').get()
                    if not description:
                        description = ''.join(result.css('div.VwiC3b *::text, div.s *::text').getall())
                    
                    if title and url:
                        item['title'] = title.strip()
                        item['url'] = url.strip()
                        item['description'] = description.strip() if description else ''
                        item['search_query'] = self.search_query
                        item['page_number'] = page_number
                        item['crawled_at'] = datetime.now().isoformat()
                        yield item
                        extracted_count += 1
            
            self.logger.info(f"第 {page_number} 页提取了 {extracted_count} 个结果")
            
            # 检查是否有下一页
            if page_number < self.max_pages:
                next_page_url = None
                
                # 方法1: 查找下一页按钮（多种选择器）
                next_selectors = [
                    'a#pnnext',  # 标准下一页按钮
                    'a[aria-label="Next"]',  # 通过 aria-label
                    'a[id*="next"]',  # 包含 next 的 id
                    'td:has-text("Next") a',  # 包含 Next 文本的链接
                ]
                
                for selector in next_selectors:
                    try:
                        next_button = await page.query_selector(selector)
                        if next_button:
                            next_page_url = await next_button.get_attribute('href')
                            if next_page_url:
                                self.logger.info(f"通过选择器 '{selector}' 找到下一页")
                                break
                    except Exception as e:
                        self.logger.debug(f"选择器 '{selector}' 未找到: {e}")
                
                # 方法2: 如果没找到按钮，尝试直接构建下一页 URL
                if not next_page_url:
                    try:
                        # 谷歌搜索的翻页通常使用 start 参数
                        import urllib.parse
                        parsed = urllib.parse.urlparse(response.url)
                        params = urllib.parse.parse_qs(parsed.query)
                        
                        # 计算下一页的 start 值（每页通常 10 个结果）
                        current_start = int(params.get('start', ['0'])[0])
                        next_start = current_start + 10
                        
                        params['start'] = [str(next_start)]
                        new_query = urllib.parse.urlencode(params, doseq=True)
                        next_page_url = urllib.parse.urlunparse((
                            parsed.scheme,
                            parsed.netloc,
                            parsed.path,
                            parsed.params,
                            new_query,
                            parsed.fragment
                        ))
                        self.logger.info(f"通过 URL 构建找到下一页: {next_page_url}")
                    except Exception as e:
                        self.logger.warning(f"构建下一页 URL 失败: {e}")
                
                # 如果找到了下一页 URL，生成请求
                if next_page_url:
                    if not next_page_url.startswith('http'):
                        next_page_url = response.urljoin(next_page_url)
                    
                    self.logger.info(f"准备爬取第 {page_number + 1} 页: {next_page_url}")
                    
                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "div.g", timeout=10000),
                                PageMethod("wait_for_load_state", "networkidle"),
                            ],
                            "page_number": page_number + 1,
                        },
                        dont_filter=True
                    )
                else:
                    self.logger.info("未找到下一页，爬取完成")
            else:
                self.logger.info(f"已达到最大页数限制 ({self.max_pages})，爬取完成")
        
        except Exception as e:
            self.logger.error(f"解析页面时出错: {e}")
        
        finally:
            if page:
                await page.close()

