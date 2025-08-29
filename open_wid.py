from pywinauto import Application
import subprocess
import time
import os
import glob
from datetime import datetime

def capture_image():
    # -----------------------------
    # مسار الملف التنفيذي
    # -----------------------------
    exe_path = r"Image_capture.exe"
    
    # Get current directory for image path detection
    current_dir = os.getcwd()
    
    # -----------------------------
    # تشغيل EXE مرئي أولاً (SW_SHOWNORMAL)
    # -----------------------------
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 1  # SW_SHOWNORMAL
    proc = subprocess.Popen(exe_path, startupinfo=si)

    # -----------------------------
    # الاتصال بالتطبيق عبر pywinauto
    # -----------------------------
    app = Application(backend="uia").connect(process=proc.pid)

    # انتظر النافذة حتى تظهر وتصبح جاهزة
    dlg = app.top_window()
    dlg.wait('exists ready', timeout=15)
    print("🟢 Window found:", dlg.window_text())

    # -----------------------------
    # صغر النافذة بعد التحميل لتقليل الإزعاج
    # -----------------------------
    dlg.minimize()
    time.sleep(1)  # تأخير بسيط بعد التصغير

    # -----------------------------
    # 1️⃣ اضغط زر Open Port
    # -----------------------------
    try:
        dlg.child_window(title="Open Port", control_type="Button").click()
        print("✅ Connected to device")
    except Exception as e:
        print("⚠️ Could not click Open Port:", e)

    time.sleep(2)

    # -----------------------------
    # 2️⃣ اضغط زر Capture Image
    # -----------------------------
    try:
        dlg.child_window(title="Capture Image", control_type="Button").click()
        print("📸 Capture triggered")
    except Exception as e:
        print("⚠️ Could not click Capture Image:", e)

    time.sleep(3)

    # -----------------------------
    # 3️⃣ اضغط زر Save Image
    # -----------------------------
    try:
        dlg.child_window(title="Save Image", control_type="Button").click()
        print("💾 Save triggered")
    except Exception as e:
        print("⚠️ Could not click Save Image:", e)

    time.sleep(2)

    # -----------------------------
    # 4️⃣ اضغط زر Close Port
    # -----------------------------
    try:
        dlg.child_window(title="Close Port", control_type="Button").click()
        print("🔌 Disconnected")
    except Exception as e:
        print("⚠️ Could not click Close Port:", e)

    # -----------------------------
    # 5️⃣ البحث عن الصورة المحفوظة
    # -----------------------------
    time.sleep(1)  # انتظار لحفظ الملف
    
    # البحث عن ملفات الصور الجديدة (jpg, png, jpeg)
    image_extensions = ['*.jpg', '*.jpeg', '*.png']
    captured_image_path = None
    
    for ext in image_extensions:
        # البحث عن الملفات في المجلد الحالي
        image_files = glob.glob(os.path.join(current_dir, ext))
        image_files.extend(glob.glob(os.path.join(current_dir, ext.upper())))
        
        if image_files:
            # ترتيب الملفات حسب وقت التعديل (الأحدث أولاً)
            image_files.sort(key=os.path.getmtime, reverse=True)
            captured_image_path = image_files[0]
            break
    
    if captured_image_path:
        print(f"📁 Image saved at: {captured_image_path}")
        return captured_image_path
    else:
        print("⚠️ Could not find captured image file")
        return None

if __name__ == "__main__":
    result = capture_image()
    if result:
        print(f"SUCCESS: {result}")
    else:
        print("FAILED: No image captured")
