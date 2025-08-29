from pywinauto import Application
import subprocess
import time

# -----------------------------
# مسار الملف التنفيذي
# -----------------------------
exe_path = r"Image_capture.exe"

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
