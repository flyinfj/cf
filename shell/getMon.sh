#!/bin/sh
export CFLAGS=$(pkg-config --cflags openssl11)
export LDFLAGS=$(pkg-config --libs openssl11)
export LD_LIBRARY_PATH=/usr/local/python3.13/lib:$LD_LIBRARY_PATH

# 切换到 Python 脚本所在目录
cd /root/cf/lh

# 执行 Python 脚本
/usr/local/python3.13/bin/python3.13 8_getLimitUpBank.py
/usr/local/python3.13/bin/python3.13 1_getQingXu.py
/usr/local/python3.13/bin/python3.13 7_getLimitUp.py
/usr/local/python3.13/bin/python3.13 2_getRcList.py
/usr/local/python3.13/bin/python3.13 3_getRcHis.py
/usr/local/python3.13/bin/python3.13 4_getShenQi.py
/usr/local/python3.13/bin/python3.13 5_getColdStock.py
/usr/local/python3.13/bin/python3.13 6_getChange.py
/usr/local/python3.13/bin/python3.13 sendMail.py 1
