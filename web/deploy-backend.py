#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端 JAR Linux 部署脚本（Python 版）

使用方法: python deploy-backend.py [选项]

选项:
  --upload-only    仅上传 JAR，不重启服务
  --restart-only   仅远程重启服务，不上传
  --server=IP      指定服务器 IP
  --user=USER      指定 SSH 用户
  --path=PATH      指定服务器部署路径（默认: /root/cf/web/backend）
  --password=PWD   SSH 密码（默认: Cf@123321）
  --skip-build     跳过本地 Maven 打包，直接使用已有 JAR 上传

行为:
  - 在上传前执行 Maven install 打包（Windows 默认使用指定 mvn.cmd 与 settings.xml）
  - 上传 backend/target/stock-info-backend-1.0.0.jar 到服务器
  - 远程执行：先 kill 已有 java -jar stock-info-backend-1.0.0.jar 进程，再 nohup 启动新进程
  - 首次 SSH 连接自动接受主机密钥
  - 需安装: pip install paramiko
"""

import argparse
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

try:
    import paramiko
except ImportError:
    paramiko = None

# 默认配置
DEFAULT_SERVER = "120.27.198.74"
DEFAULT_USER = "root"
DEFAULT_DEPLOY_PATH = "/root/cf/web/backend"
DEFAULT_PASSWORD = "Cf@123321"  # 主机 SSH 密码（生产环境建议改为环境变量）
JAR_NAME = "stock-info-backend-1.0.0.jar"
BACKEND_TARGET_DIR = "backend/target"
BACKEND_POM = "backend/pom.xml"

# Maven 可执行路径（Windows 默认使用指定绿色版）
if platform.system() == "Windows":
    DEFAULT_MVN_CMD = r"D:\Program Files (green)\apache-maven-3.8.1\bin\mvn.cmd"
    DEFAULT_MVN_SETTINGS = r"D:\Program Files (green)\apache-maven-3.8.1\conf\settings.xml"
else:
    DEFAULT_MVN_CMD = "mvn"
    DEFAULT_MVN_SETTINGS = ""


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


def run_maven_build(
    script_dir: Path,
    mvn_cmd: str,
    mvn_settings: str,
) -> None:
    """本地执行 Maven install 打包后端 JAR。"""
    pom_path = script_dir / BACKEND_POM
    if not pom_path.is_file():
        echo_error(f"pom.xml 不存在: {pom_path}")
        sys.exit(1)
    echo_info("执行 Maven 打包...")
    cmd = [mvn_cmd, "install", "-f", str(pom_path)]
    if mvn_settings:
        cmd = [mvn_cmd, "-s", mvn_settings, "install", "-f", str(pom_path)]
    echo_info("命令: " + " ".join(cmd))
    try:
        ret = subprocess.run(cmd, cwd=str(script_dir), check=False)
        if ret.returncode != 0:
            echo_error("Maven 打包失败，终止部署")
            sys.exit(1)
    except FileNotFoundError:
        echo_error(f"未找到 Maven: {mvn_cmd}，请检查路径或使用 --skip-build 跳过打包")
        sys.exit(1)
    echo_info("Maven 打包完成。")


def upload_jar(
    server: str,
    user: str,
    deploy_path: str,
    password: str,
    script_dir: Path,
) -> None:
    """上传 JAR 到服务器。"""
    if not server:
        echo_error("请指定服务器地址: --server=IP")
        sys.exit(1)

    local_jar = script_dir / BACKEND_TARGET_DIR / JAR_NAME
    if not local_jar.is_file():
        echo_error(f"JAR 不存在: {local_jar}")
        echo_warn("请先在项目根目录执行 Maven 打包: mvn -f backend/pom.xml package")
        sys.exit(1)

    echo_info("准备上传 JAR 到服务器...")
    echo_info(f"服务器: {user}@{server}")
    echo_info(f"部署路径: {deploy_path}")

    if paramiko is None:
        echo_error("请先安装 paramiko: pip install paramiko")
        sys.exit(1)

    echo_info("连接服务器（首次连接自动接受主机密钥）...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        server,
        username=user,
        password=password,
        allow_agent=False,
        look_for_keys=False,
    )

    try:
        sftp = client.open_sftp()
        path = deploy_path.rstrip("/")
        if path.startswith("/"):
            path = path[1:]
        parts = path.split("/")
        for i in range(1, len(parts) + 1):
            d = "/" + "/".join(parts[:i])
            try:
                sftp.mkdir(d)
            except OSError:
                pass
        remote_jar = f"{deploy_path.rstrip('/')}/{JAR_NAME}"
        echo_info(f"上传: {local_jar.name} -> {remote_jar}")
        sftp.put(str(local_jar), remote_jar)
        sftp.close()
    finally:
        client.close()

    echo_info("上传完成！")


def restart_backend(
    server: str,
    user: str,
    deploy_path: str,
    password: str,
) -> None:
    """远程：kill 已有 java -jar 进程，再 nohup 启动。"""
    if not server:
        echo_error("请指定服务器地址: --server=IP")
        sys.exit(1)

    if paramiko is None:
        echo_error("请先安装 paramiko: pip install paramiko")
        sys.exit(1)

    echo_info("连接服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        server,
        username=user,
        password=password,
        allow_agent=False,
        look_for_keys=False,
    )

    remote_jar_path = f"{deploy_path.rstrip('/')}/{JAR_NAME}"

    try:
        # 1. 查找并 kill 已有 java -jar stock-info-backend-1.0.0.jar 进程
        echo_info("查找并停止已有后端进程...")
        kill_cmd = (
            f"pkill -f 'java -jar {JAR_NAME}' || true"
        )
        stdin, stdout, stderr = client.exec_command(kill_cmd)
        stdout.channel.recv_exit_status()
        time.sleep(2)  # 等待进程完全退出

        # 2. 再次确认 kill（按 jar 名）
        client.exec_command(f"pkill -f '{JAR_NAME}' || true")
        time.sleep(1)

        # 3. 在部署目录下 nohup 启动
        echo_info("启动后端服务...")
        start_cmd = (
            f"cd {deploy_path} && nohup java -jar {JAR_NAME} > backend.log 2>&1 &"
        )
        stdin, stdout, stderr = client.exec_command(start_cmd)
        stdout.channel.recv_exit_status()
        time.sleep(1)

        # 简单检查是否启动
        _, out, _ = client.exec_command(
            f"pgrep -f '{JAR_NAME}' && echo 'OK' || echo 'FAIL'"
        )
        result = out.read().decode().strip()
        if "OK" in result:
            echo_info("后端服务已启动。")
        else:
            echo_warn("进程可能未找到，请登录服务器检查: " + remote_jar_path)
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="后端 JAR Linux 部署脚本（上传 + 远程重启）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python deploy-backend.py                    # 上传并重启
  python deploy-backend.py --upload-only      # 仅上传
  python deploy-backend.py --restart-only     # 仅远程重启
  python deploy-backend.py --server=1.2.3.4   # 指定服务器
        """,
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="仅上传 JAR，不重启服务",
    )
    parser.add_argument(
        "--restart-only",
        action="store_true",
        help="仅远程重启服务，不上传",
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
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="跳过本地 Maven 打包，直接使用已有 JAR",
    )
    parser.add_argument(
        "--mvn",
        default=DEFAULT_MVN_CMD,
        help=f"Maven 可执行路径（默认: {DEFAULT_MVN_CMD}）",
    )
    parser.add_argument(
        "--mvn-settings",
        default=DEFAULT_MVN_SETTINGS,
        help="Maven settings.xml 路径（默认随平台）",
    )
    args = parser.parse_args()

    if args.upload_only and args.restart_only:
        echo_error("不能同时指定 --upload-only 和 --restart-only")
        sys.exit(1)

    script_dir = Path(__file__).resolve().parent

    echo_info("=== 后端部署脚本 ===")

    do_upload = not args.restart_only
    do_restart = not args.upload_only

    if do_upload:
        if not args.skip_build:
            run_maven_build(
                script_dir,
                args.mvn,
                args.mvn_settings or "",
            )
        upload_jar(
            args.server,
            args.user,
            args.deploy_path,
            args.password,
            script_dir,
        )

    if do_restart:
        restart_backend(
            args.server,
            args.user,
            args.deploy_path,
            args.password,
        )

    if args.upload_only:
        echo_info("仅上传模式，未执行重启。可稍后执行: python deploy-backend.py --restart-only")


if __name__ == "__main__":
    main()
