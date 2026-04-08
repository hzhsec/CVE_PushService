from datetime import datetime
import os
import requests
import logging
import time
from serverchan_sdk import sc_send


def get_current_year():
    """获取当前年份"""
    return datetime.now().year


def format_display_time(time_str: str) -> str:
    """将时间格式化为适合放在标题中的短时间"""
    if not time_str:
        return "未知时间"

    text = str(time_str).strip()
    candidates = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]

    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue

    return text.replace("T", " ")[:16]


def get_cve_overview(cve_id: str) -> str:
    """通过CVE API获取CVE的英文描述信息"""
    try:
        url = f"https://cve.circl.lu/api/cve/{cve_id}"
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        data = response.json()

        # 匹配漏洞描述，查找包含在 "containers" -> "cna" -> "descriptions"
        if 'containers' in data and 'cna' in data['containers']:
            for description in data['containers']['cna'].get('descriptions', []):
                return description.get('value', "No description available for this CVE.")

        return "No English description available for this CVE."

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch CVE overview for {cve_id}: {str(e)}")
        return "Error fetching CVE overview."

def translate(text, delay_seconds):
    url = 'https://aidemo.youdao.com/trans'
    try:
        data = {"q": text, "from": "auto", "to": "zh-CHS"}
        resp = requests.post(url, data, timeout=15)
        if resp is not None and resp.status_code == 200:
            respJson = resp.json()
            if "translation" in respJson:
                return "\n".join(str(i) for i in respJson["translation"])
            if delay_seconds > 0:
                time.sleep(delay_seconds)
    except Exception:
        logging.warning("Error translating message!")
    return text

# 模板加载函数
def load_template(file_path: str) -> str:
    """加载通知模板"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading template from {file_path}: {str(e)}")
        return ""


def send_pushme_notification(title: str, content: str, msg_type: str = "markdown") -> bool:
    """通过 PushMe 发送通知，支持自建服务地址"""
    pushme_key = os.getenv("PUSHME_KEY")
    pushme_url = os.getenv("PUSHME_URL", "https://push.i-i.me").strip()

    if not pushme_key:
        return False

    endpoint = pushme_url.rstrip("/") + "/"
    data = {
        "push_key": pushme_key,
        "title": title,
        "content": content,
        "type": msg_type,
    }

    try:
        response = requests.post(endpoint, data=data, timeout=15)
        response.raise_for_status()
        if response.text.strip() == "success":
            return True
        logging.error(f"PushMe response is not success: {response.text}")
    except Exception as e:
        logging.error(f"Failed to send PushMe notification: {str(e)}")
    return False


def send_notifications(title: str, content: str, tags: str = "") -> dict:
    """同时兼容 Server酱3 与 PushMe 推送"""
    results = {
        "serverchan_enabled": False,
        "serverchan_success": False,
        "pushme_enabled": False,
        "pushme_success": False,
    }

    sckey = os.getenv("SCKEY")
    if sckey:
        results["serverchan_enabled"] = True
        try:
            sc_send(sckey, title, content, {"tags": tags} if tags else None)
            results["serverchan_success"] = True
        except Exception as e:
            logging.error(f"Failed to send ServerChan notification: {str(e)}")

    if os.getenv("PUSHME_KEY"):
        results["pushme_enabled"] = True
        results["pushme_success"] = send_pushme_notification(title, content)

    return results
