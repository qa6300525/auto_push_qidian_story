# coding:utf-8
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from email.header import Header
import logging

import config
import analysis_page
import utils

logger = logging.getLogger(__name__)


def send_email(title, book_name, user_message):
    # 第三方 SMTP 服务
    mail_host = config.Gmail_Email.mail_host  # 设置服务器
    mail_user = config.Gmail_Email.mail_user  # 用户名
    mail_pass = config.Gmail_Email.mail_pass  # QQ邮箱密码？，在qq邮箱设置 里用验证过的手机发送短信获得。

    sender = config.Gmail_Email.sender
    receivers = config.Gmail_Email.receivers

    msg = email.mime.multipart.MIMEMultipart()
    msg['From'] = mail_user
    msg['To'] = config.Gmail_Email.receivers[0]

    msg['Subject'] = Header(title, 'utf-8').encode()
    # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    txt = MIMEText(
        html_Msg(book_name, user_message), 'html', 'utf-8')
    msg.attach(txt)
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465, timeout=20)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.quit()
        logger.info('邮件发送成功')
    except Exception as e:
        logger.error(e, exc_info=True)


def html_Msg(book_name, user_message):
    tr = '''<tr>
            <td class="showtxt" width="760" height="56" border="0"
             align="left" colspan="2"
             style="vertical-align:bottom;font-family:'Microsoft YaHei';">
             %s</td>
        </tr> '''
    text_list = get_text_list(user_message)
    html_content = tr % str(user_message)
    for line in text_list:
        html_content += tr % line
    path = utils.get_file_path(__file__)
    with open(path + '/email_template.html', 'r', encoding='utf-8') as f:
        text = f.read()
    html_body = text % (book_name, html_content)
    return html_body


def get_text_list(user_message):
    session = analysis_page.get_session()
    text_list = []
    for chapter in user_message:
        text_list += [chapter[1]]
        text_list += analysis_page.get_yulaige_text(session, chapter[2])
    return text_list


if __name__ == '__main__':
    session = analysis_page.get_session()
    user_message = ([
        '1', '1', "http://www.yunlaige.com/html/17/17654/7773424.html"],)
    send_email('text', 'test', user_message)
