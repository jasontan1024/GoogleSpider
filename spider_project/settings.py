# Scrapy settings for spider_project project
import os

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
    "headless": False,  # 有头模式，可以看到浏览器窗口
    "timeout": 30000,
    # 增强反检测参数
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-infobars",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--disable-translate",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-ipc-flooding-protection",
        "--enable-features=NetworkService,NetworkServiceLogging",
        "--force-color-profile=srgb",
        "--metrics-recording-only",
        "--use-mock-keychain",
        "--no-first-run",
        "--no-default-browser-check",
        "--password-store=basic",
        "--use-mock-keychain",
        "--lang=en-US,en",
    ],
}

# 设置浏览器上下文选项，使其更像真实浏览器
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "viewport": {"width": 1920, "height": 1080},
        # 使用最新的Chrome User-Agent
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "permissions": ["geolocation", "notifications"],
        "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
        "color_scheme": "light",
        # 添加更多真实浏览器特征
        "screen": {"width": 1920, "height": 1080},
        "has_touch": False,
        "is_mobile": False,
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        },
    }
}

# 可选: 使用代理
# PLAYWRIGHT_LAUNCH_OPTIONS = {
#     "headless": True,
#     "proxy": {
#         "server": "http://proxy.example.com:8080",
#     },
# }

# 请求延迟（秒）- 大幅增加延迟以降低请求频率
DOWNLOAD_DELAY = 15  # 增加到15秒，大幅降低请求频率

# 并发请求数 - 保持为1，确保串行请求
CONCURRENT_REQUESTS = 1

# 用户代理（与PLAYWRIGHT_CONTEXTS保持一致）
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# 随机化下载延迟（模拟人类行为）- 增加随机化范围
RANDOMIZE_DOWNLOAD_DELAY = 1.0  # 在DOWNLOAD_DELAY基础上随机化100%（即15-30秒之间）

# 每个域名的并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# 自动限流（启用自动限流功能）
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 10  # 初始延迟10秒
AUTOTHROTTLE_MAX_DELAY = 60  # 最大延迟60秒
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5  # 目标并发数（降低到0.5）
AUTOTHROTTLE_DEBUG = False  # 设置为True可以看到限流信息

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

