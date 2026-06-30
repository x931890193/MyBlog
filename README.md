# MyBlog

基于 Django 1.11 的个人技术博客，包含文章、相册、随机音乐、评论、赞赏、RSS 技术资讯采集和七牛 CDN 静态资源发布。仓库不包含生产密钥，首次部署通过 `.env.example` 生成本机 `.env`。

## 项目结构

```text
MyBlog/                     Django 项目配置、WSGI、运行时工具
blog/                       文章模型、视图、模板标签、management commands
blog/management/commands/   自定义管理命令，例如技术资讯采集
cdn/                        项目静态资源源目录，collectstatic 后发布到 CDN
spider/                     采集脚本和外部数据处理
templates/                  页面模板与历史静态样式
manage.py                   Django 命令入口
.env.example                环境变量示例，不包含真实密钥
```

## 环境变量

复制示例文件并填写真实值：

```bash
cp .env.example .env
```

真实 `.env` 只保留在服务器，不提交到 Git。当前运行时会自动加载项目根目录下的 `.env`，也可以用 `MYBLOG_ENV_FILE=/path/to/.env` 指定路径。

常用变量：

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
MYSQL_HOST
MYSQL_PORT
REDIS_HOST
REDIS_PORT
REDIS_DB
REDIS_PASSWD
MONGO_URI
MONGODB_NAME
HAYSTACK_URL
HAYSTACK_INDEX_NAME
STATIC_ROOT
MEDIA_ROOT
LOG_FILE_PATH
QINIU_STATIC_PREFIX
PAGE_CACHE_SECONDS
PAGE_CACHE_DEBUG_HEADER
SITE_INFO_CACHE_SECONDS
BANNER_CACHE_SECONDS
REQUEST_INFO_WRITE_INTERVAL_SECONDS
IP_REGION_LOOKUP_TIMEOUT_SECONDS
IP_REGION_LOOKUP_MISS_SECONDS
QINIU_ACCESS_KEY
QINIU_SECRET_KEY
QINIU_BUCKET_NAME
QINIU_BUCKET_DOMAIN
QINIU_SECURE_URL
GITALK_CLIENT_ID
GITALK_CLIENT_SECRET
VALINE_APP_ID
VALINE_APP_KEY
WEATHER_APP_ID
WEATHER_APP_SECRET
MUSIC_API_BASE_URL
MUSIC_LOGIN_EMAIL
MUSIC_LOGIN_PASSWORD
```

七牛配置为空时，项目默认使用本地 `/static/` 和 `/media/`，适合本地开发；生产环境填完整七牛变量后会自动切到 CDN。启用七牛时 `QINIU_STATIC_PREFIX` 默认是 `static`，不要填服务器绝对路径。

性能相关变量：

```text
PAGE_CACHE_SECONDS=900
PAGE_CACHE_DEBUG_HEADER=false
SITE_INFO_CACHE_SECONDS=60
BANNER_CACHE_SECONDS=300
REQUEST_INFO_WRITE_INTERVAL_SECONDS=60
IP_REGION_LOOKUP_TIMEOUT_SECONDS=0.4
IP_REGION_LOOKUP_MISS_SECONDS=3600
```

这些值控制匿名 HTML 微缓存、公共站点信息缓存、随机 banner 缓存、访客明细写库节流和 IP 归属接口超时。调大缓存能进一步降低数据库压力，调小则内容刷新更及时。文章详情、点赞接口、API、后台和上传路径默认不走 HTML 微缓存。

## 本地运行

项目依赖较老，建议使用独立虚拟环境。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

本地最少需要 MySQL 可连接，并按 `.env` 创建对应数据库。Redis、MongoDB、Elasticsearch、七牛、评论和天气配置可以后续补齐；缺少外部服务时，相关采集、搜索或上传能力不可用，但基础 Django 服务可以启动。

服务器当前虚拟环境路径：

```bash
/root/.virtualenvs/blog/bin/python
```

## 数据库

文章表已迁移到 `utf8mb4`，支持 emoji 和更多中文/英文特殊字符。

```bash
python manage.py migrate blog
python manage.py showmigrations blog
```

关键迁移：

```text
blog/migrations/0017_article_utf8mb4_and_lengths.py
```

## 静态资源和 CDN

样式源文件主要在：

```text
cdn/main.css
cdn/css/style.css
```

发布静态资源：

```bash
python manage.py collectstatic --noinput
```

CDN 缓存时间较长，页面模板中的 CSS URL 使用版本参数让浏览器立即获取新样式。生产环境发布到七牛前先确认 `.env` 中 `QINIU_ACCESS_KEY`、`QINIU_SECRET_KEY`、`QINIU_BUCKET_NAME`、`QINIU_BUCKET_DOMAIN` 已配置；本地开发不填这些值。

## 技术资讯采集

采集命令：

```bash
python manage.py import_tech_news --max-items 24 --per-source 2 --update-existing
```

dry-run：

```bash
python manage.py import_tech_news --dry-run --max-items 12 --per-source 1
```

采集逻辑：

- 使用公开 RSS/Atom Feed。
- 保存标题、摘要、公开 Feed 摘录和原文链接。
- 正文注明转载来源和版权说明。
- 根据标题、摘要、摘录关键词匹配已有分类。
- 不全文转载，降低版权风险，但不能完全消除转载合规风险。

当前定时任务：

```cron
23 6 * * * cd /data/MyBlog && /root/.virtualenvs/blog/bin/python manage.py import_tech_news --max-items 24 --per-source 2 --update-existing >> /data/logs/blog_tech_news.log 2>&1
```

## 部署

Supervisor 管理服务：

```bash
supervisorctl status blog
supervisorctl restart blog
```

常用上线流程：

```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
supervisorctl restart blog
```

## 安全规范

- 不提交 `.env`、真实密钥、数据库密码、七牛密钥、Gitalk secret、SSH 密钥。
- 新配置优先放入 `.env`，代码只读取环境变量。
- 七牛 SDK host cache、`.bash_history`、日志、上传文件、静态构建产物不进入 Git。
- 提交前检查：

```bash
git diff --check
git status --short
```
