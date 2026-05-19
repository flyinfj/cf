import os

try:
    import paramiko
except ImportError:
    print("Error: 缺少 'paramiko' 库。请运行命令安装: pip install paramiko")
    exit(1)

def _ensure_remote_dir(sftp, path):
    """递归创建远程目录（若不存在）。path 为绝对路径。"""
    dirs = []
    p = path
    while p and p != '/':
        dirs.append(p)
        p = os.path.dirname(p)
    dirs.reverse()
    for d in dirs:
        try:
            sftp.stat(d)
        except FileNotFoundError:
            try:
                sftp.mkdir(d)
            except Exception:
                pass


def upload_recent_files():
    # 配置信息
    host = '120.27.198.74'
    port = 22
    username = 'root'
    password = 'Cf@123321'
    remote_dir = '/root/cf/web/frontend'

    # 本地目录：frontend/build（相对于当前工作目录）
    local_dir = os.getcwd()
    local_build = os.path.join(local_dir, 'frontend', 'build')

    if not os.path.isdir(local_build):
        print(f"错误：本地目录不存在 {local_build}")
        return

    # 收集 frontend/build 下所有文件（保留相对路径）
    files_to_upload = []
    print(f"正在扫描 {local_build} 下的所有文件...")
    for root, _, filenames in os.walk(local_build):
        for name in filenames:
            filepath = os.path.join(root, name)
            rel = os.path.relpath(filepath, local_build)
            files_to_upload.append((filepath, rel))

    if not files_to_upload:
        print("frontend/build 下没有文件。")
        return

    print(f"发现 {len(files_to_upload)} 个文件待上传到 {remote_dir}")

    try:
        print(f"正在连接到 {host}...")
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        for filepath, rel in files_to_upload:
            remote_path = remote_dir + '/' + rel.replace('\\', '/')
            remote_parent = os.path.dirname(remote_path)
            _ensure_remote_dir(sftp, remote_parent)
            print(f"正在上传 {rel} ...")
            try:
                sftp.put(filepath, remote_path)
                print(f"  上传成功")
            except Exception as e:
                print(f"  上传失败: {e}")

        sftp.close()
        transport.close()
        print("所有任务完成。")
    except Exception as e:
        print(f"连接或传输发生错误：{e}")

if __name__ == "__main__":
    upload_recent_files()