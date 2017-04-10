# coding=utf-8
import requests
from lxml import etree
from urllib import parse
import json
import re
import logging

Nruan_Header = {
    'Accept': 'text/html,application/xhtml+xml, \
    application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,ko;q=0.6',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
}

logger = logging.getLogger(__name__)
# 返回格式，多层嵌套的tuple
# (
#   (卷类型,[rid,章节名,url],[rid,章节名,url],...),
#   (卷类型,[rid,章节名,url],[rid,章节名,url],...),
#   ...
# )
# def get_book_catalogue(_session, book_URL, query_URL):
#     r = _session.get(book_URL)
#     content = r.text
#     tree = etree.HTML(content)
#     nodes = tree.xpath('//div[@class="book-info "]')
#     nodes = tree.xpath('//div[@class="volume-wrap"]')
#     retData = tuple()
#     for n in nodes:
#         volume = get_book_volume(n)
#         if volume[0] == ' VIP':
#             replace_url(_session, volume, query_URL)
#         retData += volume[1:]
#     for i in range(len(retData)):
#         retData[i][0] = i
#     return retData


# def get_book_volume(node):
#     volume_type = node.xpath('./h3/span/child::text()')
#     nodes = node.xpath('./ul/li')
#     retData = (volume_type[0],)
#     for n in nodes:
#         retData += get_book_chapter(n)
#     return retData


# def get_book_chapter(node):
#     a = node.getchildren()[0]
#     chapter_name = a.text
#     url = a.attrib['href']
#     return ([node.attrib['data-rid'], chapter_name, url],)


# 返回格式
# (
#   ([rid,章节名,url],[rid,章节名,url],...),
#   ([rid,章节名,url],[rid,章节名,url],...),
#   ...
# )
def get_catalogue_json(bookId, query_URL, uuid=0):
    url = 'http://book.qidian.com/ajax/book/category?bookId=' + bookId
    logger.info('目标url ' + url)
    _session = requests.session()
    _session.headers.update(Nruan_Header)
    logger.info('开始获取url内容...')
    r = _session.get(url)
    logger.info('获取url成功!')
    r = _session.get(url)
    js = r.content.decode('utf-8')
    js = json.loads(js)
    if js['code'] == 1:
        logger.error('json 获取失败！')
        return False
    # print(js)
    return resolver_json_qidian(_session, js, query_URL, uuid)


def resolver_json_qidian(_session, js, query_url, uuid):
    bookData = ()
    # query_url_content
    try:
        r = _session.get(query_url)
    except Exception as e:
        logger.error(e, exc_info=True)
        return False
    except ConnectionError as e:
        logger.error(e, exc_info=True)
        return False
    content = r.text
    tree = etree.HTML(content)
    # 只匹配章节，跳过公告
    pattern = re.compile(r'第?[\u4e00-\u9fa5,0-9]{1,7}章 {0,3}.{1,}')
    pattern_rp = re.compile(r'第?[\u4e00-\u9fa5,0-9]{1,7}章')
    for volume in js['data']['vs']:
        for chapter in volume['cs']:
            if chapter['uuid'] <= uuid:
                continue
            chapter['cN'] = chapter['cN'].replace('*', '\*')
            match = pattern.match(chapter['cN'])
            if match is None:
                continue  # 跳过公告
            chapterData = ([chapter['uuid'],
                            chapter['cN'], chapter['cU']],)
            if volume['hS'] is False:
                chapterData[0][2] = url_joint(chapterData[0][2])
            else:
                replace_url(tree, chapterData[0], query_url, pattern_rp)
            bookData += chapterData
    # print(bookData)
    return bookData


def replace_url(tree, chapter_list, url, pattern_rp):
    # print(chapter_list)
    match = pattern_rp.match(chapter_list[1])
    index = match.span()[1]
    reStr = chapter_list[1][:index] + \
        r"\s{0,3}" + chapter_list[1][index:].strip()
    print(reStr)
    try:
        nodes = tree.xpath(r'//dd[re:match(a, "' + reStr + '")]', namespaces={
            "re": "http://exslt.org/regular-expressions"})
    except Exception as e:
        print(e)
        return False
    if len(nodes) == 0:
        return False
    a = nodes[0].getchildren()[0]
    ab_url = parse.urljoin(url, a.attrib['href'])
    chapter_list[2] = ab_url
    # print(ab_url)
    return True


