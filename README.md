# 谷歌搜索结果爬虫

使用 Scrapy + Playwright 爬取谷歌搜索结果，并将数据保存到 MongoDB。

## 功能特性

- ✅ 使用 Playwright 处理 JavaScript 渲染的页面
- ✅ 提取搜索结果标题、URL 和描述
- ✅ 支持多页爬取
- ✅ 自动保存到 MongoDB
- ✅ Docker Compose 一键部署
- ✅ 配置化提取元素（通过 `config.json`）
- ✅ JavaScript 代码独立存放（`js/` 文件夹）
- ✅ 反检测措施（指纹保护、行为模拟）
- ✅ 支持有头/无头模式
- ✅ 支持手动完成验证码（有头模式下）
- ✅ 降低请求频率，模拟人类行为

## 项目结构

```
.
├── docker-compose.yml      # Docker Compose 配置文件
├── Dockerfile              # Docker 镜像构建文件
├── requirements.txt        # Python 依赖
├── scrapy.cfg             # Scrapy 配置文件
├── run_local.sh           # 本机运行脚本
├── logs/                  # 日志目录（自动创建）
└── spider_project/        # Scrapy 项目目录
    ├── __init__.py
    ├── items.py           # 数据项定义
    ├── pipelines.py       # 数据处理管道
    ├── settings.py        # Scrapy 设置
    ├── config.json        # 提取元素配置（必须）
    └── js/                # JavaScript 代码目录
        ├── extractors.js      # 数据提取脚本（必须）
        ├── stealth.js         # 反检测脚本（页面加载前）
        ├── stealth_after.js   # 反检测脚本（页面加载后）
        ├── human_behavior.js  # 人类行为模拟
        ├── debug.js           # 调试工具
        └── utils.js           # 工具函数
    └── spiders/           # 爬虫目录
        ├── __init__.py
        └── google_search_spider.py  # 谷歌搜索爬虫
```

## 快速开始

### 1. 使用 Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 查看日志
docker-compose logs -f spider

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 2. 自定义搜索关键词

编辑 `docker-compose.yml` 文件，修改环境变量：

```yaml
environment:
  - SEARCH_QUERY=你的搜索关键词
  - MAX_PAGES=2  # 最多爬取页数
```

或者使用环境变量文件 `.env`：

```bash
SEARCH_QUERY=python machine learning
MAX_PAGES=2
```

然后在 `docker-compose.yml` 中添加：

```yaml
env_file:
  - .env
```

### 3. 本地开发（不使用 Docker）

#### 方式一：使用提供的脚本（推荐）

```bash
# 赋予执行权限（首次运行）
chmod +x run_local.sh

# 运行脚本（会自动创建虚拟环境、安装依赖、运行爬虫）
./run_local.sh
```

脚本会自动：
- 创建虚拟环境（如果不存在）
- 激活虚拟环境
- 安装依赖
- 安装 Playwright 浏览器
- 检查 MongoDB 连接
- 运行爬虫

#### 方式二：手动运行

```bash
# 创建虚拟环境（如果不存在）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 启动 MongoDB（需要本地安装 MongoDB）
# 或者使用 Docker 只启动 MongoDB：
docker-compose up mongo -d

# 设置环境变量并运行爬虫
export MONGO_URI="mongodb://localhost:27017/"
export MONGO_DATABASE="google_search"
export MONGO_COLLECTION="results"
export SEARCH_QUERY="python scrapy"
export MAX_PAGES=2
scrapy crawl google_search
```

**重要提示**：
- 必须激活虚拟环境后再运行 `scrapy crawl google_search`
- 脚本会自动使用虚拟环境中的 Python 和依赖

## 配置说明

### 环境变量

- `MONGO_URI`: MongoDB 连接地址（默认: `mongodb://mongo:27017/`）
- `MONGO_DATABASE`: 数据库名称（默认: `google_search`）
- `MONGO_COLLECTION`: 集合名称（默认: `results`）
- `SEARCH_QUERY`: 搜索关键词（默认: `python scrapy`）
- `MAX_PAGES`: 最多爬取页数（默认: `2`）

### 配置文件

#### `spider_project/config.json`

配置所有提取元素的选择器，包括：
- 结果容器选择器
- 标题选择器
- URL 选择器
- 描述选择器
- 下一页选择器
- 验证码检测关键词

**注意**: 此文件必须存在，否则爬虫无法启动。

#### `spider_project/settings.py`

- `DOWNLOAD_DELAY`: 请求延迟（默认: 15秒，随机化后15-30秒）
- `CONCURRENT_REQUESTS`: 并发请求数（默认: 1）
- `AUTOTHROTTLE_ENABLED`: 自动限流（默认: True）
- `PLAYWRIGHT_LAUNCH_OPTIONS["headless"]`: 有头/无头模式（默认: False，有头模式）

### 有头/无头模式

在 `spider_project/settings.py` 中修改：

```python
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,  # True = 无头模式, False = 有头模式
    # ...
}
```

**有头模式**：
- 浏览器窗口会自动打开
- 可以看到爬虫运行过程
- 如果遇到验证码，可以在浏览器中手动完成
- 爬虫会等待最多60秒，等待您完成验证码

