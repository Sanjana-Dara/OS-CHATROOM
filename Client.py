import json
import sys
import tkinter
#from PIL import Image, ImageTk
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import messagebox
from datetime import datetime
import pytz

class ClientHelper:
    # encode client message and send it.
    def encodemessage(self, request):

        body = {'message': request}
        body_string = json.dumps(body)
        method = 'POST'
        host = '35.246.29.33'
        url = '/chat'
        protocol = 'HTTP/1.1'
        user_agent = 'Chat Room'
        content_type = 'application/json'
        content_length = len(body)
        tz_NY = pytz.timezone('Asia/Kolkata') 
        datetime_NY = datetime.now(tz_NY)
        date=datetime_NY.strftime("%H:%M")
        #date = datetime.strftime('%a , %d  %b %Y %H:%M:%S GMT')
        #utc_dt_aware = datetime.datetime.now(datetime.timezone.utc)

        header = method + url + protocol + "\r\n" + 'Host: ' + host + "\r\n" + 'User-Agent: ' + user_agent + "\r\n" \
                 + 'Content-Type: ' + content_type + "\r\n" + 'Content-Length: ' + str(content_length) + "\r\n" + \
                 'Date: ' + date

        encodedMessage = header + "\r\n\r\n" + body_string

        return encodedMessage

def receive():
    _last_time = 0
    while True:
        try:
            # receive message from server.
            msg = client_socket.recv(buffer_size).decode("utf8")
            # split the header and body.
            msg_after_split = msg.split('\r\n\r\n')
            body = json.loads(msg_after_split[1])         
            if _last_time == 0:
                _last_time = body['time']
            time_passed = body['time'] - _last_time
            m, s = divmod(time_passed, 60)
            h, m = divmod(m, 60)
            tz_NY = pytz.timezone('Asia/Kolkata') 
            datetime_NY = datetime.now(tz_NY)
            date=datetime_NY.strftime("%H:%M")
            body['message'].format(time=date)
            msg_list.insert(tkinter.END, body['message'].format(time=date))
            _last_time = body['time']
        except OSError:  # Possibly client has left the chat.
            sys.exit()


def send(event=None): 
    msg = my_msg.get()
    my_msg.set("")  # Clears input field
    encoded_message = ClientHelper().encodemessage(msg)
    client_socket.send(encoded_message.encode())
    if msg == "quit":
        client_socket.close()
        top.destroy()
        top.quit()


def closing():
    # ask to close the application.
    if tkinter.messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        top.destroy()
        encoded_message = ClientHelper().encodemessage('has left the chat.')
        client_socket.send(encoded_message.encode())
        client_socket.close()
    else:
        pass

print("Enter a title for your room: ");
titlename = input()
top = tkinter.Tk()

top.title(titlename)

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.

msg_list = tkinter.Listbox(messages_frame, height=15, width=80,bg="black",fg="white",yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", closing)

# Socket and port name is defined and thread starts from here.
host = '35.246.29.33'
port = 9002
address = (host, port)
buffer_size = 1024
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(address)
receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()
