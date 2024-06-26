import rsa
import datetime
import customtkinter as CTk
from PIL import Image
import json
import socket
import os
import hashlib
import viginere
import time
import threading

global login_check
login_check = False

global ping_ans
ping_ans = ""

global name_text_dict
name_text_dict = {}

global logn
logn = ""

global lets_ping
lets_ping = ""

global host
host="217.71.129.139"
global port
port=4258

global oldlen
oldlen = 0

def sha256(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode('utf-8'))
    return sha256_hash.hexdigest()

def key_gen(parameter):
    global logn
    if os.path.exists(logn + '-keys' + '.json'):
        if parameter == 0:
            with open(logn + '-keys' + '.json', 'r') as file:
                (e, n), (d, n) = json.load(file)
            return (e, n), (d, n)
        elif parameter == 1:
            print("RSA process!")
            (e, n), (d, n) = rsa.generate_keypair()
            print("RSA done!")
            with open(logn + '-keys' + '.json', 'w', encoding='utf-8') as file:
                json.dump(((e, n), (d, n)), file, ensure_ascii=False, indent=4)
            return (e, n), (d, n)
    else:
        print("RSA process!")
        (e, n), (d, n) = rsa.generate_keypair()
        print("RSA done!")
        with open(logn + '-keys' + '.json', 'w', encoding='utf-8') as file:
            json.dump(((e, n), (d, n)), file, ensure_ascii=False, indent=4)
        return (e, n), (d, n)

def sort_messages():
    global name_text_dict
    for user, messages in name_text_dict.items():
        sorted_messages = sorted(messages.split('\n'), key=lambda x: x.split(' - ', 1)[0][-19:])
        sorted_dialog = ""
        for i in sorted_messages:
            if i != "":
                sorted_dialog += i + '\n'
        name_text_dict[user] = sorted_dialog

def remove_special_characters(input_string):
    special_characters = "~|+-`"
    output_string = ''.join(char for char in input_string if char not in special_characters)
    return output_string
    
    

def send_tcp_message(message):
    global host
    global port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print("Connection done!")
        s.sendall(message.encode())

        response = s.recv(1024).decode()
        print(f"Получен ответ от сервера: {response}")
        
        return response

class ServerRequestSender:
    def __init__(self):
        def send_server_request():
            CTk.set_appearance_mode("light")
            global ping_ans
            global logn
            global name_text_dict
            global host
            global port
            global userto
            while True:
                if logn != "" and lets_ping != "":
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            message = '~ping~ + ' + logn
                            s.connect((host, port))
                            print("Connection done!")
                            s.sendall(message.encode())
                            resp = s.recv(1024).decode()
                            if resp != "":
                                print(resp)
                                ans = resp.split('+')
                                _userto = ans[0]
                                message_text = ans[1].split(',')
                                mssage_convert = []
                                for i in message_text:
                                    if i != "":
                                        mssage_convert.append(int(i))

                                with open(logn + '-keys' + '.json', 'r') as file:
                                    loaded_dict = json.load(file)
                                    d, n = int(loaded_dict[1][0]), int(loaded_dict[1][1])

                                message_text = rsa.decrypt((d, n), mssage_convert)

                                if ans[0] != "":
                                    if _userto.lower() in name_text_dict.keys():
                                        st = name_text_dict.get(_userto)
                                        st += _userto.upper() + ' | ' + message_text
                                        name_text_dict[_userto.lower()] = st
                                    else:
                                        name_text_dict[_userto.lower()] = _userto.upper() + ' | ' + message_text

                                    if _userto == userto:
                                        app.addMessageIncome(_userto.upper() + ' | ' + message_text)
                                        app.chat_frame.after(100, app.chat_frame._parent_canvas.yview_moveto, 1.0)
                                
                                sort_messages()
                                

                        except Exception as e:
                            print(f"Error occurred: {e}")

                    time.sleep(2)

        request_thread = threading.Thread(target=send_server_request)
        request_thread.daemon = True
        request_thread.start()



