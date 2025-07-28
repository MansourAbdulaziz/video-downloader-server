from flask import Flask, request, jsonify
import subprocess
import os
import json
import uuid
import time

# 🔹 إعداد Flask
app = Flask(__name__)

# 📁 إعداد مجلد التحميل
DOWNLOAD_DIR = "downloads"
MAX_FILE_AGE_SECONDS = 3600  # ⏱ 1 ساعة

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ تحديد ملف الكوكيز المناسب حسب رابط الفيديو
def get_cookie_path_by_url(url):
    url = url.lower()
    if "youtube.com" in url or "youtu.be" in url:
        return "cookies/youtube.txt"
    elif "tiktok.com" in url:
        return "cookies/tiktok.txt"
    elif "instagram.com" in url:
        return "cookies/instagram.txt"
    elif "facebook.com" in url:
        return "cookies/facebook.txt"
    elif "x.com" in url or "twitter.com" in url:
        return "cookies/twitter.txt"
    elif "snapchat.com" in url:
        return "cookies/snapchat.txt"
    elif "linkedin.com" in url:
        return "cookies/linkedin.txt"
    elif "pinterest.com" in url:
        return "cookies/pinterest.txt"
    elif "rumble.com" in url:
        return "cookies/rumble.txt"
    elif "vimeo.com" in url:
        return "cookies/vimeo.txt"
    elif "twitch.tv" in url:
        return "cookies/twitch.txt"
    elif "kick.com" in url:
        return "cookies/kick.txt"
    elif "chingari.io" in url:
        return "cookies/chingari.txt"
    elif "capcut.com" in url:
        return "cookies/capcut.txt"
    elif "jaco.com" in url:
        return "cookies/jaco.txt"
    else:
        return None

# ✅ استخراج معلومات الفيديو بدون تحميل
def process_url(url):
    cookie_path = get_cookie_path_by_url(url)
    command = [
        "yt-dlp",
        "--no-warnings",
        "--skip-download",
        "--print-json",
        url
    ]
    if cookie_path and os.path.exists(cookie_path):
        command.extend(["--cookies", cookie_path])

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print("yt-dlp failed:", result.stderr.strip())
            return {"error": "yt-dlp failed", "details": result.stderr.strip()}

        info = json.loads(result.stdout)
        print("DEBUG yt-dlp info:", info)

        best_url = None
        if "formats" in info:
            formats = info.get("formats", [])
            if not isinstance(formats, list):
                formats = []

            formats = sorted(
                formats,
                key=lambda f: f.get("height") if isinstance(f.get("height"), int) else -1,
                reverse=True
            )

            for f in formats:
                url_candidate = f.get("url")
                ext = f.get("ext", "")
                if url_candidate:
                    if ext == "mp4":
                        best_url = url_candidate
                        break
                    elif ext == "m3u8" or url_candidate.endswith(".m3u8"):
                        best_url = url_candidate
                        break

            if not best_url and formats:
                best_url = formats[0].get("url")

        if not best_url:
            best_url = info.get("url")

        if not best_url:
            return {"error": "No valid download URL found."}

        # ✅ تحديد نوع الوسيط
        media_type = "unknown"
        lowered = best_url.lower()
        if any(ext in lowered for ext in [".mp4", ".mkv", ".mov", ".webm"]):
            media_type = "video"
        elif any(ext in lowered for ext in [".mp3", ".wav", ".m4a", ".aac"]):
            media_type = "audio"
        elif any(ext in lowered for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
            media_type = "image"

        return {
            "title": info.get("title"),
            "download_url": best_url,
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "platform": info.get("extractor_key"),
            "media_type": media_type
        }

    except subprocess.TimeoutExpired:
        return {"error": "yt-dlp timed out after 30 seconds"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse yt-dlp output"}
    except Exception as e:
        print("Exception in process_url:", str(e))
        return {"error": str(e)}

# ✅ نقطة دخول API من Flutter
@app.route("/")
def index():
    return "✅ Server is running"

@app.route("/process", methods=["POST"])
def api_process_url():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        result = process_url(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ تشغيل السيرفر في حال التشغيل المباشر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
