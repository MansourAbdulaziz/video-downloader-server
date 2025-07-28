# auto_cookie_updater.py

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# المنصات المستهدفة مع ملفات الكوكيز الخاصة بها
TARGETS = {
    "facebook.com": "facebook.txt",
    "instagram.com": "instagram.txt",
    "snapchat.com": "snapchat.txt",
    "tiktok.com": "tiktok.txt",
    "x.com": "twitter.txt",  # X = Twitter
    "youtube.com": "youtube.txt",
    "pinterest.com": "pinterest.txt",
    "kwai.com": "kwai.txt",
    "chingari.io": "chingari.txt",
    "rumble.com": "rumble.txt",
    "telegram.org": "telegram.txt",
    "vimeo.com": "vimeo.txt",
    "bilibili.com": "bilibili.txt",
    "jaco.live": "jaco.txt",
    "dailymotion.com": "dailymotion.txt",
    "linkedin.com": "linkedin.txt",
    "kick.com": "kick.txt",
    "twitch.tv": "twitch.txt",
}

COOKIES_DIR = Path("cookies")
COOKIES_DIR.mkdir(exist_ok=True)

def save_cookies_for_site(playwright, domain, filename):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print(f"🔗 افتح المتصفح: {domain}")
    page.goto(f"https://{domain}")
    print(f"⏳ الرجاء الانتظار 5-10 ثوانٍ على الصفحة: {domain}")
    page.wait_for_timeout(7000)

    cookies = context.cookies()
    cookie_path = COOKIES_DIR / filename

    # رأس ملف الكوكيز بصيغة Netscape
    header = "# Netscape HTTP Cookie File\n"
    lines = [header]

    for cookie in cookies:
        domain_cookie = cookie["domain"]
        include_subdomains = "TRUE" if domain_cookie.startswith(".") else "FALSE"
        path = cookie.get("path", "/")
        secure = "TRUE" if cookie.get("secure", False) else "FALSE"
        expiry = str(cookie.get("expires", 0))
        name = cookie["name"]
        value = cookie["value"]

        line = f"{domain_cookie}\t{include_subdomains}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n"
        lines.append(line)

    cookie_path.write_text("".join(lines), encoding="utf-8")
    print(f"✅ تم حفظ الكوكيز في: {cookie_path}")

    context.close()
    browser.close()


def main():
    with sync_playwright() as playwright:
        for domain, filename in TARGETS.items():
            try:
                save_cookies_for_site(playwright, domain, filename)
            except Exception as e:
                print(f"❌ فشل حفظ الكوكيز لـ {domain}: {e}")

if __name__ == "__main__":
    main()
