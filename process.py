import threading
import logging

# from qidian_book import *
import analysis_page
from book_sql import *

import logConfig
import send_email


def add_new_book(book_name, source_book_url, query_book_urls):
    conn = connect_mysql()
    book_id = source_book_url.split('/')[-1]
    logger.info('查询 ' + book_name + ' 是否存在...')
    retData = execute_sql(conn, has_book, (book_id,))
    if retData is False:
        logger.error('发生错误in function has_book')
        return
    if len(retData) != 0:
        logger.info(book_name + ' 已存在，取消操作！')
        return
    logger.info(book_name + ' 不存在，正在添加...')
    logger.info('正在创建数据库表 ' + book_name + ' ...')
    retData = execute_sql(conn, creat_new_book,
                          (book_id, book_name,
                           source_book_url, query_book_urls))
    if retData is False:
        logger.error('发生错误in function creat_new_book')
        return
    logger.info('正在获取 ' + book_name + ' 目录信息...')
    retData = analysis_page.get_book_data(book_id, query_book_urls)
    logger.info('正在将目录信息插入到数据库中...')
    retData = execute_sql(conn, insert_new_chapters,
                          (book_id, retData))
    if retData is False:
        logger.error('发生错误in function insert_new_chapters')
        return
    conn.close()


def update_books():
    conn = connect_mysql()
    # 获取所有书籍信息
    retData = execute_sql(conn, get_all_books_info, ())
    if retData is False:
        logger.error('发生错误in function get_all_books_info')
        return
    # 遍历所有书籍
    for book in retData:
        logger.info('正在更新“' + book['book_name'] + '”...')
        # 查看数据库中保存的最新章节
        retData = execute_sql(conn, get_max_uuid, book['book_id'])
        if retData is False:
            logger.error('发生错误in function get_max_uuid')
            return
        max_uuid = retData[0]['uuid']
        logger.info('最大max_uuid = ' + str(max_uuid))
        # 查看起点网页中是否有更新章节
        try:
            retData = analysis_page.get_new_chapter(book['book_id'], book[
                'query_urls'], max_uuid)
        except Exception as e:
            raise e
            logger.error('发生错误in function get_new_chapter')
            continue
        if retData is False:
            continue
        new_num = len(retData)
        # 判断是否有更新
        if new_num == 0:
            logger.info('无更新章节！')
            continue
        logger.info('更新 ' + str(new_num) + ' 章')
        logger.info('正在发送提示邮件...')
        t_send_email('《%s》更新了' % book['book_name'], book['book_name'], retData)
        logger.info('正在将' + str(retData) + '信息插入到数据库中...')
        # 将更新插入数据库中
        retData = execute_sql(conn, insert_new_chapters,
                              (book['book_id'], retData))
        if retData is False:
            logger.error('发生错误in function insert_new_chapters')
            return
        logger.info('将目录信息插入成功！')
    conn.close()


def t_send_email(title, book_name, retData):
    t = threading.Thread(target=send_email.send_email,
                         args=(title, book_name, retData))
    t.start()


def execute_sql(conn, fuc, parameters):
    try:
        retData = fuc(conn, parameters)
    except Exception as e:
        logger.error(e, exc_info=True)
        conn.close()
        return False
    return retData


if __name__ == '__main__':
    logConfig.init()
    logger = logging.getLogger(__name__)
    # add_new_book(u'走进修仙', 'http://book.qidian.com/info/3406500',
    #              'http://www.yunlaige.com/html/17/17654/index.html')

    # add_new_book(u'银弧', 'http://book.qidian.com/info/3650892',
    #              'http://www.yunlaige.com/html/18/18570/index.html')
    # add_new_book(u'怒瀚', 'http://book.qidian.com/info/1002491915',
    #              'http://www.yunlaige.com/html/18/18826/index.html')
    update_books()
