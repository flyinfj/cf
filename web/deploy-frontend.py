#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端 Linux 部署脚本（Python 版）

使用方法: python deploy-frontend.py [选项]

选项:
  --build-only    仅构建，不上传
  --upload-only   仅上传，不构建（需要先有 build 目录）
  --server=IP     指定服务器 IP
  --user=USER     指定 SSH 用户
  --path=PATH     指定服务器部署路径（默认: /var/www/html/frontend）
  --password=PWD  SSH 密码（默认: Cf@123321）

行为:
  - 上传前不再询问，直接执行（默认确认）
  - 首次 SSH 连接自动接受主机密钥（相当于自动 yes）
  - 使用密码认证，需安装: pip install paramiko
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    paramiko = None  # 未安装时用 ssh/scp，需手动输入密码

# 默认配置
DEFAULT_SERVER = "120.27.198.74"
DEFAULT_USER = "root"
DEFAULT_DEPLOY_PATH = "/root/cf/web/frontend"
DEFAULT_PASSWORD = "Cf@123321"  # 主机 SSH 密码（生产环境建议改为环境变量）
FRONTEND_DIR = "frontend"


# ANSI 颜色码
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


def echo_info(msg: str) -> None:
    print(f"{GREEN}[INFO]{NC} {msg}")


def echo_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN]{NC} {msg}")


def echo_error(msg: str) -> None:
    print(f"{RED}[ERROR]{NC} {msg}")


def run_cmd(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """执行命令，返回 CompletedProcess。check=True 时失败则抛出 CalledProcessError。"""
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def run_npm(args: list[str], cwd: str) -> None:
    """执行 npm 命令。Windows 上 npm 为 npm.cmd，需通过 shell 调用。"""
    cmd_str = " ".join(args)  # 固定为 npm 子命令，无用户输入，安全
    subprocess.run(
        cmd_str,
        cwd=cwd,
        shell=True,
        check=True,
    )


def check_node() -> None:
    """检查 Node.js 是否安装且版本 >= 16。"""
    try:
        result = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        echo_error("未找到 Node.js，请先安装 Node.js 16+")
        sys.exit(1)

    if result.returncode != 0:
        echo_error("无法获取 Node.js 版本")
        sys.exit(1)

    version_str = result.stdout.strip().lstrip("v")
    match = re.match(r"(\d+)", version_str)
    if not match:
        echo_error(f"无法解析 Node.js 版本: {result.stdout.strip()}")
        sys.exit(1)

    node_version = int(match.group(1))
    if node_version < 16:
        echo_error(f"Node.js 版本过低，需要 16+，当前版本: {result.stdout.strip()}")
        sys.exit(1)

    echo_info(f"Node.js 版本: {result.stdout.strip()}")


def build_project(script_dir: Path) -> None:
    """构建前端项目。"""
    echo_info("开始构建前端项目...")

    frontend_path = script_dir / FRONTEND_DIR
    if not frontend_path.is_dir():
        echo_error(f"前端目录不存在: {frontend_path}")
        sys.exit(1)

    if not (frontend_path / "package.json").is_file():
        echo_error("未找到 package.json")
        sys.exit(1)

    if not (frontend_path / "node_modules").is_dir():
        echo_info("安装依赖...")
        run_npm(["npm", "install"], cwd=str(frontend_path))

    echo_info("执行构建...")
    run_npm(["npm", "run", "build"], cwd=str(frontend_path))

    if not (frontend_path / "build").is_dir():
        echo_error("构建失败，未找到 build 目录")
        sys.exit(1)

    echo_info("构建完成！")


def _sftp_upload_dir(sftp, local_path: Path, remote_path: str) -> None:
    """递归上传本地目录到 SFTP 远程路径。"""
    try:
        sftp.mkdir(remote_path)
    except OSError:
        pass  # 目录已存在
    for name in os.listdir(local_path):
        local = local_path / name
        remote = f"{remote_path.rstrip('/')}/{name}"
        if local.is_file():
            sftp.put(str(local), remote)
        else:
            _sftp_upload_dir(sftp, local, remote)


def upload_files(
    server: str,
    user: str,
    deploy_path: str,
    password: str,
    script_dir: Path,
) -> None:
    """上传构建产物到服务器。确认上传默认执行；首次连接自动接受主机密钥；使用密码认证。"""
    if not server:
        echo_error("请指定服务器地址: --server=IP")
        sys.exit(1)

    build_dir = script_dir / FRONTEND_DIR / "build"
    if not build_dir.is_dir():
        echo_error(f"构建目录不存在: {build_dir}")
        echo_warn("请先运行构建: npm run build")
        sys.exit(1)

    echo_info("准备上传文件到服务器（默认确认，无需输入 y/n）...")
    echo_info(f"服务器: {user}@{server}")
    echo_info(f"部署路径: {deploy_path}")

    if paramiko is None:
        echo_error("请先安装 paramiko 以支持密码自动登录: pip install paramiko")
        sys.exit(1)

    echo_info("连接服务器（首次连接自动接受主机密钥）...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 相当于自动 yes
    client.connect(
        server,
        username=user,
        password=password,
        allow_agent=False,
        look_for_keys=False,
    )

    try:
        sftp = client.open_sftp()
        echo_info("创建远程目录...")
        # 递归创建 deploy_path 及其父目录（SFTP 无 mkdir -p）
        path = deploy_path.rstrip("/")
        if path.startswith("/"):
            path = path[1:]
        parts = path.split("/")
        for i in range(1, len(parts) + 1):
            d = "/" + "/".join(parts[:i])
            try:
                sftp.mkdir(d)
            except OSError:
                pass  # 已存在则忽略

        echo_info("上传文件...")
        for name in os.listdir(build_dir):
            local = build_dir / name
            remote = f"{deploy_path.rstrip('/')}/{name}"
            if local.is_file():
                sftp.put(str(local), remote)
            else:
                _sftp_upload_dir(sftp, local, remote)
        sftp.close()
    finally:
        client.close()

    echo_info("上传完成！")
    echo_info("请在服务器上配置 Nginx 并重启服务")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="前端 Linux 部署脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python deploy-frontend.py                    # 构建并上传
  python deploy-frontend.py --build-only        # 仅构建
  python deploy-frontend.py --upload-only      # 仅上传
  python deploy-frontend.py --server=1.2.3.4   # 指定服务器
        """,
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="仅构建，不上传",
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="仅上传，不构建（需要先有 build 目录）",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER,
        help=f"服务器 IP（默认: {DEFAULT_SERVER}）",
    )
    parser.add_argument(
        "--user",
        default=DEFAULT_USER,
        help=f"SSH 用户（默认: {DEFAULT_USER}）",
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_DEPLOY_PATH,
        dest="deploy_path",
        help=f"服务器部署路径（默认: {DEFAULT_DEPLOY_PATH}）",
    )
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="SSH 密码（默认使用脚本内配置）",
    )
    args = parser.parse_args()

    if args.build_only and args.upload_only:
        echo_error("不能同时指定 --build-only 和 --upload-only")
        sys.exit(1)

    script_dir = Path(__file__).resolve().parent

    echo_info("=== 前端部署脚本 ===")

    if not args.upload_only:
        check_node()
        build_project(script_dir)

    if not args.build_only:
        upload_files(
            args.server,
            args.user,
            args.deploy_path,
            args.password,
            script_dir,
        )
    else:
        echo_info("仅构建模式，跳过上传")
        echo_info(f"构建文件位于: {script_dir / FRONTEND_DIR / 'build'}")


if __name__ == "__main__":
    main()
