# -*- coding: utf-8 -*
import requests
from lxml import etree
from urllib import parse
import json
import re
import logging


HTTP_Header = {
    # 模拟浏览器访问网站
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


def get_session():
    '''创建连接session
    :return 所创建的session
    '''
    _session = requests.session()
    _session.headers.update(HTTP_Header)
    _session.get('http://www.qidian.com/')  # 获取cookie
    return _session


def analysis_qidian(_session, book_id, uuid=0):
    '''从“起点中文网”查看关注小说是否更新
    _session: 这是连接网站使用的session
    book_id: 小说的id号，每本小说id号唯一
    uuid: 小说章节id，是小说的章节序号
    :return 返回值为(['uuid','章节名'],['uuid','章节名'],...)，
    '''
    url = 'http://book.qidian.com/ajax/book/category?bookId=' + book_id
    r = _session.get(url)
    json_chapter = r.content.decode('utf-8')
    # print(js)
    json_chapter = json.loads(json_chapter)
    if json_chapter['code'] == 1:
        logger.error('json 获取失败！')
        return False
    new_chapter = ()
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
            new_chapter += chapterData
    return new_chapter


def analysis_lewen(_session, new_chapter, query_URL):
    '''从“乐文小说网”获取小说内容
    _session:
    new_chapter: 是analysis_qidian函数的返回值
    query_URL: 对应小说的目录页面
    return: 返回值为(['uuid','章节名','url'],['uuid','章节名','url'],...)，
    '''
    xpath_str = r'//div/div/dl/dd/a'
    return _analysis_catalogue(_session, new_chapter, query_URL, xpath_str)


def analysis_yunlaige(_session, new_chapter, query_URL):
    '''从“云来阁小说网”获取小说内容
    _session:
    new_chapter: 是analysis_qidian函数的返回值
    query_URL: 对应小说的目录页面
    return: 返回值为(['uuid','章节名','url'],['uuid','章节名','url'],...)，
    '''
    xpath_str = r'//tr/td/a'
    return _analysis_catalogue(_session, new_chapter, query_URL, xpath_str)


def analysis_zhaobizhongwen(_session, new_chapter, query_URL):
    '''从“着笔中文小说网”获取小说内容
    _session:
    new_chapter: 是analysis_qidian函数的返回值
    query_URL: 对应小说的目录页面
    return: 返回值为(['uuid','章节名','url'],['uuid','章节名','url'],...)，
    '''
    xpath_str = r'//dd/a'
    return _analysis_catalogue(_session, new_chapter, query_URL, xpath_str)


def get_lewen_text(
        _session,
        detail_url='http://www.lewenxiaoshuo.com/books/zoujinxiuxian/32387919.html'):
    '''获取网页中的小说内容
    _session:
    detail_url: 这个是小说章节的具体页面地址
    返回：字符串list
    '''
    xpath_str = r'//div[@id="content"]/text()'
    return _get_page_text(_session, detail_url, xpath_str)


def get_yulaige_text(
        _session,
        detail_url='http://www.yunlaige.com/html/17/17654/7773424.html'):
    '''获取云来阁网页中的小说内容
    _session:
    detail_url: 这个是小说章节的具体页面地址
    返回：字符串list
    '''
    xpath_str = r'//div[@id="content"]/text()'
    return _get_page_text(_session, detail_url, xpath_str)


def get_zhaobizhongwen_text(
        _session,
        detail_url='http://www.zbzw.com/yinhu/5623917.html'):
    '''获取云来阁网页中的小说内容
    _session:
    detail_url: 这个是小说章节的具体页面地址
    返回：字符串list
    '''
    xpath_str = r'//div[@id="content"]/text()'
    return _get_page_text(_session, detail_url, xpath_str)


def get_book_data(book_id, query_URL):
    """添加新书时调用
    book_id：
    query_URL：乐文小说对应小说章节目录网址
    """
    _session = get_session()
    new_chapter = analysis_qidian(_session, book_id)
    data = analysis_zhaobizhongwen(_session, new_chapter, query_URL)
    return data


def get_new_chapter(book_id, query_URL, uuid):
    """更新时调用
    book_id：
    query_URL：乐文小说对应小说章节目录网址
    uuid：数据库中记录的最新章节
    """
    _session = get_session()
    new_chapter = analysis_qidian(_session, book_id, uuid)
    data = analysis_zhaobizhongwen(_session, new_chapter, query_URL)
    return data


def _get_page_text(_session, detail_url, xpath_str):
    r = _get_url(_session, detail_url)
    if r is False:
        return False
    text = r.content.decode('gbk')
    tree = etree.HTML(text)
    content_list = tree.xpath(xpath_str)
    return content_list


def _get_url(_session, url):
    try:
        return _session.get(url)
    except Exception as e:
        raise e
        return False


def _analysis_catalogue(_session, new_chapter, query_URL, xpath_str):
    '''从“小说网”目录获取小说文本连接
    _session:
    new_chapter: 是analysis_qidian函数的返回值
    query_URL: 对应小说的目录页面
    xpath_str: 匹配规则
    return: 返回值为(['uuid','章节名','url'],['uuid','章节名','url'],...)，
    '''
    r = _get_url(_session, query_URL)
    if r is False:
        return False
    content = r.content.decode('gbk')
    tree = etree.HTML(content)
    nodes = tree.xpath(xpath_str)
    # query_URL.find('') 
    ret = ()
    for i in nodes:
        for chapter in new_chapter:
            if len(chapter) == 3:
                continue
            if i.text.find(chapter[1]) == 0:
                chapter += [parse.urljoin(query_URL, i.attrib['href'])]
                ret += (chapter,)
    return ret


if __name__ == '__main__':

    # url = 'http://www.yunlaige.com/html/17/17654/index.html'
    # a = url[:-10]
    # print(a)
    _session = get_session()
    # new_chapter = analysis_qidian(_session, '3406500', 1260)
    # analysis_yunlaige(_session, new_chapter,
    #                   'http://www.yunlaige.com/html/17/17654/index.html')

    # new_chapter = analysis_qidian(
    #     _session, '3406500', 2500)
    # analysis_lewen(_session, new_chapter,
    #                'http://www.lewenxiaoshuo.com/books/zoujinxiuxian/')
    print(get_zhaobizhongwen_text(_session))
