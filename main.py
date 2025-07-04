# -*- coding: utf-8 -*-
import requests
import os
import json
import ssl
from datetime import datetime, timezone, timedelta

# --- [最终解决方案] 创建一个非常宽松的HTTP适配器以解决顽固的SSL错误 ---
# 这个类将创建一个自定义的SSL上下文，以兼容旧版或不标准的服务器配置
class PermissiveHttpAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # 创建一个自定义的SSL上下文
        context = ssl.create_default_context()
        # 允许连接到使用旧版协议的服务器，这是解决问题的关键
        context.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0)
        # 强制降低安全等级，以应对最严格的环境
        context.set_ciphers('DEFAULT:@SECLEVEL=1')
        
        kwargs['ssl_context'] = context
        return super(PermissiveHttpAdapter, self).init_poolmanager(*args, **kwargs)


# --- 全局配置 (根据您的截图信息填写) ---

# 身份凭证Cookie，将从GitHub Secrets中读取
MY_COOKIE = os.environ.get('CM_COOKIE')

# 签到请求的URL (来自截图的第一行)
SIGN_IN_URL = "https://h5.bj.10086.cn/ActSignIn2023/doPrize/JT/ActSignIn2023JT?token=9855077a-0bf5-4e7d-9de6-509e950de842&type=sign&constid=6867cfaawfe5Q32A8pqykEpyIyEj3DV5KR7FoAv1"

# 签到请求的Headers (来自截图的Request Header部分)
HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/wkwebview leadeon/11.9.5/CMCCIT',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://h5.bj.10086.cn',
    'Referer': 'https://h5.bj.10086.cn/cmcc/cmcc_app/checkin/index.html',
    'Connection': 'keep-alive',
}

# 签到请求的Body数据
PAYLOAD = {
    "token": "9855077a-0bf5-4e7d-9de6-509e950de842",
    "type": "sign",
    "constid": "6867cfaawfe5Q32A8pqykEpyIyEj3DV5KR7FoAv1"
}

def get_beijing_time():
    """获取北京时间，用于日志记录"""
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')

def sign_in():
    """
    执行签到操作
    """
    print(f"--- 北京时间: {get_beijing_time()} ---")
    print("开始执行中国移动App签到任务...")

    if not MY_COOKIE:
        print("❌ 错误：在GitHub Secrets中未找到名为 CM_COOKIE 的配置。")
        return

    HEADERS['Cookie'] = MY_COOKIE
    
    print(f"签到目标URL: {SIGN_IN_URL}")
    print("请求方法: POST")
    print(f"请求Body: {json.dumps(PAYLOAD, indent=2)}")

    # 【已修改】创建一个使用我们自定义的、宽松的适配器的会话
    session = requests.Session()
    session.mount("https://", PermissiveHttpAdapter())

    try:
        # 【已修改】使用自定义的session发送请求，不再需要 verify=False
        response = session.post(SIGN_IN_URL, headers=HEADERS, json=PAYLOAD, timeout=20)
        
        if response.status_code == 200:
            print("✅ 请求成功，服务器返回状态码 200。")
            
            try:
                result = response.json()
                print("服务器响应 (JSON):")
                print(json.dumps(result, indent=2, ensure_ascii=False))

                res_msg = result.get('resMsg', '')
                if result.get('resCode') == '0000' or "成功" in res_msg:
                    print(f"🎉 签到成功: {res_msg}")
                elif "已签到" in res_msg or "已参与" in res_msg:
                    print(f"✅ 测试通过: {res_msg} (这说明您的配置是正确的！)")
                else:
                    error_message = result.get('resMsg', '未知错误')
                    print(f"💔 签到失败: {error_message}")

            except json.JSONDecodeError:
                print("解析服务器响应失败，可能不是有效的JSON格式。")
                print("服务器原始响应内容:")
                print(response.text)
        else:
            print(f"❌ 请求失败，HTTP状态码: {response.status_code}")
            print("服务器响应:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")

    print("签到任务执行完毕。")


if __name__ == '__main__':
    sign_in()
