export CFLAGS=$(pkg-config --cflags openssl11)
export LDFLAGS=$(pkg-config --libs openssl11)
export LD_LIBRARY_PATH=/usr/local/python3.13/lib:$LD_LIBRARY_PATH

cd /root/cf/lh
/usr/local/python3.13/bin/python3.13 getTrend.py
/usr/local/python3.13/bin/python3.13 getYanbao.py