from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText  # 添加这行导入
import datetime  # 添加这行导入
import smtplib  # 添加这行导入
from email.header import Header
import os
import sys
import myLib
import shutil

def getAIMessage(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        contents = f.read()
    # 构建提示语
    prompt = f'''
    根据以下今日盘面信息分析行情：
	1)根据涨停股统计信息、连板天梯信息、上证/深证神奇指数情况，分析今日的情绪周期处于哪个阶段？
	2)根据热门板块的人气类型信息、飙升个股信息、人气个股信息1/2/3/4，分析人气类型板块中，比较有潜力的个股，且不在热门板块的大涨类型板块中。
	3)根据热门板块的飙升类型信息、飙升个股信息、人气个股信息1/2/3/4，分析飙升类型板块中，比较有潜力的个股，且不在热门板块的大涨类型板块中。
	4)根据个股连板情况、飙升个股信息、人气个股信息1/2/3/4，分析与5连板+的个股同板块，人气股票中比较有潜力的个股。
	5)根据热门板块信息、高换手率的冷门股情况，分析冷门股比较有潜力的个股，且不在热门板块的大涨类型板块中。
    今日盘面信息:
    {contents}
    '''
    ai_df = model.get_chat(prompt)
    return ai_df

# 配置邮箱信息
model = myLib.MyLib()
mail_host = "smtp.126.com"  # SMTP服务器地址（163邮箱）
mail_port = 465             # SSL加密端口
sender = "flyinfj@126.com"  # 发件人邮箱
password = "UG3HHEjFvjatfp8q"  # 邮箱授权码（不是登录密码！）
receiver = "flyinfj@126.com"    # 收件人邮箱
# 构造邮件内容
args = sys.argv 
now = datetime.datetime.now()
if len(args) > 1:
    subject = f"{args[1]}_{now.strftime("%m%d%H")}"
else:
    subject = f"{now.strftime("%m%d%H")}"
content = ""  # 邮件正文

# 创建带附件的邮件对象
message = MIMEMultipart()
message["From"] = Header(sender, "utf-8")       # 发件人
message["To"] = Header(receiver, "utf-8")       # 收件人
message["Subject"] = Header(subject, "utf-8")    # 邮件主题

# 添加正文
text = MIMEText(content, "plain", "utf-8")
message.attach(text)

#删除1天前的文件
html_dir = f"{model.data_dir}/data/html"
bak_dir = f"{model.data_dir}/data/html/history"
now = datetime.datetime.now()
for filename in os.listdir(html_dir):
    file_path = os.path.join(html_dir, filename)
    if os.path.isfile(file_path):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        if (now - file_time).days >= 1:
            dst_file = os.path.join(bak_dir, filename)
            if os.path.exists(dst_file):
                os.remove(dst_file) 
            shutil.move(file_path, bak_dir)
# 获取html_dir下的文件列表，生成html文件dir.html
dir_html = os.path.join(html_dir, "dir.html")
with open(dir_html, 'w', encoding='utf-8') as f:
    f.write('<html><head><meta charset="UTF-8"><style>li {font-size: 20px;margin-bottom: 20px; }</style></head><body><ul>')
    for filename in sorted(os.listdir(html_dir)):
        if filename.endswith('.html') and filename != 'dir.html':
            file_path = os.path.join(html_dir, filename)
            f.write(f'<li><a href=http://175.178.27.33:3389/{filename}>{filename}</a></li>')
    f.write('</ul></body></html>')

# 添加附件（如test.txt）
now = datetime.datetime.now()
if len(args) > 1:
    if args[1] == '1':
        file_name1 = f"{model.data_dir}/data/html/{now.strftime("%m%d%H")}.html"
        if  os.path.exists(file_name1):
            with open(file_name1, "rb") as f:
                attachment = MIMEApplication(f.read(), Name="stock.html")
                attachment["Content-Disposition"] = 'attachment; filename="stock.html"'
                message.attach(attachment)
            """
            ai_df = getAIMessage(file_name1)
            file_name2 = f"{model.data_dir}/data/html/{now.strftime("%m%d%H")}_ai.html"
            with open(file_name2, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><pre>{ai_df}</pre></body></html>")
            with open(file_name2, "rb") as f:
                attachment = MIMEApplication(f.read(), Name="ai.html")
                attachment["Content-Disposition"] = 'attachment; filename="ai.html"'
                message.attach(attachment)
            """
    if args[1] == '3':
        file_name3 = f"{model.data_dir}/data/html/messages.html"
        if  os.path.exists(file_name3):
            with open(file_name3, "rb") as f:
                attachment = MIMEApplication(f.read(), Name="messages.html")
                attachment["Content-Disposition"] = 'attachment; filename="messages.html"'
                message.attach(attachment)
"""
try:
    # 连接SMTP服务器并发送邮件
    smtp = smtplib.SMTP_SSL(mail_host, mail_port)  # 使用SSL加密
    smtp.login(sender, password)                   # 登录
    smtp.sendmail(sender, [receiver], message.as_string())  # 发送
    smtp.quit()  # 关闭连接
    print("邮件发送成功！")
except Exception as e:
    print(f"邮件发送失败: {e}")
"""