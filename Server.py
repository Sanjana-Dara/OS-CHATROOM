import re
import os
import json
import threading
import time
import socket
from threading import Thread
import pytz
from datetime import datetime
from json import dumps

class Helper:
    # encode the request and send it.
    def encodehttprequest(self, messsage, timestamp):
        body = {'message': messsage, 'time': timestamp}
        body_str = dumps(body)
        method = "POST"
        contentType = "application/json; " + '\n' + "Accept-charset = UTF-8"
        userAgent = "Chat Room"
        host = '127.0.0.1'
        contentlength = len(body_str)
        tz_NY = pytz.timezone('Asia/Kolkata') 
        datetime_NY = datetime.now(tz_NY)
        date=datetime_NY.strftime("%H:%M")
        titleheader = 'HTTP/1.1 200 OK\r\n'

        headers = method + ' ' + titleheader + "Host: " + host + '\r\n' + "Content-Length: " + str(contentlength) + "\r\n" + "User-Agent: " + \
                  userAgent + "\r\n" + "Content-Type: " + contentType + '\r\n' +  'Date: ' + date

        encodedMessage = headers + "\r\n\r\n" + body_str
        return encodedMessage

def accept_connections():
    while True:
        client, client_address = server_socket.accept()
        # print("%s:%s has connected." % client_address)
        # it encodes the message from client and sent it to server.
        encoded_message = Helper().encodehttprequest(
            messsage="Greetings from the server! Now type your name and press enter!", timestamp=time.time())
        client.send(encoded_message.encode())
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    try:
        while 1:
            # server receives the message every time client sends it.
            name = client.recv(buffer_size).decode("utf8")
            msg_after_split = name.split('\r\n\r\n')
            body = json.loads(msg_after_split[1])
            name = body['message']
            # check the bad name here.
            if re.match('^[a-z A-Z]+$', name):
                break
            else:
                error_message = Helper().encodehttprequest(messsage='Only alphabets are allowed, Numbers or special characters are not allowed.', timestamp=time.time())
                client.send(error_message.encode())
        print(name, ':handles by', threading.current_thread())
        welcome = 'Welcome %s! If you ever want to quit, type quit to exit.' % name
        # Use to generate response in HTTP format.
        print(Helper().encodehttprequest(messsage=welcome, timestamp=time.time()))
        encoded_message = Helper().encodehttprequest(messsage=welcome, timestamp=time.time())
        client.send(encoded_message.encode())
        msg = "%s has joined the chat!" % name
        broadcast(msg, name)
        clients[client] = name
        while True:
            # used to receive message from client.
            msg = client.recv(buffer_size).decode()
            msg_after_split = msg.split('\r\n\r\n')
            body = json.loads(msg_after_split[1])
            #print("body receive at the server is: ", body)
            msg = body['message']
            if msg != "quit":
                broadcast(msg, name, name + ": ")
            else:
                encoded_message = Helper().encodehttprequest(messsage='quit', timestamp=time.time())
                client.send(encoded_message.encode())
                client.close()
                del clients[client]
                broadcast("%s has left the chat." % name,name)
                break

    except OSError:
        pass
        # if someone left the chat it goes here.
        closed_connection_msg = ' has closed connection forcefully.'
        print(name, closed_connection_msg)
        file = open('log.txt', '+a')
        file.write(json.dumps({'name': name, 'message': closed_connection_msg}))
        file.write('\n')
        file.close()


def broadcast(msg, name, prefix=""):  # prefix is for name identification.
    #Broadcasts a message to all the clients.
    # write all the log to log.txt file.
    file = open('log.txt', '+a')
    file.write(json.dumps({'client_name': name, 'message': msg}))
    file.write('\n')
    file.close()
    for sock in clients:
        encoded_message = Helper().encodehttprequest(messsage=prefix + ' ({time}) - ' + msg, timestamp=time.time())
        #print(clients)
        #print("\n\nServer Broadcasted: ", encoded_message)
        sock.send(encoded_message.encode())


clients = {}
addresses = {}
# give host address of the server
host = '127.0.0.1'
# give port number of the server
port = 9008
# assign buffer size to store the data
buffer_size = 1024

# create socket to listen to client.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind host and port

server_socket.bind((host, port))
if __name__ == "__main__":
    server_socket.listen()
    print("Server is running.\nWaiting for connection...\n")
    restart_file = open('log.txt', 'r')
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    print('Thread with ID {} has been created.'.format(os.getpid()))
    ACCEPT_THREAD.join()
    server_socket.close()

