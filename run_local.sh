#!/bin/bash
# 本机运行爬虫脚本

set -e

echo "=== 本机运行爬虫测试 ==="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.11+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查依赖
echo ""
echo "检查依赖..."
if ! python3 -c "import scrapy" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip3 install -r requirements.txt
fi

if ! python3 -c "import playwright" 2>/dev/null; then
    echo "📦 安装 Playwright 浏览器..."
    playwright install chromium
fi

# 检查MongoDB连接
echo ""
echo "检查MongoDB连接..."
MONGO_URI=${MONGO_URI:-"mongodb://localhost:27017/"}
MONGO_DATABASE=${MONGO_DATABASE:-"google_search"}
MONGO_COLLECTION=${MONGO_COLLECTION:-"results"}

# 尝试连接MongoDB
if python3 -c "from pymongo import MongoClient; MongoClient('$MONGO_URI').admin.command('ping')" 2>/dev/null; then
    echo "✅ MongoDB连接成功: $MONGO_URI"
else
    echo "⚠️  MongoDB连接失败，请确保MongoDB正在运行"
    echo "   可以使用: docker-compose up -d mongo"
    exit 1
fi

# 设置环境变量
export MONGO_URI=$MONGO_URI
export MONGO_DATABASE=$MONGO_DATABASE
export MONGO_COLLECTION=$MONGO_COLLECTION
export SEARCH_QUERY=${SEARCH_QUERY:-"python scrapy"}
export MAX_PAGES=${MAX_PAGES:-"2"}

echo ""
echo "=== 开始爬取 ==="
echo "搜索关键词: $SEARCH_QUERY"
echo "最大页数: $MAX_PAGES"
echo "MongoDB: $MONGO_URI$MONGO_DATABASE/$MONGO_COLLECTION"
echo ""

# 运行爬虫
cd /Users/jason/code/spider
scrapy crawl google_search

echo ""
echo "=== 爬取完成 ==="
echo ""
echo "查看结果:"
echo "  docker-compose exec mongo mongosh google_search --quiet --eval \"db.results.countDocuments()\""
echo "  或"
echo "  python3 -c \"from pymongo import MongoClient; db = MongoClient('$MONGO_URI')['$MONGO_DATABASE']; print('记录数:', db['$MONGO_COLLECTION'].count_documents({}))\""

