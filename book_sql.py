# coding=utf-8
import pymysql.cursors

import config


def connect_mysql():
    return pymysql.connect(
        host=config.DateBase.host,
        port=config.DateBase.port, user=config.DateBase.user,
        passwd=config.DateBase.passwd,
        db=config.DateBase.db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)


def creat_books_table(conn):
    sql = 'CREATE TABLE `books` (' +\
        '`book_id` char(20),' +\
        '`book_name` char(41),' +\
        '`source_url` text NOT NULL,' +\
        '`query_urls` text NOT NULL,' +\
        'PRIMARY KEY (`book_id`)' +\
        ') ENGINE=InnoDB DEFAULT CHARSET=utf8;'
    return __execute_sql(conn, sql, ())


def creat_new_book(conn, tup):
    book_id, book_name, source_url, query_urls = tup
    sql = 'INSERT INTO books(book_id,book_name,source_url,' +\
        'query_urls) VALUES( %s, %s, %s, %s)'
    __execute_sql(conn, sql, (book_id, book_name, source_url, query_urls))
    sql = 'CREATE TABLE `%s` (' +\
        '`uuid` int(11) NOT NULL DEFAULT 0,' +\
        '`chapter_name` varchar(255) NOT NULL DEFAULT "",' +\
        '`url` text NOT NULL,' +\
        'PRIMARY KEY (`uuid`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
    # print(sql)
    return __execute_sql(conn, sql, (book_id,))


def insert_new_chapter(conn, tup):
    book_id, uuid, chapter_name, url = tup
    sql = 'INSERT INTO `%s`(uuid,chapter_name,url)' +\
        ' VALUES( %s, %s, %s)'
    __execute_sql(conn, sql, (book_id, uuid, chapter_name, url))


def insert_new_chapters(conn, tup):
    book_id, array = tup
    sql = 'INSERT INTO `%s`(uuid,chapter_name,url) VALUES( %s, %s, %s)'
    param = (book_id,) + tuple(array[0])
    for l in array[1:]:
        sql += ',( %s, %s, %s)'
        param += tuple(l)
    # print(sql)
    # print(param)
    __execute_sql(conn, sql, param)


def has_book(conn, book_id):
    sql = 'SELECT book_id FROM `books` WHERE book_id = %s'
    try:
        return __execute_sql(conn, sql, (book_id,))
    except Exception as e:
        if e.args[0] == 1146:
            creat_books_table(conn)
    return ()


def get_all_books_info(conn, invalid=None):
    sql = 'SELECT * FROM `books`'
    return __execute_sql(conn, sql, ())


def get_max_uuid(conn, book_id):
    sql = 'SELECT uuid FROM `%s` order by uuid desc limit 0,1'
    return __execute_sql(conn, sql, (book_id,))


def __execute_sql(conn, sql, parameters):
    with conn.cursor() as cursor:
        # 执行sql语句，进行查询
        cursor.execute(sql, parameters)
        # 获取查询结果
        result = cursor.fetchall()
        # print(result)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        conn.commit()
    return result


if __name__ == '__main__':
    conn = connect_mysql()
    sql = 'select * from books;'
    try:
        __execute_sql(conn, sql, ())
    except Exception as e:
        if e.args[0] == 1146:
            print('1111')
        # print(dir(e.args[0]))
