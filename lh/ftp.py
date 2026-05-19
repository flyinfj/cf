import os
import time
from datetime import datetime

try:
    import paramiko
except ImportError:
    print("Error: 缺少 'paramiko' 库。请运行命令安装: pip install paramiko")
    exit(1)

def upload_recent_files():
    # 配置信息
    host = '120.27.198.74'
    port = 22
    username = 'root'  # 目标目录为/root/cf/lh，推测用户为root
    password = 'Cf@123321' # 使用tools.py中的常用密码，如有不同请修改
    remote_dir = '/root/cf/lh'

    # 获取当前工作目录
    local_dir = os.getcwd()
    
    # 计算时间阈值（1小时前）
    now = time.time()
    one_hour_ago = now - 3600
    
    # 查找最近一小时更新的文件
    files_to_upload = []
    print(f"正在扫描 {local_dir} 目录下最近一小时更新的文件...")
    
    for filename in os.listdir(local_dir):
        filepath = os.path.join(local_dir, filename)
        
        # 排除自身脚本
        if filename == 'upload_recent.py':
            continue

        # 检查是否为文件
        if os.path.isfile(filepath):
            # 检查修改时间
            mtime = os.path.getmtime(filepath)
            if mtime > one_hour_ago:
                files_to_upload.append(filepath)
    
    if not files_to_upload:
        print("未发现最近一小时更新的文件。")
        return

    print(f"发现 {len(files_to_upload)} 个文件待上传：")
    for f in files_to_upload:
        print(f" - {os.path.basename(f)}")

    # 连接SFTP
    try:
        print(f"正在连接到 {host}...")
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # 切换远程目录
        try:
            sftp.chdir(remote_dir)
        except IOError:
            print(f"错误：远程目录 {remote_dir} 不存在。")
            sftp.close()
            transport.close()
            return

        # 上传文件
        for filepath in files_to_upload:
            filename = os.path.basename(filepath)
            print(f"正在上传 {filename} ...")
            try:
                sftp.put(filepath, filename)
                print(f"上传成功：{filename}")
            except Exception as e:
                print(f"上传失败 {filename}: {e}")
            
        sftp.close()
        transport.close()
        print("所有任务完成。")
        
    except Exception as e:
        print(f"连接或传输发生错误：{e}")

if __name__ == "__main__":
    upload_recent_files()