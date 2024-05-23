from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from kivy.uix.image import Image
import sqlite3
import threading
import socket
import os
import subprocess
import queue
import tkinter as tk
import client_side_monitoring

global session_id_server

class AntiCheatingAppServer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_login_page()

    def create_login_page(self):
        BoxLayout(orientation='horizontal', padding=10, spacing=10)
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 30.0}))
        left_layout.add_widget(Label(text="Welcome to LabGuard!\n", font_name="Roboto", font_size=25, pos_hint={'x': 0.025}))
        left_layout.add_widget(Label(text="\n", font_name="Roboto", font_size=20))
        left_layout.add_widget(Label(text="\n", font_name="Roboto", font_size=20))
        left_layout.add_widget(Label(text="Please enter your username and password\n", font_name="Roboto", font_size=16, pos_hint={'x': 0.03}))
        left_layout.add_widget(Label(text="to login as examiner.", font_name="Roboto", font_size=16, pos_hint={'x': 0.03}))
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.03}))
        self.add_widget(left_layout)

        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        
        # Adding widgets to the right layout
        self.username_entry = TextInput(multiline=False, font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        right_layout.add_widget(Label(text="Username:", font_name="Roboto", font_size=16, pos_hint={'x': 0.07}))
        right_layout.add_widget(self.username_entry)
        self.password_entry = TextInput(password=True, multiline=False, font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        right_layout.add_widget(Label(text="Password:", font_name="Roboto", font_size=16, pos_hint={'x': 0.07}))
        right_layout.add_widget(self.password_entry)
        login_button = Button(text="LOGIN", font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        login_button.bind(on_press=self.verify_credentials)
        right_layout.add_widget(login_button)
        self.add_widget(right_layout)

    def verify_credentials(self, instance):
        global username_server
        global password_server
        username_server = self.username_entry.text
        password_server = self.password_entry.text
        # Check if the username and password combination is correct
        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Retrieve the username and password from the database
        cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username_server, password_server))
        result = cursor.fetchone()

        if result is not None:
            self.go_to_session_page()
        else:
            warning_label = Label(text="Incorrect username or password", color=(1, 0, 0, 1), font_name="Roboto", pos_hint={'x': 0.07})
            if not hasattr(self, 'warning_label'):
                right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
                right_layout.add_widget(warning_label)
                self.add_widget(right_layout)

        # Close the database connection
        conn.close()
    
    def checkNotEmpty(self, instance=None):
        if self.session_id_server.text:
            global session_id_server
            threading.Thread(target=self.server).start()
            self.go_to_proctoring_page()
        else:
            error_label = Label(text="The text field cannot be empty. Please enter a session ID.", color=(1, 0, 0, 1))
            if not hasattr(self, 'error_label'):
                right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
                self.error_label = error_label
                right_layout.add_widget(error_label)
                self.add_widget(right_layout)

    def go_to_session_page(self, instance=None):
        self.clear_widgets()
        BoxLayout(orientation='horizontal', padding=10, spacing=10)
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        
        
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        session_id_label1 = Label(text="Welcome, admin.\n", font_name="Roboto", pos_hint={'x': 0.055})
        session_id_label2 = Label(text="To start an exam session,", font_name="Roboto", pos_hint={'x': 0.06})
        session_id_label3= Label(text="please enter a session ID and click on", font_name="Roboto", pos_hint={'x': 0.06})
        session_id_label4 = Label(text='"Start Session". You can also view records of', font_name="Roboto", pos_hint={'x': 0.06})
        session_id_label5 = Label(text="past sessions from here.", font_name="Roboto", pos_hint={'x': 0.06})
        session_id_label6 = Label(text="Enter a session ID here:", font_name="Roboto", pos_hint={'x': 0.06})
        global session_id_server
        self.session_id_server = TextInput(pos_hint={'x': 0.07})
        start_session_button = Button(text="Start Session", pos_hint={'x': 0.07})
        
        left_layout.add_widget(session_id_label1)
        left_layout.add_widget(session_id_label2)
        left_layout.add_widget(session_id_label3)
        left_layout.add_widget(session_id_label4)
        left_layout.add_widget(session_id_label5)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.025}))
        right_layout.add_widget(session_id_label6)
        right_layout.add_widget(self.session_id_server)
        right_layout.add_widget(start_session_button)

        start_session_button.bind(on_press=self.checkNotEmpty)

        self.add_widget(left_layout)
        self.add_widget(right_layout)

        view_records_button = Button(text="View Past Records", pos_hint={'x': 0.07})
        database_instance = client_side_monitoring.LogSessionSelector()
        view_records_button.bind(on_press=lambda instance: database_instance.open())
        right_layout.add_widget(view_records_button)

        back_button = Button(text="Back", pos_hint={'x': 0.07})
        back_button.bind(on_press=self.go_to_login_page)
        right_layout.add_widget(back_button)

    def go_to_proctoring_page(self, instance=None):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
            
        session_label = Label(text="Session ID: " + self.session_id_server.text, font_name="Roboto", font_size=20, pos_hint={'x': 0.07})
        right_layout.add_widget(session_label)

        waiting_label1 = Label(text="Waiting for", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        waiting_label2 = Label(text="students to connect...", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        left_layout.add_widget(waiting_label1)
        left_layout.add_widget(waiting_label2)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.025}))

        start_proctoring_button = Button(text="Start Proctoring", font_name="Roboto", pos_hint={'x': 0.07})
        
        
        start_proctoring_button.bind(on_press=self.go_to_proctoring_in_progress_page)
        start_proctoring_button.bind(on_release=lambda instance: self.send_start_message(message_queue, conn, "START_PROCTORING"))
        
        right_layout.add_widget(start_proctoring_button)

        back_button = Button(text="Back", font_name="Roboto", pos_hint={'x': 0.07})
        back_button.bind(on_press=self.go_to_session_page)
        right_layout.add_widget(back_button)
        self.add_widget(left_layout)
        self.add_widget(right_layout)
        
        global server_session_id
        server_session_id = self.session_id_server.text

    def go_to_proctoring_in_progress_page(self, instance=None):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        session_label = Label(text="Session ID: " + self.session_id_server.text, font_size=20, pos_hint={'x': 0.07})
        right_layout.add_widget(session_label)
        
        progress_label1 = Label(text="Proctoring", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        progress_label2 = Label(text="in progress...", font_name="Roboto", font_size=25, pos_hint={'x': 0.03})
        left_layout.add_widget(progress_label1)
        left_layout.add_widget(progress_label2)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.025}))
        
        show_connections_button = Button(text="Show Connected Users", font_name="Roboto", pos_hint={'x': 0.075})
        show_connections_button.bind(on_press=lambda instance: self.prompt_to_show_connected_users())
        right_layout.add_widget(show_connections_button)
        
        stop_proctoring_button = Button(text="Stop Proctoring", font_name="Roboto", pos_hint={'x': 0.075})
        stop_proctoring_button.bind(on_press=self.go_to_end_of_proctoring_page)
        stop_proctoring_button.bind(on_release=lambda instance: self.send_stop_message(message_queue, conn, "STOP_PROCTORING"))
        right_layout.add_widget(stop_proctoring_button)
        
        self.add_widget(left_layout)
        self.add_widget(right_layout)

    def go_to_end_of_proctoring_page(self, instance=None):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        end_label1 = Label(text=" The proctoring session", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        end_label2 = Label(text="with ID " + self.session_id_server.text, font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        end_label3 = Label(text="has ended.", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        left_layout.add_widget(end_label1)
        left_layout.add_widget(end_label2)
        left_layout.add_widget(end_label3)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.025}))
        
        end_message=Label(text="Click below to view records"+"\n"+"for proctoring sessions.", font_name="Roboto", font_size=20, pos_hint={'x': 0.07})
        
        right_layout.add_widget(end_message)
        view_records_button = Button(text="View Proctoring Records", font_name="Roboto", pos_hint={'x': 0.07})
        database_instance = client_side_monitoring.LogSessionSelector()
        view_records_button.bind(on_press=lambda instance: database_instance.open())
        right_layout.add_widget(view_records_button)
        self.add_widget(left_layout)
        self.add_widget(right_layout)


    def go_to_records_page(self, instance):
        self.clear_widgets()

        records_label = Label(text="Past Exam Records")
        self.add_widget(records_label)

        back_button = Button(text="Back")
        back_button.bind(on_press=self.go_to_session_page)
        self.add_widget(back_button)

    def go_to_login_page(self, instance):
        self.clear_widgets()
        self.create_login_page()

    def start_proctoring(self, instance):
        print("Proctoring started")
    
    def show_active_connections(self, active_connections):
        root = tk.Tk()
        root.title("Active Connections")

        listbox = tk.Listbox(root, width=50, height=15)
        listbox.pack(padx=10, pady=10)

        for _, addr in active_connections:
            listbox.insert(tk.END, f"'student1'{addr}")

        root.mainloop()
    
    def send_message(self, message_queue, active_connections, conn, message=None):
        if message is None:
            while True:
                message = input("Enter message to send to the clients or 'list' to see active connections: ")
                if message.lower() == 'list':
                    self.show_active_connections(active_connections)
                message_queue.put(message)
                conn.sendall(message.encode())
                

    def handle_client(self, conn, addr, message_queue, active_connections):
        with conn:
            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    print(f"Received from {addr}: {data}")
                except BlockingIOError:
                    continue
            print(f"Connection from {addr} closed")
            active_connections.remove((conn, addr))

    def accept_connections(self, conn, addr, s, message_queue, active_connections, server_session_id):
        print(f"Checking session ID from {addr}")
        session_id_client = conn.recv(1024).decode()
        print(session_id_client)
        if session_id_client != server_session_id:
            conn.sendall("Session ID mismatch".encode())
            conn.close()
            return
        else:
            conn.sendall("Session ID verified".encode())
            while True:
                try:
                    conn.setblocking(False)
                    active_connections.append((conn, addr)) 
                    print(f"Connected by {addr}")
                    threading.Thread(target=self.handle_client, args=(conn, addr, message_queue, active_connections), daemon=True).start()
                    self.send_message(message_queue, active_connections, conn)
                except BlockingIOError:
                    continue

    def server(self):
        host = '192.168.0.171'
        port = 5050
        global message_queue
        message_queue = queue.Queue()
        global active_connections
        active_connections = []

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print("Server listening...")
            global conn
            global addr
            conn, addr = s.accept()
            threading.Thread(target=self.accept_connections, args=(conn, addr, s, message_queue, active_connections, server_session_id), daemon=True).start()

    def prompt_to_show_connected_users(self):
        self.show_active_connections(active_connections)

    def send_start_message(self, message_queue, conn, message="START_PROCTORING", instance=None):
        message_queue.put(message)
        conn.sendall(message.encode())

    def send_stop_message(self, message_queue, conn, message="STOP_PROCTORING", instance=None):
        message_queue.put(message)
        conn.sendall(message.encode())

class LabGuard_server(App):
    def build(self):
        return AntiCheatingAppServer()

if __name__ == "__main__":
    LabGuard_server().run()