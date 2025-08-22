import sys

import time

import keyboard

import pyperclip

import json

import os

import serial

import serial.tools.list_ports

from PyQt6.QtWidgets import (

  QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,

  QGroupBox, QComboBox, QMessageBox, QTabWidget, QLabel, QLineEdit, QPushButton

)

from PyQt6.QtCore import pyqtSignal, QObject, Qt, QThread

from PyQt6.QtGui import QIcon, QPixmap, QShortcut, QKeySequence



def get_settings_path():

  if sys.platform == "win32":

    appdata_path = os.environ.get('LOCALAPPDATA')

    if not appdata_path:

      appdata_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')

    app_name = "BarcodeFiller"

    settings_dir = os.path.join(appdata_path, app_name)

  else:

    settings_dir = os.path.join(os.path.expanduser('~'), '.BarcodeFiller')

  os.makedirs(settings_dir, exist_ok=True)

  return os.path.join(settings_dir, "settings.json")



def resource_path(relative_path):

  try:

    base_path = sys._MEIPASS

  except Exception:

    base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)



class SerialCommunicator(QObject):

  data_received = pyqtSignal(str)

  connection_status = pyqtSignal(bool)

  error = pyqtSignal(str)



class SerialReader(QThread):

  def __init__(self, com_port, communicator):

    super().__init__()

    self.com_port = com_port

    self.communicator = communicator

    self.is_running = False

    self.ser = None



  def run(self):

    self.is_running = True

    try:

      # هنا يمكنك تجربة تغيير الـ baudrate إذا لزم الأمر

      self.ser = serial.Serial(self.com_port, 9600, timeout=1)

      self.communicator.connection_status.emit(True)

    except serial.SerialException as e:

      self.communicator.error.emit(f"خطأ في الاتصال بالمنفذ {self.com_port}: {e}")

      self.is_running = False

      return

   

    while self.is_running:

      try:

        if self.ser.in_waiting > 0:

          # تعديل الترميز هنا

          data = self.ser.readline().decode('cp1256', errors='ignore').strip()

          if data:

            self.communicator.data_received.emit(data)

      except Exception as e:

        self.communicator.error.emit(f"خطأ في قراءة البيانات: {e}")

        self.is_running = False

       

    if self.ser and self.ser.is_open:

      self.ser.close()

      self.communicator.connection_status.emit(False)



  def stop(self):

    self.is_running = False

    self.wait()



class Communicate(QObject):

  paste_success = pyqtSignal()

  paste_warning = pyqtSignal()

  paste_error = pyqtSignal(str)

 

