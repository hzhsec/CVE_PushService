# coding=utf-8
import os
import sys
from datetime import datetime

from pkg.utils import send_pushme_notification


def main():
    """发送一条 PushMe 测试消息，用于验证自建服务连通性"""
    pushme_key = os.getenv("PUSHME_KEY")
    pushme_url = os.getenv("PUSHME_URL", "https://push.i-i.me")

    if not pushme_key:
        print("未检测到 PUSHME_KEY，无法发送测试消息。")
        return 1

    title = "[#CVEPush!测]PushMe 测试消息"
    content = (
        "## PushMe 测试成功\n\n"
        f"- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- 服务地址：`{pushme_url}`\n"
        "- 说明：如果你收到了这条消息，说明当前 PushMe 配置可用。"
    )

    success = send_pushme_notification(title, content, "markdown")
    if success:
        print("PushMe 测试消息发送成功。")
        return 0

    print("PushMe 测试消息发送失败，请检查 PUSHME_URL、PUSHME_KEY 和服务器端口。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
