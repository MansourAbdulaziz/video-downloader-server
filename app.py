from flask import Flask, request, jsonify, send_from_directory
from downloader import process_url, download_video, cleanup_old_files
import os

app = Flask(__name__)

# ✅ فحص حالة السيرفر
@app.route('/')
def home():
    return '✅ yt-dlp proxy server is running'

# ✅ استخراج معلومات الفيديو بدون تحميل
@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json(force=True)
        url = data.get('url')

        if not url:
            return jsonify({'error': 'Missing url'}), 400

        result = process_url(url)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ تحميل الفيديو فعليًا
@app.route('/download-file', methods=['POST'])
def download_file():
    try:
        data = request.get_json(force=True)
        url = data.get('url')

        if not url:
            return jsonify({'error': 'Missing url'}), 400

        result = download_video(url)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ تقديم الملف للتحميل (اختياري)
@app.route('/file/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory('downloads', filename)

# ✅ تنظيف الملفات القديمة يدويًا
@app.route('/cleanup', methods=['POST'])
def cleanup():
    result = cleanup_old_files()
    return jsonify(result), 200

# ✅ تشغيل السيرفر فقط إذا كان الملف هو الرئيسي
if __name__ == '__main__':
    cleanup_old_files()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)