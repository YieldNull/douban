#统计豆瓣电影条目

主要是通过`AJAX`来获取电影信息，因为直接访问HTML源码太花时间了。而且直接访问`API`跟直接访问网页的被封概率应该不一样吧？

首先通过`tag`搜索已有年份标签的电影，范围为`[current_year,1888]`

```language
http://www.douban.com/tag/2015/?focus=movie
```

上面是获取`The URL of AJAX`的链接，在调试窗口就可以看到其链接为

```language
http://www.douban.com/j/tag/items?start=9&limit=6&topic_id=65330&topic_name=2015&mod=movie
```

通过`limit`可以控制每次返回数据量。

可以发现，该链接中含有`topic_id`字段，这个id是未知的，因此只好到标签搜索结果的`HTML`源码中找。有时候可以在源码中直接找到`payload`信息，然后从中提取`topic_id`，但是有时候找不到。找不到时，可以获取下面的`js`文件，在其中可以找到`payload`信息。


~有且只有一个匹配~

```python
pattern='http://img3\.douban\.com/misc/mixed_static/.*?\.js'
```

~从js文件提取或直接从HTML源码获取~

```javascript
var payload = {
    start: start,
    limit: limit,
    topic_id: 65330,
    topic_name: '2015',
    mod: mod_name
};
```

`Request Header`:

```python
'Accept':'*/*'，
'Accept-Encoding':'gzip, deflate, sdch'，
'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'，
'Connection':'keep-alive'，
'Host':'www.douban.com'，
'Referer':'http://www.douban.com/tag/2015/?focus=movie'，
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'，
'X-Requested-With':'XMLHttpRequest'
```

其中`Referer`是变化的。为了最真实的模拟浏览器的请求，这些`Headers`都会包含在请求中。

然而有的电影并没有年份标签，因此可以获取到电影的演员列表，然后再获取演员参演过的电影来查漏。作品列表仍然不全，若不是主角可能被忽略。而且国外演员被标签的不全。

```language
http://www.douban.com/tag/苏有朋/?focus=movie
```

因此可以直接进入演员详情页，演员id可以在获取演员列表时获取。（主演一般都有链接，链接中包含id）

```language
http://movie.douban.com/celebrity/1050540/movies?start=0&format=pic&sortby=time&role=A
```

这东西是翻页的，每次都会请求`HTML`源码。每页10条，总条数可以从源码获取。比如下面的。不过感觉会好慢好慢。

```language
<title>
苏有朋 Alec Su的演出作品（47）
</title>
```
