# auto_cookie_updater.py
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

# المواقع المستهدفة واسم ملفات الكوكيز
TARGETS = {
    "tiktok.com": "tiktok.txt",
    "instagram.com": "instagram.txt",
    "twitter.com": "twitter.txt",
    "facebook.com": "facebook.txt",
}

COOKIES_DIR = Path("cookies")
COOKIES_DIR.mkdir(exist_ok=True)

def save_cookies_for_site(playwright, domain, filename):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    print(f"🔗 افتح المتصفح: {domain}")
    page = context.new_page()
    page.goto(f"https://{domain}")
    print(f"⏳ الرجاء الانتظار 5-10 ثوانٍ على الصفحة: {domain}")
    page.wait_for_timeout(7000)

    cookies = context.cookies()
    cookie_str = "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies if domain in cookie['domain'])
    cookie_path = COOKIES_DIR / filename
    cookie_path.write_text(cookie_str, encoding="utf-8")
    print(f"✅ تم حفظ الكوكيز في: {cookie_path}")

    context.close()
    browser.close()

def main():
    with sync_playwright() as playwright:
        for domain, filename in TARGETS.items():
            save_cookies_for_site(playwright, domain, filename)

if __name__ == "__main__":
    main()