def url_joint(href, url='http://read.qidian.com/chapter/'):
    return parse.urljoin(url, href)


def get_book_data(source_URL, query_URL):
    book_id = source_URL.split('/')[-1]
    return get_catalogue_json(book_id, query_URL)


# 返回格式
# (
#   ([rid,章节名,url],[rid,章节名,url],...),
#   ([rid,章节名,url],[rid,章节名,url],...),
#   ...
# )
def get_new_chapter(source_URL, query_URL, uuid):
    book_id = source_URL.split('/')[-1]
    return get_catalogue_json(book_id, query_URL, uuid)


def get_session():
    _session = requests.session()
    _session.headers.update(Nruan_Header)
    _session.get('http://www.qidian.com/')  # 获取cookie
    return _session


def analysis_qidian(_session, query_URL, uuid=0):
    url = 'http://book.qidian.com/ajax/book/category?bookId=' + '3650892'
    r = _session.get(url)
    json_chapter = r.content.decode('utf-8')
    # print(js)
    json_chapter = json.loads(json_chapter)
    if json_chapter['code'] == 1:
        logger.error('json 获取失败！')
        return False
    bookData = ()
    pattern = re.compile(r'第?[\u4e00-\u9fa5,0-9]{1,7}章 {0,3}.{1,}')
    for volume in json_chapter['data']['vs']:

        for chapter in volume['cs']:
            if chapter['uuid'] <= uuid:
                continue
            chapter['cN'] = chapter['cN'].replace('*', '\*')
            match = pattern.match(chapter['cN'])
            if match is None:
                continue  # 跳过公告
            chapterData = ([chapter['uuid'],
                            chapter['cN']],)
            bookData += chapterData
    print(bookData)
    return bookData


def analysis_lewen(_session, new_chapter, query_URL):
    lewen_url = 'http://www.lwxiaoshuo.com'
    # query_url_content
    try:
        r = _session.get(query_URL)
    except Exception as e:
        logger.error(e, exc_info=True)
        return False

    content = r.content.decode('gbk')
    tree = etree.HTML(content)
    nodes = tree.xpath(r'//div/div/dl/dd/a')
    for i in nodes:
        for chapter in new_chapter:
            if i.text.find(chapter[1]) == 0:
                print(i.text, chapter[1], i.attrib['href'])
            # print(reStr)
            # chapter_name = chapter[1]
            # if i.text.find(chapter_name):
            #     print(i.attrib['href'])
            #     print(i.text)
    # pattern = re.compile(r'第?[\u4e00-\u9fa5,0-9]{1,7}章')


def get_text(_session, detail_url):
    r = _session.get(detail_url)
    text = r.content.decode('gbk')
    text = text.replace('&nbsp;', ' ')
    # print(text)
    tree = etree.HTML(text)
    content_list = tree.xpath(r'//p/text()')
    print(content_list)
    return content_list

    # text = re.sub('<[^>]*>', '', text)
    # text = re.sub('[ \t\r\n\u3000]', '', text)
    # print(text)


if __name__ == '__main__':
    _session = get_session()
    # get_text(_session, 'http://www.lwxiaoshuo.com/53/53888/12224583.html')
    new_chapter = analysis_qidian(
        _session, 'http://book.qidian.com/info/3650892', 1260)
    analysis_lewen(_session, new_chapter,
                   'http://www.lewenxiaoshuo.com/books/yinhu/')
    # a = get_new_chapter('http://book.qidian.com/info/3650892',
    #                     'http://www.zbzw.com/yinhu/', uuid=1260)
    # print(a)
    # get_book_data('http://book.qidian.com/info/3650892',
    #               'http://www.zbzw.com/yinhu/')
    # get_book_data('http://book.qidian.com/info/3406500',
    #               'http://www.zbzw.com/zoujinxiuxian/')
