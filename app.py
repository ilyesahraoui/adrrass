from datetime import datetime
import base64
import requests
from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# ضع التوكن الخاص بك هنا (ويفضل دائماً وضعه في متغيرات البيئة Environmental Variables)
GITHUB_TOKEN = "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"
REPO_OWNER = "muslimhaydra"  # ضع اسم حسابك الحقيقي
REPO_NAME = "haydra"  # ضع اسم المستودع الحقيقي
FILE_PATH = "adrr.txt"  # اسم الملف داخل المستودع


def update_github_file(new_log):
  url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
  headers = {
      "Authorization": f"Bearer {GITHUB_TOKEN}",
      "Accept": "application/vnd.github+json",
  }

  # 1. جلب المحتوى الحالي للملف والحصول على الـ SHA (مطلوب لتحديث الملفات في غيت هاب)
  resp = requests.get(url, headers=headers)
  sha = None
  content = ""
  if resp.status_code == 200:
    data = resp.json()
    sha = data["sha"]
    content = base64.b64decode(data["content"]).decode("utf-8")

  # إضافة السجل الجديد
  updated_content = content + "\n" + new_log if content else new_log
  encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode(
      "utf-8"
  )

  # 2. تحديث الملف عبر API
  payload = {
      "message": "Update visitor logs automatically",
      "content": encoded_content,
      "sha": sha,
  }
  requests.put(url, headers=headers, json=payload)


@app.route("/")
def index():
  # استخراج الـ IP ومعلومات المتصفح والجهاز
  ip = request.headers.get("X-Forwarded-For", request.remote_addr)
  user_agent = request.headers.get("User-Agent")
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  log_entry = (
      f"[{timestamp}] IP: {ip} | Device/Browser: {user_agent}"
  )

  # إرسال البيانات إلى غيت هاب
  try:
    update_github_file(log_entry)
  except Exception as e:
    print(f"Error updating GitHub: {e}")

  # عرض صفحة تحتوي على فيديو تيكتوك (عبر تضمين iframe)
  html = """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>TikTok Video</title>
        <style>
            body { background-color: #0f0f0f; color: #fff; font-family: Arial, sans-serif; text-align: center; padding-top: 50px; }
            .video-container { margin-top: 20px; }
        </head>
        <body>
            <h2>شاهد الفيديو</h2>
            <div class="video-container">
                <!-- تضمين فيديو تيكتوك المطلوب -->
                <blockquote class="tiktok-embed" cite="https://www.tiktok.com/@404.fsociety/video/7700082199449718024" data-video-id="7700082199449718024" style="max-width: 605px; min-width: 325px;" > <section> <a target="_blank" title="@404.fsociety" href="https://www.tiktok.com/@404.fsociety?refer=embed">@404.fsociety</a> </section> </blockquote> <script async src="https://www.tiktok.com/embed.js"></script>
            </div>
        </body>
    </html>
    """
  return render_template_string(html)


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)