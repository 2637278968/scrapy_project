
+ 项目所需要的包都在requirements.txt里面可以通过pip install -r requirements.txt来安装
+ 目前是1.0的版本没有断点续传也
+ scrapyProject目录下的config是配置文件包含了redis的配置，是否覆盖的配置，有每个请求超过多少秒就认为失败重新发起请求的参数REQUEST_TIMEOUT
+ 项目目录结构：
    -
    - io_redis.py是封装的redis操作
+ 执行命令的方法 先cd到scrapyProject里面然后执行命令 scrapy crawl quanben
+ 爬取之后的存储结构
    - 数据结构的key的构成：book-书名-章节id：{
    "chapter_title":章节名称, 
    "chapter_id":章节id也就相当于第几章, 
    "chapter_content":章节内容, 
    "book_title":书名, 
    "book_author":书的作者 
    }
    - 书名存在集合 book_title里面