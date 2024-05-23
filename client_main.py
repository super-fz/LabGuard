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
import client_side_monitoring

class AntiCheatingAppClient(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_login_page()

    def create_login_page(self):
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        welcome_label1 = Label(text="Welcome to LabGuard!\n", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        space_label1=Label(text="\n")
        space_label2=Label(text="\n")
        welcome_label2 = Label(text="Please enter your username and password", font_name="Roboto", font_size=16, pos_hint={'x': 0.025})
        welcome_label3 = Label(text="to login as examinee.", font_name="Roboto", font_size=16, pos_hint={'x': 0.025})
        left_layout.add_widget(welcome_label1)
        left_layout.add_widget(space_label1)
        left_layout.add_widget(space_label2)
        left_layout.add_widget(welcome_label2)
        left_layout.add_widget(welcome_label3)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.03}))
        
        username_label = Label(text="Username:", font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        self.username_entry = TextInput(font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        right_layout.add_widget(username_label)
        right_layout.add_widget(self.username_entry)

        password_label = Label(text="Password:", font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        self.password_entry = TextInput(password=True, font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        right_layout.add_widget(password_label)
        right_layout.add_widget(self.password_entry)

        login_button = Button(text="Login", font_name="Roboto", font_size=16, pos_hint={'x': 0.07})
        login_button.bind(on_press=self.verify_credentials)
        right_layout.add_widget(login_button)
        
        self.add_widget(left_layout)
        self.add_widget(right_layout)

    def go_to_login_page(self, instance):
        self.clear_widgets()
        self.create_login_page()

    def verify_credentials(self, instance):
        global username_client
        global password_client
        username_client = self.username_entry.text
        password_client = self.password_entry.text
        # Check if the username and password combination is correct
        # Connect to the database
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        # Retrieve the username and password from the database
        cursor.execute("SELECT username, password FROM students WHERE username = ? AND password = ?", (username_client, password_client))
        result = cursor.fetchone()

        if result is not None:
            self.go_to_session_page()
        else:
            warning_label = Label(text="Incorrect username or password", color=(1, 0, 0, 1))
            if not hasattr(self, 'warning_label'):
                right_layout = BoxLayout(orientation='horizontal', spacing=10, padding=[10, 50, 50, 50])
                right_layout.add_widget(warning_label)
                self.add_widget(right_layout)

        # Close the database connection
        conn.close()

    def checkNotEmpty(self, instance=None):
        if self.session_id_client.text:
            threading.Thread(target=self.request_connection, args=(self.session_id_client.text,)).start()
            self.go_to_proctoring_page()
        else:
            error_label = Label(text="The text field cannot be empty. Please enter a session ID.", color=(1, 0, 0, 1))
            if not hasattr(self, 'error_label'):
                right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
                self.error_label = error_label
                right_layout.add_widget(self.error_label)
                self.add_widget(right_layout)


    def go_to_session_page(self, instance=None):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)
        
        session_id_label1 = Label(text="Welcome, student1\n", font_name="Roboto", font_size=25, pos_hint={'x': 0.025})
        space_label = Label(text="\n")
        session_id_label2 = Label(text = "To enter an exam session,", font_name="Roboto", pos_hint={'x': 0.025})
        session_id_label3 = Label(text="please enter a session ID,", font_name="Roboto", pos_hint={'x': 0.025})
        session_id_label4 = Label(text='and click on "Enter Exam Session".', font_name="Roboto", pos_hint={'x': 0.065})
        session_id_label5 = Label(text="Enter a session ID here:", font_name="Roboto", pos_hint={'x': 0.07})
        self.session_id_client = TextInput(font_name="Roboto", pos_hint={'x': 0.07})
        start_session_button = Button(text="Enter Exam Session", font_name="Roboto", pos_hint={'x': 0.07})
        left_layout.add_widget(session_id_label1)
        left_layout.add_widget(space_label)
        left_layout.add_widget(session_id_label2)
        left_layout.add_widget(session_id_label3)
        left_layout.add_widget(session_id_label4)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.03}))
        right_layout.add_widget(session_id_label5)
        right_layout.add_widget(self.session_id_client)
        right_layout.add_widget(start_session_button)
        global session_id_client
        session_id_client = self.session_id_client.text

        start_session_button.bind(on_press=lambda instance: self.checkNotEmpty(self.session_id_client.text))


        back_button = Button(text="Back", font_name="Roboto", pos_hint={'x': 0.07})
        back_button.bind(on_press=self.go_to_login_page)
        right_layout.add_widget(back_button)
        self.add_widget(left_layout)
        self.add_widget(right_layout)

    def go_to_proctoring_page(self, instance=None):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)

        session_label = Label(text="Session ID: " + self.session_id_client.text + "\n" + "\n", font_name="Roboto", font_size=16,  pos_hint={'x': 0.03})
        left_layout.add_widget(session_label)

        waiting_label1 = Label(text="Please wait for your examiner to\n", font_name="Roboto", font_size=17,  pos_hint={'x': 0.03}) 
        waiting_label2 = Label(text="inform you about the starting\n", font_name="Roboto", font_size=17,  pos_hint={'x': 0.03})
        waiting_label3 = Label(text="of the proctoring session.\n", font_name="Roboto", font_size=17,  pos_hint={'x': 0.03})
        waiting_label4 = Label(text="In the meanwhile, kindly read the guidelines.", font_name="Roboto", font_size=14,  pos_hint={'x': 0.03})
        left_layout.add_widget(waiting_label1)
        left_layout.add_widget(waiting_label2)
        left_layout.add_widget(waiting_label3)
        left_layout.add_widget(waiting_label4)
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.03}))
        guideline_label = Label(text="[b][u]Guidelines:[/u][/b]", font_name="Roboto", pos_hint={'x': 0.07}, markup=True)
        guideline_zero_label1 = Label(text="Once the proctoring session starts,", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_zero_label2 = Label(text="the program will start capturing the following:\n", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_one_label = Label(text="- Application/Window switching", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_two_label = Label(text="- Number of keystrokes used to type the answer", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_three_label = Label(text="- Whether you used the copy command\n"  + "\n", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_four_label = Label(text="Therefore, under proctoring conditions:\n", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_five_label = Label(text="- Do NOT switch between windows or apps", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_six_label1 = Label(text="- Do NOT copy and paste materials from any other resources,", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_six_label2 = Label(text="UNLESS otherwise allowed by your examiner\n", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_seven_label1 = Label(text="The above captured information will be used by your", font_name="Roboto", pos_hint={'x': 0.07})
        guideline_seven_label2 = Label(text="examiner to determine any cases of using unfair means", font_name="Roboto", pos_hint={'x': 0.07})
        
        right_layout.add_widget(guideline_label)
        right_layout.add_widget(guideline_zero_label1)
        right_layout.add_widget(guideline_zero_label2)
        right_layout.add_widget(guideline_one_label)
        right_layout.add_widget(guideline_two_label)
        right_layout.add_widget(guideline_three_label)
        right_layout.add_widget(guideline_four_label)
        right_layout.add_widget(guideline_five_label)
        right_layout.add_widget(guideline_six_label1)
        right_layout.add_widget(guideline_six_label2)
        right_layout.add_widget(guideline_seven_label1)
        right_layout.add_widget(guideline_seven_label2)


        back_button = Button(text="Back", font_name="Roboto", pos_hint={'x': 0.07})
        back_button.bind(on_press=self.go_to_session_page)
        right_layout.add_widget(back_button)
        
        self.add_widget(left_layout)
        self.add_widget(right_layout)

    def go_to_started_proctoring_page(self, instance):
        self.clear_widgets()
        
        left_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=300)
        right_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 50, 50, 50])
        left_layout.add_widget(Image(source='LabGuard Final Logo.png', size_hint=(None, None), size=(300, 300), pos_hint={'top': 0.2, 'left': 20.0}))
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            Line(points=[left_layout.width + 35, left_layout.y, left_layout.width + 35, left_layout.y + left_layout.height + 600], width=0.5)


        session_label = Label(text="Session ID: " + self.session_id_entry.text)
        left_layout.add_widget(session_label)

        proctoring_label1 = Label(text="Proctoring in progress...", font_name="Roboto", font_size=17,  pos_hint={'x': 0.03})
        left_layout.add_widget(Image(source='AU White Logo Final.png', size_hint=(None, None), size=(175, 175), pos_hint={'center_y': -20.0, 'x': 0.03}))
        proctoring_label2 = Label(text="You are now being proctored.", font_name="Roboto", pos_hint={'x': 0.07})
        proctoring_label3 = Label(text="Please minimize this window and start your exam.", font_name="Roboto", pos_hint={'x': 0.07})
        proctoring_label4 = Label(text="Do not switch apps, or copy any content during this time.", font_name="Roboto", pos_hint={'x': 0.07})
        
        left_layout.add_widget(proctoring_label1)
        right_layout.add_widget(proctoring_label2)
        right_layout.add_widget(proctoring_label3)
        right_layout.add_widget(proctoring_label4)
        
        self.add_widget(left_layout)
        self.add_widget(right_layout)

    def receive_messages(self, s, instance=None):
        my_instance = client_side_monitoring.KeyLoggerApp()
        while True:
            data = s.recv(1024).decode()
            if not data:
                print("Disconnected from server")
            else:
                print('Received:', data)
            try:
                if data == "START_PROCTORING":
                    print("Monitoring has begun")
                    my_instance.start_monitoring(my_instance)
                if data == "STOP_PROCTORING":
                    my_instance.stop_monitoring(my_instance)
            except FileNotFoundError:
                print("Error: file not found")

    def request_connection(self, session_id_client):
        print("status:")
        print("Session ID: " + session_id_client)
        
        host = '192.168.0.171'  # The server's hostname or IP address
        port = 5050
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(str(session_id_client).encode())
            response = s.recv(1024).decode()
            if response == "Session ID verified":
                print("Session accepted the connection.")
                print("Connected to the server. Waiting for messages.")

                threading.Thread(target=self.receive_messages, args=(s,), daemon=True).start()

                while True:
                    message = input()
                    if message.lower() == 'quit':
                        break
                    s.sendall(message.encode())
            else:
                print(response)
    
class LabGuard_client(App):
    def build(self):
        return AntiCheatingAppClient()
    
if __name__ == "__main__":
    LabGuard_client().run()