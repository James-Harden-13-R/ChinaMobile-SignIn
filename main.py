# -*- coding: utf-8 -*-
import requests
import os
import json
from datetime import datetime, timezone, timedelta

# --- 全局配置 (根据您的截图信息填写) ---

# 身份凭证Cookie，将从GitHub Secrets中读取
# 您需要将截图中完整的Cookie长字符串，设置到名为 CM_COOKIE 的Secret中
MY_COOKIE = os.environ.get('CM_COOKIE')

# 签到请求的URL (来自截图的第一行)
SIGN_IN_URL = "https://h5.bj.10086.cn/ActSignIn2023/doPrize/JT/ActSignIn2023JT?token=9855077a-0bf5-4e7d-9de6-509e950de842&type=sign&constid=6867cfaawfe5Q32A8pqykEpyIyEj3DV5KR7FoAv1"

# 签到请求的Headers (来自截图的Request Header部分)
HEADERS = {
    # Content-Type 表明我们发送的是JSON数据
    'Content-Type': 'application/json; charset=utf-8',
    # User-Agent 模拟您的iPhone环境，让请求更真实
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/wkwebview leadeon/11.9.5/CMCCIT',
    # 其他一些通用的头部信息
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://h5.bj.10086.cn',
    'Referer': 'https://h5.bj.10086.cn/cmcc/cmcc_app/checkin/index.html',
    'Connection': 'keep-alive',
}

# 【已更新】签到请求的Body数据 (来自您的最新发现)
# 这部分数据是发送给服务器的具体指令
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
        print("请将您截图中完整的Cookie字符串，设置到仓库的Secrets中。")
        return

    # 将从Secrets获取的Cookie添加到请求头中
    HEADERS['Cookie'] = MY_COOKIE
    
    print(f"签到目标URL: {SIGN_IN_URL}")
    print("请求方法: POST")
    print(f"请求Body: {json.dumps(PAYLOAD, indent=2)}")


    try:
        # 发送POST请求
        response = requests.post(SIGN_IN_URL, headers=HEADERS, json=PAYLOAD, timeout=20)
        
        # 检查响应状态码
        if response.status_code == 200:
            print("✅ 请求成功，服务器返回状态码 200。")
            
            try:
                result = response.json()
                print("服务器响应 (JSON):")
                print(json.dumps(result, indent=2, ensure_ascii=False))

                # 根据响应内容判断签到是否成功
                # 您可以根据实际返回的 'msg' 或 'code' 来调整这里的逻辑
                if result.get('resCode') == '0000' or "成功" in result.get('resMsg', ''):
                    message = result.get('resMsg', '签到成功！')
                    print(f"🎉 签到成功: {message}")
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
