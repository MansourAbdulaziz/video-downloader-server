import subprocess
import os
import json
import uuid
import time

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
    elif "twitter.com" in url or "x.com" in url:
        return "cookies/twitter.txt"
    else:
        return None  # تحميل بدون كوكيز

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
            formats = sorted(info["formats"], key=lambda f: f.get("height", 0), reverse=True)
            for f in formats:
                url_candidate = f.get("url")
                ext = f.get("ext", "")
                if url_candidate:
                    if ext == "mp4":
                        best_url = url_candidate
                        print(f"Selected mp4 url with height {f.get('height')}")
                        break
                    elif ext == "m3u8" or (url_candidate.endswith(".m3u8")):
                        best_url = url_candidate
                        print("Selected m3u8 url")
                        break

            if not best_url and len(info["formats"]) > 0:
                best_url = formats[0].get("url")
                print("Fallback to first available format url")
        else:
            best_url = info.get("url")

        print("Selected download_url:", best_url)

        if not best_url:
            return {"error": "No valid download URL found."}

        return {
            "title": info.get("title"),
            "download_url": best_url,
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "platform": info.get("extractor_key"),
        }

    except subprocess.TimeoutExpired:
        return {"error": "yt-dlp timed out after 30 seconds"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse yt-dlp output"}
    except Exception as e:
        print("Exception in process_url:", str(e))
        return {"error": str(e)}

# ✅ تحميل الفيديو فعليًا
def download_video(url):
    cookie_path = get_cookie_path_by_url(url)
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    command = [
        "yt-dlp",
        "-f", "best",
        "-o", output_path,
        url
    ]
    if cookie_path and os.path.exists(cookie_path):
        command.extend(["--cookies", cookie_path])

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {"error": "Download failed", "details": result.stderr.strip()}

        download_link = f"https://video-downloader-server-msm2.onrender.com/file/{filename}"

        return {
            "message": "Download successful",
            "file": filename,
            "path": output_path,
            "download_url": download_link
        }

    except subprocess.TimeoutExpired:
        return {"error": "Download timed out after 120 seconds"}
    except Exception as e:
        return {"error": str(e)}

# ✅ حذف الملفات القديمة من مجلد التحميل
def cleanup_old_files():
    now = time.time()
    deleted = []

    for filename in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > MAX_FILE_AGE_SECONDS:
                try:
                    os.remove(filepath)
                    deleted.append(filename)
                except Exception as e:
                    print(f"❌ Failed to delete {filename}: {e}")

    return {"deleted_files": deleted, "count": len(deleted)}