class App(CTk.CTk):
    def __init__(self):
        super().__init__()
        print("Interface loaded!")

        global password
        password = ""

        global userto
        userto = ""

        self.server_request_sender = ServerRequestSender()

        self.geometry("1000x600")
        self.title("messenger")
        self.resizable(False, False)

        self.chat_frame = CTk.CTkScrollableFrame(master=self, width=630, height=490, fg_color="white")
        self.chat_frame.place(x=350, y=10)

        self.textbox = CTk.CTkEntry(master=self, width=590, height=30)
        self.textbox.place(x=350, y=520)
        self.textbox.bind("<Return>", lambda x: self.sendtext())
        
        self.sendbutton = CTk.CTkButton(master=self, width=30, height=30, fg_color="#5e00ff", text_color="white", text="send", command=self.sendtext)
        self.sendbutton.place(x=950, y=520)


        self.setbutton = CTk.CTkButton(master=self, width=40, height=30, fg_color="#5e00ff", text_color="white", text="settings")
        self.setbutton.place(x=10, y=10)

        self.newchat = CTk.CTkButton(master=self, width=30, height=30, fg_color="#5e00ff", text_color="white", text="+", command=self.new_user_add)
        self.newchat.place(x=80, y=10)

        self.chater_frame = CTk.CTkScrollableFrame(master=self, width=200, height=490, fg_color="white")
        self.chater_frame.place(x=10, y=50)

        self.ToplevelWindow()
    
    def sort_messages():
        global name_text_dict
        for user, messages in name_text_dict.items():
            sorted_messages = sorted(messages.split('\n'), key=lambda x: x.split(' - ', 1)[0][-19:])
            sorted_dialog = ""
            for i in sorted_messages:
                if i != "":
                    sorted_dialog += i + '\n'
            name_text_dict[user] = sorted_dialog
        #print(name_text_dict)
        
    def ToplevelWindow(self):
        new_window = CTk.CTkToplevel(self)
        new_window.geometry("400x300")
        new_window.title("Login")

        my_image = CTk.CTkImage(light_image=Image.open("7516814.png"),
                                dark_image=Image.open("7516814.png"),
                                size=(100, 100))
        new_window.label = CTk.CTkLabel(new_window, image=my_image, text="", )
        new_window.label.pack(padx=20, pady=20)


        def login():
            global login_check
            global logn
            global password
            global lets_ping
            logn = new_window.user.get()
            logn = logn.lower()
            password = new_window.password.get()
            password = password.lower()
            password = sha256(password)
            if login == "" or password == "":
                new_window.destroy()
                self.ToplevelWindow()

            (e, n), (d, n) = key_gen(0)
            openkey = str(e) + ":" + str(n)
            
            print("key`s generated!")

            resp = send_tcp_message(logn + "~" + password + "~" + openkey)

            if resp == "User created successfully" or resp == "Login successful":
                new_window.destroy()
                lets_ping = "1"
                self.load_data(logn)
                return
            elif resp == "Bad password":
                new_window.destroy()
                self.ToplevelWindow()

        new_window.user = CTk.CTkEntry(master=new_window, width=200, height=30)
        new_window.user.place(x=100, y=150)
        new_window.user.bind("<Return>", lambda x: login())

        new_window.password = CTk.CTkEntry(master=new_window, width=200, height=30)
        new_window.password.place(x=100, y=200)
        new_window.password.bind("<Return>", lambda x: login())
        
        new_window.login = CTk.CTkButton(master=new_window, width=50, height=30, fg_color="#5e00ff", text_color="white", text="register/login", command=login)
        new_window.login.place(x=150, y=250)

        new_window.user.focus()


    def send_To_Server(self, message):
        global userto
        global logn
        openkey = send_tcp_message(userto + '`' + ' ')
        keys = openkey.split(':')

        if keys[0] == 'bad_user':
            return
        
        message = rsa.encrypt((int(keys[0]), int(keys[1])), message)
        #print(message)
        mes = ""
        mes = ','.join(map(str, message))
        ifls = send_tcp_message(userto + '+' + logn + '+' + mes)
        if ifls:
            pass

    
    def sendtext(self):
        global userto
        global name_text_dict
        global password 
        message = self.textbox.get()
        message = remove_special_characters(message)
        current_time = str(datetime.datetime.now())[:-7]
        message_text = f"{current_time} - {message}\n"

        self.send_To_Server(message_text)

        if "|" in message:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message_text, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.W)
            message = self.textbox.delete(first_index=0, last_index=10000)
        else:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message_text, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.E)
            message = self.textbox.delete(first_index=0, last_index=10000)

        if userto.lower() in name_text_dict.keys():
            st = name_text_dict.get(userto)
            st += message_text
            name_text_dict[userto.lower()] = st
        else:
            name_text_dict[userto.lower()] = message_text


        sort_messages()
        self.chat_frame.after(100, self.chat_frame._parent_canvas.yview_moveto, 1.0)
        self.save_data()

    def addMessageIncome(self, message):
        if "|" in message:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.W)
        else:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.E)


    def text_add(self, message):
        if "|" in message:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.W)
            message = self.textbox.delete(first_index=0, last_index=10000)
        else:
            text_label = CTk.CTkLabel(master=self.chat_frame, text=message, justify=CTk.LEFT)
            text_label.pack(anchor=CTk.E)
            message = self.textbox.delete(first_index=0, last_index=10000)


    def new_user_add(self):
        global name_text_dict
        new_usr_window = CTk.CTkInputDialog(text="Type a usename", title="Test")
        username = new_usr_window.get_input()
        username = username.lower()
        if username not in name_text_dict.keys() and username != "":
            ifls = send_tcp_message(username.lower() + "`" + " ")
            if ifls != "bad_user":
                name_text_dict[username] = ""
                button = CTk.CTkButton(master=self.chater_frame, width=190, height=30, text=username.lower(), fg_color="#5e00ff", text_color="white", command=lambda: self.switch_dialog(username))
                button.pack()
                self.switch_dialog(username)
            else:
                new_usr_window.destroy()
                return


    def old_user_add(self, username):
        global name_text_dict
        name_text_dict[username] = ""
        button = CTk.CTkButton(master=self.chater_frame, width=190, height=30, text=username, fg_color="#5e00ff", text_color="white", command=lambda: self.switch_dialog(username))
        button.pack()
        self.switch_dialog(username)


    def switch_dialog(self, username):
        global name_text_dict
        global userto
        global oldlen
        userto = username
        oldlen = len(name_text_dict.get(userto))
        self.chat_frame.place_forget()

        print(f"{username} in {name_text_dict.keys()} == {username in name_text_dict.keys()}")
        if username in name_text_dict.keys() and name_text_dict.get(username) != "":
            #print("Trying to replace")
            self.chat_frame.place_forget()

            new_dialog_frame = CTk.CTkScrollableFrame(master=self, width=630, height=490, fg_color="white")
            new_dialog_frame.place(x=350, y=10)

            self.chat_frame = new_dialog_frame
            self.chat_frame.tkraise()
            self.chat_frame.place()

            self.chat_frame.after(300, self.chat_frame._parent_canvas.yview_moveto, 1.0)

            st = name_text_dict.get(username)
            st_arr = st.split("\n")
            for message in st_arr:
                self.text_add(message)
            #rint("DONE :)")
        else:
            new_dialog_frame = CTk.CTkScrollableFrame(master=self, width=630, height=490, fg_color="white")
            new_dialog_frame.place(x=350, y=10)
            self.chat_frame = new_dialog_frame
            self.chat_frame.tkraise()
            self.chat_frame.place()
            
            self.chat_frame.after(300, self.chat_frame._parent_canvas.yview_moveto, 1.0)

        print(f"user switched to: {username}")
        

    def save_data(self):
        global logn
        global name_text_dict
        global password
        for_save_dict = {}
        for i in name_text_dict.keys():
            x = name_text_dict.get(i)
            x = x.split('\n')
            st = ""
            for j in x:
                if j != '':
                    a = j.split('-')
                    a_enc = viginere.vig_encrypt(a[3], password)
                    st += a[0] + '-' + a[1] + '-' + a[2] + '-' + a_enc + "\n"
            for_save_dict[i] = st

        with open(str(logn)+'.json', 'w') as file:
            json.dump(for_save_dict, file, ensure_ascii=False, indent=4)


    def load_data(self, usr):
        global password
        global name_text_dict
        global old_user_add
        with open(str(usr)+'.json', 'r') as file:
            loaded_dict = json.load(file)
        for i in loaded_dict.keys():
            self.old_user_add(i)
            st = loaded_dict.get(i)
            st_old = st.split("\n")
            for j in st_old:
                a = j.split('-')
                if len(a) >= 2:
                    a_dec = viginere.vig_decrypt(a[3], password)
                    mes = a[0] + '-' + a[1] + '-' + a[2] + '-' + a_dec
                    if i.lower() in name_text_dict.keys():
                        st_new = name_text_dict.get(i)
                        st_new += mes + '\n'
                        name_text_dict[i.lower()] = st_new
                    else:
                        name_text_dict[i.lower()] = mes
                    self.text_add(mes)



if __name__ == "__main__":
    global app
    app = App()
    app.mainloop()