class BarcodeFillerApp(QWidget):

  def __init__(self):

    super().__init__()

    self.setWindowTitle("Barcode Filler - اعدادات")

    self.setWindowIcon(QIcon(resource_path("app_icon.ico")))

    self.setGeometry(100, 100, 600, 400)

   

    self.settings_file = get_settings_path()

   

    self.is_listening = False

    self.serial_thread = None

    self.serial_communicator = SerialCommunicator()

    self.serial_communicator.data_received.connect(self.handle_barcode_data)

    self.serial_communicator.connection_status.connect(self.update_serial_status)

    self.serial_communicator.error.connect(self.show_error_message)

   

    self.setup_ui()

    self.load_settings()

   

    self.comm = Communicate()

    self.comm.paste_warning.connect(self.show_warning_message)

    self.comm.paste_error.connect(self.show_error_message)

    self.toggle_listening_button.setText("تفعيل الاستماع (Ctrl+Alt+P)")

   

    self.set_stylesheet()

   

    self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)

    self.save_shortcut.activated.connect(self.save_settings)



  def set_stylesheet(self):

    self.setStyleSheet("""

      QWidget {

        background-color: #f0f0f0;

        font-family: Arial, sans-serif;

        font-size: 14px;

      }

      QTabWidget::pane {

        border: 1px solid #c4c4c4;

        background: white;

      }

      QTabWidget::tab-bar {

        left: 5px;

      }

      QTabBar::tab {

        background: #e1e1e1;

        border: 1px solid #c4c4c4;

        border-bottom-color: #c2c7cb;

        border-top-left-radius: 4px;

        border-top-right-radius: 4px;

        min-width: 80px;

        padding: 10px;

      }

      QTabBar::tab:selected, QTabBar::tab:hover {

        background: #ffffff;

        border-color: #9B9B9B;

        border-bottom-color: white;

      }

      QGroupBox {

        border: 1px solid #c4c4c4;

        border-radius: 5px;

        margin-top: 1ex;

        background-color: #ffffff;

      }

      QGroupBox::title {

        subcontrol-origin: margin;

        subcontrol-position: top center;

        padding: 0 3px;

        background-color: #ffffff;

      }

      QPushButton {

        background-color: #007bff;

        color: white;

        border-radius: 5px;

        padding: 10px;

        font-size: 16px;

      }

      QPushButton:hover {

        background-color: #0056b3;

      }

      QLineEdit, QComboBox {

        padding: 5px;

        border: 1px solid #c4c4c4;

        border-radius: 3px;

      }

      QLabel#logoLabel {

      }

      QLabel#appTitle {

        font-size: 18px;

      }

      QLabel#serialStatusLabel {

        font-weight: bold;

        margin-top: 5px;

        padding: 5px;

        border-radius: 5px;

        background-color: #dc3545; /* Red for Disconnected */

        color: white;

      }

    """)



  def setup_ui(self):

    main_layout = QVBoxLayout(self)

    self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

   

    header_layout = QVBoxLayout()

    header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

   

    try:

      logo_label = QLabel()

      logo_pixmap = QPixmap(resource_path("logo.png"))

      if not logo_pixmap.isNull():

        logo_label.setPixmap(logo_pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation))

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label.setObjectName("logoLabel")

        header_layout.addWidget(logo_label)

    except ImportError:

      text_logo = QLabel("Barcode Filler Logo")

      text_logo.setObjectName("logoLabel")

      text_logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #007bff; text-align: center;")

      header_layout.addWidget(text_logo)



    app_name_label = QLabel("Barcode Filler - تطبيق إفراغ الباركود")

    app_name_label.setObjectName("appTitle")

    app_name_label.setStyleSheet("font-weight: bold; color: #333333; text-align: center;")

    header_layout.addWidget(app_name_label)

   

    self.serial_status_label = QLabel("حالة الجهاز: غير متصل")

    self.serial_status_label.setObjectName("serialStatusLabel")

    header_layout.addWidget(self.serial_status_label)

   

    self.available_ports_combo = QComboBox()

    self.refresh_ports_button = QPushButton("تحديث المنافذ")

    self.refresh_ports_button.clicked.connect(self.list_available_ports)

   

    port_layout = QHBoxLayout()

    port_layout.addWidget(QLabel("اختر منفذ COM:"))

    port_layout.addWidget(self.available_ports_combo)

    port_layout.addWidget(self.refresh_ports_button)

   

    header_layout.addLayout(port_layout)

    main_layout.addLayout(header_layout)



    self.tabs = QTabWidget()

    self.tabs.setTabPosition(QTabWidget.TabPosition.North)

    self.tabs.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    main_layout.addWidget(self.tabs)

   

    self.settings_tab = self.create_settings_tab()

    self.about_tab = self.create_about_tab()

    self.contact_tab = self.create_contact_tab()



    self.tabs.addTab(self.settings_tab, "الإعدادات")

    self.tabs.addTab(self.about_tab, "من نحن")

    self.tabs.addTab(self.contact_tab, "التواصل")

   

    self.list_available_ports()



  def list_available_ports(self):

    self.available_ports_combo.clear()

    ports = serial.tools.list_ports.comports()

    if not ports:

      self.available_ports_combo.addItem("لا يوجد منافذ COM متاحة")

    else:

      for port in ports:

        self.available_ports_combo.addItem(port.device)



  def create_settings_tab(self):

    settings_widget = QWidget()

    settings_layout = QVBoxLayout(settings_widget)

   

    description_label = QLabel("في وضع الفك سيتم لصق الحقل السادس فقط المفصول بالرمز #، كما سيتم تطبيق الفاصل بعده وفقًا لما هو محدد في ملف الإعدادات settings.json (مثل Tab أو Enter). في وضع النسخ المباشر يتم لصق النص كما هو.")

    settings_layout.addWidget(description_label)

   

    self.mode_combo_box = QComboBox()

    self.mode_combo_box.addItems(["وضع الفك (Demux)", "وضع النسخ المباشر (Direct Copy)"])

    mode_layout = QHBoxLayout()

    mode_layout.addWidget(QLabel("اختر وضع التشغيل:"))

    mode_layout.addWidget(self.mode_combo_box)

    settings_layout.addLayout(mode_layout)

   

    fields_group_box = QGroupBox("ترتيب الحقول")

    fields_layout = QGridLayout()

   

    self.field_labels = [

      "الحقل 1:", "الحقل 2:", "الحقل 3:", "الحقل 4:", "الحقل 5:", "الحقل 6:", "الحقل 7:",

    ]

    self.field_combo_boxes = []

    self.separator_inputs = []



    for i, label_text in enumerate(self.field_labels):

      field_label = QLabel(label_text)

      fields_layout.addWidget(field_label, i, 0)



      combo_box = QComboBox()

      combo_box.addItems(["", "الاسم الأول", "الاسم الأخير", "اسم الأب", "اسم الأم", "مكان الميلاد", "تاريخ الميلاد", "الرقم الوطني"])

      self.field_combo_boxes.append(combo_box)

      fields_layout.addWidget(combo_box, i, 1)



      separator_input = QLineEdit()

      separator_input.setPlaceholderText("فاصل (مثال: Tab أو مسافة)")

      self.separator_inputs.append(separator_input)

      fields_layout.addWidget(separator_input, i, 2)

   

    fields_group_box.setLayout(fields_layout)

    settings_layout.addWidget(fields_group_box)

   

    button_layout = QHBoxLayout()

    self.toggle_listening_button = QPushButton("تفعيل الاستماع")

    self.toggle_listening_button.setStyleSheet("background-color: #28a745;")

    self.toggle_listening_button.clicked.connect(self.toggle_listening)

    button_layout.addWidget(self.toggle_listening_button)

   

    settings_layout.addLayout(button_layout)

    return settings_widget



  def create_about_tab(self):

    about_widget = QWidget()

    about_layout = QVBoxLayout(about_widget)

    about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

   

    title_label = QLabel("حول التطبيق")

    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")

    about_layout.addWidget(title_label)

   

    about_text = QLabel("""

      <p style='text-align: center; color: #555555; font-size: 14px;'>

      تم تطوير هذا التطبيق لمساعدة المستخدمين في أتمتة إفراغ البيانات من الباركود.

      يهدف التطبيق إلى توفير الوقت والجهد من خلال إدخال البيانات تلقائيًا في

      أي حقل نصي، مما يجعل العمليات اليومية أسهل وأسرع.

      </p>

      <br>

      <p style='text-align: center; color: #555555; font-size: 14px;'>

      جميع الحقوق محفوظة للمبرمج وشركة صادق حسن للتجارة

      <br>

      تم التطوير بواسطة د.عمر العثمان

      <br>

      Developed By: Dr.Omar Alothman

      </p>

    """)

    about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

    about_layout.addWidget(about_text)

   

    return about_widget



  def create_contact_tab(self):

    contact_widget = QWidget()

    contact_layout = QVBoxLayout(contact_widget)

    contact_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

   

    title_label = QLabel("التواصل")

    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")

    contact_layout.addWidget(title_label)

   

    contact_text = QLabel("""

      <p style='text-align: center; color: #555555; font-size: 14px;'>

      للدعم أو الاقتراحات يمكنك التواصل معنا عبر:

      </p>

      <p style='text-align: center; color: #555555; font-size: 14px;'>

      <b>البريد الإلكتروني:</b> omar.ghass95@gmail.com<br>

      </p>

    """)

    contact_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

    contact_layout.addWidget(contact_text)



    return contact_widget

 

  def update_serial_status(self, is_connected):

    if is_connected:

      self.serial_status_label.setText("حالة الجهاز: متصل")

      self.serial_status_label.setStyleSheet("background-color: #28a745; color: white;")

    else:

      self.serial_status_label.setText("حالة الجهاز: غير متصل")

      self.serial_status_label.setStyleSheet("background-color: #dc3545; color: white;")



  def toggle_listening(self):

    if not self.is_listening:

      selected_port = self.available_ports_combo.currentText()

      if not selected_port or selected_port == "لا يوجد منافذ COM متاحة":

        self.show_error_message("يرجى توصيل جهاز الباركود أو تحديث المنافذ.")

        return



      self.is_listening = True

      self.toggle_listening_button.setStyleSheet("background-color: #dc3545;")

      self.toggle_listening_button.setText("تعطيل الاستماع")

     

      self.serial_thread = SerialReader(selected_port, self.serial_communicator)

      self.serial_thread.start()

     

      self.save_settings()

    else:

      self.is_listening = False

      self.toggle_listening_button.setStyleSheet("background-color: #28a745;")

      self.toggle_listening_button.setText("تفعيل الاستماع")

     

      if self.serial_thread and self.serial_thread.isRunning():

        self.serial_thread.stop()

        self.serial_thread = None



  def handle_barcode_data(self, data):

    if self.mode_combo_box.currentText() == "وضع النسخ المباشر (Direct Copy)":

      self.direct_paste(data)

    else:

      self.demux_paste(data)

 

  def demux_paste(self, data):
        # لصق الحقل السادس فقط من البيانات المفصولة بـ # وتطبيق الفاصل من settings.json
        try:
            data_parts = data.split('#')
            # التأكد من أن عدد الحقول يتطابق
            if len(data_parts) < 6:
                self.show_error_message(f"تنسيق البيانات غير صحيح. يجب أن يحتوي النص على 6 حقول على الأقل مفصولة بـ #. البيانات المستلمة: {data}")
                return

            value_to_paste = data_parts[5]
            sep_char = ""
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    settings_data = json.load(f)
                if isinstance(settings_data, dict):
                    fields = settings_data.get("fields", [])
                    if len(fields) >= 6:
                        raw_sep = str(fields[5].get("separator", "")).strip().lower()
                        if raw_sep == "tab":
                            sep_char = "\t"
                        elif raw_sep == "enter":
                            sep_char = "\n"
                        else:
                            sep_char = fields[5].get("separator", "")
            except Exception:
                sep_char = ""

            full_string = f"{value_to_paste}{sep_char}"
            if not value_to_paste.strip():
                self.comm.paste_warning.emit()
                return

            try:
                pyperclip.copy(full_string)
                time.sleep(0.5)
                keyboard.send('ctrl+v')
            except Exception as e:
                self.comm.paste_error.emit(f"حدث خطأ أثناء عملية اللصق: {e}")
        except Exception as e:
            self.show_error_message(f"حدث خطأ غير متوقع أثناء فك التشفير: {e}")



  def direct_paste(self, data):

    try:

      pyperclip.copy(data)

      time.sleep(0.5)

      keyboard.send('ctrl+v')

    except Exception as e:

      self.comm.paste_error.emit(f"حدث خطأ أثناء عملية اللصق: {e}")

     

  def show_warning_message(self):

    QMessageBox.warning(self, "خطأ", "لم يتم اختيار أي حقل للإفراغ.")



  def show_error_message(self, message):

    QMessageBox.critical(self, "خطأ", message)



  def save_settings(self):

    settings = []

    for i in range(len(self.field_combo_boxes)):

      field_name = self.field_combo_boxes[i].currentText()

      separator = self.separator_inputs[i].text()

      settings.append({"field": field_name, "separator": separator})

   

    settings_data = {

      "fields": settings,

      "mode": self.mode_combo_box.currentText()

    }



    try:

      with open(self.settings_file, "w", encoding="utf-8") as f:

        json.dump(settings_data, f, ensure_ascii=False, indent=4)

    except IOError as e:

      self.comm.paste_error.emit(f"حدث خطأ في حفظ الإعدادات: {e}")



  def load_settings(self):

    if os.path.exists(self.settings_file):

      try:

        with open(self.settings_file, "r", encoding="utf-8") as f:

          settings_data = json.load(f)

       

        if isinstance(settings_data, dict):

          settings = settings_data.get("fields", [])

          for i, setting in enumerate(settings):

            if i < len(self.field_combo_boxes):

              self.field_combo_boxes[i].setCurrentText(setting["field"])

              self.separator_inputs[i].setText(setting["separator"])

         

          mode = settings_data.get("mode", "وضع الفك (Demux)")

          self.mode_combo_box.setCurrentText(mode)

         

          # سطر جديد للتأكد من وضع التشغيل

          print(f"تم تحميل وضع التشغيل: {self.mode_combo_box.currentText()}")

        else:

          self.save_settings()

      except (IOError, json.JSONDecodeError) as e:

        self.comm.paste_error.emit(f"حدث خطأ في تحميل الإعدادات: {e}")

        self.save_settings()

    else:

      self.save_settings()



if __name__ == "__main__":

  app = QApplication(sys.argv)

  window = BarcodeFillerApp()

  window.show()

  sys.exit(app.exec())