## 统计豆瓣电影条目

使用[Scrapy](https://doc.scrapy.org/en/latest/)，共爬取`362622`条影视信息。其中电影`139784`条，电视剧综艺等`222838`条。

首先通过年份标签(https://www.douban.com/tag/2016/?focus=movie)页面中的XHRAPI获取从1888年到现在的一些电影作为seeds。 然后爬取每个电影详情页面中的推荐电影，最后通过演职人员参与的作品进行查漏。

see [notes](https://github.com/YieldNull/douban/wiki/Notes).

## LICENSE

MIT License

Copyright (c) 2017 YieldNull

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
