import scrapy
from scrapy_playwright.page import PageMethod
from spider_project.items import GoogleSearchItem
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
import os
from datetime import datetime
import json
from pathlib import Path


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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_path = Path(__file__).parent.parent
        js_path = base_path / 'js'
        
        # 加载配置文件（必须，无默认配置）
        config_path = base_path / 'config.json'
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info(f"已加载配置文件: {config_path}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}") from e
        
        # 加载 JavaScript 提取脚本（必须）
        extractor_path = js_path / 'extractors.js'
        if not extractor_path.exists():
            raise FileNotFoundError(f"JavaScript 提取器不存在: {extractor_path}")
        
        try:
            with open(extractor_path, 'r', encoding='utf-8') as f:
                self.extractor_js = f.read()
            self.logger.info(f"已加载 JavaScript 提取器: {extractor_path}")
        except Exception as e:
            raise RuntimeError(f"加载 JavaScript 提取器失败: {e}") from e
        
        # 加载工具函数脚本（可选）
        utils_path = js_path / 'utils.js'
        try:
            if utils_path.exists():
                with open(utils_path, 'r', encoding='utf-8') as f:
                    self.utils_js = f.read()
            else:
                self.utils_js = None
        except Exception as e:
            self.logger.warning(f"加载工具函数脚本失败: {e}")
            self.utils_js = None
        
        # 加载人类行为模拟脚本（可选）
        human_behavior_path = js_path / 'human_behavior.js'
        try:
            if human_behavior_path.exists():
                with open(human_behavior_path, 'r', encoding='utf-8') as f:
                    self.human_behavior_js = f.read()
            else:
                self.human_behavior_js = None
        except Exception as e:
            self.logger.warning(f"加载人类行为模拟脚本失败: {e}")
            self.human_behavior_js = None
        
        # 加载反检测脚本
        stealth_init_path = js_path / 'stealth.js'
        stealth_after_path = js_path / 'stealth_after.js'
        
        try:
            if stealth_init_path.exists():
                with open(stealth_init_path, 'r', encoding='utf-8') as f:
                    self.stealth_init_js = f.read()
            else:
                self.stealth_init_js = None
                self.logger.warning(f"反检测脚本不存在: {stealth_init_path}")
        except Exception as e:
            self.logger.warning(f"加载反检测脚本失败: {e}")
            self.stealth_init_js = None
        
        try:
            if stealth_after_path.exists():
                with open(stealth_after_path, 'r', encoding='utf-8') as f:
                    self.stealth_after_js = f.read()
            else:
                self.stealth_after_js = None
                self.logger.warning(f"反检测脚本不存在: {stealth_after_path}")
        except Exception as e:
            self.logger.warning(f"加载反检测脚本失败: {e}")
            self.stealth_after_js = None
    
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
                    # 等待页面完全加载
                    PageMethod("wait_for_load_state", "networkidle", timeout=60000),
                ],
            },
            dont_filter=True
        )
    
    async def parse(self, response):
        """解析搜索结果页面"""
        page = response.meta.get("playwright_page")
        page_number = response.meta.get("page_number", 1)
        
        try:
            # 在页面加载前注入反检测脚本
            if self.stealth_init_js:
                await page.add_init_script(self.stealth_init_js)
            
            # 注入人类行为模拟脚本
            if self.human_behavior_js:
                await page.add_init_script(self.human_behavior_js)
            
            # 等待页面加载完成
            self.logger.info(f"等待页面加载完成...")
            await page.wait_for_load_state("networkidle", timeout=60000)
            
            # 模拟人类行为：随机等待和滚动（增加等待时间以降低频率）
            import random
            initial_wait = 5000 + random.randint(0, 5000)  # 5-10秒随机等待
            self.logger.info(f"页面加载后等待 {initial_wait/1000:.1f} 秒...")
            await page.wait_for_timeout(initial_wait)
            
            # 模拟鼠标移动和滚动（增加等待时间以降低频率）
            try:
                # 随机滚动
                scroll_amount = random.randint(100, 500)
                await page.evaluate(f"window.scrollBy(0, {scroll_amount});")
                scroll_wait1 = 2000 + random.randint(0, 3000)  # 2-5秒等待
                await page.wait_for_timeout(scroll_wait1)
                
                # 继续滚动
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3);")
                scroll_wait2 = 2000 + random.randint(0, 3000)  # 2-5秒等待
                await page.wait_for_timeout(scroll_wait2)
                
                # 滚动回顶部附近
                await page.evaluate("window.scrollTo(0, 100);")
                scroll_wait3 = 3000 + random.randint(0, 5000)  # 3-8秒等待
                await page.wait_for_timeout(scroll_wait3)
                total_wait = initial_wait + scroll_wait1 + scroll_wait2 + scroll_wait3
                self.logger.info(f"页面交互完成，总等待时间约 {total_wait/1000:.1f} 秒")
            except Exception as e:
                self.logger.debug(f"模拟滚动时出错: {e}")
            
            # 注入更多反检测脚本
            if self.stealth_after_js:
                try:
                    await page.evaluate(self.stealth_after_js)
                except Exception as e:
                    self.logger.warning(f"注入反检测脚本失败（页面可能已关闭）: {e}")
                    # 检查页面是否仍然有效
                    if page.is_closed():
                        self.logger.error("页面已被关闭，无法继续")
                        return
            
            # 保存页面内容以便调试（总是保存第一页）
            if page_number == 1:
                try:
                    # 检查logs目录是否存在，不存在则创建
                    logs_dir = Path(__file__).parent.parent.parent / "logs"
                    logs_dir.mkdir(exist_ok=True)
                    
                    screenshot_path = logs_dir / "page_screenshot.png"
                    html_path = logs_dir / "page_content.html"
                    
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    html_content = await page.content()
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    self.logger.info(f"已保存页面截图和HTML到 {logs_dir}/ 目录")
                except Exception as e:
                    self.logger.warning(f"保存调试文件失败: {e}")
            
            # 检查是否有验证码或其他拦截页面
            page_title = await page.title()
            # 使用工具函数获取页面文本
            if self.utils_js:
                page_text = await page.evaluate(f"{self.utils_js}\ngetPageText();")
            else:
                # 如果工具函数未加载，使用简单方式
                page_text = await page.evaluate("document.body.innerText")
            page_url = page.url
            
            self.logger.info(f"页面标题: {page_title}")
            self.logger.info(f"页面URL: {page_url}")
            
            # 更宽松的验证码检测 - 从配置中读取
            captcha_indicators = self.config['validation']['captcha_indicators']
            has_captcha = any(indicator in page_text.lower() for indicator in captcha_indicators)
            
            if has_captcha:
                self.logger.warning("⚠️  检测到验证码页面！")
                self.logger.warning("📌 请在浏览器窗口中手动完成验证码")
                self.logger.warning("⏳ 等待60秒，请在此期间完成验证码...")
                
                # 等待用户完成验证码（最多60秒）
                import asyncio
                max_wait_time = 60  # 最多等待60秒
                check_interval = 3  # 每3秒检查一次
                waited_time = 0
                
                while waited_time < max_wait_time:
                    await asyncio.sleep(check_interval)
                    waited_time += check_interval
                    
                    # 检查页面是否已不再是验证码页面
                    try:
                        current_url = page.url
                        current_title = await page.title()
                        current_text = ""
                        if self.utils_js:
                            current_text = await page.evaluate(f"{self.utils_js}\ngetPageText();")
                        else:
                            current_text = await page.evaluate("document.body.innerText")
                        
                        # 检查是否还在验证码页面
                        still_captcha = any(indicator in current_text.lower() for indicator in captcha_indicators) or "sorry" in current_url.lower()
                        
                        if not still_captcha:
                            self.logger.info(f"✅ 验证码已完成！等待了 {waited_time} 秒")
                            # 等待页面稳定
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            await page.wait_for_timeout(2000)
                            break
                        else:
                            remaining = max_wait_time - waited_time
                            if remaining > 0 and waited_time % 10 == 0:  # 每10秒提示一次
                                self.logger.info(f"⏳ 仍在等待验证码完成... 剩余 {remaining} 秒")
                    except Exception as e:
                        self.logger.debug(f"检查验证码状态时出错: {e}")
                
                if waited_time >= max_wait_time:
                    self.logger.warning("⏰ 等待超时，继续尝试提取数据...")
                else:
                    self.logger.info("✅ 验证码已完成，继续提取数据...")
            
            # 使用 JavaScript 直接提取搜索结果（更可靠）
            self.logger.info("开始提取搜索结果...")
            
            # 执行提取函数，传入配置
            # extractor_js 已从文件加载，包含 executeExtraction 函数
            js_code = f"{self.extractor_js}\nexecuteExtraction({json.dumps(self.config, ensure_ascii=False)});"
            
            results_data = await page.evaluate(js_code)
            
            # 处理提取到的数据
            extracted_count = 0
            if results_data and len(results_data) > 0:
                self.logger.info(f"通过 JavaScript 提取到 {len(results_data)} 个结果")
                
                for result in results_data:
                    try:
                        item = GoogleSearchItem()
                        item['title'] = result.get('title', '').strip()
                        item['url'] = result.get('url', '').strip()
                        item['description'] = result.get('description', '').strip()
                        item['search_query'] = self.search_query
                        item['page_number'] = page_number
                        item['crawled_at'] = datetime.now().isoformat()
                        
                        # 验证数据有效性
                        if item['title'] and item['url']:
                            yield item
                            extracted_count += 1
                    except Exception as e:
                        self.logger.warning(f"处理结果时出错: {e}")
            else:
                self.logger.warning("未提取到任何结果！")
                # 保存页面信息以便调试
                try:
                    # 读取调试脚本
                    debug_js_path = Path(__file__).parent.parent / 'js' / 'debug.js'
                    if debug_js_path.exists():
                        with open(debug_js_path, 'r', encoding='utf-8') as f:
                            debug_js = f.read()
                        # 执行调试脚本
                        page_info = await page.evaluate(f"{debug_js}\ngetPageInfo();")
                    else:
                        # 如果文件不存在，使用简单的页面信息
                        if self.utils_js:
                            body_text = (await page.evaluate(f"{self.utils_js}\ngetPageText();"))[:500]
                        else:
                            body_text = (await page.evaluate("document.body.innerText"))[:500]
                        
                        page_info = {
                            "title": await page.title(),
                            "url": page.url,
                            "bodyText": body_text
                        }
                    # 使用相对路径保存日志
                    logs_dir = Path(__file__).parent.parent.parent / "logs"
                    logs_dir.mkdir(exist_ok=True)
                    page_info_path = logs_dir / "page_info.json"
                    with open(page_info_path, "w", encoding="utf-8") as f:
                        json.dump(page_info, f, ensure_ascii=False, indent=2)
                    self.logger.info(f"页面信息已保存到: {page_info_path}")
                except Exception as e:
                    self.logger.error(f"保存页面信息失败: {e}")
            
            self.logger.info(f"第 {page_number} 页成功提取了 {extracted_count} 个结果")
            
            # 检查是否有下一页
            if page_number < self.max_pages and extracted_count > 0:
                next_page_url = None
                
                # 方法1: 查找下一页按钮 - 从配置中读取
                next_selectors = self.config['selectors']['next_page']['selectors']
                
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
                        parsed = urlparse(response.url)
                        params = parse_qs(parsed.query)
                        current_start = int(params.get('start', ['0'])[0])
                        next_start = current_start + 10
                        params['start'] = [str(next_start)]
                        new_query = urlencode(params, doseq=True)
                        next_page_url = urlunparse((
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
                    
                    # 在翻页前添加额外延迟，降低请求频率
                    import random
                    page_delay = 10 + random.randint(0, 10)  # 10-20秒额外延迟
                    self.logger.info(f"翻页前等待 {page_delay} 秒以降低请求频率...")
                    await page.wait_for_timeout(page_delay * 1000)
                    
                    self.logger.info(f"准备爬取第 {page_number + 1} 页: {next_page_url}")
                    
                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_load_state", "networkidle", timeout=60000),
                            ],
                            "page_number": page_number + 1,
                        },
                        dont_filter=True
                    )
                else:
                    self.logger.info("未找到下一页，爬取完成")
            elif extracted_count == 0:
                self.logger.warning("未提取到数据，停止翻页")
            else:
                self.logger.info(f"已达到最大页数限制 ({self.max_pages})，爬取完成")
        
        except Exception as e:
            self.logger.error(f"解析页面时出错: {e}", exc_info=True)
            # 保存错误信息
            try:
                error_info = {
                    "error": str(e),
                    "url": response.url,
                    "page_number": page_number
                }
                # 使用相对路径保存错误信息
                logs_dir = Path(__file__).parent.parent.parent / "logs"
                logs_dir.mkdir(exist_ok=True)
                error_info_path = logs_dir / "error_info.json"
                with open(error_info_path, "w", encoding="utf-8") as f:
                    json.dump(error_info, f, ensure_ascii=False, indent=2)
            except:
                pass
        
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
