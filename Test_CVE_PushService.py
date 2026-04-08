# coding=utf-8
import os
import sys

from pkg.utils import format_display_time, load_template, send_notifications


def main():
    """模拟一条 CVE 情报推送，验证主服务推送链路是否可用"""
    template_path = os.path.join(os.path.dirname(__file__), "template", "nvd_cve.md")
    template = load_template(template_path)
    if not template:
        print("模板加载失败，无法发送测试消息。")
        return 1

    vuln_info = {
        "id": "CVE-2099-0001",
        "cvss_score": 9.8,
        "published_date": "2099-01-01T08:00:00.000",
        "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "description": "This is a simulated CVE message for testing the PushMe notification pipeline.",
        "refs": "https://nvd.nist.gov/vuln/detail/CVE-2099-0001",
        "source": "NVD-Test",
    }

    message = template.format(
        cve_id=vuln_info["id"],
        cvss_score=vuln_info["cvss_score"],
        published_date=vuln_info["published_date"],
        vector_string=vuln_info["vector_string"],
        description=vuln_info["description"],
        url=vuln_info["refs"],
        source=vuln_info["source"],
    )
    title = f"[{format_display_time(vuln_info['published_date'])}] 高危漏洞: {vuln_info['id']} ({vuln_info['cvss_score']})"

    results = send_notifications(title, message, "🚨漏洞警报")
    print(results)

    if results["pushme_success"] or results["serverchan_success"]:
        print("CVE 模拟消息发送成功。")
        return 0

    print("CVE 模拟消息发送失败，请检查推送配置。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