**无头模式**：
- 后台运行，不显示浏览器窗口
- 适合生产环境

### MongoDB 数据格式

```json
{
  "title": "搜索结果标题",
  "url": "https://example.com",
  "description": "搜索结果描述",
  "search_query": "python scrapy",
  "page_number": 1,
  "crawled_at": "2024-01-01T12:00:00"
}
```

## 查看数据

### 使用 MongoDB Shell

```bash
# 进入 MongoDB 容器
docker-compose exec mongo mongosh

# 在 MongoDB Shell 中
use google_search
db.results.find().pretty()
db.results.countDocuments()

# 按页码统计
db.results.aggregate([
  {$group: {_id: "$page_number", count: {$sum: 1}}},
  {$sort: {_id: 1}}
])
```

### 使用 Python

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['google_search']
collection = db['results']

# 查询所有结果
for result in collection.find():
    print(result)

# 统计数量
print(collection.count_documents({}))

# 按页码统计
from collections import Counter
page_counts = Counter(r['page_number'] for r in collection.find())
print(page_counts)
```

## 反检测措施

项目已实现多种反检测措施：

1. **浏览器指纹保护**：
   - Canvas/WebGL/音频指纹保护
   - 硬件信息伪装
   - 网络连接信息伪装

2. **自动化痕迹清除**：
   - 隐藏 webdriver 特征
   - 删除 CDP 痕迹
   - 修改 Chrome 对象

3. **人类行为模拟**：
   - 平滑鼠标移动
   - 智能滚动
   - 随机等待时间

4. **请求频率控制**：
   - 基础延迟：15秒（随机化后15-30秒）
   - 页面内等待：5-10秒
   - 翻页前延迟：10-20秒
   - 自动限流：启用

## 注意事项

1. **反爬虫机制**: 谷歌有强大的反爬虫机制，建议：
   - 使用代理服务器（在 `settings.py` 中配置）
   - 使用住宅代理或高质量代理服务
   - 不要过于频繁地爬取

2. **法律合规**: 请确保你的爬虫使用符合相关法律法规和网站的服务条款。

3. **数据去重**: 爬虫会自动根据 URL 和搜索关键词创建唯一索引，避免重复数据。

4. **验证码处理**: 
   - 有头模式下，如果遇到验证码，可以在浏览器中手动完成
   - 爬虫会等待最多60秒，等待您完成验证码
   - 无头模式下，建议使用代理或 Google Custom Search API

5. **配置文件**: 
   - `config.json` 必须存在，否则爬虫无法启动
   - `js/extractors.js` 必须存在，否则无法提取数据

## 故障排除

### 爬虫无法连接 MongoDB

确保 MongoDB 服务已启动并健康：

```bash
docker-compose ps
docker-compose logs mongo
```

### Playwright 浏览器问题

如果遇到浏览器相关错误，尝试重新安装：

```bash
# Docker 环境
docker-compose exec spider playwright install chromium

# 本地环境
playwright install chromium
```

### 配置文件缺失

如果遇到 `FileNotFoundError: 配置文件不存在`：

确保以下文件存在：
- `spider_project/config.json`（必须）
- `spider_project/js/extractors.js`（必须）

### 没有提取到数据 / 遇到验证码

**常见问题：谷歌检测到自动化访问并显示验证码**

这是谷歌的反爬虫机制。如果遇到验证码，可以尝试以下解决方案：

1. **使用有头模式并手动完成验证码**（推荐用于测试）：
   - 在 `settings.py` 中设置 `headless: False`
   - 浏览器窗口会自动打开
   - 如果遇到验证码，在浏览器中手动完成
   - 爬虫会等待最多60秒

2. **使用代理服务器**（推荐用于生产）：
   - 在 `settings.py` 中配置代理：
   ```python
   PLAYWRIGHT_LAUNCH_OPTIONS = {
       "headless": True,
       "proxy": {
           "server": "http://your-proxy-server:port",
           "username": "your-username",  # 如果需要
           "password": "your-password",  # 如果需要
       },
   }
   ```
   - 使用住宅代理或高质量代理服务

3. **使用 Google Custom Search API**（最稳定）：
   - 这是谷歌官方提供的搜索 API
   - 需要 API 密钥，但更稳定可靠
   - 参考：https://developers.google.com/custom-search/v1/overview

4. **检查调试文件**：
   - 查看 `logs/page_screenshot.png` 查看实际页面
   - 查看 `logs/page_content.html` 查看页面源码
   - 查看 `logs/page_info.json` 查看页面信息

5. **进一步降低请求频率**：
   - 在 `settings.py` 中增加 `DOWNLOAD_DELAY`
   - 在 `google_search_spider.py` 中增加页面内等待时间

### 页面关闭错误

如果遇到 `Target page, context or browser has been closed`：

- 有头模式下，请不要手动关闭浏览器窗口
- 浏览器会在爬取完成后自动关闭
- 如果必须关闭，请使用 Ctrl+C 停止爬虫

## 许可证

MIT License
