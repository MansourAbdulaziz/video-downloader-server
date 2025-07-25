import subprocess
import os
import json
import uuid
import time

# 📁 إعداد مجلد التحميل
DOWNLOAD_DIR = "downloads"
MAX_FILE_AGE_SECONDS = 3600  # ⏱ 1 ساعة

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ تحديد مسار ملف الكوكيز حسب المنصة
def get_cookie_path(platform):
    path = f"cookies/{platform}.txt"
    return path if os.path.exists(path) else None

# ✅ استخراج معلومات الفيديو بدون تحميل
def process_url(url, platform):
    cookie_path = get_cookie_path(platform)
    command = [
        "yt-dlp",
        "--no-warnings",
        "--skip-download",
        "--print-json",
        url
    ]
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": "yt-dlp failed", "details": result.stderr.strip()}

        info = json.loads(result.stdout)
        return {
            "title": info.get("title"),
            "download_url": info.get("url"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "platform": platform
        }

    except subprocess.TimeoutExpired:
        return {"error": "yt-dlp timed out after 30 seconds"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse yt-dlp output"}
    except Exception as e:
        return {"error": str(e)}

# ✅ تحميل الفيديو فعليًا
def download_video(url, platform):
    cookie_path = get_cookie_path(platform)
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    command = [
        "yt-dlp",
        "-f", "best",
        "-o", output_path,
        url
    ]
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {"error": "Download failed", "details": result.stderr.strip()}

        return {
            "message": "Download successful",
            "file": filename,
            "path": output_path
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