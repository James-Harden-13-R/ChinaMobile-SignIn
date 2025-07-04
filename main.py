# -*- coding: utf-8 -*-
import requests
import os
import json
from datetime import datetime, timezone, timedelta

# --- 全局配置 ---
MY_COOKIE = os.environ.get('CM_COOKIE')
SIGN_IN_URL = "https://h5.bj.10086.cn/ActSignIn2023/doPrize/JT/ActSignIn2023JT?token=9855077a-0bf5-4e7d-9de6-509e950de842&type=sign&constid=6867cfaawfe5Q32A8pqykEpyIyEj3DV5KR7FoAv1"
HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/wkwebview leadeon/11.9.5/CMCCIT',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://h5.bj.10086.cn',
    'Referer': 'https://h5.bj.10086.cn/cmcc/cmcc_app/checkin/index.html',
    'Connection': 'keep-alive',
}
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
    """执行签到操作"""
    print(f"--- 北京时间: {get_beijing_time()} ---")
    print("开始执行中国移动App签到任务...")

    if not MY_COOKIE:
        print("❌ 错误：在GitHub Secrets中未找到名为 CM_COOKIE 的配置。")
        return

    HEADERS['Cookie'] = MY_COOKIE
    
    print(f"签到目标URL: {SIGN_IN_URL}")
    print("请求方法: POST")
    print(f"请求Body: {json.dumps(PAYLOAD, indent=2)}")

    try:
        # 直接使用 requests 发送请求，无需任何复杂的SSL处理
        response = requests.post(SIGN_IN_URL, headers=HEADERS, json=PAYLOAD, timeout=20)
        
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
                    print(f"✅ 测试通过: {res_msg}")
                else:
                    print(f"💔 签到失败: {res_msg}")
            except json.JSONDecodeError:
                print("解析服务器响应失败，可能不是有效的JSON格式。")
                print(f"服务器原始响应内容: {response.text}")
        else:
            print(f"❌ 请求失败，HTTP状态码: {response.status_code}")
            print(f"服务器响应: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")

    print("签到任务执行完毕。")

if __name__ == '__main__':
    sign_in()
