
+ 项目所需要的包都在requirements.txt里面可以通过pip install -r requirements.txt来安装
+ 这个分支包含了scrapy-redis有断点续传功能
    - 建议每次只爬一个类别的数据这样能比较快速的爬取数据，在文件quanben.py里面的start_requests函数里面的urls参数可以每次注释只留一个类目
+ scrapyProject目录下的config是配置文件包含了redis的配置，是否覆盖的配置，有每个请求超过多少秒就认为失败重新发起请求的参数REQUEST_TIMEOUT
+ 项目目录结构：
    - 爬虫所有逻辑都在spider文件下的quanben.py里面
        + start_requests函数开始发请求的url，所有分类的url都要放入url
        + parse_type函数 处理每一个分类的请求包含下一页和每一本小说
        + parse_book函数 处理点击目录
        + parse_book_list函数 处理每一章的url
        + parse_book_content 处理每一章的内容
        + parse_book_content_detail 因为每次都要点阅读全文才能出下半页数据所有要单独处理
        + save_data 封装数据存入redis操作
        + parse开头的函数之间传参都是通过meta属性来传递
        + 貌似全本小说网是通过设置cookie来达到访问控制的
        + 然后有时候某个请求会超时，需要重新传，所幸scrapy封装了自动重传的东西，可以通过修改设置来达到高效爬取
        
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
    - 书名存在集合 book_title里面,后期可以根据这里来统计爬了多少本小说以及每本小说的章节