# 谷歌搜索结果爬虫

使用 Scrapy + Playwright 爬取谷歌搜索结果，并将数据保存到 MongoDB。

## 功能特性

- ✅ 使用 Playwright 处理 JavaScript 渲染的页面
- ✅ 提取搜索结果标题、URL 和描述
- ✅ 支持多页爬取
- ✅ 自动保存到 MongoDB
- ✅ Docker Compose 一键部署

## 项目结构

```
.
├── docker-compose.yml      # Docker Compose 配置文件
├── Dockerfile              # Docker 镜像构建文件
├── requirements.txt        # Python 依赖
├── scrapy.cfg             # Scrapy 配置文件
└── spider_project/        # Scrapy 项目目录
    ├── __init__.py
    ├── items.py           # 数据项定义
    ├── pipelines.py       # 数据处理管道
    ├── settings.py        # Scrapy 设置
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
  - MAX_PAGES=5  # 最多爬取页数
```

或者使用环境变量文件 `.env`：

```bash
SEARCH_QUERY=python machine learning
MAX_PAGES=5
```

然后在 `docker-compose.yml` 中添加：

```yaml
env_file:
  - .env
```

### 3. 本地开发（不使用 Docker）

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 启动 MongoDB（需要本地安装 MongoDB）
# 或者使用 Docker 只启动 MongoDB：
docker-compose up mongo -d

# 运行爬虫
export MONGO_URI=mongodb://localhost:27017/
export SEARCH_QUERY="python scrapy"
export MAX_PAGES=3
scrapy crawl google_search
```

## 配置说明

### 环境变量

- `MONGO_URI`: MongoDB 连接地址（默认: `mongodb://mongo:27017/`）
- `MONGO_DATABASE`: 数据库名称（默认: `google_search`）
- `MONGO_COLLECTION`: 集合名称（默认: `results`）
- `SEARCH_QUERY`: 搜索关键词（默认: `python scrapy`）
- `MAX_PAGES`: 最多爬取页数（默认: `3`）

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
```

## 注意事项

1. **反爬虫机制**: 谷歌有反爬虫机制，建议：
   - 设置合理的请求延迟
   - 使用代理（可在 `settings.py` 中配置）
   - 不要过于频繁地爬取

2. **法律合规**: 请确保你的爬虫使用符合相关法律法规和网站的服务条款。

3. **数据去重**: 爬虫会自动根据 URL 和搜索关键词创建唯一索引，避免重复数据。

4. **错误处理**: 如果遇到验证码或访问限制，需要手动处理或使用更高级的反反爬虫策略。

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
docker-compose exec spider playwright install chromium
```

### 没有提取到数据

- 检查谷歌页面结构是否变化
- 查看日志：`docker-compose logs spider`
- 尝试增加等待时间或调整选择器

## 许可证

MIT License

