# Scrapy settings for spider_project project

BOT_NAME = 'spider_project'

SPIDER_MODULES = ['spider_project.spiders']
NEWSPIDER_MODULE = 'spider_project.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"  # 可选: chromium, firefox, webkit
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # 设置为 False 可以看到浏览器窗口
    "timeout": 30000,
}

# 可选: 使用代理
# PLAYWRIGHT_LAUNCH_OPTIONS = {
#     "headless": True,
#     "proxy": {
#         "server": "http://proxy.example.com:8080",
#     },
# }

# 请求延迟（秒）
DOWNLOAD_DELAY = 1

# 并发请求数
CONCURRENT_REQUESTS = 16

# 用户代理
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 日志级别
LOG_LEVEL = 'INFO'

# MongoDB 配置
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'google_search')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'results')

# 启用管道
ITEM_PIPELINES = {
    'spider_project.pipelines.SpiderProjectPipeline': 300,
    'spider_project.pipelines.MongoPipeline': 400,
}

