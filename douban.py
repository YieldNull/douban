#!/usr/bin/env python2
#coding:utf-8
"""
Collect all the movies in 'movie.douban.com.
Choose movie tag searching at
    'http://www.douban.com/tag/{tag}/?focus=movie' as entrance.
And get movie ids via XHR at
    'http://www.douban.com/j/tag/items?start={start}&limit={limit}&topic_id={topic_id}&topic_name={topic}&mod=movie'

Author : hejunjie.net
Create at 2015/12/13
"""

import copy
import requests
import re
import multiprocessing as mp
import threading

# Use placeholders
URL_HOME = 'http://www.douban.com/tag/{tag}/?focus=movie'
URL_XHR = 'http://www.douban.com/j/tag/items?' \
            'start={start}&limit={limit}&topic_id={topic_id}&' \
            'topic_name={topic}&mod=movie'
XHR_LIMIT = 100

# Add <Referer> when trigger requests.
# And add <X-Requested-With> when sending XHR
HEADERS = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'Connection':'keep-alive',
    #'Referer':'http://www.douban.com/tag/{tag}/?focus=movie',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                '(KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
    #'X-Requested-With':'XMLHttpRequest'
}


def gen_headers(ext_headers):
    """
    Add extra headers to base HEADERS.
    """
    headers = HEADERS.copy()
    headers.update(ext_headers)
    return headers


def get_topic_id(tag):
    """
    Get topic id from the HTML source of the home of tag <tag>.
    If <topic_id> is missing in HTML, extract it from the js file.
    """
    r = requests.get(URL_HOME.format(tag=tag), headers=HEADERS)
    m = re.search('topic_id:\s+(\d+)', r.text)
    if m:
        return m.group(1)
    else:
        ptn = 'http://img3\.douban\.com/misc/mixed_static/.*?\.js'
        js = re.search(ptn, r.text).group(0)
        headers = gen_headers({'Referer': URL_HOME.format(tag=tag)})
        r = requests.get(js, headers=headers)
        return re.search('topic_id:\s+(\d+)', r.text).group(1)


def store_id(id_list):
    """
    Worker's callback, receiving get_info' result and store it in file.
    Invoked in the same result_handler_thread, not the main-thread.
    """
    with open('id_list.txt', 'a') as f:
        for _id in id_list:
            f.write('%s\n' % _id)
            print _id


def do_xhr(tag, topic_id, start, return_total=False):
    """
    Secondary Worker job.
    Do XHR to fetch movie list, and extract ids.
    Return total entries under this tag if <return_total> and
    a list of <limit=XHR_LIMIT> ids after <start>
    """
    url = URL_XHR.format(start=start,
                         limit=XHR_LIMIT,
                         topic_id=topic_id,
                         topic=tag)
    headers = gen_headers({
        'Referer': URL_HOME.format(tag=tag),
        'X-Requested-With': 'XMLHttpRequest'
    })
    r = requests.get(url=url, headers=headers)

    # total entries under this tag. Useful for stoping task.
    total = r.json()['total']

    # Extract <subject_id> from
    # http://movie.douban.com/subject/3072086/?from=tag
    html = r.json()['html']
    ptn = r'<a\s+href="http://movie\.douban\.com/subject/(\d+)/\?from=tag"\s+class="title".*?>'
    id_list = re.findall(ptn, html)

    if return_total:
        return total, id_list
    else:
        return id_list


def get_info(tag):
    """
    Primary Worker job.
    Get the sum of movie entries under this tag,
    and the first entry list.
    """
    topic_id = get_topic_id(tag)
    total, id_list = do_xhr(tag, topic_id, 0, return_total=True)
    store_id(id_list)

    return {'tag': tag, 'topic_id': topic_id, 'total': total}


if __name__ == '__main__':
    import os
    os.system('[ -f id_list.txt ] && mv id_list.txt id_list.txt.bac')

    pool = mp.Pool(processes=20)

    # apply primary jobs
    results = [pool.apply_async(get_info,
                                args=(i, ), ) for i in range(1888, 2016)]

    # apply secondary jobs
    for res in results:
        r = res.get()

        # sub-jobs' task  is in the range of (XHR_LIMIT, total)
        # whose step length is XHR_LIMIT
        for start in range(XHR_LIMIT, r['total'], XHR_LIMIT):
            pool.apply_async(do_xhr,
                             args=(r['tag'], r['topic_id'], start),
                             callback=store_id)

    pool.close()
    pool.join()
