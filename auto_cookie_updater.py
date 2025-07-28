# auto_cookie_updater.py
import os
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

def save_cookies_as_netscape(cookies, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie.get("domain", "")
            include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
            path = cookie.get("path", "/")
            secure = "TRUE" if cookie.get("secure", False) else "FALSE"
            expires = int(cookie.get("expires", 0))
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            f.write(f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")

def save_cookies_for_site(playwright, domain, filename):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    print(f"🔗 افتح المتصفح: {domain}")
    page = context.new_page()
    page.goto(f"https://{domain}")
    print(f"⏳ الرجاء الانتظار 5-10 ثوانٍ على الصفحة: {domain}")
    page.wait_for_timeout(7000)

    cookies = context.cookies()
    file_path = COOKIES_DIR / filename
    save_cookies_as_netscape(cookies, file_path)
    print(f"✅ تم حفظ الكوكيز في: {file_path}")

    context.close()
    browser.close()

def main():
    with sync_playwright() as playwright:
        for domain, filename in TARGETS.items():
            save_cookies_for_site(playwright, domain, filename)

if __name__ == "__main__":
    main()
