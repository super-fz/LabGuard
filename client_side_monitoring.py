import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import threading
from pynput.keyboard import Listener as KeyboardListener
import ctypes
from ctypes.wintypes import HWND, DWORD, WPARAM, LPARAM, MSG
import time
import win32clipboard
import pyautogui
LONG = ctypes.c_long





def setup_database():
    conn = sqlite3.connect('activity_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  start_time DATETIME,
                  end_time DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  event_type TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  detail TEXT,
                  FOREIGN KEY (session_id) REFERENCES sessions(session_id))''')
    conn.commit()
    conn.close()

def log_event(session_id, event_type, detail):
    conn = sqlite3.connect('activity_log.db')
    c = conn.cursor()
    c.execute("INSERT INTO activity_log (session_id, event_type, detail) VALUES (?, ?, ?)", (session_id, event_type, detail))
    conn.commit()
    conn.close()

def start_monitoring_session():
    conn = sqlite3.connect('activity_log.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (start_time) VALUES (datetime('now'))")
    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id

def stop_monitoring_session(session_id):
    conn = sqlite3.connect('activity_log.db')
    c = conn.cursor()
    c.execute("UPDATE sessions SET end_time = datetime('now') WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


class WindowFocusMonitor:
    def __init__(self, session_id):
        self.session_id = session_id
        self.hook = None
        self.callback = None
        self.user32 = ctypes.windll.user32
        self.ole32 = ctypes.windll.ole32
        self.WIN_EVENT_PROC_TYPE = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, DWORD, HWND, DWORD, DWORD, DWORD, DWORD)
        self.EVENT_SYSTEM_FOREGROUND = 0x0003
        self.WINEVENT_OUTOFCONTEXT = 0x0000

    def win_event_proc(self):
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            if event == self.EVENT_SYSTEM_FOREGROUND:
                length = self.user32.GetWindowTextLengthW(hwnd) + 1
                if length > 1:  # Check if there is a window title
                    buffer = ctypes.create_unicode_buffer(length)
                    self.user32.GetWindowTextW(hwnd, buffer, length)
                    window_title = buffer.value.strip()  # Trim any leading/trailing whitespace
                    if window_title:  # Log only if window title is not empty
                        log_event(self.session_id, 'window_focus', window_title)
        return callback

    def start_monitoring(self):
        self.ole32.CoInitialize(0)
        self.callback = self.WIN_EVENT_PROC_TYPE(self.win_event_proc())
        self.hook = self.user32.SetWinEventHook(
            self.EVENT_SYSTEM_FOREGROUND,
            self.EVENT_SYSTEM_FOREGROUND,
            0,
            self.callback,
            0,
            0,
            self.WINEVENT_OUTOFCONTEXT
        )
        if not self.hook:
            print("Failed to set hook")
            return None
        print("Window focus monitoring started...")

    def stop_monitoring(self):
        if self.hook:
            self.user32.UnhookWinEvent(self.hook)
            self.hook = None
        self.ole32.CoUninitialize()
        print("Window focus monitoring stopped...")
        
class ClipboardMonitor(threading.Thread):
    def __init__(self, session_id):
        super().__init__(daemon=True)
        self.session_id = session_id
        self.previous_text = ""
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                    text = win32clipboard.GetClipboardData()
                    if text != self.previous_text:
                        window_title = pyautogui.getActiveWindowTitle()
                        # Updated to log the window title instead of the copied text
                        log_event(self.session_id, 'clipboard', f"Copy action detected from window: {window_title}")
                        self.previous_text = text
            finally:
                win32clipboard.CloseClipboard()
            time.sleep(1)

    def stop(self):
        self.running = False

class KeyLogger:
    def __init__(self, session_id):
        self.session_id = session_id
        self.count = 0
        self.running = False
        self.listener = None

    def on_press(self, key):
        if self.running:
            self.count += 1

    def start(self):
        self.running = True
        if not self.listener:
            self.listener = KeyboardListener(on_press=self.on_press)
            self.listener.start()

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            log_event(self.session_id, 'keystroke', str(self.count))
            self.count = 0

class SessionLogViewer(Popup):
    def __init__(self, session_id, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Logs for Session {session_id}"
        self.size_hint = (None, None)
        self.size = (1024, 600)

        # Layout to hold everything
        layout = BoxLayout(orientation='vertical', padding=10)

        # Header
        header_layout = GridLayout(cols=3, size_hint_y=None, height=30, spacing=10)
        header_layout.add_widget(Label(text='Timestamp', size_hint_x=None, width=200))
        header_layout.add_widget(Label(text='Event Type', size_hint_x=None, width=200))
        header_layout.add_widget(Label(text='Detail', size_hint_x=None, width=600))
        layout.add_widget(header_layout)

        # ScrollView allows us to scroll through the log entries if they exceed the viewable area
        scroll_view = ScrollView(size_hint=(1, 1), bar_width=10)
        log_layout = GridLayout(cols=3, size_hint_y=None, spacing=10)
        log_layout.bind(minimum_height=log_layout.setter('height'))

        # Fetch records from the database
        conn = sqlite3.connect('activity_log.db')
        c = conn.cursor()
        c.execute("SELECT timestamp, event_type, detail FROM activity_log WHERE session_id=? ORDER BY timestamp", (session_id,))
        records = c.fetchall()
        conn.close()

        # Populate the log entries
        for record in records:
            timestamp, event_type, detail = record
            log_layout.add_widget(Label(text=str(timestamp), size_hint_y=None, height=30, size_hint_x=None, width=200))
            log_layout.add_widget(Label(text=str(event_type), size_hint_y=None, height=30, size_hint_x=None, width=200))
            # Detail label with bound width for text wrapping
            detail_label = Label(text=str(detail), size_hint_y=None, height=30, size_hint_x=None, width=600, halign='left', valign='middle', text_size=(600, None))
            detail_label.bind(size=detail_label.setter('text_size'))
            log_layout.add_widget(detail_label)

        log_layout.height = 30 * len(records)  # Set the height based on the number of records
        scroll_view.add_widget(log_layout)
        layout.add_widget(scroll_view)

        self.add_widget(layout)


class LogSessionSelector(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Select Session to View"
        self.size_hint = (0.5, 0.5)

        layout = BoxLayout(orientation='vertical')

        conn = sqlite3.connect('activity_log.db')
        c = conn.cursor()
        c.execute("SELECT session_id, start_time, end_time FROM sessions ORDER BY session_id DESC")
        sessions = c.fetchall()

        for session in sessions:
            session_id, start_time, end_time = session
            btn = Button(text=f"Session {session_id}: {start_time} to {end_time if end_time else 'Now'}")
            btn.bind(on_press=lambda instance, sid=session_id: self.show_session_logs(sid))
            layout.add_widget(btn)

        self.add_widget(layout)

    def show_session_logs(self, session_id, *args):
        session_log_viewer = SessionLogViewer(session_id=session_id)
        session_log_viewer.open()

class KeyLoggerApp(App):
    def build(self):
        self.session_id = None
        layout = BoxLayout(orientation='vertical')
        start_button = Button(text='Start Monitoring')
        stop_button = Button(text='Stop Monitoring')
        show_button = Button(text='Show Records')

        start_button.bind(on_press=self.start_monitoring)
        stop_button.bind(on_press=self.stop_monitoring)
        show_button.bind(on_press=lambda instance: LogSessionSelector().open())

        layout.add_widget(start_button)
        layout.add_widget(stop_button)
        layout.add_widget(show_button)

        return layout

    def start_monitoring(self, instance):
        self.session_id = start_monitoring_session()
        self.clipboard_monitor = ClipboardMonitor(self.session_id)
        self.clipboard_monitor.start()
        self.key_logger = KeyLogger(self.session_id)
        self.key_logger.start()
        self.window_monitor = WindowFocusMonitor(self.session_id)
        self.window_monitor.start_monitoring()
        print("Monitoring started...")

    def stop_monitoring(self, instance):
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
        if self.key_logger:
            self.key_logger.stop()
        if self.window_monitor:
            self.window_monitor.stop_monitoring()
        if self.session_id:
            stop_monitoring_session(self.session_id)
        print("Monitoring stopped...")

if __name__ == '__main__':
    setup_database()
    KeyLoggerApp().run()

if __name__ == '__main__':
    setup_database()
    KeyLoggerApp().run()
