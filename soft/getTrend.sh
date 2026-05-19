#!/bin/sh
export CFLAGS=$(pkg-config --cflags openssl111)
export LDFLAGS=$(pkg-config --libs openssl111)
export LD_LIBRARY_PATH=/usr/local/python3.13/lib:$LD_LIBRARY_PATH

cd /root/cf/lh
/usr/local/python3.13/bin/python3.13 getTrend.py
/usr/local/python3.13/bin/python3.13 getYanbao.py
/usr/local/python3.13/bin/python3.13 10_getLimitTrend.py
/usr/local/python3.13/bin/python3.13 sendMail.py 4
