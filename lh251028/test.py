import json
import urllib.request

url = "https://emappdata.eastmoney.com/label/getSecurityCodeLabelList"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Sec-GPC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "Content-type": "application/json",
    "Priority": "u=4",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}
data = {
    "appId": "appId01",
    "globalId": "786e4c21-70dc-435a-93bb-38",
    "securityCodes": "600001"
}

payload = json.dumps(data).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read()
        try:
            print(json.loads(body.decode("utf-8")))
        except Exception:
            print(body.decode("utf-8", errors="replace"))
except Exception as e:
    print(f"请求失败: {e}")